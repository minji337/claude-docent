import json
import os
import shutil
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def extract_relic_data():
    """JSON 정보 추출 함수"""
    base_url = "https://www.museum.go.kr/MUSEUM/contents/M0504000000.do"
    relic_index_json = {}

    # relic_links.json 파일 읽기
    with open('data/relic_links.json', 'r', encoding='utf-8') as f:
        relic_links = json.load(f)

    for idx, link_data in enumerate(relic_links):
        # if idx > 3:
        #     break
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
            img_element = soup.select_one('.swiper-container.gallery-thumbs .swiper-slide img')
            img_src = img_element['src'] if img_element else ""

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
            content_element = soup.select_one('.view-info-cont.view-info-cont2 p')
            content = content_element.get_text(strip=True) if content_element else ""
            # HTML 엔티티 디코딩
            content = content.replace('&lt;', '<').replace('&gt;', '>')

            # 저작권 이미지 추출
            copyright_img_element = soup.select_one('.codeView01 img')
            copyright_img = copyright_img_element['src'] if copyright_img_element else ""

            # 데이터 구성
            relic_index_json[relic_id] = {
                "url": url,
                "img": img_src,
                "label": label_data,
                "content": content,
                "copyright_img": copyright_img
            }

            print(f"처리 완료: relicId {relic_id}")

        except Exception as e:
            print(f"오류 발생 (relicId {relic_id}): {e}")

        # 서버 부하 방지를 위한 1초 휴지
        time.sleep(2)

    return relic_index_json

def check_copyright_license(relic_index_json):
    """공공누리 유형 점검 함수"""
    target_copyright = "https://www.kogl.or.kr/open/web/images/images_2014/codetype/new_img_opentype01.png"

    # 삭제할 키들을 먼저 수집
    keys_to_remove = []
    for relic_id, data in relic_index_json.items():
        if data.get('copyright_img') != target_copyright:
            keys_to_remove.append(relic_id)

    # 해당 전시물들 삭제
    for key in keys_to_remove:
        del relic_index_json[key]
        print(f"삭제됨: relicId {key} (공공누리 유형 불일치)")

    print(f"공공누리 유형 점검 완료. 남은 전시물 수: {len(relic_index_json)}")
    return relic_index_json

def build_database(relic_index_json):
    """데이터베이스 구축 함수"""
    base_url = "https://www.museum.go.kr"

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
        relic_folder = os.path.join(database_path, relic_id)
        os.makedirs(relic_folder)

        # relic_data.json 파일 생성
        with open(os.path.join(relic_folder, 'relic_data.json'), 'w', encoding='utf-8') as f:
            json.dump({relic_id: data}, f, ensure_ascii=False, indent=2)

        # 이미지 다운로드
        if data['img']:
            try:
                img_url = urljoin(base_url, data['img'])
                img_response = requests.get(img_url)

                if img_response.status_code == 200:
                    # 파일 확장자 추출
                    parsed_url = urlparse(data['img'])
                    filename = os.path.basename(parsed_url.path)
                    if not filename:
                        filename = f"{relic_id}.jpg"

                    img_path = os.path.join(relic_folder, filename)
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_response.content)

                    print(f"이미지 다운로드 완료: {relic_id}/{filename}")
                else:
                    print(f"이미지 다운로드 실패: {relic_id} (상태코드: {img_response.status_code})")

            except Exception as e:
                print(f"이미지 다운로드 오류 (relicId {relic_id}): {e}")

        # 서버 부하 방지
        time.sleep(0.5)

    print(f"데이터베이스 구축 완료. 총 {len(relic_index_json)}개 전시물 처리됨.")

def main():
    """메인 함수"""
    print("전시물 데이터베이스 구축을 시작합니다...")

    # 1. JSON 정보 추출
    print("\n1. JSON 정보 추출 중...")
    relic_index_json = extract_relic_data()

    # 2. 공공누리 유형 점검
    print("\n2. 공공누리 유형 점검 중...")
    relic_index_json = check_copyright_license(relic_index_json)

    # 3. 데이터베이스 구축
    print("\n3. 데이터베이스 구축 중...")
    build_database(relic_index_json)

    print("\n전시물 데이터베이스 구축이 완료되었습니다!")

if __name__ == "__main__":
    main()