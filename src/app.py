import streamlit as st
import logging
from utils import setup_logging, logger, get_base64_data, email_to_6digit_hash
from llm import DocentBot
import datetime
import asyncio
import threading
from concurrent.futures import Future
from reservation import reservation_agent as reservation_agent_module
from reservation.reservation_agent import ReservationAgent
import re
import datetime


setup_logging()

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


def on_progress(func) -> tuple[list, str] | None:
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
            return "", "오류가 발생했네요. 죄송하지만 잠시 후 다시 시도해주세요."

    overlay_placeholder.empty()
    return result


@st.cache_resource(show_spinner=False)
def _get_loop() -> asyncio.AbstractEventLoop:
    """
    새로운 이벤트 루프를 만들고 별도 데몬 스레드에서 run_forever로 영원히 돌린다.Streamlit 스크립트가 재실행되어도 이 루프는 그대로 유지된다.
    """
    loop = asyncio.new_event_loop()  # 새 루프
    t = threading.Thread(target=loop.run_forever, daemon=True)
    t.start()
    return loop


def run_async(coro) -> Future:
    # concurrent.futures.Future 를 즉시 반환하므로 Streamlit 쪽에서는 동기 코드처럼 상태를 확인할 수 있다.
    loop = _get_loop()
    return asyncio.run_coroutine_threadsafe(coro, loop)


@st.cache_resource(show_spinner=False)
def get_reservation_agent() -> tuple[ReservationAgent, Future]:
    agent = ReservationAgent()
    reservation_agent_module.reservation_agent = agent

    # 비동기 초기화 함수
    async def initialize_agent():
        await agent.initialize_socket_handler()
        await agent.connect_server()
        agent.build_agents()

    future = run_async(initialize_agent())
    return agent, future


resv_agent, mcp_connection_future = get_reservation_agent()


def init_page() -> None:
    # 사이드바 설정
    with st.sidebar:
        st.markdown(how_to_use)

    # 카드 형태의 안내문구
    st.markdown(
        """
        <div class="intro-text">
            <h3>AI 도슨트 👩‍🦰 뮤지입니다</h2>
            <p>안녕하세요! 저희 K-디지털 박물관에 오신 것을 환영합니다.<p>
            <p>
                저는 이곳 박물관에서 근무하는 인공지능 도슨트 봇 뮤지입니다.<br>
                이곳에서는 430여 여종의 대한민국 국보/보물 이미지를 소장하고 있습니다.<br>
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

            with st.form("docent_program_form"):
                st.subheader("문화해설 프로그램 신청")

                program = st.selectbox(
                    label="프로그램을 선택하세요",
                    options=[
                        "대표 유물 해설",
                        "전시관별 해설",
                        "외국인을 위한 해설(영어)",
                        "외국인을 위한 해설(중국어)",
                        "외국인을 위한 해설(일본어)",
                    ],
                    disabled=st.session_state.get("form_submitted", False),
                )

                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                weekday_map = ["월", "화", "수", "목", "금"]
                weekdays = []
                d = tomorrow
                while len(weekdays) < 10:
                    if d.weekday() < 5:  # 0~4: 월~금
                        weekdays.append(
                            f"{d.strftime('%Y-%m-%d')} ({weekday_map[d.weekday()]})"
                        )
                    d += datetime.timedelta(days=1)

                visit_date = st.selectbox(
                    label="방문 일자를 선택하세요",
                    options=weekdays,
                    disabled=st.session_state.get("form_submitted", False),
                )

                visit_hours = st.selectbox(
                    label="방문 시간을 선택하세요",
                    options=["11:00", "13:00", "15:00"],
                    disabled=st.session_state.get("form_submitted", False),
                )

                visitors = st.number_input(
                    label="방문 인원수를 입력하세요",
                    min_value=1,
                    value=1,
                    disabled=st.session_state.get("form_submitted", False),
                )

                applicant_email = st.text_input(
                    label="신청자 이메일을 입력하세요",
                    value="minjigobi@gmail.com",
                    disabled=st.session_state.get("form_submitted", False),
                )

                submitted = st.form_submit_button(
                    label="신청하기",
                    disabled=st.session_state.get("locked", False),
                    on_click=lambda: st.session_state.update(locked=True),
                )
                if submitted:
                    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                    if not re.match(email_pattern, applicant_email):
                        st.error("유효한 이메일 주소를 입력해주세요.")
                        return

                    st.session_state.form_submitted = True
                    application = {
                        "program": program,
                        "visit_date": visit_date,
                        "visit_hours": visit_hours,
                        "visitors": visitors,
                        "applicant_email": applicant_email,
                        "applicant_number": email_to_6digit_hash(applicant_email),
                        "application_time": datetime.datetime.now().strftime(
                            "%Y.%m.%d %H:%M:%S.%f"
                        ),
                    }
                    # ① 아직 연결 중이라면: 메시지만 띄우고 함수 종료``
                    if not mcp_connection_future.done():
                        st.error(
                            "MCP 서버에 연결 중입니다. 연결이 완료되면 다시 '신청하기'를 눌러 주세요."
                        )
                        return

                    if (
                        mcp_connection_future.done()
                        and mcp_connection_future.exception()
                    ):
                        st.error(
                            f"MCP 서버 연결 실패: {str(mcp_connection_future.exception())}"
                        )
                        return

                    run_async(resv_agent.make_reservation(application))
                    st.rerun()
                else:
                    st.markdown(
                        "🔔문화해설사님이 배정되면 이메일로 알려드립니다.  \n🚨부득이한 사정으로 취소해야 할 경우 방문일 전일까지 배정된 문화해설사님의 이메일로 통지 부탁드립니다."
                    )

    def chat_area() -> None:
        for message in docent_bot.get_conversation():
            with st.chat_message(message["role"], avatar=avatar[message["role"]]):
                st.markdown(message["content"])
        user_message = st.chat_input("메시지를 입력하세요.")
        if user_message:
            with st.chat_message("user", avatar=avatar["user"]):
                st.markdown(user_message)
            references, docent_answer = on_progress(
                lambda: docent_bot.answer(user_message)
            )
            with st.chat_message("assistant", avatar=avatar["assistant"]):
                st.markdown(docent_answer)
                if references:
                    expander = st.expander("📚 출처:")
                    for title, url in references:
                        expander.markdown(f"- [{title}]({url})")

    side_bar()
    chat_area()


if "status" not in st.session_state:
    init_page()
elif st.session_state.status == "entered":
    docent_bot: DocentBot = st.session_state.docent_bot
    with st.chat_message("assistant", avatar=avatar["assistant"]):
        st.markdown(docent_bot.greet())

    st.session_state.status = "guide_active"
    on_progress(lambda: docent_bot.move(is_next=True))
    st.session_state.relic_card = docent_bot.relics.current_to_card()
    st.rerun()
elif st.session_state.status == "guide_active":
    docent_bot: DocentBot = st.session_state.docent_bot
    main_page(docent_bot)
else:
    st.error("알 수 없는 세션 상태입니다. 페이지를 새로고침해주세요.")
