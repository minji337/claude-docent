from pathlib import Path
import anthropic
import json

ROOT_DIR = Path(__file__).resolve().parent.parent

file_root = ROOT_DIR / "data" / "leaflet" 

client = anthropic.Anthropic()

with open(file_root / "국립중앙박물관리플릿_국어.pdf", "rb") as f:
    leaflet_upload = client.beta.files.upload(file=("leaflet.pdf", f, "application/pdf"))

with open(file_root / "leaflet_meta.json", 'w', encoding="utf-8") as f:
    json.dump(leaflet_upload.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

with open(file_root / "guide_program.json", "rb") as f:
    guide_program_upload = client.beta.files.upload(file=("guide_program.json", f, "text/plain"))

with open(file_root / "guide_program_meta.json", 'w', encoding="utf-8") as f:
    json.dump(guide_program_upload.model_dump(mode='json'), f, ensure_ascii=False, indent=2)
