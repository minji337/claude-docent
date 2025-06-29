import base64
import anthropic
from PIL import Image   
from io import BytesIO
import tempfile, webbrowser, urllib.parse, pathlib

def get_base64_data(file_path):
    # 이미지를 한 번만 열기
    img = Image.open(file_path)
    width, height = img.size
    print(f"이미지 크기: {width}x{height}, 토큰≈{(width*height)//750}")

    # BytesIO를 사용하여 이미지를 바이트로 변환    
    buffer = BytesIO()
    img.save(buffer, format=img.format or "JPEG")  # 원본 포맷 유지 또는 JPEG 기본값
    base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_data

image_file = "data/database/348/image.jpg"
#image_file = "data/resized_relic_348.jpg"

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": get_base64_data(image_file),
                    },
                },
                {
                    "type": "text",
                    "text": "이 전시물을 3문장으로 간략히 묘사하세요."
                }
            ],
        }
    ],
)

print("클로드 응답 ===\n" + response.content[0].text)
print("클로드 토큰 사용 ===\n" + response.usage.model_dump_json())
