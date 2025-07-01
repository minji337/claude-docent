import anthropic
client = anthropic.Anthropic()

messages = [
    {
        "role": "user",
        "content": "한국 증시에 대해 100자 이내로 조사해."
    }
]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=messages,
    tools=[{
"name": "web_search",
        "type": "web_search_20250305",
"user_location": {
            "type": "approximate",   
            "city": "Seoul",         
            "region": "Seoul",       
            "country": "KR",         
            "timezone": "Asia/Seoul" 
        },
        "max_uses": 5,
#       "allowed_domains": ["naver.com", "daum.net"],
#       "blocked_domains": ["untrustedsource.com"],
    }]
)

def get_citations_from_response(response):
    message = ""
    citations = set()
    for block in response.content:        
        if hasattr(block, 'citations') and block.citations:
            for citation in block.citations:
                citations.add(f"{citation.url}, {citation.title}")    
        if block.type == "text":
            message += block.text
    return citations, message

citations, message = get_citations_from_response(response)
print(message)
for citation in citations:
    print(f"URL: {citation}")

