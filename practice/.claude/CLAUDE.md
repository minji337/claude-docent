# K-디지털 박물관 도슨트 봇 프로젝트

## 프로젝트 개요

국립중앙박물관의 국보·보물 이미지를 활용한 AI 도슨트 챗봇 서비스입니다.
Streamlit 기반 웹 앱으로, Claude API를 활용하여 전시물 해설과 문화해설 프로그램 예약 기능을 제공합니다.

## 기술 스택

| 분류 | 기술 | 버전 |
|------|------|------|
| **언어** | Python | 3.11+ |
| **웹 프레임워크** | Streamlit | 1.50+ |
| **AI/LLM** | Anthropic Claude API | anthropic 0.69.0 |
| **MCP** | mcp, fastmcp | 1.16.0, 2.5.2 |
| **스크래핑** | BeautifulSoup4, Requests | - |
| **메시징** | Slack Bolt | 1.29.0 |
| **스케줄링** | APScheduler | 3.10.0 |
| **이미지 처리** | Pillow | 11.3.0 |

## 프로젝트 구조

```
k-digital-museum-docent-bot/
├── src/
│ ├── app.py # Streamlit 메인 앱 (진입점)
│ ├── llm/
│ │ ├── docent.py # DocentBot 클래스 (도슨트 대화 관리)
│ │ ├── llm.py # LLM 래퍼 클래스 (Claude API 호출)
│ │ ├── prompt_templates.py # 프롬프트 템플릿 정의
│ │ ├── tools.py # 도구 정의 (검색, 분류 등)
│ │ └── vector_search.py # 벡터 검색 기능
│ ├── relics/
│ │ └── relics.py # Relics 데이터 관리 (전시물 로드/탐색)
│ ├── reservation/
│ │ ├── reservation_agent.py # MCP 기반 예약 에이전트
│ │ └── email_sender.py # 이메일 발송 기능
│ └── utils/
│ └── utils.py # 유틸리티 함수 (로깅, 인코딩 등)
├── crawler.py # 국립중앙박물관 크롤러
├── database/ # 크롤링된 전시물 데이터 (435점)
│ └── {relic_id}/
│ ├── relic_data.json # 전시물 메타데이터
│ └── .jpg # 전시물 이미지
├── data/ # 앱 데이터 (리플렛, 프로그램 안내 등)
├── mcp-slack-python/ # Slack MCP 서버
│ ├── main.py # MCP 서버 진입점
│ └── tools/
│ ├── slack_tools.py # Slack 도구 정의
│ └── config.py # 설정
└── pyproject.toml # 프로젝트 의존성 (uv/pip)
```

## 실행 명령어

# 개발 서버 실행
streamlit run src/app.py

환경 변수 (.env)
ANTHROPIC_API_KEY=...
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SMITHERY_API_KEY=...시물 해설 |
| `LLM` | llm/llm.py | Claude API 호출 래퍼 |
| `Relics` | relics/relics.py | 전시물 데이터 로드 및 탐색 |
| `ReservationAgent` | reservation/reservation_agent.py | MCP 기반 예약 처리 |

## ⚠️ 주의사항

- `database/` 폴더의 기존 JSON/이미지 파일 수정 금지
- `.env` 파일에 API 키 직접 노출 금지 (Git 커밋 금지)
- 크롤링 시 1초 미만 간격 요청 금지 (서버 부하 방지)