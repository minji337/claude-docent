import json
from pathlib import Path
import re
from dataclasses import dataclass, field
import numpy as np
import os
from openai import OpenAI
import dill
import json


BASE_DIR = Path(__file__).resolve().parent          
ROOT_DIR = BASE_DIR.parent                          

upstage = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"), base_url="https://api.upstage.ai/v1"
)

import re

HANJA_RE = re.compile(
    r"["
    r"\u4E00-\u9FFF"  # 기본
    r"\u3400-\u4DBF"  # 확장 A
    r"\uF900-\uFAFF"  # 호환 한자
    r"\U00020000-\U0002A6DF"  # 확장 B
    r"\U0002A700-\U0002B73F"  # 확장 C–D
    r"\U0002B740-\U0002B81F"  # 확장 E
    r"]+"
)

def clean_text(text: str, replace_with: str = "") -> str:
    text = re.sub(r"\([^)]*\)|,", "", text)
    text = HANJA_RE.sub(replace_with, text)
    return text


@dataclass
class DocEmbedding:
    id: str
    doc: str
    embedding: list[float] | None = None


@dataclass
class Similarity:
    id: str
    doc: str
    score: float = 0


class Collection:
 
    def __init__(self, name: str):
        self.name = name
        self.file_path = ROOT_DIR / "data" / "vector_store" / f"{name}"
        self.index: dict[str, DocEmbedding] = {}
    
    def load(self) -> "Collection":
        with open(f"{self.file_path}_meta.json", "r", encoding="utf-8") as f:
            docs_list = json.load(f)

        embeddings_array = np.load(f"{self.file_path}_embeddings.npy")

        for doc, embedding in zip(docs_list, embeddings_array):
            self.index[doc["id"]] = DocEmbedding(
                id=doc["id"], doc=doc["doc"], embedding=embedding.tolist()
            )

        return self        

    def add_doc(self, id: str, doc: str) -> None:
        self.index[id] = DocEmbedding(id=id, doc=doc)

    def build(self) -> None:
        doc_embeddings_all = list(self.index.values())
        doc_embeddings_chunks = [
            doc_embeddings_all[i:i+100] 
            for i in range(0, len(doc_embeddings_all), 100)
        ]

        doc_all_list = []
        embedding_all_list = []
        for doc_embeddings in doc_embeddings_chunks:
            docs = [doc_embedding.doc for doc_embedding in doc_embeddings]
            embeddings = self._get_embeddings(docs)
            for doc_embedding, embedding in zip(doc_embeddings, embeddings):
                doc_embedding.embedding = embedding
                doc_all_list.append({"id": doc_embedding.id, "doc": doc_embedding.doc})
                embedding_all_list.append(embedding)

        embedding_np_array = np.array(embedding_all_list)
        np.save(f"{self.file_path}_embeddings.npy", embedding_np_array)        

        with open(f"{self.file_path}_meta.json", "w", encoding="utf-8") as f:
            json.dump(doc_all_list, f, ensure_ascii=False, indent=2)

    def query(self, query: str, cutoff=0.4, top_k: int = 60) -> list[Similarity]:
        query_embedding = self._get_embeddings(query)[0]
        similarities: list[Similarity] = []
        for doc_embedding in self.index.values():
            score = np.dot(query_embedding, doc_embedding.embedding) / (
                np.linalg.norm(query_embedding)
                * np.linalg.norm(doc_embedding.embedding)
            )
            if score < cutoff:
                continue
            similarities.append(
                Similarity(
                    id=doc_embedding.id,
                    doc=doc_embedding.doc,
                    score=float(score)
                )
            )

        similarities = sorted(similarities, key=lambda x: x.score, reverse=True)[:top_k]
        return similarities

    def _get_embeddings(self, texts: list[str]) -> list[float]:
        embeddings = upstage.embeddings.create(input=texts, model="embedding-query")
        return [embedding_data.embedding for embedding_data in embeddings.data]            

    def __len__(self) -> int:
        return len(self.index)


relic_index_path = ROOT_DIR / "data" / "database" / "relic_index.json"

with open(relic_index_path, "r", encoding="utf-8") as f:
    relic_index = json.load(f)

#---------------------------------------------
# 제목 인덱스 만들기
#--------------------------------------------
title_collection = Collection("title")
for i, (key, value) in enumerate(relic_index.items()):    
    if i >= 2: break
    doc=f"{clean_text(value['label']['명칭']).strip()}, {clean_text(value['label']['다른명칭']).strip()}"
    title_collection.add_doc(id=key, doc=doc)

print("title len:", len(title_collection))

#title_collection.build()

title_collection = Collection("title")
title_collection.load()
resp =title_collection.query("감산사 석조미륵보살입상, 국보 경주 감산사 석조 미륵보살 입상")
print(f"{resp[0].score} >> {resp[0].doc}")
print(f"{resp[1].score} >> {resp[1].doc}")


#---------------------------------------------
# content 인덱스 만들기
#--------------------------------------------
content_collection = Collection("content")
for i, (key, value) in enumerate(relic_index.items()):    
    if i >= 2: break
    if not value['content']:
        doc=f"{clean_text(value['label']['명칭']).strip()}, {clean_text(value['label']['다른명칭']).strip()}"
    else:
        doc=f"{clean_text(value['content']).strip()}"

    content_collection.add_doc(id=key, doc=doc)

print("content_collection len:", len(content_collection))
#content_collection.build()

# print("\ncontent 기준 검색", "="*20)
# content_collection = Collection("content")
# content_collection.load()
# resp = content_collection.query("신체와 광배는 하나의 돌로 제작하고 별도로 제작한 대좌에 결합시켰다. 이러한 형식은 감산사 절터에서 함께 수습된 <아미타불>과 같다. 머리에는 높은 보관을 썼는데 중앙에 화불이 있다. 얼굴은 갸름하나 살이 올라 있고 눈과 입에 미소가 어려 있다. 목에는 삼도가 뚜렷하며 목걸이 팔찌 영락 장식 등으로 신체를 화려하게 장식하고 있다. 오른손은 자연스럽게 내려뜨리고 있고 왼손은 들어 올려 손바닥을 보이고 있다. 팔목에는 천의가 걸쳐져 있는데 법의는 얇아서 신체의 풍만하고 유려한 곡선을 더욱 살려주고 있다. 광배는 배모양에 신체를 모두 감싸는 주형거신광으로 세 가닥의 선으로 두광과 신광을 구분하였다. 광배 뒷면에는 명문이 새겨져 있는데 이를 통해 719년 김지성이 돌아가신 어머니를 위해 조성한 미륵보살상임을 알 수 있다. 표현이 사실적이고 관능적인 모습을 한 통일신라 8세기 불상의 대표적인 사례이다.")
# print(f"{resp[0].score} >> {resp[0].doc[:30]}..")


#---------------------------------------------
# description 인덱스 만들기
#--------------------------------------------
description_collection = Collection("description")
for i, (key, value) in enumerate(relic_index.items()):    
    if i >= 2: break
    doc=f"{clean_text(value['image_description']).strip()}"    
    description_collection.add_doc(id=key, doc=doc)

print("description_collection len:", len(description_collection))
#description_collection.build()

# description_collection = Collection("description")
# description_collection.load()
# resp = description_collection.query("회색 배경 앞에 서 있는 석조 불상으로, 높은 보관을 쓰고 있으며 얼굴에는 온화한 미소가 어려 있다. 신체는 풍만하고 유려한 곡선을 보이며, 목걸이와 팔찌 등으로 화려하게 장식되어 있다. 오른손은 자연스럽게 내려뜨리고 왼손은 들어 올려 손바닥을 보이고 있다. 전체적으로 배 모양의 광배가 신체를 감싸고 있으며, 사각형의 대좌 위에 서 있다.")
# print(f"{resp[0].score} >> {resp[0].doc[:30]}..")
# print(f"{resp[1].score} >> {resp[1].doc[:30]}..")