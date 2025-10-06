import os

from typing import Optional
from contextlib import AsyncExitStack
import traceback
from fastmcp import Client
import json
import os
from pydantic import BaseModel, Field
import asyncio
import base64

from llm import claude_4_5 as claude
from llm.prompt_templates import slackbot_system_prompt, slackbot_message
from .email_sender import send_success_mail, send_fail_mail
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

SMITHERY_API_KEY = os.getenv("SMITHERY_API_KEY")

slack_url = (
    f"https://server.smithery.ai/@smithery-ai/slack/mcp?api_key={SMITHERY_API_KEY}"
)

base_slack_url = "https://server.smithery.ai/@smithery-ai/slack/mcp"
params = {"api_key": SMITHERY_API_KEY}
slack_url = f"{base_slack_url}?{urlencode(params)}"

base_weather_url = "https://server.smithery.ai/@glassBead-tc/weather-mcp/mcp"
params = {"api_key": SMITHERY_API_KEY}
weather_url = f"{base_weather_url}?{urlencode(params)}"

config = {
    "mcpServers": {
        "slack": {"url": slack_url, "transport": "streamable-http"},
        "weather": {"url": weather_url, "transport": "streamable-http"},
    }
}

application_template = """
🏺 프로그램: {program}
📅 방문일자: {visit_date}
⏰ 방문시간: {visit_hours}
👥 방문인원: {visitors}
🕒 신청일시: {application_time}
🕒 신청자번호: {applicant_number}
""".strip()


def modify_input_schema(input_schema) -> dict:
    if "properties" in input_schema:
        if "required" not in input_schema or not isinstance(
            input_schema["required"], list
        ):
            input_schema["required"] = list(input_schema["properties"].keys())
        else:
            for key in input_schema["properties"].keys():
                if key not in input_schema["required"]:
                    input_schema["required"].append(key)

        for key, value in input_schema["properties"].items():
            if "default" in value:
                del value["default"]

    return input_schema


class Report(BaseModel):
    is_success: bool = Field(description="예약 성공 여부")
    failure_message: Optional[str] = Field(description="예약 실패 사유")
    thread_ts: str = Field(description="스레드의 timestamp")
    channel_id: str = Field(description="스레드가 있는 채널의 id")
    docent_name: Optional[str] = Field(description="예약된 경우 도슨트의 이름")
    docent_email: Optional[str] = Field(description="예약된 경우 도슨트의 이메일")


report_reservation = {
    "name": "report_reservation",
    "description": "예약 작업 수행 결과",
    "input_schema": Report.model_json_schema(),
}


class ReservationAgent:

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.tools: list[dict] = []
        self.reply_ts: dict[str, float] = {}

    async def connect_server(self, timeout: float = 30.0) -> None:
        try:
            self.session = await self.exit_stack.enter_async_context(
                Client(config, timeout=timeout)
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
                    # "input_schema": modify_input_schema(tool.inputSchema),
                    "input_schema": tool.inputSchema,
                }
                for tool in mcp_tools
            ] + [report_reservation]
            logger.info(f"도구 목록: {[tool['name'] for tool in self.tools]}")

        except Exception as e:
            logger.error(f"도구 Setup 실패: {e}")
            traceback.print_exc()
            raise e

    def _call_llm(self, messages: list[dict]) -> dict:
        response = claude.create_tool_response(
            messages=messages,
            temperature=0.0,
            max_tokens=1024,
            tools=self.tools,
            tool_system_prompt=slackbot_system_prompt,
        )
        logger.info(f"\n\n<<ReAct message>>\n{response.content[0].text}\n\n")
        return response

    async def _polling_result(
        self, application_id: str, tool_name, tool_args: str, tool_result: dict
    ) -> str | dict:
        for _ in range(1, 10):
            message = json.loads(tool_result[0].text)["messages"]
            if (
                "latest_reply" in message[0]
                and float(message[0]["latest_reply"]) > self.reply_ts[application_id]
            ):
                self.reply_ts[application_id] = float(message[0]["latest_reply"])
                return tool_result
            await asyncio.sleep(5)  # 실제 운영 시에는 대기 시간을 적절히 늘려야 함.
            tool_result = await self.session.call_tool(tool_name, tool_args)
        return "응답한 문화해설사가 없습니다. 요청 건 취소가 필요합니다."

    async def _delegate_to_slackbot(
        self, application_id: str, messages: list[dict]
    ) -> dict:
        response = self._call_llm(messages)
        tries = 0
        while True:
            tool_content = next(
                content for content in response.content if content.type == "tool_use"
            )
            tool_name, tool_args = tool_content.name, tool_content.input
            logger.info(f"call_tool {tool_name} {tool_args}")

            if tool_name == "report_reservation":
                return tool_args

            tool_result = await self.session.call_tool(tool_name, tool_args)
            logger.info(f"tool_result {tool_name} {tool_args} {tool_result}")

            if "slack_get_thread_replies" in tool_name:
                tool_result = await self._polling_result(
                    application_id, tool_name, tool_args, tool_result
                )

            logger.info(f"tool_result: {tool_result}")
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
            if tries > 10:
                raise ValueError("Too many tries")
            tries += 1

    async def make_reservation(self, application: dict) -> None:
        application_without_email = {}
        for k, v in application.items():
            if k == "applicant_email":
                continue
            if k == "application_time":
                application_without_email[k] = v.rsplit(".", 1)[0]
            else:
                application_without_email[k] = v

        application_form = application_template.format(**application_without_email)
        input_messages = [
            {
                "role": "user",
                "content": slackbot_message.format(application_form=application_form),
            },
        ]

        application_id: str = application["application_time"]
        self.reply_ts[application_id] = 0.0
        slackbot_response = await self._delegate_to_slackbot(
            application_id, input_messages
        )
        receiver = application["applicant_email"]
        try:
            if slackbot_response["is_success"]:
                send_success_mail(application_form, receiver, slackbot_response)
            else:
                send_fail_mail(receiver, slackbot_response["failure_message"])
        except Exception as e:
            logger.error(f"메일 전송 실패: {e}")
            traceback.print_exc()
            raise e

    async def cleanup(self) -> None:
        try:
            await self.exit_stack.aclose()
            logger.info("MCP 서버 연결 해제")
        except Exception as e:
            logger.error(f"정리 중 오류 발생: {e}")
            traceback.print_exc()
            raise e


async def main() -> None:
    agent = ReservationAgent()
    await agent.connect_server()
    await agent.make_reservation(
        {
            "program": "대표 유물 해설",
            "visit_date": "2025-06-09 (월)",
            "visit_hours": "11:00",
            "visitors": 1,
            "applicant_email": "heyjin337@gmail.com",
        }
    )


if __name__ == "__main__":
    asyncio.run(main())
