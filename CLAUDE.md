# 국립중앙박물관 국보·보물 스크레이퍼

## 개요
국립중앙박물관 누리집의 국보·보물 상세 페이지를 스크래핑하여 로컬 데이터베이스를 구축하는 Python 스크레이퍼입니다.

- **데이터 출처**: [국립중앙박물관 국보·보물 검색](https://www.museum.go.kr/MUSEUM/contents/M0504000000.do?searchId=treasure&schM=list)
- **서버 부하 방지**: 요청 간 1초 휴지 (Rate Limiting)
- **자동 재시도**: 서버 에러 시 5초 대기 후 1회 재시도
- **로깅**: 파일(`scraper.log`) 및 콘솔 동시 출력

## 주요 기능

- 국보·보물 목록 자동 수집
- 각 유물의 상세 정보 스크래핑 (명칭, 시대, 출토지, 재질, 크기 등)
- 고해상도 이미지 다운로드 및 저장
- 본문 설명 텍스트 추출
- 저작권 정보 수집
- 구조화된 JSON 형식 저장

## 필수 요구사항

- **Python**: 3.11 이상
- **주요 라이브러리**:
  - `requests`: HTTP 요청 처리
  - `beautifulsoup4`: HTML 파싱
  - `Pillow`: 이미지 검증 및 처리

## 사용 방법

```bash
# 전체 스크래핑 (모든 국보·보물)
python scraper.py

# 테스트용 1건만 스크래핑
python scraper.py 1

# 10건만 스크래핑
python scraper.py 10

# 중단: Ctrl+C (진행 상황 통계 자동 저장)
```

## 프로젝트 구조

```
.
├── scraper.py              # 메인 스크레이퍼 스크립트
├── scraper.log             # 스크래핑 로그 파일
├── database/               # 수집 데이터 저장소
│   ├── 348/                # relic_id별 폴더
│   │   ├── bon001958-000-0001.jpg
│   │   └── relic_data.json
│   ├── 349/
│   └── ...
├── pyproject.toml          # 프로젝트 의존성 관리
└── CLAUDE.md               # 프로젝트 문서 (이 파일)
```

## 데이터 수집 및 작성

### 이미지 데이터
- <div class="swiper-container gallery-thumbs">태그 내의 첫 번째 이미지

### relic_data.json 필드

- `url`: 유물 상세 페이지 URL
- `img`: 이미지 경로 (상대 경로)
- `label`: 유물 메타데이터 (딕셔너리)
  - 명칭, 다른명칭, 전시명칭
  - 국적/시대, 출토지
  - 재질, 분류, 크기
  - 지정문화유산, 소장품번호, 전시위치
- `content`: 유물 설명 본문
- `copyright_img`: 저작권 표시 이미지 URL

### relic_data.json 예시
```json
{
  "348": {
    "url": "https://www.museum.go.kr/MUSEUM/contents/M0504000000.do?schM=view&relicId=348",
    "img": "/relic_image//PS01001001/bon001/2016/1124093013018/700/bon001958-000-0001.jpg",
    "label": {
      "명칭": "감산사 석조미륵보살입상",
      "다른명칭": "국보 경주 감산사 석조 미륵보살 입상(1962), 慶州 甘山寺 石造彌勒菩薩立像",
      "전시명칭": "감산사미륵보살과 아미타불",
      "국적/시대": "한국 - 통일신라",
      "출토지": "출토지 - 경상북도",
      "재질": "돌 - 화강암",
      "분류": "종교신앙 - 불교 - 예배 - 불상",
      "크기": "높이 270.0cm",
      "지정문화유산": "국보",
      "소장품번호": "본관1958",
      "전시위치": "불교조각"
    },
    "content": "신체와 광배는 하나의 돌로 제작하고, 별도로 제작한 대좌에 결합시켰다...",
    "copyright_img": "https://www.kogl.or.kr/open/web/images/images_2014/codetype/new_img_opentype01.png"
  }
}
```

## 제약사항
- **Rate Limiting**: 요청 간 1초 대기 필수 (서버 부하 방지)

## 네트워크 불안정시 참고사항
- **IPv6 DNS 불안정 시 우회**: IPv4 강제

