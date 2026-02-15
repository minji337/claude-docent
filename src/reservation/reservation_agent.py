import asyncio
import json
import logging
import os
import sys
import traceback
from pathlib import Path
from urllib.parse import urlencode

from pydantic import BaseModel, Field
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from datetime import datetime
from zoneinfo import ZoneInfo


from llm.prompt_templates import (
    react_prompt,
    notice_system_prompt,
    reply_system_prompt,
    expiry_check_system_prompt,
    notice_message,
    expiry_check_message,
)
from .email_sender import (
    send_success_mail,
    send_fail_mail,
    retrieve_email_address,
    store_email_address,
)
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


logger = logging.getLogger(__name__)

SMITHERY_API_KEY = os.getenv("SMITHERY_API_KEY")

# 프로젝트 루트에서 mcp-slack-python 디렉토리 경로 계산
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
mcp_slack_path = project_root / "mcp-slack-python" / "main.py"

base_weather_url = "https://server.smithery.ai/@isdaniel/mcp_weather_server/mcp"

params = {"api_key": SMITHERY_API_KEY}
weather_url = f"{base_weather_url}?{urlencode(params)}"

config = {
    "mcpServers": {
        "slack": {
            "type": "stdio",
            "command": sys.executable,  # 현재 Python 인터프리터
            "args": [str(mcp_slack_path)],
        },
        "weather": {"type": "http", "url": weather_url},
    }
}

application_template = """
🏺 프로그램: {program}
📅 방문일자: {visit_date}
⏰ 방문시간: {visit_hours}
👥 방문인원: {visitors}
🕒 신청일시: {application_time}
🔢 신청자번호: {applicant_number}
""".strip()


app = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))
KST = ZoneInfo("Asia/Seoul")

class SuccessMail(BaseModel):
    application_form: str = Field(description="슬랙에 공지했던 형식과 내용")
    applicant_email: str
    docent_name: str
    docent_email: str


class FailMail(BaseModel):
    applicant_email: str
    failure_message: str


class EmailAddressRetriever(BaseModel):
    applicant_number: str


# Local tools - wrapped as SDK MCP tools
@tool(
    "send_success_mail",
    "예약 성공 메일",
    SuccessMail.model_json_schema(),
)
async def send_success_mail_tool(args: dict):
    result = send_success_mail(**args)
    return {"content": [{"type": "text", "text": str(result)}]}


@tool(
    "send_fail_mail",
    "예약 실패 메일",
    FailMail.model_json_schema(),
)
async def send_fail_mail_tool(args: dict):
    result = send_fail_mail(**args)
    return {"content": [{"type": "text", "text": str(result)}]}


@tool(
    "retrieve_email_address",
    "신청자 이메일 주소 검색",
    EmailAddressRetriever.model_json_schema(),
)
async def retrieve_email_address_tool(args: dict):
    result = retrieve_email_address(**args)
    return {"content": [{"type": "text", "text": str(result)}]}


class Agent:

    def __init__(
        self,
        system_prompt: str,
        mcp_servers: dict,
        allowed_tools: list[str],
    ):
        self.mcp_servers: dict = mcp_servers
        self.allowed_tools: list[str] = allowed_tools
        self.options = ClaudeAgentOptions(
            system_prompt=repr(system_prompt),
            mcp_servers=self.mcp_servers,
            allowed_tools=self.allowed_tools,
            permission_mode="bypassPermissions",
            model="sonnet"
        )

    async def do_work(self, messages: list[dict]) -> dict:

        try:
            self.options.system_prompt = self.options.system_prompt.replace(
                "$today", datetime.now(KST).strftime("%Y-%m-%d")
            )

            async with ClaudeSDKClient(options=self.options) as client:
                user_content = messages[-1]["content"]
                if isinstance(user_content, list):
                    user_content = user_content[0].get("text", "")

                await client.query(user_content)

                final_message = None
                async for message in client.receive_response():
                    logger.info(f"Received: {message}")
                    final_message = message

                if final_message:
                    return {
                        "role": "assistant",
                        "content": final_message.result,
                    }
                else:
                    return {
                        "role": "assistant",
                        "content": "작업이 완료되었습니다.",
                    }

        except Exception as e:
            logger.error(f"do_work error: {e}")
            traceback.print_exc()
            raise e


class ReservationAgent:

    def __init__(self):
        self.socket_handler = None
        self.socket_task: asyncio.Task | None = None
        self.local_mcp_server = None
        self.mcp_servers = {}

    def _on_socket_task_done(self, task: asyncio.Task) -> None:
        try:
            task.result()
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Slack SocketMode handler terminated with error: {e}")

    async def initialize_socket_handler(self):
        app_token = os.getenv("SLACK_APP_TOKEN")
        if not app_token:
            raise RuntimeError("SLACK_APP_TOKEN is not configured")

        self.socket_handler = AsyncSocketModeHandler(app, app_token)
        loop = asyncio.get_running_loop()
        self.socket_task = loop.create_task(self.socket_handler.start_async())
        self.socket_task.add_done_callback(self._on_socket_task_done)
        await asyncio.sleep(0)

    async def connect_server(self) -> None:
        try:
            self.local_mcp_server = create_sdk_mcp_server(
                name="local_tools",
                version="1.0.0",
                tools=[
                    send_success_mail_tool,
                    send_fail_mail_tool,
                    retrieve_email_address_tool,
                ],
            )

            self.mcp_servers = {
                "local_tools": self.local_mcp_server,
                **config["mcpServers"],
            }

            logger.info("MCP 서버 설정 완료")

        except Exception as e:
            logger.error(f"도구 Setup 실패: {e}")
            traceback.print_exc()
            raise e

    def build_agents(self) -> None:
        allowed_tools = [
            "mcp__local_tools__*",  # All local tools
            "mcp__slack__*",  # All Slack tools
            "mcp__weather__*",  # All Weather tools
        ]

        self.notice_agent = Agent(
            system_prompt=notice_system_prompt.format(react_prompt=react_prompt),
            mcp_servers=self.mcp_servers,
            allowed_tools=allowed_tools
        )
        self.reply_agent = Agent(
            system_prompt=reply_system_prompt.format(react_prompt=react_prompt),
            mcp_servers=self.mcp_servers,
            allowed_tools=allowed_tools
        )
        self.expiry_check_agent = Agent(
            system_prompt=expiry_check_system_prompt.format(react_prompt=react_prompt),
            mcp_servers=self.mcp_servers,
            allowed_tools=allowed_tools
        )

    async def make_reservation(self, application: dict) -> None:
        application_without_email = {}
        applicant_number: str = application["applicant_number"]
        for item_name, item_value in application.items():
            if item_name == "applicant_email":
                store_email_address(applicant_number, item_value)
                continue
            if item_name == "application_time":
                application_without_email[item_name] = item_value.rsplit(".", 1)[0]
            else:
                application_without_email[item_name] = item_value

        application_form = application_template.format(**application_without_email)

        messages = [
            {
                "role": "user",
                "content": notice_message.format(application_form=application_form),
            },
        ]

        response = await self.notice_agent.do_work(messages)
        logger.info(f"response: {response}")

    async def make_reply(self, event: dict):
        messages = [
            {
                "role": "user",
                "content": json.dumps(event, ensure_ascii=False),
            },
        ]
        response = await self.reply_agent.do_work(messages)
        logger.info(f"response: {response}")

    async def check_expired_reservations(self) -> None:
        logger.info("만료된 예약 체크 시작")
        messages = [
            {"role": "user", "content": expiry_check_message},
        ]
        try:
            await self.expiry_check_agent.do_work(messages)
            logger.info("만료된 예약 체크 완료")
        except Exception as e:
            logger.error(f"만료된 예약 체크 중 오류: {e}")
            traceback.print_exc()

    async def cleanup(self) -> None:
        try:
            if self.socket_task and not self.socket_task.done():
                self.socket_task.cancel()
                try:
                    await self.socket_task
                except asyncio.CancelledError:
                    pass
            self.socket_task = None
            self.socket_handler = None
            logger.info("MCP 서버 연결 해제")
        except Exception as e:
            logger.error(f"정리 중 오류 발생: {e}")
            traceback.print_exc()
            raise e


reservation_agent: ReservationAgent | None = None


@app.event("message")
async def on_message(event):
    if event.get("bot_id") or not event.get("user") or not event.get("thread_ts"):
        return
    # 슬랙 소켓 모드 타임아웃 방지를 위해 백그라운드 태스크로 처리
    asyncio.create_task(reservation_agent.make_reply(event))
