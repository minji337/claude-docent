from pathlib import Path
import json
from pydantic import BaseModel, Field
from typing import Literal
from PIL import Image
from io import BytesIO
import base64
import anthropic


class Category(BaseModel):
    id: str = Field(description="전시물 id")
    image_description: str = Field(
        description="입력된 텍스트 정보를 고려하지 않고 순수하게 이미지 외관만 묘사(최소 3문장)"
    )
    nationality: str = Field(description="예: 한국, 중국, 일본")
    period: str = Field(
        description="예: 신라, 고려, 조선. 단, 통일신라는 '신라'로 표기"
    )
    genre: Literal[
        "건축",
        "조각(불상)",
        "조각(불상 외)",
        "공예",
        "회화",
        "서예",
        "장신구",
        "복식",
        "과학기술",
        "기타",
    ]


BASE_DIR = Path(__file__).resolve().parent          # .../workspace/batch
ROOT_DIR = BASE_DIR.parent                          # .../workspace

relic_index_path = ROOT_DIR / "data" / "database" / "relic_index.json"
with open(relic_index_path, "r", encoding="utf-8") as f:
    relic_index_json = json.load(f)

def get_base64_data(file_path):
    img = Image.open(file_path)
    buffer = BytesIO()
    img.save(buffer, format=img.format or "JPEG")
    base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_data


tools = [
    {
        "name": "Category",
        "input_schema": Category.model_json_schema(),
    }
]

client = anthropic.Anthropic()
    
category_data = []
for relic_id, relic_info in relic_index_json.items():
    image_path = (
        ROOT_DIR
        / "data"
        / "database"
        / relic_id
        / "image.jpg"
    )
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0.3,
        tools=tools,
        tool_choice={"type": "tool", "name": "Category"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": get_base64_data(image_path),
                        },
                    },
                    {
                        "type": "text",
                        "text": f"id:{relic_id}\n{relic_info['label']}\n, {relic_info['content']}",
                    },
                ],
            },
        ],
    )
    category_data.append(message.content[0].input)
    if len(category_data) >= 2:
        break

for i in range(len(category_data)):
    print(category_data[i])
