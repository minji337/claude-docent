import anthropic
from pprint import pprint

tools = [
    {
        "name": "Applicants",
        "description": "다수 지원자의 정보를 기술합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "applicants": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "이름"
                            },
                            "gender": { 
                                "type": "string",
                                "enum": ["M", "F"],
                                "description": "지원자의 성별"
                            },
                            "age": {    
                                "type": "integer",
                                "description": "나이"
                            },
                            "major": {  
                                "type": "string",
                                "description": "전공(학과)"
                            }
                        },
                        "required": ["name", "gender", "age", "major"]
                    },
                    "description": "지원자 객체들의 배열"
                }
            },
            "required": ["applicants"]
        }
    }
]

user_messsage = """
이번 저희 회사 지원자들에 대해 들은 정보를 짧게 말씀드릴게요.
먼저 김지훈 씨는 남자고 나이가 스물여덟이라고 하네요. 전공은 컴퓨터공학이라고 합니다.
박민서 씨는 여자분이고 서른한 살, 전공은 산업공학이라고 들었습니다.
그리고 마지막으로 이서연 씨인데, 여자분에 스물다섯 살이고요, 경영학 쪽을 전공했다고 해요.
"""

client = anthropic.Anthropic()

response = client.messages.create(  
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,      
    tool_choice = {"type": "tool", "name": "Applicants"},
    messages=[
        {
            "role": "user",
            "content": user_messsage
        }
    ],
)
pprint(response.content[0].input['applicants'])
