import anthropic

client = anthropic.Anthropic()

user_query = "한국 증시 기사를 조사한 뒤 핵심 기사 하나를 선별해서 100자 이내로 요약해."

messages = [
    {
        "role": "user",
        "content": user_query
    }
]

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=messages,
    tools=[
        {
            "name": "web_search",
            "type": "web_search_20250305",
            "max_uses": 5
        },
        {
            "name": "web_fetch",
            "type": "web_fetch_20250910",
            "max_uses": 1,
            "citations": {"enabled": True}
        }
    ],
    betas=["web-fetch-2025-09-10"]
)

print(response)
