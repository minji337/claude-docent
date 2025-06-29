import sys, time, base64
from io import BytesIO
from PIL import Image
import anthropic
import subprocess, tempfile, os
import tempfile, webbrowser, urllib.parse, pathlib

MAX_PIXELS = 1_150_000
#MAX_PIXELS = 1_000_000

def show_image(img: Image.Image):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        img.save(tmp, "JPEG")
        tmp.flush()
        file_url = "file://" + urllib.parse.quote(
            str(pathlib.Path(tmp.name).resolve())
        )
        webbrowser.open_new_tab(file_url)
        
def resize(img: Image.Image, max_pixels: int = MAX_PIXELS):
    """필요하면 해상도를 줄여 반환(별도 시간 측정 없음)."""
    w, h = img.size
    while w * h > max_pixels:
        scale = (max_pixels / float(w * h)) ** 0.5
        img   = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        w, h  = img.size
    return img                                   # ← 조기 return 제거

def encode_image(path: str, do_resize: bool) -> str:
    with Image.open(path) as img:
        w, h = img.size
        print(f"원본: {w}×{h}px, 토큰≈{(w*h)//750}")
        show_image(img)
        if do_resize:
            img = resize(img)
            w, h = img.size
            print(f"리사이즈 후: {w}×{h}px, 토큰≈{(w*h)//750}")
            show_image(img)
        else:
            print("리사이즈 건너뜀")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

def main():
    do_resize  = sys.argv[1] == "1"
    #image_file = "data/database/348/image.jpg"
    image_file = "data/resized_relic_348.jpg"
    encoded_image = encode_image(image_file, do_resize)

    t0 = time.perf_counter()

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": encoded_image,
                    },
                },
            ],
        }]
    )

    print("\n=== 클로드 응답 ===\n" + response.content[0].text)
    print("\n=== 클로드 토큰 사용 ===\n" + response.usage.model_dump_json())
    print(f"\n[LLM 전체 수행 시간] {time.perf_counter() - t0:.3f} 초")

if __name__ == "__main__":
    main()
