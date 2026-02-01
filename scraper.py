#!/usr/bin/env python3
"""국립중앙박물관 국보·보물 스크레이퍼"""

import json
import logging
import re
import signal
import sys
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin

import requests
import urllib3.util.connection
from bs4 import BeautifulSoup
from PIL import Image

# ── 상수 ──────────────────────────────────────────────
BASE_URL = "https://www.museum.go.kr/MUSEUM/contents/M0504000000.do"
SITE_ORIGIN = "https://www.museum.go.kr"
DATABASE_DIR = Path("database")
REQUEST_DELAY = 1.0
RETRY_DELAY = 5.0
REQUEST_TIMEOUT = 30

# ── 전역 플래그 ───────────────────────────────────────
shutdown_requested = False


# ── IPv4 강제 어댑터 ──────────────────────────────────
class IPv4HTTPAdapter(requests.adapters.HTTPAdapter):
    """IPv6 DNS 불안정 시 IPv4를 강제하는 어댑터"""

    def __init__(self, *args, **kwargs):
        urllib3.util.connection.HAS_IPV6 = False
        super().__init__(*args, **kwargs)


# ── 로깅 설정 ─────────────────────────────────────────
def setup_logging():
    logger = logging.getLogger("scraper")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")

    fh = logging.FileHandler("scraper.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


# ── 세션 생성 ─────────────────────────────────────────
def create_session():
    session = requests.Session()
    adapter = IPv4HTTPAdapter()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    return session


# ── HTTP 요청 (재시도 포함) ───────────────────────────
def fetch_url(session, url, params=None, logger=None):
    """GET 요청. 5xx 시 1회 재시도. 항상 1초 sleep."""
    for attempt in range(2):
        try:
            resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code >= 500:
                if attempt == 0:
                    if logger:
                        logger.warning(
                            "서버 에러 %d, %s초 후 재시도: %s",
                            resp.status_code,
                            RETRY_DELAY,
                            url,
                        )
                    time.sleep(RETRY_DELAY)
                    continue
                if logger:
                    logger.error("서버 에러 %d (재시도 실패): %s", resp.status_code, url)
                return None
            if resp.status_code >= 400:
                if logger:
                    logger.error("클라이언트 에러 %d: %s", resp.status_code, url)
                return None
            return resp
        except requests.RequestException as e:
            if attempt == 0:
                if logger:
                    logger.warning("요청 실패 (%s), %s초 후 재시도", e, RETRY_DELAY)
                time.sleep(RETRY_DELAY)
                continue
            if logger:
                logger.error("요청 실패 (재시도 실패): %s", e)
            return None
        finally:
            time.sleep(REQUEST_DELAY)
    return None


# ── 목록 수집 ─────────────────────────────────────────
def collect_relic_ids(session, logger):
    """전체 국보·보물 relicId 목록을 수집한다."""
    all_ids = set()
    page = 1

    while True:
        if shutdown_requested:
            break

        logger.info("목록 페이지 %d 수집 중...", page)
        params = {"searchId": "treasure", "schM": "list", "pageIndex": page}
        resp = fetch_url(session, BASE_URL, params=params, logger=logger)
        if resp is None:
            logger.error("목록 페이지 %d 요청 실패, 수집 중단", page)
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=True)
        page_ids = set()
        for link in links:
            m = re.search(r"relicId=(\d+)", link["href"])
            if m:
                page_ids.add(int(m.group(1)))

        if not page_ids:
            logger.info("페이지 %d: 더 이상 유물 없음, 목록 수집 완료", page)
            break

        new_ids = page_ids - all_ids
        if not new_ids:
            logger.info("페이지 %d: 새로운 ID 없음, 목록 수집 완료", page)
            break

        all_ids.update(page_ids)
        logger.info("페이지 %d: %d개 ID 발견 (누적 %d개)", page, len(new_ids), len(all_ids))
        page += 1

    return sorted(all_ids)


# ── 상세 페이지 파싱 ──────────────────────────────────
def parse_detail_page(html, relic_id):
    """상세 페이지 HTML에서 유물 데이터를 추출한다."""
    soup = BeautifulSoup(html, "html.parser")

    # 명칭
    title_tag = soup.select_one("strong.outveiw-tit")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # 메타데이터 (label)
    label = {"명칭": title}
    meta_list = soup.select("ul.outview-list li")
    for li in meta_list:
        key_tag = li.find("strong")
        val_tag = li.find("p")
        if key_tag and val_tag:
            key = key_tag.get_text(strip=True)
            val = val_tag.get_text(strip=True)
            label[key] = val

    # 이미지 (gallery-thumbs 내 첫 번째)
    thumb_container = soup.select_one(".swiper-container.gallery-thumbs")
    img_path = None
    if thumb_container:
        first_img = thumb_container.select_one(".swiper-slide img")
        if first_img and first_img.get("src"):
            img_path = first_img["src"]

    # 본문
    content_tag = soup.select_one(".view-info-cont2 p")
    content = content_tag.get_text(strip=True) if content_tag else ""

    # 저작권 이미지
    copyright_tag = soup.select_one(".codeView01.codeCopyright img")
    copyright_img = copyright_tag["src"] if copyright_tag and copyright_tag.get("src") else ""

    url = f"{BASE_URL}?schM=view&relicId={relic_id}"

    return {
        "url": url,
        "img": img_path or "",
        "label": label,
        "content": content,
        "copyright_img": copyright_img,
    }


# ── 이미지 다운로드 ──────────────────────────────────
def download_image(session, img_path, save_dir, logger):
    """이미지를 다운로드하고 검증 후 저장한다."""
    if not img_path:
        return None

    img_url = SITE_ORIGIN + img_path
    resp = fetch_url(session, img_url, logger=logger)
    if resp is None:
        return None

    try:
        img = Image.open(BytesIO(resp.content))
        img.verify()
    except Exception as e:
        logger.warning("이미지 검증 실패: %s (%s)", img_url, e)
        return None

    filename = img_path.rsplit("/", 1)[-1]
    save_path = save_dir / filename
    save_path.write_bytes(resp.content)
    return filename


# ── JSON 저장 ─────────────────────────────────────────
def save_relic_data(relic_id, data):
    """유물 데이터를 JSON 파일로 저장한다."""
    relic_dir = DATABASE_DIR / str(relic_id)
    relic_dir.mkdir(parents=True, exist_ok=True)

    json_path = relic_dir / "relic_data.json"
    output = {str(relic_id): data}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


# ── 완료 ID 확인 ─────────────────────────────────────
def get_scraped_ids():
    """이미 수집 완료된 relic_id 집합을 반환한다."""
    scraped = set()
    if not DATABASE_DIR.exists():
        return scraped
    for d in DATABASE_DIR.iterdir():
        if d.is_dir() and (d / "relic_data.json").exists():
            try:
                scraped.add(int(d.name))
            except ValueError:
                pass
    return scraped


# ── 시그널 핸들러 ─────────────────────────────────────
def handle_sigint(signum, frame):
    global shutdown_requested
    shutdown_requested = True


# ── 메인 ──────────────────────────────────────────────
def main():
    global shutdown_requested

    # 최대 건수
    max_count = None
    if len(sys.argv) > 1:
        try:
            max_count = int(sys.argv[1])
        except ValueError:
            print(f"사용법: python scraper.py [최대건수]")
            sys.exit(1)

    logger = setup_logging()
    session = create_session()
    signal.signal(signal.SIGINT, handle_sigint)

    logger.info("=== 국립중앙박물관 국보·보물 스크레이퍼 시작 ===")

    # 1) 목록 수집
    relic_ids = collect_relic_ids(session, logger)
    logger.info("총 %d개의 유물 ID 수집 완료", len(relic_ids))

    if not relic_ids:
        logger.error("수집된 유물 ID가 없습니다. 종료합니다.")
        return

    # 2) 이미 완료된 항목 제외
    scraped = get_scraped_ids()
    pending = [rid for rid in relic_ids if rid not in scraped]

    if max_count is not None:
        pending = pending[:max_count]

    logger.info(
        "대상: %d건 (전체 %d, 완료 %d, 건너뜀 %d)",
        len(pending),
        len(relic_ids),
        len(scraped),
        len(scraped),
    )

    # 3) 스크래핑
    success = 0
    fail = 0
    skipped = len(scraped)

    for idx, relic_id in enumerate(pending, 1):
        if shutdown_requested:
            logger.info("중단 요청 감지, 스크래핑을 중단합니다.")
            break

        detail_url = BASE_URL
        params = {"schM": "view", "relicId": relic_id}
        resp = fetch_url(session, detail_url, params=params, logger=logger)
        if resp is None:
            logger.error("[%d/%d] relic %d: 페이지 요청 실패", idx, len(pending), relic_id)
            fail += 1
            continue

        data = parse_detail_page(resp.text, relic_id)
        if data is None:
            logger.error("[%d/%d] relic %d: 파싱 실패", idx, len(pending), relic_id)
            fail += 1
            continue

        # 이미지 다운로드
        relic_dir = DATABASE_DIR / str(relic_id)
        relic_dir.mkdir(parents=True, exist_ok=True)
        if data["img"]:
            downloaded = download_image(session, data["img"], relic_dir, logger)
            if not downloaded:
                logger.warning(
                    "[%d/%d] relic %d: 이미지 다운로드 실패", idx, len(pending), relic_id
                )

        # 저장
        save_relic_data(relic_id, data)
        title = data.get("label", {}).get("명칭", "제목 없음")
        logger.info("[%d/%d] relic %d: %s", idx, len(pending), relic_id, title)
        success += 1

    # 4) 통계 출력
    logger.info("=== 스크래핑 완료 ===")
    logger.info("성공: %d건", success)
    logger.info("실패: %d건", fail)
    logger.info("건너뜀 (이미 수집): %d건", skipped)


if __name__ == "__main__":
    main()
