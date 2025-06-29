import base64
import anthropic
from PIL import Image   
from io import BytesIO
import tempfile, webbrowser, urllib.parse, pathlib

image_file = "data/leaflet/전시해설프로그램.png"
json_file = "data/leaflet/guide_program.json"

prompt = """
1. 전시해설프로그램을 JSON 형식의 데이터베이스로 만들 것
2, 최상단의 키는 "상설전시관 정기 해설", "큐레이터와의 대화", "상설전시관 예약 해설" 세 가지로 할 것
3. 출력은 <json> 태그로 감싼 JSON 포맷으로 할 것
"""

def show_image(img: Image.Image):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        img.save(tmp, "PNG")
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

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": get_base64_data(image_file),
                    },
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ],
        },
        {
            "role": "assistant",
            "content": "<json>"
        }
    ],
    stop_sequences=["</json>"],
)
print(response.content[0].text)

json_data = response.content[0].text

with open(json_file, 'w', encoding='utf-8') as f:
    f.write(json_data)
