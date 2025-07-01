import anthropic
from pprint import pprint
from datetime import datetime
import pytz

def get_weather(location: str, unit: str = "섭씨") -> dict:
    try:
        # 실제 구현시에는 기상청 API 등을 사용
        weather_info = {
            "location": location,
            "temperature": 20 if unit == "섭씨" else 68,
            "unit": unit,
            "condition": "맑음",
            "humidity": 60
        }
        return weather_info
    except Exception as e:
        return {"error": f"날씨 정보를 가져오는데 실패했습니다: {str(e)}"}

def get_time(timezone: str) -> dict:
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)

        time_info = {
            "timezone": timezone,
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone_offset": current_time.strftime("%z"),
            "timezone_name": tz.zone
        }
        return time_info
    except pytz.exceptions.UnknownTimeZoneError:
        return {"error": f"알 수 없는 시간대입니다: {timezone}"}
    except Exception as e:
        return {"error": f"시간 정보를 가져오는데 실패했습니다: {str(e)}"}

tools=[
    {
        "name": "get_weather",
        "description": "주어진 지역의 날씨를 가져옵니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "광역시도, e.g. 서울, 경기도"
                },
                "unit": {
                    "type": "string",
                    "enum": ["섭씨", "화씨"],
                    "description": "온도 단위, 섭씨 또는 화씨"
                }
            },
            "required": ["location", "unit"]
        }
    },
    {
        "name": "get_time",
        "description": "주어진 시간대의 현재 시간을 가져옵니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "표준시간, e.g. Asia/Seoul"
                }
            },
            "required": ["timezone"]
        }
    }
]


client = anthropic.Anthropic()

def request_tool_call(messages: list):
    response = client.messages.create(  
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        tool_choice={"type": "auto"},
        messages=messages
    )
    return response 

messages = [
    {
        "role": "user",
        "content": "서울 날씨는 어때?"
        #"content": "서울은 지금 몇 시이고, 날씨는 어때?" # 오류 발생하는 질문
    }
]

response = request_tool_call(messages)
pprint(response.model_dump())

# if response.stop_reason == "tool_use":
#     tool_content = next(content for content in response.content if content.type == "tool_use")
#     func_name, args = tool_content.name, tool_content.input
#     if func_name == "get_weather":
#         tool_result = get_weather(args["location"], args["unit"])
#     elif func_name == "get_time":
#         tool_result = get_time(args["timezone"])
#     print(tool_result)

tool_repository = {
    "get_weather": lambda location, unit: get_weather(location, unit),
    "get_time": lambda timezone: get_time(timezone),
    # 신규함수는 여기에만 추가
}

if response.stop_reason == "tool_use":
    tool_content = next(content for content in response.content if content.type == "tool_use")
    func_name, args = tool_content.name, tool_content.input
    tool_result = tool_repository[func_name](**args)    
print(tool_result)


messages.append({"role": "assistant", "content": response.content})
messages.append(
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_content.id,
                "content": str(tool_result),
            }
        ],
    }
)
response = request_tool_call(messages)
print(response.content[0].text)


messages = [
{
        "role": "assistant",
        "content": [tool_content]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_content.id,
                "content": str(tool_result),
            }
        ],
    }
]


response = request_tool_call(messages)
print(response.content[0].text)

