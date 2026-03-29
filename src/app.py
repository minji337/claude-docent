import streamlit as st
import logging
from utils import setup_logging

setup_logging()

from utils import get_base64_data
from llm import DocentBot

logger = logging.getLogger(__name__)
logger.info("도슨트 봇 시작 >>>>>")

# Streamlit 페이지 설정
st.set_page_config(page_title="도슨트 봇", page_icon="🎭", layout="centered")

# 공통 CSS 스타일 정의
st.markdown(
    """
    <style>        
        .stSidebar {
            width: 35rem !important;
        }          

        .intro-text {
            text-align: center; 
            padding: 1.25rem; 
            margin-top: 4.5rem; 
            border-radius: 10px; 
            background-color: #f9f9f9; 
            color: #333333;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .relic-card {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .relic-header {
            font-weight: bold;
            font-size: 18px;
            color: #333;
            margin-top: -1.25rem;
        }

        .relic-title {
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 0.93rem;
            color: #333;
        }

        .stChatMessage > div:first-child {
            flex: 0 0 30px !important;   
            font-size: 30px !important;  
            line-height: 30px !important;
            width: 30px !important;      
            height: 30px !important;

        }

        div[data-testid="stChatInput"]::after {
            content: "도슨트 봇은 실수를 할 수 있으니 중요한 정보는 꼭 다시 확인하세요.";
            position: absolute;
            bottom: -25px;        
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.8rem;
            color: #888888;
        } 

        .stSpinner {
            position: fixed;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);            
            margin: 0 auto;
            width: 350px;
            font-size: 20px;
            font-weight: bold;
            background-color: #f0f0f0; /* 스피너 배경색 추가 */
            padding: 10px; /* 배경색이 잘 보이도록 패딩 추가 */
            border-radius: 5px; /* 모서리 둥글게 */
            z-index: 9999; /* 최상단에 위치 */
        }

        .disable_overlay {
            position: fixed;
            top: 0; 
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 9998; 
            background-color: rgba(0,0,0,0);
            box-shadow: 2px 2px 10px rgba(0,0,0,0);
        }

       

    </style>
    """,
    unsafe_allow_html=True,
)

how_to_use = """
### 사용 방법
1. 전시물에 관해 편안하게 이야기 나누세요.
2. 찾고 싶은 전시물이 있으면 말씀해주세요.
3. 문화해설 프로그램은 아래에서 신청할 수 있어요.
4. 개인정보는 절대 입력하지 마세요.

### 예시 질문
- 이 전시물의 감상 포인트는 무엇인가요?
- 이 전시물의 시대적 배경을 설명해주세요.
- 조선시대 불상을 찾아주세요.
- 문화해설 프로그램을 소개해주세요.
"""

st.session_state.relics = [
    {
        "header": "2점 중 1번째 이미지",
        "img_path": "data/relic1.png",
        "title": "1번 전시물",
    },
    {
        "header": "2점 중 2번째 이미지",
        "img_path": "data/relic2.png",
        "title": "2번 전시물",
    },
]

avatar = {"assistant": "👩‍🦰", "user": "🧑🏻‍💻"}


def on_progress(func) -> str | None:
    overlay_placeholder = st.empty()
    overlay_placeholder.markdown(
        """
        <div class="disable_overlay"></div>
        """,
        unsafe_allow_html=True,
    )
    with st.spinner("잠시만 기다려주세요."):
        try:
            result = func()
        except Exception as e:
            st.error(f"도슨트 챗봇에서 오류가 발생했습니다: {e}")
            return "오류가 발생했네요. 죄송하지만 잠시 후 다시 시도해주세요."

    overlay_placeholder.empty()
    return result


def init_page() -> None:
    # 사이드바 설정
    with st.sidebar:
        st.markdown(how_to_use)

    # 카드 형태의 안내문구
    st.markdown(
        """
        <div class="intro-text">
            <h3>AI 도슨트 👩‍🦰 뮤지입니다</h3>
            <p>안녕하세요! 저희 K-디지털 박물관에 오신 것을 환영합니다.</p>
            <p>
                저는 이곳 박물관에서 근무하는 인공지능 도슨트 봇 뮤지입니다.<br>
                이곳에서는 430여 종의 대한민국 국보/보물 이미지를 소장하고 있습니다.<br>
                작품 설명은 물론 저의 감상까지도 자세히 말씀드려요.
            </p>
            <p>
                아래의 <strong>'입장하기'</strong> 버튼을 눌러 투어를 시작해 보세요!
            </p>            
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3개의 컬럼으로 나눈 후 가운데에만 버튼을 배치하여 중앙 정렬
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        if st.button("입장하기", use_container_width=True, type="primary"):
            st.session_state.status = "entered"
            logger.info("입장하기 버튼이 클릭되었습니다.")
            docent_bot = DocentBot()
            st.session_state.docent_bot = docent_bot
            st.rerun()


def main_page(docent_bot: DocentBot) -> None:
    def side_bar() -> None:
        # 사이드바 설정
        with st.sidebar:
            header, img_path, title = (
                st.session_state.relic_card["header"],
                st.session_state.relic_card["img_path"],
                st.session_state.relic_card["title"],
            )

            with open(img_path, "rb") as img_file:
                img_base64 = get_base64_data(img_file)

            st.markdown(
                f'<div class="relic-card">'
                f'<div class="relic-header">{header}</div>'
                f'<img src="data:image/png;base64,{img_base64}" style="width:450px; height:540px; object-fit:contain;">'
                f'<div class="relic-title">{title}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

            _, col_left, _, col_right, _ = st.columns(
                [5, 5, 1, 5, 5]
            )  # 네비게이션 버튼
            with col_left:
                if st.button("이전", use_container_width=True):
                    logger.info("이전 버튼이 클릭되었습니다.")
                    on_progress(lambda: docent_bot.move(is_next=False))
                    st.session_state.relic_card = docent_bot.relics.current_to_card()
                    st.rerun()

            with col_right:
                if st.button("다음", use_container_width=True):
                    logger.info("다음 버튼이 클릭되었습니다.")
                    on_progress(lambda: docent_bot.move(is_next=True))
                    st.session_state.relic_card = docent_bot.relics.current_to_card()
                    st.rerun()

            st.markdown(
                """     
                <div style="font-size: 0.87em; text-align: center;">
                본 이미지는 <strong>국립중앙박물관</strong>이 공공누리 제1유형으로 개방한 자료로서<br><a href="https://www.museum.go.kr">museum.go.kr</a>에서 무료로 다운로드 받을 수 있습니다.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("---")
            st.markdown(how_to_use)

    def chat_area() -> None:
        for message in docent_bot.get_conversation():
            with st.chat_message(message["role"], avatar=avatar[message["role"]]):
                st.markdown(message["content"])
        user_message = st.chat_input("메시지를 입력하세요.")
        if user_message:
            with st.chat_message("user", avatar=avatar["user"]):
                st.markdown(user_message)
            docent_answer = on_progress(lambda: docent_bot.answer(user_message))
            with st.chat_message("assistant", avatar=avatar["assistant"]):
                st.markdown(docent_answer)

    side_bar()
    chat_area()


if "status" not in st.session_state:
    init_page()
elif st.session_state.status == "entered":
    docent_bot: DocentBot = st.session_state.docent_bot
    st.session_state.status = "guide_active"
    on_progress(lambda: docent_bot.move(is_next=True))
    st.session_state.relic_card = docent_bot.relics.current_to_card()
    st.rerun()
elif st.session_state.status == "guide_active":
    docent_bot: DocentBot = st.session_state.docent_bot
    main_page(docent_bot)
else:
    st.error("알 수 없는 세션 상태입니다. 페이지를 새로고침해주세요.")
