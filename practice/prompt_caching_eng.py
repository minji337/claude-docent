import anthropic

llm_definition = """1
Claude and the mission of Anthropic
""".strip()

llm_definition *= 120


client = anthropic.Anthropic()

token_count = client.messages.count_tokens(
    model="claude-sonnet-4-5", messages=[{"role": "user", "content": llm_definition}]
)
print("Token Count:", token_count.input_tokens)
print("*" * 100)

system_prompt = [
    {
        "type": "text",
        "text": "8. Based on the provided content, give a concise answer in three sentences or less.",
    },
    {"type": "text", "text": llm_definition, "cache_control": {"type": "ephemeral"}},
]

user_messages = [
    {"role": "user", "content": "Please explain what an LLM is."},
    {"role": "user", "content": "Please explain the Transformer model."},
]

messages = []
for num, user_message in enumerate(user_messages, start=1):
    messages.append(user_message)
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        temperature=0,
        system=system_prompt,
        messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content[0].text})
    print(f"\nDialogue Round {num}.{"-"*100}")
    print(response.content[0].text)
    print(response.usage.model_dump_json())