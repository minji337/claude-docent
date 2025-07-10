import streamlit as st
import sys

print("start...")  #로그 출력

text = "마지막 레이어의 로짓값을 가정2"
st.header(text, divider='rainbow')
st.subheader(text)
st.title(text)
st.write(text)
st.text_input(label="Title", placeholder=text)
st.write("# Bar Chart")
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
    "왔다": 0.95
}
st.bar_chart(vocab_logits)
st.caption(text)
print("end...")  #로그 출력
