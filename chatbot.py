import streamlit as st

prompt = st.chat_input("메시지를 입력하세요.")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("이것은 인공지능 응답입니다.")
