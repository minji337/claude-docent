import os
import json
import time
import requests
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_relic_data():
    """
    relic_links.json 파일을 읽고 각 전시물의 정보를 추출하여 JSON 형태로 반환하는 함수
    """
    base_url = "https://www.museum.go.kr/MUSEUM/contents/M0504000000.do"

    # relic_links.json 파일 읽기
    with open('relic_links.json', 'r', encoding='utf-8') as f:
        relic_links = json.load(f)

    relic_index_json = {}

for item in relic_links:
        link = item['link']
        # relicId 추출
        relic_id = link.split('relicId=')[1]

        # URL 생성
        url = base_url + link

        try:
            # 웹 페이지 요청
            response = requests.get(url)
            response.raise_for_status()  # 오류 발생 시 예외 발생

            # BeautifulSoup 객체 생성
            soup = BeautifulSoup(response.text, 'html.parser')

            # 이미지 URL 추출
            image_tag = soup.select_one('.swiper-slide')
            if image_tag:
                img_url = image_tag['style'].split("url('")[1].split("')")[0]
            else:
                img_url = ""

            # 라벨 정보 추출
            label_data = {}
            outview_tit = soup.select_one('.outveiw-tit')
            if outview_tit:
                label_data['명칭'] = outview_tit.text.strip()

            outview_list = soup.select('.outview-list li')
            for li in outview_list:
                key = li.select_one('strong').text.strip()
                value = li.select_one('p').text.strip()
                label_data[key] = value

            # 내용 추출
            content = soup.select_one('.view-info-cont p')
            content_text = content.text.strip() if content else ""

            # 저작권 이미지 URL 추출
            copyright_img = soup.select_one('.codeView01 img')
            copyright_img_url = copyright_img['src'] if copyright_img else ""

            # 데이터 구성
            relic_index_json[relic_id] = {
                "url": url,
                "img": img_url,
                "label": label_data,
                "content": content_text,
                "copyright_img": copyright_img_url
            }

            print(f"Extracted data for relic ID: {relic_id}")

        except Exception as e:
            print(f"Error extracting data for relic ID {relic_id}: {e}")

        # 서버 부하 방지를 위한 1초 대기
        time.sleep(1)

    return relic_index_json

def check_copyright(relic_index_json):
    """
    공공누리 유형 1 (출처표시)가 아닌 전시물을 삭제하는 함수
    """
    kogl_type1_url = "https://www.kogl.or.kr/open/web/images/images_2014/codetype/new_img_opentype01.png"

    # 삭제할 항목의 ID 목록
    to_delete = []

    for relic_id, relic_data in relic_index_json.items():
        if relic_data.get("copyright_img") != kogl_type1_url:
            to_delete.append(relic_id)

    # 삭제 실행
    for relic_id in to_delete:
        del relic_index_json[relic_id]
        print(f"Removed relic ID {relic_id} due to copyright restrictions")

    return relic_index_json

def build_database(relic_index_json):
    """
    데이터베이스 구축 함수
    """
    # 기본 경로 설정
    base_dir = "/content/drive/MyDrive/Colab Notebooks/claude/database"

    # 기존 폴더가 있으면 삭제
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)

    # 데이터베이스 폴더 생성
    os.makedirs(base_dir)

    # relic_index.json 파일 생성
    with open(os.path.join(base_dir, "relic_index.json"), 'w', encoding='utf-8') as f:
        json.dump(relic_index_json, f, ensure_ascii=False, indent=4)

    # 각 전시물별 폴더 생성 및 파일 저장
    for relic_id, relic_data in relic_index_json.items():
        # 전시물 폴더 생성
        relic_dir = os.path.join(base_dir, relic_id)
        os.makedirs(relic_dir)

        # relic_data.json 파일 생성
        with open(os.path.join(relic_dir, "relic_data.json"), 'w', encoding='utf-8') as f:
            json.dump(relic_data, f, ensure_ascii=False, indent=4)

        # 이미지 다운로드
        img_url = relic_data.get("img", "")
        if img_url:
            # 상대 URL을 절대 URL로 변환
            if img_url.startswith('/'):
                img_url = urljoin("https://www.museum.go.kr", img_url)

            try:
                img_response = requests.get(img_url, stream=True)
                img_response.raise_for_status()

                # 이미지 파일명 추출
                img_filename = os.path.basename(img_url)
                img_path = os.path.join(relic_dir, img_filename)

                # 이미지 저장
                with open(img_path, 'wb') as img_file:
                    img_response.raw.decode_content = True
                    shutil.copyfileobj(img_response.raw, img_file)

                print(f"Downloaded image for relic ID {relic_id}")

            except Exception as e:
                print(f"Error downloading image for relic ID {relic_id}: {e}")

    print(f"Database built successfully at {base_dir}")

def main():
    # 전시물 데이터 추출
    relic_index_json = extract_relic_data()

    # 공공누리 유형 점검
    relic_index_json = check_copyright(relic_index_json)

    # 데이터베이스 구축
    build_database(relic_index_json)

if __name__ == "__main__":
    main()
