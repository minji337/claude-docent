from openai import OpenAI
import os
from cosine_similarity import cosine_similarity
from itertools import repeat

client = OpenAI(
    api_key=os.environ['UPSTAGE_API_KEY'],
    base_url="https://api.upstage.ai/v1"
)


text1 = """
인간은 지구상에서 가장 흔하고, 널리 분포하는 영장류의 일종이다. 
""".strip()
text2 = "사람의 정의"
text3 = "생명체의 정의"
text4 = "인식의 정의"

text_list = [text1, text2, text3, text4]
emb_list = []
for no, text in enumerate(text_list, start=1):
    response = client.embeddings.create(
        input=text,
        model="embedding-query"
    )
    emb_list.append(response.data[0].embedding)
    print(f"text{no} 임베딩 벡터 사이즈: {len(response.data[0].embedding)}")

for index, (emb_a, emb_b) in enumerate(zip(repeat(emb_list[0]), emb_list[1:]), start=1): 
    cos = cosine_similarity(emb_a, emb_b)
    print(f"text1과 '{text_list[index]}' 사이의 코사인 유사도: {cos}")
