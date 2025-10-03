import anthropic

client = anthropic.Anthropic()

for i in range(3):
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        temperature=1,
        messages=[{"role": "user", "content": "당신을 두 문장으로 소개하세요."}],
    )
    print(f"{i+1}번째: {response.content[0].text}")
