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
글자수가 5개인 단어들을 선별하여 출현빈도를 작성하세요.
출력형식: {<단어>: <숫자>, ..}
"""

response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=2000,
    messages=[
        {"role": "user", 'content': prompt},
    ]
)
print(response.content[0].text)
