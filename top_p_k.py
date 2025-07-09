import anthropic

client = anthropic.Anthropic()

top_p=0.1
for i in range(3):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        top_p=top_p,
        messages=[{"role": "user", "content": "여섯 어절로 당신을 소개하세요."}]
    )
    print(f"top_p={top_p} ===> {i+1}번째: {response.content[0].text}")

print()

top_k=1
for i in range(3):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        top_k=top_k,
        messages=[{"role": "user", "content": "여섯 어절로 당신을 소개하세요."}]
    )
    print(f"top_k={top_k} ===> {i+1}번째: {response.content[0].text}")
