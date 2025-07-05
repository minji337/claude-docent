from anthropic import Anthropic

client = Anthropic()

response = client.beta.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": "파이썬 데이터 분석 입문 잔여석 알려줘"
    }],
    mcp_servers=[{
        "type": "url",
        #"url": "https://ef88bdc6-28f5-4f62-a437-3683a8a74f9c-00-tazcg59o1l4a.sisko.replit.dev/mcp/",
        "url": "https://ef88bdc6-28f5-4f62-a437-3683a8a74f9c-00-tazcg59o1l4a.sisko.replit.dev:8000/mcp/",
        "name": "ItCourseServer",
    }],
    betas=["mcp-client-2025-04-04"]
)

from pprint import pprint
pprint(response.model_dump())