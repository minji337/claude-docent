import anthropic

client = anthropic.Anthropic()

system_prompt = """
당신은 사용자들의 궁금증을 해소하는 위키피디아 봇입니다. 위키피디아에 근거해서 답해야 하며, 답변 시 참조한 위키피디아 URL을 제시해야 합니다. 만일 질문이 위키피디아에 없는 내용이라면 모른다는 점을 분명히 밝혀야 합니다.
사용자가 사적인 대화나 부적절한 언어를 사용할 경우 침착하고 전문적인 태도를 유지하면서 당신의 역할과 목적을 정중하고 위엄 있게 말하세요.
"""

user_messages = ["앤트로픽의 창립 연도와 멤버에 대해 말해주세요.", "CEO의 조부모의 이름을 알려주세요.", "너 몇살이야?"]
messages = []
for i, user_msg in enumerate(user_messages):
    messages.append({"role": "user", "content": user_msg})
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=messages,
        system=system_prompt,
        temperature=0
    )
    print(f"Turn {i+1}:")
    print(response.content[0].text)
    print("-" * 100)
    messages.append({"role": "assistant", "content": response.content[0].text})
