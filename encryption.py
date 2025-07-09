import anthropic

client = anthropic.Anthropic()          

response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=4000,                    
    thinking={
        "type": "enabled",              
        "budget_tokens": 2000           
    },
    messages=[{
        "role": "user",
        "content": "ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB"
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

