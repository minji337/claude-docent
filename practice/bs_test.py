import requests
from bs4 import BeautifulSoup

# 웹 페이지 가져오기
url = "https://docs.anthropic.com/ko/docs/welcome"
response = requests.get(url)

# BeautifulSoup 객체 생성
soup = BeautifulSoup(response.text, 'html.parser')

# 모든 p 태그 찾기
p_tags = soup.find_all('p')

# p 태그 내용 출력
for no, p in enumerate(p_tags, start=1):
    print(f"{no}번째 p tag: {p.text}")
