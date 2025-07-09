from anthropic import Anthropic
import json
from pprint import pprint

user_message = """
한국 중국 일본의 수도를 <json> 태그로 감싸 JSON 포맷으로 응답하세요:
{{<국가>: {"수도":<수도 이름>, "인구":<국가의 전체 인구, e.g: 약 1억명>},.. }}
"""

client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    temperature=0,
     messages=[
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": "<json>"}
    ],
    stop_sequences=["</json>"]
)

pprint(json.loads(message.content[0].text))
