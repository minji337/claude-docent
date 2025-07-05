from openai import OpenAI
import os
from cosine_similarity import cosine_similarity

client = OpenAI(
    api_key=os.environ['UPSTAGE_API_KEY'],
    base_url="https://api.upstage.ai/v1"
)

docs = [
    "인간은 지구상에서 가장 흔하고, 널리 분포하는 영장류의 일종이다.",
    "빅뱅은 우주가 약 138억 년 전 극단적으로 밀도 높고 뜨거운 상태에서 급격히 팽창하며 시작되었다는 우주론적 모델이다.",
    "인터넷은 전 세계 컴퓨터를 TCP/IP 프로토콜로 연결해 정보를 실시간 교환하는 거대 네트워크이다.",
    "모나리자는 레오나르도 다빈치가 16세기 초 그린 인물화로, 수수께끼 같은 미소로 유명한 르네상스 걸작이다.",
    "재즈는 19세기 말 뉴올리언스에서 탄생한 즉흥 연주 중심의 아프리카계 미국 음악 장르이다.",
    "빅데이터는 대용량·고속·다양성 데이터를 분석해 가치를 추출하는 정보 처리 패러다임이다.",
    "양자역학은 미시 세계에서 입자와 파동의 이중성을 설명하는 현대 물리학의 근간이다.",
    "월드컵은 FIFA가 주관해 4년 주기로 열리는 지구촌 최대 축구 국가 대항전이다.",
    "바둑은 흑백 돌로 집을 차지해 승부를 겨루는 4천 년 역사의 전략 보드게임이다.",
    "비트코인은 탈중앙 P2P 네트워크에서 채굴·거래되는 최초의 암호화폐이다."
]

from dataclasses import dataclass

@dataclass
class DocEmbeddings:    
    doc: str
    embeddings: float

doc_embeddings_db: list[DocEmbeddings]= []

def build(docs, doc_embeddings_db: list[DocEmbeddings]):
    for doc in docs:
            response = client.embeddings.create(
                input=doc,
                model="embedding-query"
            )
            doc_embeddings_db.append(DocEmbeddings(doc=doc, embeddings=response.data[0].embedding))
    
build(docs, doc_embeddings_db)

def query(query: str, top_k: int = 1):
    response = client.embeddings.create(
        input=query,
        model="embedding-query"
    )
    query_embeddings = response.data[0].embedding
    similarities = {}
    for index, doc_embeddings in enumerate(doc_embeddings_db):          
        similarities[index] = cosine_similarity(query_embeddings, doc_embeddings.embeddings)

    indexes = sorted(
            similarities.keys(), key=lambda x: similarities[x], reverse=True
        )[:top_k]
    return [doc_embeddings_db[index].doc for index in indexes]

results = query("블루스에 대해 알려줘")
print(results)

from anthropic import Anthropic

anthropic_client = Anthropic()

rag_prompt_template = """
다음의 **맥락**만 활용해 질문에 답하세요.  
{context}

질문: {question}

맥락을 제공받았다는 말은 생략하세요.
""".strip()


questions = [
    "오래 전에 만들어진 경기에 대해 알려주세요.",
    "세계 최대의 스포츠 이벤트 중 하나를 소개해주세요.",
]

for question in questions:
    context = query(question)
    rag_prompt = rag_prompt_template.format(context=context, question=question)
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0,
        messages=[
            {"role": "user", "content": rag_prompt}
        ]
    )
    print(response.content[0].text ,"\n")
        