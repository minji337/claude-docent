import anthropic

client = anthropic.Anthropic()

user_messages = ["가장 최근에 월드컵이 언제 열렸지?", "대한민국의 성적은?", "이전 대회에 비해 잘한거니?"]
messages = []

for i, user_msg in enumerate(user_messages):
    messages.append({"role": "user", "content": user_msg})
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=messages,
        temperature=0
    )
    print(f"Turn {i+1}:")
    print(response.content[0].text)
    print("-" * 100)
    messages.append({"role": "assistant", "content": response.content[0].text})

