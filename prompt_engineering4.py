import anthropic

client = anthropic.Anthropic()

prompt = """
<text>
  In the quiet town of Riverwood, a bright young boy named David lived.
  Every morning, he would fetch a bucket of fresh water from the nearby stream.
  His favorite part of the day was the walk through the lush, green forest.
  One day, David found a particularly shiny stone and decided to keep it as a lucky charm.
  Later that day, he showed the stone to his friends, and they marveled at its unique patterns.
  The stone reminded David of his happy morning walks.
</text>

지시사항:
1 - <text/>를 읽으면서 각 단어의 글자 수를 나열한다.
2 - 글자수가 5개인 단어를 골라낸다.
3 - 골라낸 단어의 빈도를 계산한다.

출력 형식은 다음을 따를 것:
1 - [단어: 글자수, ..]
2 - 골라낸 단어: ["단어",..]
3 - 출현빈도: {<단어>: <숫자>, ..}
"""

response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=2000,
    messages=[
        {"role": "user", 'content': prompt},
    ]
)
print(response.content[0].text)
