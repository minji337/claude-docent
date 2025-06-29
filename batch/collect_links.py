import requests
from bs4 import BeautifulSoup
import time
import json
import os

def collect_relic_links():
    """
    국립중앙박물관 웹사이트에서 문화재 링크 정보를 수집하는 함수

    Returns:
        list: 페이지 번호와 문화재 링크의 쿼리 스트링 정보를 담은 딕셔너리 리스트
    """
    base_url = "https://www.museum.go.kr/MUSEUM/contents/M0504000000.do"
    results = []

    # 37페이지 순회 (startCount는 0부터 시작하여 12씩 증가)
    for page in range(37):
        start_count = page * 12
        page_url = f"{base_url}?startCount={start_count}&searchId=treasure&schM=list"

        try:
            # 웹페이지 요청
            response = requests.get(page_url)
            response.raise_for_status()  # 오류 발생 시 예외 발생

            # BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')

            # 카드 리스트 찾기
            cards = soup.select('li.card')

            # 각 카드에서 링크 추출
            for card in cards:
                link_tag = card.select_one('div.txt a')
                if link_tag and 'href' in link_tag.attrs:
                    query_string = link_tag['href']
                    results.append({
                        "page": page + 1,  # 페이지 번호는 1부터 시작
                        "query": query_string
                    })

            print(f"페이지 {page + 1}/37 처리 완료: {len(cards)}개 항목 발견")

            # 서버 부하 방지를 위한 1초 대기
            time.sleep(1)

        except Exception as e:
            print(f"페이지 {page + 1} 처리 중 오류 발생: {e}")

    return results

def save_to_json(data, filename):
    """
    수집된 데이터를 JSON 파일로 저장하는 함수
    """
    # data 폴더가 없으면 생성
    if not os.path.exists('data'):
        os.makedirs('data')

    filepath = os.path.join('data', filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"데이터가 {filepath}로 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")

# 메인 실행 부분
if __name__ == "__main__":
    relic_links = collect_relic_links()
    print(f"총 {len(relic_links)}개의 쿼리 스트링을 수집했습니다.")

# JSON 파일로 저장
    save_to_json(relic_links, 'relic_links.json')

# 수집된 데이터 샘플 출력
    if relic_links:
        print("\n수집된 데이터 샘플 (처음 5개):")
        for i, link in enumerate(relic_links[:5]):
            print(f"{i+1}. 페이지: {link['page']}, 쿼리: {link['query']}")
