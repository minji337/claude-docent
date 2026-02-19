import json
from typing import Literal
from anthropic import Anthropic, beta_tool

@beta_tool
def get_weather(location: str, unit: Literal["섭씨", "화씨"]) -> str:
    """
    주어진 지역의 날씨를 가져옵니다.
    Args:
        location: 광역시도, e.g. 서울, 경기도
        unit: 온도 단위, 섭씨(default) 또는 화씨
    Returns:
        JSON 문자열
    """
    weather_info = {
        "location": location,
        "temperature": 20 if unit == "섭씨" else 68,
        "unit": unit,
        "condition": "맑음",
        "humidity": 60,
    }
    return json.dumps(weather_info, ensure_ascii=False)


client = Anthropic()

# response = client.messages.create(
#     model="claude-sonnet-4-6",
#     max_tokens=1024,
#     tools=[get_weather.to_dict()], # to_dict()로 JSON 스키마를 자동 생성하여 tools에 전달
#     tool_choice={"type": "auto"},
#     messages=[{"role": "user", "content": "서울 날씨는 어때?"}],
# )

# print("도구 명세:", get_weather.to_dict())
# print("*"*50)
# print("사용할 도구:", response.content[0])

tool_runner = client.beta.messages.tool_runner(
    model="claude-sonnet-4-6",
    max_tokens=512,
    tools=[get_weather],
    messages=[{"role": "user", "content": "서울 날씨는 어때?"}],
)

# 도구 실행과 결과 전달이 내부에서 자동 처리되고 최종 응답을 반환
final_response = tool_runner.until_done()
print(final_response.content[0].text)
