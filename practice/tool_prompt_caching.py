import anthropic
from PIL import Image
from io import BytesIO
import base64
from pathlib import Path

llm_definition ="""
대규모 언어 모델(영어: large language model, LLM)[1] 또는 거대 언어 모델(巨大言語 - )[2]은 수많은 파라미터(보통 수십억 웨이트 이상)를 보유한 인공 신경망으로 구성되는 언어 모델이다. 자기 지도 학습이나 반자기지도학습을 사용하여 레이블링되지 않은 상당한 양의 텍스트로 훈련된다.[3] LLM은 2018년 즈음에 모습을 드러냈으며 다양한 작업을 위해 수행된다. 이전의 특정 작업의 특수한 지도 학습 모델의 훈련 패러다임에서 벗어나 자연어 처리 연구로 초점이 옮겨졌다.
대규모 언어 모델(LLM) 은 AI 챗봇 기술을 가능하게 하는 요소이며 많은 화제를 불러일으키고 있는 주제 중 하나다. 대규모 언어 모델(LLM)의 작동 방식은 크게 3가지로 나뉘고 있다. 토큰화, 트랜스포머 모델, 프롬프트 등. 토큰화는 자연어 처리의 일부로 일반 인간 언어를 저수준 기계 시스템(LLMS)이 이해할 수 있는 시퀀스로 변환하는 작업을 말하며 여기에는 섹션에 숫자 값을 할당하고 빠른 분석을 위해 인코딩하는 작업이 수반된다. 이는 음성학의 AI 버전과 같으며 토큰화의 목적은 인공지능이 문장의 구조를 예측하기 위한 학습 가이드 또는 공식과 같은 컨텍스트 백터를 생성하는 것이 목적. 언어를 더 많이 연구하고 문장이 어떻게 구성되는지 이해할수록 특정 유형의 문장에서 다음 언어에 대한 예측이 더 정확해진다. 이로 인해 온라인에서 사람들이 사용하는 다양한 커뮤니케이션 스타일을 재현하는 모델을 개발할 수 있다.
트랜스포머 모델은 순차적 데이터를 검사하여 어떤 단어가 서로 뒤따를 가능성이 높은지 관련 패턴을 식별하는 신경망의 일종으로 각각 다른 분석을 수행하여 어떤 단어가 호환되는지 결정하는 계층으로 구성된다. 이러한 모델은 언어를 학습하지 않고 알고리즘에 의존하여 사람이 쓴 단어를 이해하고 예를 들어, 힙스터 커피 블로그를 제공함으로써 커피에 대한 표준 글을 작성하도록 학습시킨다.
프롬프트는 개발자가 정보를 분석하고 토큰화하기 위해 대규모 언어 모델 LLM에 제공하는 정보로 프롬프트는 기본적으로 다양한 사용 사례에서 LLM에 도움이 되는 학습 데이터이다. 더 정확한 프롬프트를 받을수록 LLM은 다음 단어를 더 잘 예측하고 정확한 문장을 구성할 수 있다. 따라서 딥러닝 AI의 적절한 학습을 위해서는 적절한 프롬프트를 선택하는 것이 중요하다.
""".strip()

BASE_DIR = Path(__file__).resolve().parent

def get_base64_data(file_path):
    img = Image.open(file_path)
    buffer = BytesIO()
    img.save(buffer, format=img.format or "JPEG")
    base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_data

tools=[
    # 여러 가지 도구 정의들....
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
            "required": ["location"]
        },
    }    
]

system_prompt=[
    {
        "type": "text",
        "text": "3.주어진 내용을 바탕으로 세 문장 이내로 간략히 답변하세요.", #캐싱되지 않도록 하려면 '1.'을 '2.'등으로 바꿉니다.
    },
    {
        "type": "text",
        "text": llm_definition,
    },
]

user_messages=[
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": get_base64_data(BASE_DIR.parent / "data" / "transformer.png")
                }
            },
            {
                "type": "text",
                "text": "이 그림을 바탕으로 LLM에 대해 설명해주세요.",
                "cache_control": {"type": "ephemeral"}
            },
        ]        
    },    
    {
        "role": "user",
        "content": "양쪽에 있는 태극 마크 같은 모양은 뭐에요?"
    },
]

client = anthropic.Anthropic()

messages = []
for num, user_message in enumerate(user_messages, start=1):
    messages.append(user_message)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0,   
        tools=tools,
        system=system_prompt,    
        messages=messages        
    )
    messages.append({"role": "assistant", "content": response.content[0].text})
    print(f"\n{num}번째 대화입니다.{"-"*100}")
    print(response.content[0].text)
    print(response.usage.model_dump_json())
