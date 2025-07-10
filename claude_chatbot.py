import streamlit as st
from anthropic import Anthropic

# Streamlit 페이지 설정
st.set_page_config(page_title="도슨트 봇", page_icon=" 🤖 ", layout="wide")

# Streamlit 페이지 설정
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

# 사이드 바 설정
with st.sidebar:
    st.markdown(sidebar_text)


@st.cache_resource
def get_client():
    client = Anthropic()
    print("client loaded...")
    return client

client = get_client()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 사용자 메시지 입력 및 AI 응답 생성
if prompt := st.chat_input("메시지를 입력하세요."):
    with st.chat_message("user"): 
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = ""
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
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
    with st.chat_message("assistant"):        
        st.markdown(response)

