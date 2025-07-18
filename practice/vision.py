import base64
import anthropic
from PIL import Image   
from io import BytesIO
import tempfile, webbrowser, urllib.parse, pathlib

def show_image(img: Image.Image):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        img.save(tmp, "JPEG")
        tmp.flush()
        file_url = "file://" + urllib.parse.quote(
            str(pathlib.Path(tmp.name).resolve())
        )
        webbrowser.open_new_tab(file_url)

def get_base64_data(file_path):
    img = Image.open(file_path)
    width, height = img.size
    print(f"이미지 크기: {width}x{height}")
    show_image(img)

    # BytesIO를 사용하여 이미지를 바이트로 변환    
    buffer = BytesIO()
    img.save(buffer, format=img.format or "JPEG")  # 원본 포맷 유지 또는 JPEG 기본값
    base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_data

image_file = "data/database/348/bon001958-000-0001.jpg"


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
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": get_base64_data(image_file),
                    },
                },
                {
                    "type": "text",
                    "text": "이 전시물을 묘사하세요."
                }
            ],
        }
    ],
)
print(response.content[0].text)
