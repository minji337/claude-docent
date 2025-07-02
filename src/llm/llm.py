from anthropic import Anthropic
from .prompt_templates import (
    system_prompt as default_system_prompt,
    tool_system_prompt as default_tool_system_prompt,
)
import logging

logger = logging.getLogger(__name__)

#
class LLM:

    def __init__(self, model_name: str, system_prompt: str, tool_system_prompt):
        self.client = Anthropic()
        self.model = model_name
        self.system_prompt = system_prompt
        self.tool_system_prompt = tool_system_prompt

    def create_response_text(
        self,
        messages: list,
        temperature: float = 0.5,
        max_tokens: int = 2048,
        system_prompt: str | None = None,
        stop_sequences: list[str] | None = None,
    ) -> str:
        try:
            response = self.client.messages.create(
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or self.system_prompt,
                messages=messages,
                model=self.model,
                stop_sequences=stop_sequences,
            )
            return response.content[0].text
        except Exception as e:
            logging.error(f"[create_response error] {e}")
            raise e

    def create_tool_response(
        self,
        messages: list,
        tools: dict,
        temperature: float = 0,
        max_tokens: int = 2048,
        tool_choice: dict[str, str] = {"type": "auto"},
        tool_system_prompt: str | None = None,
        stop_sequences: list[str] = [],
    ):

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
            return response
        except Exception as e:
            logging.info(f"[LLM ERROR] {e}")
            raise e


claude_3_7 = LLM(
    model_name="claude-3-7-sonnet-20250219",
    system_prompt=default_system_prompt,
    tool_system_prompt=default_tool_system_prompt,
)
claude_4 = LLM(
    model_name="claude-sonnet-4-20250514",
    system_prompt=default_system_prompt,
    tool_system_prompt=default_tool_system_prompt,
)
claude_3_5_haiku = LLM(
    model_name="claude-3-5-haiku-20241022",
    system_prompt=default_system_prompt,
    tool_system_prompt=default_tool_system_prompt,
)
