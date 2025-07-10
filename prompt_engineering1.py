import anthropic

client = anthropic.Anthropic()

prompt = """
B612 소행성에서는 다음과 같이 연산합니다.
3 + 2 = 1
4 - 1 = 5 
6 - 2 = 8
2 + 3 = -1

당신은 현재 B612 소행성에 있습니다. 다음 문제에 답하세요.
7 - 3 = ?
"""

response = client.messages.create(
  model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", 'content': prompt},
    ]
)
print(response.content[0].text)
