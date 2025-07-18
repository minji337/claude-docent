from anthropic import Anthropic
from relics import Relics
from utils import get_base64_data
import logging
from .prompt_templates import (
    system_prompt,
    guide_instruction,
    revisit_instruction
)

logger = logging.getLogger(__name__)

client = Anthropic()

class DocentBot:

    def __init__(self, model_name="claude-sonnet-4-20250514"):
        self.model = model_name
        self.messages = []
        self.relics = Relics()
        self.last_guide_id = ""
        
    def _create_response(self) -> str:
        try:
            response = client.messages.create(
                max_tokens=2048,
                temperature=0.5,
                system=system_prompt,
                messages=self.messages,
                model=self.model,
            )
            return response.content[0].text
        except Exception as e:
            logger.info(f"Error: {str(e)}")
            raise e

    def _add_guide_instruction(self) -> None:
        guide_instruction_prompt = guide_instruction.format(
            label=self.relics.current["label"],
            content=self.relics.current["content"],
        )
        self.messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": get_base64_data(self.relics.current["img_path"]),
                        },
                    },
                    {"type": "text", "text": guide_instruction_prompt},
                ],
            }
        )
        self.last_guide_id = self.relics.current_id

    def _present_relic(self) -> None:
        self._add_guide_instruction()
        response_message = self._create_response()
        self.messages.append({"role": "assistant", "content": response_message})
        self.relics.set_presented(True)

    def _check_and_add(self) -> None:
        if self.last_guide_id == self.relics.current_id:
            return
        self._add_guide_instruction()
        self.messages.append({"role": "user", "content": revisit_instruction})

    def _overflow(self) -> None:
        self.messages.append(
            {"role": "assistant", "content": "준비한 작품을 모두 소개했습니다."}
        )

    def _underflow(self) -> None:
        self.messages.append({"role": "assistant", "content": "첫 번째 작품입니다."})
        self.relics.index = 0

    def move(self, is_next: bool) -> None:
        if is_next:
            try:
                self.relics.next()
            except IndexError as e:
                self._overflow()
        else:
            try:
                self.relics.previous()
            except ValueError as e:
                self._underflow()

        if not self.relics.is_presented(): 
            self._present_relic()

    def answer(self, user_input: str) -> str:
        self._check_and_add()
        self.messages.append({"role": "user", "content": user_input})
        response_message = self._create_response()
        self.messages.append({"role": "assistant", "content": response_message})
        return response_message

    def get_conversation(self):
        conversation = []
        for message in self.messages:
            if isinstance(message["content"], list):
                text_message: str = message["content"][1]["text"]
            else:
                text_message = message["content"]
            text_message = text_message.strip()
            if text_message.startswith("<system_command>"):
                continue
            conversation.append({"role": message["role"], "content": text_message})
        return conversation

