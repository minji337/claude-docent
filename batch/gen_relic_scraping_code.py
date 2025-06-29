base_url = "https://www.museum.go.kr/MUSEUM/contents/M0504000000.do"
image_file_sample = """
<a href="javascript:;" class="swiper-slide" style="background:url('/relic_image//PS01001001/bon001/2016/1124093013018/700/bon001958-000-0001.jpg') no-repeat center; background-size:cover">감산사 석조미륵보살입상 이미지 1 보기</a>
<a href="javascript:;" class="swiper-slide" style="background:url('/relic_image//PS01001001/bon001/2017/0508160735009/700/bon001958-00-01.jpg') no-repeat center; background-size:cover">감산사 석조미륵보살입상 이미지 2 보기</a>
...중략...
"""
label_sample = """
<div class="outview-tit-box">
    <div class="label-list">
        <span class="label-type purple-2">중요</span>
    </div>
    <div class="outview">
        <strong class="outveiw-tit">감산사 석조미륵보살입상</strong>
        <ul class="outview-list">
            <li><strong>다른명칭</strong>
                <p>국보 경주 감산사 석조 미륵보살 입상(1962), 慶州 甘山寺 石造彌勒菩薩立像</p>
            </li>
            <li>
                <strong>전시명칭</strong>
                <p>감산사미륵보살과 아미타불</p>
            </li>
            <li><strong>국적/시대</strong>
                <p>한국 - 통일신라</p>
            </li>
            <li><strong>출토지</strong>
                <p>출토지 - 경상북도</p>
            </li>
            <li><strong>재질</strong>
                <p>돌 - 화강암</p>
            </li>
            <li><strong>분류</strong>
                <p>종교신앙 - 불교 - 예배 - 불상</p>
            </li>
            <li><strong>크기</strong>
                <p>높이 270.0cm</p>
            </li>
            <li><strong>지정문화유산</strong>
                <p>국보 </p>
            </li>
            <li><strong>소장품번호</strong>
                <p>본관 1958 </p>
            </li>
            <li><strong>전시위치</strong>
                <p>불교조각</p>
            </li>
        </ul>
    </div>
</div>
"""

content_sample = """
<div class="view-info-cont view-info-cont2">
    <p>신체와 광배는 하나의 돌로 제작하고, 별도로 제작한 대좌에 결합시켰다. 이러한 형식은 감산사 절터에서 함께 수습된 &lt;아미타불&gt;과 같다. 머리에는 높은 보관을 썼는데 중앙에
        화불(化佛)이 있다. 얼굴은 갸름하나 살이 올라 있고 눈과 입에 미소가 어려 있다. 목에는 삼도가 뚜렷하며 목걸이, 팔찌, 영락 장식 등으로 신체를 화려하게 장식하고 있다. 오른손은
        자연스럽게 내려뜨리고 있고, 왼손은 들어 올려 손바닥을 보이고 있다. 팔목에는 천의가 걸쳐져 있는데, 법의(法衣)는 얇아서 신체의 풍만하고 유려한 곡선을 더욱 살려주고 있다. 광배는
        배모양에 신체를 모두 감싸는 주형거신광(舟形擧身光)으로, 세 가닥의 선으로 두광과 신광을 구분하였다. 광배 뒷면에는 명문이 새겨져 있는데, 이를 통해 719년 김지성(金志誠)이 돌아가신
        어머니를 위해 조성한 미륵보살상임을 알 수 있다. 표현이 사실적이고 관능적인 모습을 한 통일신라 8세기 불상의 대표적인 사례이다.</p>
    <div class="btn-list mt10"></div>
    <div class='codeView01 codeCopyright line'>
        <img src='https://www.kogl.or.kr/open/web/images/images_2014/codetype/new_img_opentype01.png'
            alt='공공저작물 자유이용허락 출처표시' />
        <div class="txt">
            국립중앙박물관이(가) 창작한 감산사 석조미륵보살입상 저작물은 공공누리&nbsp;<a href='https://www.kogl.or.kr/info/licenseType1.do'
                target='_blank' title='새 창으로 열기'>공공저작물 자유이용허락 출처표시</a>&nbsp;조건에 따라 이용할 수 있습니다.
        </div>
    </div>
</div>
"""	

relic_index_sample =  """
{
    "348": {
        "url": "https://www.museum.go.kr/MUSEUM/contents/M0504000000.do?schM=view&searchId=treasure&relicId=348",
        "img": "/relic_image/PS01001001/bon001/2016/1124093013018/bon001958-000-0001.jpg",
        "label": {
            "명칭": "감산사 석조미륵보살입상",
            "다른명칭": "국보 경주 감산사 석조 미륵보살 입상(1962), 慶州 甘山寺 石造彌勒菩薩立像",
            "전시명칭": "감산사미륵보살과 아미타불",
            "국적/시대": "한국 - 통일신라",
            "출토지": "출토지 - 경상북도",
            "재질": "돌 - 화강암",
            "분류": "종교신앙 - 불교 - 예배 - 불상",
            "크기": "높이 270.0cm",
            "지정문화유산": "국보",
            "소장품번호": "본관 1958",
            "전시위치": "불교조각"
        },
        "content": "신체와 광배는 하나의 돌로 제작하고, 별도로 제작한 대좌에 결합시켰다. 이러한 형식은 감산사 절터에서 함께 수습된 <아미타불>과 같다. 머리에는 높은 보관을 썼는데 중앙에 화불(化佛)이 있다. 얼굴은 갸름하나 살이 올라 있고 눈과 입에 미소가 어려 있다. 목에는 삼도가 뚜렷하며 목걸이, 팔찌, 영락 장식 등으로 신체를 화려하게 장식하고 있다. 오른손은 자연스럽게 내려뜨리고 있고, 왼손은 들어 올려 손바닥을 보이고 있다. 팔목에는 천의가 걸쳐져 있는데, 법의(法衣)는 얇아서 신체의 풍만하고 유려한 곡선을 더욱 살려주고 있다. 광배는 배모양에 신체를 모두 감싸는 주형거신광(舟形擧身光)으로, 세 가닥의 선으로 두광과 신광을 구분하였다. 광배 뒷면에는 명문이 새겨져 있는데, 이를 통해 719년 김지성(金志誠)이 돌아가신 어머니를 위해 조성한 미륵보살상임을 알 수 있다. 표현이 사실적이고 관능적인 모습을 한 통일신라 8세기 불상의 대표적인 사례이다.",
        "copyright_img": "https://www.kogl.or.kr/open/web/images/images_2014/codetype/new_img_opentype01.png"
    },
    "349": {
        ...
    },
    ...
}
"""

prompt = f"""
스크래핑을 통해 json 포맷의 데이터베이스를 만들려고 합니다.
[base_url]: {base_url}
```
[html_image_file_sample]:
{image_file_sample}
[html_label_sample]:
{label_sample}
[html_content_sample]:
{content_sample}
```
[relic_index_sample]
{relic_index_sample}
```
<INSTRUCTIONS>
다음 지침에 의거하여 전시물 데이터베이스를 구축하는 파이썬 프로그램을 작성합니다.
<JSON 정보 추출 함수 작성>
1. data/relic_links.json 파일을 읽습니다. 다음은 샘플입니다. 
    [
        {{"page": 1, "query": "?schM=view&relicId=348"}},
        {{"page": 1, "query": "?schM=view&relicId=349"}},
        ...
    ]
2. [base_url]에 “query”를 결합해서 URL을 만듭니다.
3. url에 접근하여 HTML을 수신받은 후 Beautifulsoup 파서를 통해  [relic_data_sample] 형식의 데이터를 만듭니다. 
    - 이때 Key는 relicId로 합니다.
    - [relic_index_sample] 데이터 구성은 [html_xxx_sample] 정보를 참조하되, 이미지 파일은 첫번째 <a> 태그의 정보를 가져옵니다. 
4. 결과는 relic_index_json 변수에 담습니다.
5. 서버 부하 방지를 위해 한 번 순회시마다 1초의 휴지를 둡니다.
</JSON 정보 추출 함수 작성 지침>       

<공공누리 유형 점검 함수 작성>
relic_index_json['copyright_img'] != https://www.kogl.or.kr/open/web/images/images_2014/codetype/new_img_opentype01.png인 전시물은 삭제하고 결과를 출력합니다.
</공공누리 유형 점검 함수 작성>

<데이터베이스 구축 함수 작성>
1. data 폴더 아래에 database 폴더를 만듭니다. 존재하면 삭제하고 다시 만듭니다.
2. database 폴더에 <JSON 정보 추출 함수 작성 지침/>에서 만든 relic_index_json을 relic_index.json이라는 파일로 만듭니다.
3. database 폴더 밑에 relciId를 이름으로하여 하위 폴더를 만듭니다.
4. 하위 폴더에 다음 정보를 작성합니다.
    1) relic_index_json 중 relicId에 해당하는 정보로 relic_data.json 파일을 만듭니다.
    2) 전시물 이미지 파일의 경로를 확인하고 다운로드합니다.
</데이터베이스 구축 함수 작성>
</INSTRUCTIONS>    

<RESPONSE_FORMAT>
    ```python
        ...여기에 코드 작성...
    ```
    </python>
</RESPONSE_FORMAT>
"""
print(prompt)

import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
model="claude-sonnet-4-20250514",
    max_tokens=3072,
    temperature=0,
    messages=[
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "<python>"},
    ], 
    stop_sequences=["</python>"],
)

print(response.content[0].text.replace("```python", "").replace("```", "").strip())

