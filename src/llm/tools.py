from anthropic import Anthropic
from typing import Literal, Optional, Dict, TypedDict
from pydantic import BaseModel, Field
from .llm import claude_4 as claude
import logging
from tavily import TavilyClient
from .prompt_templates import history_based_prompt

logger = logging.getLogger(__name__)


client = Anthropic()
tavily = TavilyClient()


class Category(BaseModel):
    nationality: str = Field(description="예: 한국, 중국, 일본")
    period: str = Field(
        description="예: 신라, 고려, 조선. 단, 통일신라는 '신라'로 표기"
    )
    genre: Literal[
        "건축",
        "조각(불상)",
        "조각(불상 외)",
        "공예",
        "회화",
        "서예",
        "장신구",
        "복식",
        "과학기술",
        "기타",
    ]


tools = [
    {
        "name": "search_relics_by_period_and_genre",
        "description": "사용자가 **시대**와 **장르**로 검색 요청하는 경우에 한해 선택할 것",
        "input_schema": Category.model_json_schema(),
    },
    {
        "name": "search_relics_without_period_and_genre",
        "description": "search_relics_by_period_and_genre 이외의 모든 검색 조건에 해당하는 경우 사용할 것",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "사용자 질의",
                },
            },
        },
    },    
    {
        "name": "search_historical_facts",
        "description": "역사적 사실에 대한 사용자의 질문에 답히기 위해 사용",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "웹 검색에 입력할 키워드를 3개 이내로 만들 것",
                },
            },
        },
    },
    {
        "name": "needs_relic_image",
        "description": "전시물 이미지가 필요한 질문인지 판단",
        "input_schema": {
            "type": "object",
            "properties": {
                "is_image_needed": {
                    "type": "boolean",
                    "description": "사용자의 메시지가 전시물에 관한 것인지 여부",
                },
            },
        },
    },
]


def search_relics_by_period_and_genre(
    search_condition: dict, database: dict
) -> tuple[dict, str]:
    results = {}
    for relic_id, relic_data in database.items():
        relic_category: dict = relic_data["category"]
        if relic_category == search_condition:
            results[relic_id] = relic_data
    message = (
        f"요청하신 전시물이 {len(results)}점 검색되었습니다. [다음] 버튼을 클릭해주세요."
        if len(results) > 0
        else "요청하신 전시물의 검색 결과가 없습니다."
    )
    return results, message


def search_relics_without_period_and_genre(
    query: str, database: dict, user_message: str
):
    title_similarities = title_collection.query(query, top_k=5)
    description_similarities = description_collection.query(query, top_k=30)
    content_similarities = content_collection.query(query, top_k=30)
    desc_cntn_similarities = get_rrf(
        [description_similarities, content_similarities], weights=[0.6, 0.4]
    )[:3]
    similarities = title_similarities + desc_cntn_similarities
    filtered_similarities = filter_results(similarities, user_message)
    results = {}
    for similarity in filtered_similarities:
        results[similarity.id] = database[similarity.id]
        # results[similarity.id]["is_presented"] = False
    message = (
        f"요청하신 전시물이 {len(results)}점 검색되었습니다. [다음] 버튼을 클릭해주세요."
        if len(results) > 0
        else "요청하신 전시물의 검색 결과가 없습니다. 조금 더 구체적으로 말씀해주세요!"
    )
    return results, message
    

def search_historical_facts(query):
    tavily_response = tavily.search(
        query=query,
        include_domains=["ko.wikipedia.org", "encykorea.aks.ac.kr"],
        max_results=10,
        search_depth="advanced",
        include_answer="advanced",
    )
    references: list[tuple[str, str]] = []
    for result in tavily_response["results"][:3]:
        references.append((result["title"], result["url"]))
    return references, tavily_response["answer"]


# 전시물 검색 실습용
# def use_tools(
#     messages: list, database: dict
# ) -> tuple[Optional[dict], Optional[Dict[str, str]]]:
#     response = claude.create_tool_response(
#         messages=messages,
#         tools=tools,
#     )
#     if response.stop_reason != "tool_use":
#         return None, None
#     tool_content = next(
#         content for content in response.content if content.type == "tool_use"
#     )
#     data, message_dict = None, None
#     if tool_content.name == "search_relics_by_period_and_genre":
#         data, message = search_relics_by_period_and_genre(tool_content.input, database)
#         message_dict = {"role": "assistant", "content": message}
#     return data, message_dict


# 역사적 사실 검색 실습용
class ToolData(TypedDict):
    type: Literal["relics", "facts", "needs_image"]
    items: dict | list[tuple[str, str] | bool]


def use_tools(
    messages: list, database: dict
) -> tuple[Optional[ToolData], Optional[Dict[str, str]]]:
    response = claude.create_tool_response(
        messages=messages,
        tools=tools,
    )
    if response.stop_reason != "tool_use":
        return None, None
    tool_content = next(
        content for content in response.content if content.type == "tool_use"
    )
    tool_data, message_dict = None, None
    if tool_content.name == "search_relics_by_period_and_genre":
        data, message = search_relics_by_period_and_genre(tool_content.input, database)
        tool_data: ToolData = {"type": "relics", "items": data}
        message_dict = {"role": "assistant", "content": message}
    elif tool_content.name == "search_relics_without_period_and_genre":
        data, message = search_relics_without_period_and_genre(
            tool_content.input["query"], database, messages[-1]
        )
        tool_data: ToolData = {"type": "relics", "items": data}
        message_dict = {"role": "assistant", "content": message}
    elif tool_content.name == "search_historical_facts":
        data, message = search_historical_facts(tool_content.input["query"])
        tool_data: ToolData = {"type": "facts", "items": data}
        # message_dict = {"role": "user", "content": message}
        message_dict = {
            "role": "user",
            "content": history_based_prompt.format(history_facts=message),
        }
    elif tool_content.name == "needs_relic_image":
        tool_data: ToolData = {
            "type": "needs_image",
            "items": tool_content.input["is_image_needed"],
        }
        message_dict = None
    logger.info(f"[tool_data type] {tool_data['type']}")
    return tool_data, message_dict
