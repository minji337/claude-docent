import base64
import anthropic
from PIL import Image   
from io import BytesIO

def get_base64_data(file_path):
    # 이미지를 한 번만 열기
    img = Image.open(file_path)
    width, height = img.size
    print(f"이미지 크기: {width}x{height}, 토큰 수:{(width * height) / 750}")

    # BytesIO를 사용하여 이미지를 바이트로 변환    
    buffer = BytesIO()
    img.save(buffer, format=img.format or "JPEG")  # 원본 포맷 유지 또는 JPEG 기본값
    base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_data

url = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": url,
                    },
                },
                {
                    "type": "text",
                    "text": "이 사진을 묘사하세요."
                }
            ],
        }
    ],
)
print(response.content[0].text)
