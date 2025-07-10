import streamlit as st
st.title("echo-bot")

if "messages" not in st.session_state:
    st.session_state.messages= []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])    

if prompt := st.chat_input("메시지를 입력하세요."):
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = f"{prompt}... {prompt}... {prompt}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
 