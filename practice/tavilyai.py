from tavily import TavilyClient
from pprint import pprint
import os

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
response = tavily.search(query="오징어 게임 3의 흥행 실적을 알려줘.", include_answer=True)
pprint(response)
