from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

file_path = ROOT_DIR / "data" / "leaflet" / "국립중앙박물관리플릿_국어.pdf"

import anthropic
import base64

with open(file_path, "rb") as f:
    pdf_data = base64.b64encode(f.read()).decode("utf-8")

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data
                    }
                },
                {
                    "type": "text",
                    "text": "관림 시간을 알려주세요."
                }
            ]
        }
    ],
)

print(message)
