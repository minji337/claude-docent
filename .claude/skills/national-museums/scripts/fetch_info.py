"""
국립박물관 운영정보 조회 스크립트

사용법:
    python fetch_info.py [지역명]
    예: python fetch_info.py 경주
"""

import sys
import io
import json
from pathlib import Path

# Windows 콘솔 인코딩 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).parent
DATA_FILE = SCRIPT_DIR / "museums_data.json"

# 지역명 -> 박물관명 매핑
REGION_MAP = {
    "경주": "국립경주박물관",
    "광주": "국립광주박물관",
    "전주": "국립전주박물관",
    "대구": "국립대구박물관",
    "부여": "국립부여박물관",
    "공주": "국립공주박물관",
    "진주": "국립진주박물관",
    "청주": "국립청주박물관",
    "김해": "국립김해박물관",
    "제주": "국립제주박물관",
    "춘천": "국립춘천박물관",
    "나주": "국립나주박물관",
    "익산": "국립익산박물관",
}


def print_museum_info(name: str, info: dict) -> None:
    """박물관 정보 출력"""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  운영시간:   {info.get('hours', '-')}")
    if info.get("hours_weekend"):
        print(f"  주말/공휴:  {info['hours_weekend']}")
    if info.get("hours_saturday"):
        print(f"  토요일:     {info['hours_saturday']}")
    if info.get("hours_saturday_summer"):
        print(f"  토(4~10월): {info['hours_saturday_summer']}")
    print(f"  휴관일:     {info.get('closed', '-')}")
    print(f"  입장료:     {info.get('fee', '-')}")
    print(f"  특화분야:   {info.get('specialty', '-')}")
    print(f"  대표유물:   {info.get('highlights', '-')}")
    print(f"  주소:       {info.get('address', '-')}")
    print(f"  전화:       {info.get('phone', '-')}")
    print(f"  웹사이트:   {info.get('website', '-')}")
    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print("사용법: python fetch_info.py [지역명]")
        print(
            "지역: 경주, 광주, 전주, 대구, 부여, 공주, 진주, 청주, 김해, 제주, 춘천, 나주, 익산"
        )
        return

    region = sys.argv[1]
    museum_name = REGION_MAP.get(region)

    if not museum_name:
        print(f"'{region}'은(는) 지원하지 않는 지역입니다.")
        print(
            "지원 지역: 경주, 광주, 전주, 대구, 부여, 공주, 진주, 청주, 김해, 제주, 춘천, 나주, 익산"
        )
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    museums = data.get("museums", {})
    updated = data.get("updated", "unknown")

    if museum_name in museums:
        print_museum_info(museum_name, museums[museum_name])
        print(f"데이터 업데이트: {updated}")


if __name__ == "__main__":
    main()
