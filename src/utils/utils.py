import logging
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64
import json
import hashlib


def get_base64_data(file_path) -> str:
    img = Image.open(file_path)
    buffer = BytesIO()
    img.save(buffer, format=img.format or "JPEG")  # 원본 포맷 유지 또는 JPEG 기본값
    base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_data


def email_to_6digit_hash(email: str) -> str:
    sha_hash = hashlib.sha256(email.encode()).hexdigest()
    hash_int = int(sha_hash, 16)
    six_digit_hash = hash_int % 1000000
    return f"{six_digit_hash:06}"


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        # format="%(asctime)s [%(levelname)s] %(filename)s - %(message)s",
        format="[%(levelname)s] %(filename)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()],
        force=True,
    )


logger = logging.getLogger(__name__)

project_root = Path(__file__).parents[2]

leaflet_root = project_root / "data" / "leaflet"
with open(leaflet_root / "leaflet_meta.json", "r", encoding="utf-8") as f:
    leaflet_id = json.load(f)["id"]

with open(leaflet_root / "guide_program_meta.json", "r", encoding="utf-8") as f:
    guide_program_id = json.load(f)["id"]
