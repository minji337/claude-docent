tools=[
    {
        "name": "get_balance_by_account",
        "description": "계좌별 잔액을 가져옵니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account": {
                    "type": "string",
                    "enum": ["친구모임공용계좌", "수시입출금계좌", "정기적금계좌"],
                    "description": "계좌 유형"
                }
            },
            "required": ["account"]
        }
    },
    {
        "name": "get_product_list",
        "description": "상품 목록을 가져옵니다.",
        "input_schema": {
            "type": "object",
            "properties": {},
        }
    },
    {
        "name": "get_product_price",
        "description": "상품 가격을 가져옵니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "enum": ["한식", "중식", "일식", "교통비", "식재료", "전세계약", "해외여행"],
                    "description": "상품 유형"
                }
            },
            "required": ["product"]
        }
    },
]


def get_balance_by_account(account_type: str) -> str:
  if account_type == "친구모임공용계좌":
      return "200_000원"
  elif account_type == "수시입출금계좌":
      return "300_000원"
  elif account_type == "정기적금계좌":
      return "50_000_000원"
  else:
      raise ValueError(f"Invalid type: {account_type}")

def get_product_list() -> str:
  return ["한식", "중식", "일식", "교통비", "식재료", "전세계약", "해외여행"]

def get_product_price(product: str) -> str:
  price_table= {
      "한식": "인당 20_000원",
      "중식": "인당 40_000원",
      "일식": "인당 70_000원",
      "교통비": "한달 200_000원",
      "식재료": "한달 500_000원",
      "전세계약": "100_000_000원",
      "해외여행": "10_000_000원"
  }
  return price_table[product]


import anthropic
client = anthropic.Anthropic()

sytstem_pronmpt = """
[추론], [행동], [관찰]의 단계를 번걸아가며 질문에 답하는 과정을 통해 과제를 해결합니다.

[추론]: 현재 상황에서 추론 과정을 기술합니다. 예를 들면 "문제를 해결하기 위해 무엇이 필요한가?" 또는 "다음에 어떤 정보를 검색해야 할까?" 같이 고려사항이나 계획을 서술합니다.
[행동]: 추론에 따라 문제를 해결할 수 있는 도구를 사용합니다. 
[관찰]: 행동의 결과로 얻은 정보를 객관적으로 기술합니다. 
""".strip()

# sytstem_pronmpt = """
# 사용자의 질문에 적절한 응답을 도출할 때까지 주어진 도구를 사용하세요.
# """

def request_tool_call(messages: list):
    response = client.messages.create(  
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0,
        tools=tools,
        tool_choice={"type": "auto"},
        system=sytstem_pronmpt,
        messages=messages
    )
    return response 
    

tool_repository = {
    "get_balance_by_account": lambda account: get_balance_by_account(account),
    "get_product_list": lambda: get_product_list(),
    "get_product_price": lambda product: get_product_price(product),
}

user_query = """
내일 친구들과 정기 모임을 해야 해. 총 10명인데 예산 범위 내에서 어디가면 좋을까?
""".strip()

# user_query = """
# 이번 여름에 해외여행을 가는 게 좋을까, 전세로 이사하는 게 좋을까?
# """.strip()

messages = [{"role": "user", "content": user_query}]                

response = request_tool_call(messages)
print(response.content[0].text)

while(response.stop_reason == "tool_use"):
    tool_result_blocks = []

    for content in response.content:
        if content.type != "tool_use":         
            continue
        func_name, args = content.name, content.input
        #print(func_name, args)
        tool_result = tool_repository[func_name](**args)
        tool_result_blocks.append({
            "type": "tool_result",
            "tool_use_id": content.id,
            "content": str(tool_result),
        })        

    messages.extend([
        {
            "role": "assistant",
            "content": response.content
        },
        {
            "role": "user",
            "content": tool_result_blocks,
        },
    ])
    response = request_tool_call(messages)
    print(response.content[0].text)



    #print(tool_result)   
#print(response.content[0].text)