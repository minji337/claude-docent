import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="당신은 제주도 방언을 잘 쓰는 여행 가이드입니다. 3 문장 이내로 짧게 답하세요.",
    messages=[{"role": "user", "content": "제주도에 유명한 관광지는 어디인가요?"}]
)
print(response.content[0].text)
