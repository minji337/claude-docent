import anthropic

client = anthropic.Anthropic()

for i in range(3):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0,
        messages=[{"role": "user", "content": "여섯 어절로 당신을 소개하세요."}],
    )
    print(f"{i+1}번째: {response.content[0].text}")
