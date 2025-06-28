from relics import Relics


class DocentBot:

    def __init__(self):
        self.messages = []
        self.relics = Relics()

    def _present_relic(self):
        response_message = f" 이 작품은 {self.relics.current['title']}입니다."
        self.messages.append({"role": "assistant", "content": response_message})
        self.relics.set_presented(True)

    def _overflow(self):
        self.messages.append(
            {"role": "assistant", "content": "준비한 작품울 모두 소개했습니다."}
        )

    def _underflow(self):
        self.messages.append({"role": "assistant", "content": "첫 번째 작품입니다."})
        self.relics.index = 0

    def move(self, is_next: bool):
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

        if not self.relics.current["is_presented"]:
            self._present_relic()

    def answer(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        response_message = (
            f"{self.relics.current['title']}에 대해 대화를 나누고 있습니다."
        )
        self.messages.append({"role": "assistant", "content": response_message})
        return response_message

    def get_conversation(self):
        conversation = []
        for message in self.messages:
            text_message = message["content"].strip()
            conversation.append({"role": message["role"], "content": text_message})
        return conversation
