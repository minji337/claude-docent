from openai import OpenAI
import os
from dataclasses import dataclass
import numpy as np

@dataclass
class DocEmbeddings:
    doc: str
    embeddings: float


client = OpenAI(
    api_key=os.environ["UPSTAGE_API_KEY"],
    base_url="https://api.upstage.ai/v1"
)

query_str = "서울에서 루프탑 바 야경 추천해줘"

docs = [
    "서울에 있는 루프가 있는 바 추천해줘",
    "바 루프 서울 탑 추천",
    "서울에서 루프top bar 밤 풍경 소개 부탁!",
    "서울에서 루프탑 바 야경 좋은 곳 추천해줘",
    "서울 night view 루프 바 리스트",
    "서울 지붕 옥탑 바 야경",
    "서울시에서 옥탑에서 추천시 추천",
    "추천 서울 탑 루프 바",
    "서울 시민 야경 추천 루프",
    "seoul 시민 야경 옥탑 바 추천",
]

doc_embeddings_db: list[DocEmbeddings] = []

def build(docs: list[str]):
    for doc in docs:
        response = client.embeddings.create(input=doc, model="embedding-query")
        doc_embeddings_db.append(
            DocEmbeddings(doc=doc, embeddings=response.data[0].embedding)
        )

def cosine_similarity(A, B):
  dot_product = np.dot(A, B)
  norm_A = np.linalg.norm(A)
  norm_B = np.linalg.norm(B)
  return round(float(dot_product / (norm_A * norm_B)), 4)

def query(query: str, top_k: int = 3):
    response = client.embeddings.create(input=query, model="embedding-query")
    query_embeddings = response.data[0].embedding
    similarities = {}
    for index, doc_embeddings in enumerate(doc_embeddings_db):
        similarities[index] = cosine_similarity(
            query_embeddings, doc_embeddings.embeddings
        )

    indexes = sorted(similarities.keys(), key=lambda x: similarities[x], reverse=True)[
        :top_k
    ]
    return [doc_embeddings_db[index].doc for index in indexes]


query_str = "서울에서 루프탑 바 야경 추천해줘"
build(docs)
embedding_results = query(query_str, top_k=10)
print("\n임베딩 벡터터 검색 상위 순:")
print(*embedding_results, sep="\n")

from rank_bm25 import BM25Okapi
from konlpy.tag import Okt


okt = Okt()

tokenized_docs = [okt.morphs(doc) for doc in docs]
print(*tokenized_docs, sep='\n')
bm25 = BM25Okapi(tokenized_docs)
tokenized_query = okt.morphs(query_str)
print(tokenized_query)
scores = bm25.get_scores(tokenized_query)
bm25_results = bm25.get_top_n(tokenized_query, docs, n=10)
print("\nbm25 상위 순:")
print(*bm25_results, sep="\n")


from typing import Tuple, DefaultDict
from collections import defaultdict

def get_rrf(
    ranked_lists: list[list[str]],
    k: int = 60,
    weights: list[float] | None = None,
) -> list[Tuple[str, float]]:
    scores: DefaultDict[str, float] = defaultdict(float)
    for weight, ranked_list in zip(weights, ranked_lists):
        for rank, element in enumerate(ranked_list, start=1): 
            score = weight / (k + rank)
            scores[element] += score

    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

rrf_results = get_rrf(
    ranked_lists=[embedding_results, bm25_results],
    weights=[0.5, 0.5]
)

print("\nRRF 상위 순:")
print(*rrf_results, sep="\n")
