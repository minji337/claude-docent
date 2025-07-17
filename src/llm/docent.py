from anthropic import Anthropic
from relics import Relics, SearchedRelics
from utils import get_base64_data, leaflet_id, guide_program_id
import logging
from .prompt_templates import (
    guide_instruction,
    revisit_instruction,
    museum_info_prompt,
)
from .llm import claude_4 as claude
from .tools import use_tools, ToolData

logger = logging.getLogger(__name__)


class ExceptionHandler:

    @staticmethod
    def overflow(messages: list, relics: Relics) -> Relics:
        if isinstance(relics, SearchedRelics):
            messages.append(
                {
                    "role": "assistant",
                    "content": "검색된 전시물을 모두 소개했습니다. 다음 전시물을 소개하겠습니다.",
                }
            )
            relics.original.index += 1
            return relics.original
        else:
            messages.append(
                {
                    "role": "assistant",
                    "content": "준비한 전시물을 모두 소개했습니다. 오늘 유익한 시간 되었기를 바랍니다. 감사합니다.",
                }
            )
            return relics

    @staticmethod
    def underflow(messages: list, relics: Relics) -> None:
        messages.append({"role": "assistant", "content": "첫 번째 작품입니다."})
        relics.index = 0


class InstructionHandler:

    # first_present_index = 0
    first_present_index = 1

    def __init__(self):
        self.last_guide_id = ""

    def add_museum_info(self, messages: list) -> None:
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {"type": "file", "file_id": leaflet_id},
                    },
                    {
                        "type": "document",
                        "source": {
                            "type": "file",
                            "file_id": guide_program_id,
                        },
                    },
                    {
                        "type": "text",
                        "text": museum_info_prompt,
                        "cache_control": {"type": "ephemeral"},
                    },
                ],
            }
        )

    def add_guide(self, relics: Relics, messages: list) -> None:
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
        if len(messages) == self.first_present_index + 1:
            messages[self.first_present_index]["content"][1]["cache_control"] = {
                "type": "ephemeral"
            }

    def _remove_before_guide(self, messages: list) -> None:
        for idx in reversed(range(len(messages))):
            if self.first_present_index <= idx:
                continue
            if not isinstance(messages[idx]["content"], list):
                continue
            if "text" not in messages[idx]["content"][1]:
                continue
            text_message: str = messages[idx]["content"][1]["text"]
            if "<relic_information>" in text_message:
                messages.pop(idx)
                break

    def check_and_add(self, relics: Relics, messages: list) -> None:
        if self.last_guide_id == relics.current_id:
            return
        self.add_guide(relics, messages)
        messages.append({"role": "user", "content": revisit_instruction})


class DocentBot:

    greeting_message = """
    안녕하세요? 저는 이곳 박물관에서 근무하는 인공지능 봇 뮤지입니다.  
    이곳에 전시된 작품에 대한 설명은 물론 저의 감상까지도 자세히 말씀드려요.   
    그럼 첫 번째 전시물을 소개해드릴게요! 
    """

    def __init__(self):
        self.messages = []
        self.relics = Relics()
        self.instruction = InstructionHandler()
        self.instruction.add_museum_info(self.messages)

    def greet(self) -> str:
        return self.greeting_message

    def _present_relic(self) -> None:
        self.instruction.add_guide(self.relics, self.messages)
        response_message = claude.create_response_text(messages=self.messages)
        self.messages.append({"role": "assistant", "content": response_message})
        self.relics.set_presented(True)

    def move(self, is_next: bool) -> None:
        if is_next:
            try:
                self.relics.next()
            except IndexError as e:
                self.relics = ExceptionHandler.overflow(self.messages, self.relics)
        else:
            try:
                self.relics.previous()
            except ValueError as e:
                ExceptionHandler.underflow(self.messages, self.relics)

        if not self.relics.is_presented():
            self._present_relic()

    # 전시물 검색 실습용
    # def answer(self, user_input: str) -> str:
    #     self.instruction.check_and_add(self.relics, self.messages)
    #     self.messages.append({"role": "user", "content": user_input})
    #     searched_database, message_dict = use_tools(
    #         self.get_conversation(),
    #         self.relics.original_database,
    #     )
    #     if searched_database:
    #         self.relics = SearchedRelics(searched_database, self.relics.original)
    #         self.messages.append(message_dict)
    #         response_message = message_dict["content"]
    #     else:
    #         response_message = claude.create_response_text(messages=self.messages)
    #         self.messages.append({"role": "assistant", "content": response_message})
    #     return response_message

    # 역사적 사실 검색 실습용
    def answer(self, user_input: str) -> tuple[list, str]:
        self.instruction.check_and_add(self.relics, self.messages)
        self.messages.append({"role": "user", "content": user_input})
        tool_data: ToolData | None = None
        message_dict: dict[str, str] | None = None
        conversation = self.get_conversation()
        tool_data, message_dict = use_tools(
            conversation,
            self.relics.original_database,
        )
        references: list = []
        match tool_data:
            case {"type": "relics", "items": items}:
                if len(items) > 0:
                    self.relics = SearchedRelics(items, self.relics.original)
                self.messages.append(message_dict)
                response_message = message_dict["content"]
            case {"type": "facts", "items": references}:
                self.messages.append(message_dict)
                response_message = claude.create_response_text(messages=self.messages)
                self.messages.append({"role": "assistant", "content": response_message})
            case {"type": "needs_image", "items": needs_image}:
                messages = (
                    self.messages
                    if needs_image
                    else self.museum_info_message + conversation
                )
                response_message = claude.create_response_text(messages=messages)
                self.messages.append({"role": "assistant", "content": response_message})
            case _:
                response_message = claude.create_response_text(messages=self.messages)
                self.messages.append({"role": "assistant", "content": response_message})

        return references, response_message

    @property
    def museum_info_message(self) -> list:
        return [self.messages[0]]

    def get_conversation(self) -> list:
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
