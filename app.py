
import streamlit as st
from anthropic import Anthropic
import os
from PIL import Image

# Streamlit 페이지 설정
st.set_page_config(page_title="도슨트 봇", page_icon="🤖", layout="wide")


sidebar_text = """
### 🤖 반가워요. 대화하는 챗봇입니다.

### 사용 방법
- 무엇이든 편히 말씀해주세요.
- 매너 있는 대화를 나누어요.

### 예시 질문
- 오늘 날씨는 어떤가요?
- 최신 뉴스가 궁금해요.
- 취미나 관심사에 대해 이야기 해요.
- 끝말잇기 게임을 해요.
"""

# sidebar_text = """
# ### 🎭반가워요. 도슨트봇입니다.

# ### 사용 방법
# 1. 원하는 질문이 있으면 말씀해주세요.
# 2. 작품에 대해 궁금한 점을 물어보세요.

# ### 예시 질문
# - 이 작품의 작가는 누구인가요?
# - 작품의 제작 기법에 대해 설명해주세요
# - 작품의 역사적 배경은 무엇인가요?
# - 작품에 담긴 상징적 의미는 무엇인가요?
# """

# system_prompt = """
# 당신은 한국 박물관의 전문 도슨트이며 이름은 '한이음'입니다.
# 다음 원칙들을 지켜 관람객의 질문에 답변해 주세요:
# 1. 전문성과 친근함
# - 문화재와 예술품에 대한 정확한 정보를 제공합니다
# - 전문 용어는 쉽게 풀어서 설명합니다
# - 존댓말을 사용하며 친절하게 응대합니다

# 2. 답변 방식
# - 핵심 정보를 먼저 전달한 후 상세 설명을 덧붙입니다
# - 불확실한 정보는 추측하여 답변하지 않습니다
# - 흥미로운 이야기나 일화를 포함하여 설명합니다

# 관람객의 질문에 위 원칙들을 지키면서 답변해 주세요.
# """


# 사이드바 설정
with st.sidebar:
    st.markdown(sidebar_text)

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    api_key = st.secrets["api_keys"]["anthropic"]


@st.cache_resource
def get_client():
    client = Anthropic(api_key=api_key)
    print("cleint loaded...")
    return client


client = get_client()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("메시지를 입력하세요."):
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        response = ""
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                messages=[
                    {"role": message["role"], "content": message["content"]}
                    for message in st.session_state.messages
                ],
                max_tokens=1024,
            )
            response = response.content[0].text
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            response = "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."
        finally:
            st.markdown(response)
