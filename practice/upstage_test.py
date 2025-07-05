from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ['UPSTAGE_API_KEY'],
    base_url="https://api.upstage.ai/v1"
)

response = client.embeddings.create(
    input="Solar embeddings are awesome",
    model="embedding-query"
)
print(response.data[0].embedding)
