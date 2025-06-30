from anthropic import Anthropic
from .prompt_templates import system_prompt


class LLM:

    def __init__(self, model_name: str, system_prompt: str):
        self.client = Anthropic()
        self.model = model_name
        self.system_prompt = system_prompt

    def create_response_text(
        self,
        messages: list,
        temperature: float = 0.5,
        max_tokens: int = 2048,
        system_prompt: str | None = None,
        stop_sequences: list[str] = [],
    ) -> str:
        try:
            response = self.client.messages.create(
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or self.system_prompt,
                messages=messages,
                model=self.model,
                stop_sequences=stop_sequences,
                extra_headers={"anthropic-beta": "files-api-2025-04-14"},
            )
            print("대화 토큰 사용:", response.usage.model_dump_json())
            return response.content[0].text
        except Exception as e:
            print(f"[create_response error] {e}")
            raise e


claude_3_7 = LLM(model_name="claude-3-7-sonnet-20250219", system_prompt=system_prompt)
claude_4 = LLM(model_name="claude-sonnet-4-20250514", system_prompt=system_prompt)
claude_3_5_haiku = LLM(
    model_name="claude-3-5-haiku-20241022", system_prompt=system_prompt
)
