import anthropic
from pprint import pprint

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=3,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
pprint(message.model_dump())
