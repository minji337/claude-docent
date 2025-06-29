#!/usr/bin/env python3
import time
import base64
from io import BytesIO
from PIL import Image
import anthropic

MAX_EDGE = 1568
MAX_PIXELS = 1_150_000


def resize(img):
    w, h = img.size
    while w * h > MAX_PIXELS:
        scale = (MAX_PIXELS / float(w * h)) ** 0.5
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        w, h = img.size


def get_base64_data(file_path: str) -> str:

    with Image.open(file_path) as img:
        img.show()
        w, h = img.size
        print(f"원본: {w}×{h}px, 토큰≈{(w*h)//750}")
        resize(img)
        img.show()
        w, h = img.size
        print(f"리사이즈 후: {w}×{h}px, 토큰≈{(w*h)//750}")        
        buf = BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")


image_file = "data/database/348/image.jpg"

get_base64_data(image_file)

# client = anthropic.Anthropic()
# response = client.messages.create(
#     model="claude-sonnet-4-20250514",
#     max_tokens=1024,
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image",
#                     "source": {
#                         "type": "base64",
#                         "media_type": "image/jpeg",
#                         "data": get_base64_data(image_file),
#                     },
#                 },
#                 {
#                     "type": "text",
#                     "text": "이 전시물을 묘사하세요."
#                 }
#             ],
#         }
#     ],
# )
# print(response.content[0].text)
