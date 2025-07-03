from pathlib import Path
import anthropic
from pprint import pprint

ROOT_DIR = Path(__file__).resolve().parent.parent

file_path = ROOT_DIR / "data" / "leaflet" / "guide_program.json"

client = anthropic.Anthropic()

with open(file_path, "rb") as f:
    file_upload = client.beta.files.upload(file=("guide_program.json", f, "text/plain"))

print("파일 업로드:")
print(file_upload.model_dump())

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "file",
                        "file_id": file_upload.id
                    }
                },
                {
                    "type": "text",
                    "text": "문화해설 프로그램 제목을 알려주세요."
                }
            ]
        }
    ],
    extra_headers={"anthropic-beta": "files-api-2025-04-14"}, 
)

print("LLM 응답:")
print(response.content[0].text)

result = client.beta.files.delete(file_upload.id)

print("파일 삭제:")
print(result.model_dump())

