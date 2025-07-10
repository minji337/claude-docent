import streamlit as st

class LinearModel:
    def __init__(self, filepath="weights.txt"):
        self.file_handle = open(filepath, "r")

    def predict(self, input_data):
        self.file_handle.seek(0)
        try:
            weight = float(self.file_handle.read().strip())
        except ValueError:
            weight = 0
        return input_data * weight + 2

    def close_file(self):
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None            

@st.cache_data
def load_linear_model():
    print("loading started...")
    model = LinearModel()
    return model

try:
    model = load_linear_model()
    st.write("모델이 정상적으로 로드되었습니다.")
except Exception as e:
    st.write(f"Error loading model: {e}")
