import numpy as np

김현주 = [20, 90]
고영호 = [30, 70]
박희진 = [80, 50]
이소현 = [60, 10]
오지수 = [10, 20]

def cosine_similarity(A, B):
    dot_product = np.dot(A, B)
    norm_A = np.linalg.norm(A)
    norm_B = np.linalg.norm(B)
    return round(float(dot_product / (norm_A * norm_B)), 4)

if __name__ == "__main__":
    print(f"고영호와 김현주 사이의 코사인 유사도:{cosine_similarity(고영호, 김현주)}")
    print(f"고영호와 오지수 사이의 코사인 유사도:{cosine_similarity(고영호, 오지수)}")
