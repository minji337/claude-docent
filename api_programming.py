import httpcore
import json
import os

# API 엔드포인트 URL
url = "https://api.anthropic.com/v1/messages"

# 요청 헤더 설정
headers = {
    "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

# 요청 데이터 구성
data = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello, world"}],
}

# JSON 형식으로 인코딩 (바이트 스트림)
json_data = json.dumps(data).encode("utf-8")

# httpcore를 활용한 요청/응답 처리
with httpcore.ConnectionPool() as http:
    try:
        # POST 요청
        response = http.request(
            method="POST", url=url, headers=list(headers.items()), content=json_data
        )
        # 응답 본문 출력
        print(response.content.decode("utf-8"))
    except httpcore.NetworkError as e:
        print(f"Network Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
