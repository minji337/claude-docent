import logging
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64

def get_base64_data(file_path):
    # 이미지를 한 번만 열기
    img = Image.open(file_path)
    buffer = BytesIO()
    img.save(buffer, format=img.format or "JPEG")  # 원본 포맷 유지 또는 JPEG 기본값
    base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_data


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        #format="%(asctime)s [%(levelname)s] %(filename)s - %(message)s",
        format="[%(levelname)s] %(filename)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",  
        handlers=[logging.StreamHandler()], 
        force=True,  
    )

logger = logging.getLogger(__name__)
