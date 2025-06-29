import sys, pathlib
from PIL import Image

MAX_PIXELS = 1_150_000

def resize(img: Image.Image, max_pixels: int = MAX_PIXELS) -> Image.Image:
    """픽셀 수가 max_pixels 초과 시 비율 유지하며 한 번에 축소한다."""
    w, h = img.size
    while w * h > max_pixels:
        scale = (max_pixels / float(w * h)) ** 0.5   # √(목표/현재)
        img   = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        w, h  = img.size
    return img

def main():   
    relic_id = "348"
    src_path = f"data/database/{relic_id}/image.jpg"
    dst_path = f"data/database/{relic_id}/resized_image.jpg"
    
    with Image.open(src_path) as img:
        print(f"원본 해상도: {img.size[0]}×{img.size[1]} px")
        resized = resize(img)
        resized.save(dst_path, "JPEG")
        print(f"[저장 완료] {dst_path}  ({resized.size[0]}×{resized.size[1]} px)")

if __name__ == "__main__":
    main()
