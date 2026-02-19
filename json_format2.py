from anthropic import Anthropic
import json
from pprint import pprint

user_message = """
한국 중국 일본의 수도를 <json> 태그로 감싸 다음 JSON 포맷으로 응답하세요:
{{<국가>: <수도>}}
"""
for _ in range(10):
  client = Anthropic()
  message = client.messages.create(
      model="claude-sonnet-4-6",
      max_tokens=1000,
      temperature=0,
       messages=[
          {"role": "user", "content": user_message},
      ],
      stop_sequences=["</json>"]
  )
  print("message.content[0].text:", message.content[0].text)
  print("-"*50)
  json_str = message.content[0].text.replace("<json>", "")
  print("json.loads(json_str):", json.loads(json_str)) 
  