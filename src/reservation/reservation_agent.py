from fastmcp.client.transports import MCPConfigTransport

import asyncio
import json
import logging
import os
import sys
import traceback
from contextlib import AsyncExitStack
from pathlib import Path
from urllib.parse import urlencode

from fastmcp import Client
from pydantic import BaseModel, Field
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from datetime import datetime

from llm import claude_4_5 as claude

# from llm import claude_3_5_haiku as claude
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
            "command": sys.executable,  # 현재 Python 인터프리터
            "args": [str(mcp_slack_path)],
            "transport": "stdio",
            "env": {
                  "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
              },
        },
        "weather": {"url": weather_url, "transport": "streamable-http"},
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


app = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))  # STEP-①


class SucessMail(BaseModel):
    application_form: str = Field(description="슬랙에 공지했던 형식과 내용")
    applicant_email: str
    docent_name: str
    docent_email: str


class FailMail(BaseModel):
    applicant_email: str
    failure_message: str


class EmailAddressRetriever(BaseModel):
    applicant_number: str


success_mail = {
    "name": "send_success_mail",
    "description": "예약 성공 메일",
    "input_schema": SucessMail.model_json_schema(),
}

fail_mail = {
    "name": "send_fail_mail",
    "description": "예약 실패 메일",
    "input_schema": FailMail.model_json_schema(),
}

email_address_retriever = {
    "name": "retrieve_email_address",
    "description": "신청자 이메일 주소 검색",
    "input_schema": EmailAddressRetriever.model_json_schema(),
}

local_tool_repository = {
    "send_success_mail": send_success_mail,
    "send_fail_mail": send_fail_mail,
    "retrieve_email_address": retrieve_email_address,
}


class Agent:

    def __init__(
        self, system_prompt: str, tools: list[dict], session: Client[MCPConfigTransport]
    ):
        self.system_prompt: str = system_prompt
        self.tools: list[dict] = tools
        self.session: Client[MCPConfigTransport] = session

    def _call_llm(self, messages: list[dict]) -> dict:
        response = claude.create_tool_response(
            messages=messages,
            temperature=0.0,
            max_tokens=2048,
            tools=self.tools,
            tool_system_prompt=self.system_prompt,
        )
        logger.info(f"\n\n<<ReAct message>>\n{response.content[0].text}\n\n")
        return response

    async def _call_tool(self, tool_name: str, tool_args: dict) -> dict:
        local_func = local_tool_repository.get(tool_name, None)
        if local_func:
            return local_func(**tool_args)
        else:
            return await self.session.call_tool(tool_name, tool_args)

    async def do_work(self, messages: list[dict]) -> dict:
        try:
            response = self._call_llm(messages)
            tries = 0
            while True:
                tool_content = next(
                    content
                    for content in response.content
                    if content.type == "tool_use"
                )
                tool_name, tool_args = tool_content.name, tool_content.input
                logger.info(f"call_tool {tool_name} {tool_args}")

                tool_result = await self._call_tool(tool_name, tool_args)
                logger.info(f"tool_result {tool_name} {tool_args} {tool_result}")
                messages.extend(
                    [
                        {"role": "assistant", "content": response.content},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_content.id,
                                    "content": str(tool_result),
                                }
                            ],
                        },
                    ]
                )
                response = self._call_llm(messages)
                # logger.info(f"do_work response...{response}")
                if response.stop_reason == "end_turn":
                    break
                if tries > 10:
                    raise ValueError("Too many tries")
                tries += 1

        except Exception as e:
            logger.error(f"do_work error: {e}")
            traceback.print_exc()
            raise e


class ReservationAgent:

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.tools: list[dict] = []
        self.socket_handler = None
        self.socket_task: asyncio.Task | None = None

    def _on_socket_task_done(self, task: asyncio.Task) -> None:
        try:
            task.result()
        except Exception as e:
            traceback.print_exc(e)
            logger.error(f"Slack SocketMode handler terminated with error: {e}")

    async def initialize_socket_handler(self):  # STEP-③ ~ STEP-⑦
        app_token = os.getenv("SLACK_APP_TOKEN")
        if not app_token:
            raise RuntimeError("SLACK_APP_TOKEN is not configured")

        self.socket_handler = AsyncSocketModeHandler(app, app_token)
        loop = asyncio.get_running_loop()
        self.socket_task = loop.create_task(self.socket_handler.start_async())
        self.socket_task.add_done_callback(self._on_socket_task_done)
        await asyncio.sleep(0)

    async def connect_server(self, timeout: float = 30.0 * 100) -> None:
        try:
            self.session = await self.exit_stack.enter_async_context(
                Client[MCPConfigTransport](config, timeout=timeout)
            )
            await self.setup_context()
            logger.info("MCP 서버 연결 완료")
        except Exception as e:
            logger.error(f"MCP 서버 연결 실패: {e}")
            traceback.print_exc()
            raise RuntimeError(str(e))

    async def setup_context(self) -> None:
        try:
            mcp_tools = await self.session.list_tools()
            self.tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in mcp_tools
            ] + [success_mail, fail_mail, email_address_retriever]
            logger.info(f"도구 목록: {[tool['name'] for tool in self.tools]}")

        except Exception as e:
            logger.error(f"도구 Setup 실패: {e}")
            traceback.print_exc()
            raise e

    def build_agents(self) -> None:
        self.notice_agent = Agent(
            system_prompt=notice_system_prompt.format(
                react_prompt=react_prompt, today=datetime.now().strftime("%Y-%m-%d")
            ),
            tools=self.tools,
            session=self.session,
        )
        self.reply_agent = Agent(
            system_prompt=reply_system_prompt.format(react_prompt=react_prompt),
            tools=self.tools,
            session=self.session,
        )
        self.expiry_check_agent = Agent(
            system_prompt=expiry_check_system_prompt.format(
                react_prompt=react_prompt, today=datetime.now().strftime("%Y-%m-%d")
            ),
            tools=self.tools,
            session=self.session,
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

        await self.notice_agent.do_work(messages)

    async def make_reply(self, event: dict):
        messages = [
            {
                "role": "user",
                "content": json.dumps(event, ensure_ascii=False),
            },
        ]
        await self.reply_agent.do_work(messages)

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
            await self.exit_stack.aclose()
            logger.info("MCP 서버 연결 해제")
        except Exception as e:
            logger.error(f"정리 중 오류 발생: {e}")
            traceback.print_exc()
            raise e


reservation_agent: ReservationAgent = None


@app.event("message")  # STEP-②
async def on_message(event):  # STEP-⑦, STEP-⑧
    if event.get("bot_id") or not event.get("user") or not event.get("thread_ts"):
        return
    # 슬랙 소켓 모드 타임아웃 방지를 위해 백그라운드 태스크로 처리
    asyncio.create_task(reservation_agent.make_reply(event))
