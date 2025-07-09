import os
import anthropic

#client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
print(message.content[0].text)
