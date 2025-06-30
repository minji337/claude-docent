from anthropic import Anthropic
from relics import Relics
from utils import get_base64_data
import logging
from .prompt_templates import (
    system_prompt,
    guide_instruction,
    revisit_instruction
)
from .llm import claude_4 as claude

logger = logging.getLogger(__name__)


class ExceptionHandler:

    @staticmethod
    def overflow(messages: list, relics: Relics):        
        messages.append(
            {
                "role": "assistant",
                "content": "준비한 전시물을 모두 소개했습니다. 오늘 유익한 시간 되었기를 바랍니다. 감사합니다.",
            }
        )
        return relics
    
    @staticmethod
    def underflow(messages: list, relics: Relics):
        messages.append({"role": "assistant", "content": "첫 번째 작품입니다."})
        relics.index = 0
    


class InstructionHandler:

    first_present_index = 1
    
    def __init__(self):
        self.last_guide_id = ""
    
    def add_guide(self, relics: Relics, messages: list):    
        self._remove_before_guide(messages)    
        guide_instruction_prompt = guide_instruction.format(
            label=relics.current["label"],
            content=relics.current["content"],
        )
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": get_base64_data(relics.current["img_path"]),
                        },
                    },
                    {"type": "text", "text": guide_instruction_prompt},
                ],
            }
        )
        self.last_guide_id = relics.current_id
    
    def _remove_before_guide(self, messages: list):
        for idx in reversed(range(len(messages))):
            if not isinstance(messages[idx]["content"], list):
                continue
            if "text" not in messages[idx]["content"][1]:
                continue
            text_message: str = messages[idx]["content"][1]["text"]
            if "<relic_information>" in text_message:
                messages.pop(idx)
                break
    
    def check_and_add(self, relics: Relics, messages: list):
        if self.last_guide_id == relics.current_id:
            return
        self.add_guide(relics, messages)
        messages.append({"role": "user", "content": revisit_instruction})
    

class DocentBot:

    def __init__(self, model_name="claude-sonnet-4-20250514"):
        self.model = model_name
        self.messages = []
        self.relics = Relics()
        self.instruction = InstructionHandler()

    def _present_relic(self):
        self.instruction.add_guide(self.relics, self.messages)
        response_message = claude.create_response_text(messages=self.messages)
        self.messages.append({"role": "assistant", "content": response_message})
        self.relics.set_presented(True)    

    def move(self, is_next: bool):
        if is_next:
            try:
                self.relics.next()
            except IndexError as e:
                ExceptionHandler.overflow(self.messages, self.relics)
        else:
            try:
                self.relics.previous()
            except ValueError as e:
                ExceptionHandler.underflow(self.messages, self.relics)

        if not self.relics.is_presented(): 
            self._present_relic()

    def answer(self, user_input: str) -> str:
        self.instruction.check_and_add(self.relics, self.messages)
        self.messages.append({"role": "user", "content": user_input})
        response_message = claude.create_response_text(messages=self.messages)
        self.messages.append({"role": "assistant", "content": response_message})
        return response_message

    def get_conversation(self):
        conversation = []
        for message in self.messages[1:]:
            if isinstance(message["content"], list):
                text_message: str = message["content"][1]["text"]
            else:
                text_message = message["content"]
            text_message = text_message.strip()
            if text_message.startswith("<system_command>"):
                continue
            conversation.append({"role": message["role"], "content": text_message})
        return conversation

