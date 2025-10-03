import anthropic
from pprint import pprint

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "LLM에 대해 설명해"}],
    stop_sequences=[".", "!", "?"],
)
pprint(message.model_dump())
