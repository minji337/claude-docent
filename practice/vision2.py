#!/usr/bin/env python3
import time
import base64
from io import BytesIO
from PIL import Image
import anthropic
import os

# ────────────────────────────────────────────────────────────────
# 리사이즈 & base64 변환
MAX_EDGE   = 1568        # 한 변 최대 1 568 px
MAX_PIXELS = 1_150_000   # 1.15 MP

def _pretty_bytes(n: int) -> str:
    """1234567 → '1.23 MB' 식으로 보기 좋게"""
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"

def get_base64_data(file_path: str) -> str:
    # ── 원본 크기(바이트) ───────────────────────────────
    orig_bytes = os.path.getsize(file_path)

    with Image.open(file_path) as img:
        w, h = img.size
        print(f"원본: {w}×{h}px, 토큰≈{(w*h)//750}, "
              f"파일 크기: {_pretty_bytes(orig_bytes)}")

        # ── 리사이즈 ──────────────────────────────────
        if max(w, h) > MAX_EDGE:
            scale = MAX_EDGE / float(max(w, h))
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            w, h = img.size
        

        # ── 메모리에 저장 & 크기 계산 ──────────────────
        buf = BytesIO()
        img.save(buf, format="JPEG")              # 품질 변경 없음
        resized_bytes = len(buf.getvalue())

        print(f"리사이즈 후: {w}×{h}px, 토큰≈{(w*h)//750}, "
              f"버퍼 크기: {_pretty_bytes(resized_bytes)}")

        # ── base64 인코딩 결과 반환 ────────────────────
        return base64.b64encode(buf.getvalue()).decode("utf-8")

# ────────────────────────────────────────────────────────────────
# Claude 호출 & 응답 시간 측정
def call_claude(image_path: str) -> None:
    client = anthropic.Anthropic()
    img_b64 = get_base64_data(image_path)

    # ① 전체 API 왕복 시간
    t0 = time.time()

    # ② 첫 토큰까지 걸린 시간 측정을 위해 스트리밍 사용
    first_token_time = None
    full_text_parts = []

    for event in client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        stream=True,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": img_b64,
                    },
                },
                {"type": "text", "text": "이 전시물을 묘사하세요."}
            ],
        }]
    ):
        if event.type == "content_block_delta":
            if first_token_time is None:
                first_token_time = time.time() - t0
            # 토큰 텍스트를 순차로 합치기
            full_text_parts.append(event.delta.text)

    total_time = time.time() - t0

    # ─── 결과 출력 ────────────────────────────────────────────────
    print("\n=== Claude 응답 ===")
    print("".join(full_text_parts).strip())
    print("\n┌─── 응답 시간 ───")
    if first_token_time is not None:
        print(f"첫 토큰까지: {first_token_time:.2f} s")
    print(f"전체 스트림 완료: {total_time:.2f} s")
    print("└─────────────────")

# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    call_claude("data/database/348/image.jpg")
