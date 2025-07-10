import streamlit as st
import time


@st.cache_data
def get_vocab_logits(param=0):
    print(f"get_vocab_logits({param}) starting")
    time.sleep(10)
    vocab_logits = {
        "나는": 0.01,
        "내일": 0.03,
        "오늘": 0.25,
        "어제": 0.3,
        "산에": 0.4,
        "학교에": 0.5,
        "집에": 0.65,
        "오른다": 1.2,
        "간다": 1.05,
        "왔다": 0.95,
    }
    vocab_logits = {word: logit + param for word, logit in vocab_logits.items()}
    print(f"get_vocab_logits({param}) ending")
    return vocab_logits


text = "마지막 레이어의 로짓값을 가정"
st.header(text, divider="rainbow")
st.subheader(text)
st.title(text)
st.write(text)

user_input = st.number_input(label="로짓값에 더해지는 숫자를 입력하세요.", value=0)

st.write("# Bar Chart")
st.bar_chart(get_vocab_logits(user_input))
st.caption(text)
