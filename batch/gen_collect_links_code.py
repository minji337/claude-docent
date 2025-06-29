base_url = "https://www.museum.go.kr/MUSEUM/contents/M0504000000.do"
query_string = "?startCount=<number>&searchId=treasure&schM=list"

tag_samples = """
<li class="card">
    <a href="?schM=view&relicId=348" class="img-box">
        <img src="/relic_image//PS01001001/bon001/2016/1124093013018/700/bon001958-000-0001.jpg" alt="감산사 석조미륵보살입상 대표이미지" onerror="this.src='/ux/content/museum/images/onerror.png';">
    </a>
    <div class="txt">
        <a href="?schM=view&relicId=348">
            감산사 석조미륵보살입상</a>
        <!-- <span class="label-type purple-2">국보</span>
        <span class="label-type black">추천</span> -->
    </div>
</li>

<li class="card">
    <a href="?schM=view&relicId=349" class="img-box">
        <img src="/relic_image//PS01001001/bon001/2017/0508160735009/700/bon001959-00-01.jpg" alt="감산사 석조아미타불입상 대표이미지" onerror="this.src='/ux/content/museum/images/onerror.png';">
    </a>
    <div class="txt">
        <a href="?schM=view&relicId=349">
            감산사 석조아미타불입상</a>
        <!-- <span class="label-type purple-2">국보</span>
        <span class="label-type black">추천</span> -->
    </div>
</li>
""".strip()

prompt = f"""
beautifulsoup 파서를 통해 웹 사이트 링크 정보를 수집하려고 합니다. 
```
[base_url]: {base_url}
```
[query_string]: {query_string} 
```
[tag_samples]: 
{tag_samples} 
```

<information>
1. [base_url]을 기준으로 총 37페이지로 구성되어 있습니다.
2. 한 페이지에는 총 12개의 전시물 정보가 있으므로 쿼리 파라미터는 startCount=0, startCount=12, startCount=24...방식으로 증가합니다.
3. [tag_samples]는 각 페이지별로 card 형태로 전시물 정보가 들어 있는 구조를 보여주는 예시입니다.
</information>

<instructions>
1. 37번 순회하면서 beautifulsoup 파서를 통해 페이지별 쿼리 스트링을 반환하는 파이썬 함수를 작성합니다.
2. 쿼리 스트링의 예시는 "?schM=view&relicId=348"입니다.
3. 함수의 반환값은 다음과 같은 리스트 구조입니다.
    [{{"page": <페이지 번호>, "query": <쿼리 스트링>}}, ...] 
4. 서버 부하 방지를 위해 한 번 순회시마다 1초의 휴지를 둡니다.
5. 수집된 결과는 data 폴더 밑에 relic_links.json 파일로 저장합니다.
</instructions>

<response_format>
    ```python
        ...여기에 코드 작성...
    ```
    </python>
</response_format>
""".strip()

print(prompt)

import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    temperature=0,
    messages=[
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "<python>"},
    ], 
    stop_sequences=["</python>"],
)

print(response.content[0].text.replace("```python", "").replace("```", "").strip())
