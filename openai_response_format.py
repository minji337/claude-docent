from openai import OpenAI

system_prompt = """
다음 JSON 포맷으로 응답하세요:
{{"사이즈":<S,M,L,XL,XXL, N/A 중 택 1>"}}
"""
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "저는 남성이고 키는 175cm에 체중은 75Kg입니다"}
]

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    response_format={"type": "json_object"}
)

print(response.choices[0].message.content)
