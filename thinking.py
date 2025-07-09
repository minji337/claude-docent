import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    thinking= {
        "type": "enabled",
        "budget_tokens": 2000
    },
    messages=[{
        "role": "user",
        "content": "1부터 20까지의 자연수 중에서 3의 배수이면서 동시에 4의 배수인 수들의 합은 얼마일까?"
    }]
)

for block in response.content:
    print(f"\n{block.type} {'='*100}")
    if block.type  == "thinking":
        print(block.thinking)
    elif block.type == "redacted_thinking":
        print(block.data if hasattr(block, 'data') else "No data available in redacted_thinking block.")
    elif block.type  == "text":
        print(block.text)
