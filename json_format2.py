from anthropic import Anthropic

user_message = """
한국 중국 일본의 수도를 다음 JSON 포맷으로 응답하세요:
{{<국가>: <수도>}}
"""
client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    temperature=0,
    messages=[
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": "{"}
    ],
)

print("{" + message.content[0].text)

