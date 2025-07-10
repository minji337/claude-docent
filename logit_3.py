import streamlit as st
import time


def get_vocab_logits():
  print(f"get_vocab_logits() starting")
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
      "왔다": 0.95
  }
  print(f"get_vocab_logits() ending")
  return vocab_logits


text = "마지막 레이어의 로짓값을 가정"
st.header(text, divider='rainbow')
st.subheader(text)
st.title(text)
st.write(text)
st.text_input(label="Title", placeholder=text)
st.write("# Bar Chart")
st.bar_chart(get_vocab_logits())
st.caption(text)
