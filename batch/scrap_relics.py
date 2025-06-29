import json
import os
import shutil
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def extract_relic_data():
    """JSON 정보 추출 함수"""
    base_url = "https://www.museum.go.kr/MUSEUM/contents/M0504000000.do"
    relic_index_json = {}

    # data/relic_links.json 파일 읽기
    with open('data/relic_links.json', 'r', encoding='utf-8') as f:
        relic_links = json.load(f)

    for link_data in relic_links:
    # for idx, link_data in enumerate(relic_links):
    #     if idx > 10:
    #         break
            
        query = link_data['query']
        # relicId 추출
        relic_id = re.search(r'relicId=(\d+)', query).group(1)

        # URL 생성
        url = base_url + query

        try:
            # HTML 요청
            response = requests.get(url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 이미지 정보 추출 (첫 번째 이미지)
            img_element = soup.select_one('.swiper-slide')
            img_url = ""
            if img_element:
                style = img_element.get('style', '')
                style_match = re.search(r'url\([\'"]?([^\'")]+)[\'"]?\)', style)
                img_tag = img_element.select_one('img')

                if style_match:
                    img_url = style_match.group(1)
                elif img_tag and img_tag.get('src'):
                    img_url = img_tag['src']

            # 상대 경로라면 절대경로로 보정
            if img_url.startswith('/'):
                img_url = "https://www.museum.go.kr" + img_url

            # 라벨 정보 추출
            label_data = {}
            outview_tit = soup.select_one('.outveiw-tit')
            if outview_tit:
                label_data['명칭'] = outview_tit.get_text(strip=True)

            outview_list = soup.select('.outview-list li')
            for li in outview_list:
                strong = li.select_one('strong')
                p = li.select_one('p')
                if strong and p:
                    key = strong.get_text(strip=True)
                    value = p.get_text(strip=True)
                    label_data[key] = value

            # 콘텐츠 정보 추출
            content_element = soup.select_one('.view-info-cont2 p')
            content = ""
            if content_element:
                content = content_element.get_text(strip=True)
                # HTML 엔티티 디코딩
                content = content.replace('&lt;', '<').replace('&gt;', '>')

            # 저작권 이미지 추출
            copyright_img = ""
            copyright_element = soup.select_one('.codeView01 img')
            if copyright_element:
                copyright_img = copyright_element.get('src', '')

            # 데이터 구성
            relic_data = {
                "url": url,
                "img": img_url,
                "label": label_data,
                "content": content,
                "copyright_img": copyright_img
            }

            relic_index_json[relic_id] = relic_data
            print(f"처리 완료: relicId {relic_id}")

        except Exception as e:
            print(f"오류 발생 (relicId {relic_id}): {e}")

        # 서버 부하 방지를 위한 1초 대기
        time.sleep(1)

    return relic_index_json

def check_copyright_license(relic_index_json):
    """공공누리 유형 점검 함수"""
    target_copyright = "https://www.kogl.or.kr/open/web/images/images_2014/codetype/new_img_opentype01.png"

    # 삭제할 항목들을 먼저 찾기
    items_to_remove = []
    for relic_id, data in relic_index_json.items():
        if data.get('copyright_img') != target_copyright:
            items_to_remove.append(relic_id)

    # 해당 항목들 삭제
    for relic_id in items_to_remove:
        del relic_index_json[relic_id]
        print(f"공공누리 유형 불일치로 삭제: relicId {relic_id}")

    print(f"공공누리 유형 점검 완료. 남은 항목 수: {len(relic_index_json)}")
    return relic_index_json

def build_database(relic_index_json):
    """데이터베이스 구축 함수"""

    # database 폴더 생성 (존재하면 삭제 후 재생성)
    database_path = "data/database"
    if os.path.exists(database_path):
        shutil.rmtree(database_path)
    os.makedirs(database_path)

    # relic_index.json 파일 생성
    with open(os.path.join(database_path, 'relic_index.json'), 'w', encoding='utf-8') as f:
        json.dump(relic_index_json, f, ensure_ascii=False, indent=2)

    # 각 relicId별 폴더 및 파일 생성
    for relic_id, data in relic_index_json.items():
        # relicId 폴더 생성
        relic_folder = os.path.join(database_path, relic_id)
        os.makedirs(relic_folder, exist_ok=True)

        # relic_data.json 파일 생성
        with open(os.path.join(relic_folder, 'relic_data.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 이미지 다운로드
        img_url = data.get('img', '')
        if img_url:
            try:
                # 상대 경로를 절대 경로로 변환
                if img_url.startswith('/'):
                    img_url = "https://www.museum.go.kr" + img_url

                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    # 파일 확장자 추출
                    file_extension = os.path.splitext(img_url)[1]
                    if not file_extension:
                        file_extension = '.jpg'  # 기본값

                    img_filename = f"image{file_extension}"
                    img_path = os.path.join(relic_folder, img_filename)

                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_response.content)

                    print(f"이미지 다운로드 완료: relicId {relic_id}")
                else:
                    print(f"이미지 다운로드 실패: relicId {relic_id}, 상태코드: {img_response.status_code}")

            except Exception as e:
                print(f"이미지 다운로드 오류 (relicId {relic_id}): {e}")

        # 서버 부하 방지
        time.sleep(0.5)

    print(f"데이터베이스 구축 완료. 총 {len(relic_index_json)}개 항목 처리됨")

def main():
    """메인 실행 함수"""
    print("전시물 데이터베이스 구축을 시작합니다...")

    # 1. JSON 정보 추출
    print("1. JSON 정보 추출 중...")
    relic_index_json = extract_relic_data()

    # 2. 공공누리 유형 점검
    print("2. 공공누리 유형 점검 중...")
    relic_index_json = check_copyright_license(relic_index_json)

    # 3. 데이터베이스 구축
    print("3. 데이터베이스 구축 중...")
    build_database(relic_index_json)

    print("전시물 데이터베이스 구축이 완료되었습니다!")

if __name__ == "__main__":
    main()