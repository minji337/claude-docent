from rank_bm25 import BM25Okapi

docs = ["벡터 벡터 이해", "벡터 이해", "양자역학 이해 이해", "한국어 이해", "이해 이해"]
corpus = [doc.split() for doc in docs]
bm25 = BM25Okapi(corpus)
query = "벡터 이해".split()
bm25_results = bm25.get_top_n(query, docs, n=5)
print("\nbm25 상위 순:")
for doc in bm25_results:
    print(doc)
