from anthropic import Anthropic
from anthropic.types import Message
from .prompt_templates import (
    system_prompt as default_system_prompt,
    tool_system_prompt as default_tool_system_prompt,
)
import logging
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class LLM:

    def __init__(self, model_name: str, system_prompt: str, tool_system_prompt: str):
        self.client = Anthropic()
        self.async_client = AsyncAnthropic()
        self.model = model_name
        self.system_prompt = system_prompt
        self.tool_system_prompt = tool_system_prompt

    async def create_container(self) -> dict:
        container = {
            "skills": [
                {
                    "type": "custom",
                    "skill_id": local_museums_skill_id,
                    "version": "latest",
                }
            ],
        }
        response = await self.async_client.beta.messages.create(
            max_tokens=1024,
            messages=[{"role": "user", "content": "지역 국립박물관 초기화"}],
            model=self.model,
            betas=["code-execution-2025-08-25", "skills-2025-10-02"],
            container=container,
            tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
        )
        container["id"] = response.container.id
        return container

    def create_response_text(
        self,
        messages: list,
        temperature: float = 0.5,
        max_tokens: int = 2048,
        system_prompt: str | None = None,
        stop_sequences: list[str] | None = None,
        container: dict | None = None,
    ) -> str:
        try:
            response = self.client.beta.messages.create(
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or self.system_prompt,
                messages=messages,
                model=self.model,
                stop_sequences=stop_sequences,
                betas=[
                    "files-api-2025-04-14",
                    "code-execution-2025-08-25",
                    "skills-2025-10-02",
                ],
                container=container,
                tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
            )
            logger.info(f"대화 토큰 사용: {response.usage.model_dump_json()}")
            result_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    result_text += block.text + "\n"
            return result_text.strip()
        except Exception as e:
            logger.error(f"[create_response error] {e}")
            raise e

    def create_tool_response(
        self,
        messages: list,
        tools: dict,
        temperature: float = 0,
        max_tokens: int = 2048,
        tool_choice: dict[str, str] = {"type": "auto"},
        tool_system_prompt: str | None = None,
        stop_sequences: list[str] | None = None,
    ) -> Message:

        try:
            response = self.client.messages.create(
                max_tokens=max_tokens,
                temperature=temperature,
                tools=tools,
                tool_choice=tool_choice,
                system=[
                    {
                        "type": "text",
                        "text": tool_system_prompt or self.tool_system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    },
                ],
                messages=messages,
                model=self.model,
                stop_sequences=stop_sequences,
            )
            logger.info(f"도구 토큰 사용: {response.usage.model_dump_json()}")
            return response
        except Exception as e:
            logger.error(f"[LLM ERROR] {e}")
            raise e


claude_4_6 = LLM(
    model_name="claude-sonnet-4-6",
    system_prompt=default_system_prompt,
    tool_system_prompt=default_tool_system_prompt,
)

claude_4_5 = LLM(
    model_name="claude-sonnet-4-5",
    system_prompt=default_system_prompt,
    tool_system_prompt=default_tool_system_prompt,
)

claude_3_5_haiku = LLM(
    model_name="claude-4-5-haiku-20251021",
    system_prompt=default_system_prompt,
    tool_system_prompt=default_tool_system_prompt,
)


def find_existing_skill(display_title: str) -> str | None:
    client = Anthropic()

    skills = client.beta.skills.list(source="custom", betas=["skills-2025-10-02"])

    for skill in skills.data:
        if skill.display_title == display_title:
            return skill.id
    return None


local_museums_skill_id = find_existing_skill("지역 국립박물관 안내")
