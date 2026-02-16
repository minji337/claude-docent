from typing import Literal, Optional, Dict, TypedDict
from pydantic import BaseModel, Field
from .llm import claude_4_5 as claude
import logging
from tavily import TavilyClient
from .prompt_templates import history_based_prompt

logger = logging.getLogger(__name__)


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
        "name": "search_historical_facts",
        "description": "역사적 사실에 대한 사용자의 질문에 답하기 위해 사용",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "웹 검색에 입력할 키워드를 만들 것",
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


def search_historical_facts(query) -> tuple[list, list]:
    tavily_response = tavily.search(
        query=query,
        include_domains=["ko.wikipedia.org", "encykorea.aks.ac.kr"],
        max_results=3,
        search_depth="advanced"
    )
    logger.info(f"[query] {query}")
    references: list[tuple[str, str]] = []
    contents: list[str] = []
    for result in tavily_response["results"]:
        references.append((result["title"], result["url"]))
        contents.append(result["content"])
    return references, contents


class ToolData(TypedDict):
    type: Literal["relics", "facts"]
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
    logger.info(f"[tool_content] {tool_content}")
    tool_data, message_dict = None, None
    if tool_content.name == "search_relics_by_period_and_genre":
        data, message = search_relics_by_period_and_genre(tool_content.input, database)
        tool_data: ToolData = {"type": "relics", "items": data}
        message_dict = {"role": "assistant", "content": message}
    elif tool_content.name == "search_historical_facts":
        data, message = search_historical_facts(tool_content.input["query"])
        tool_data: ToolData = {"type": "facts", "items": data}
        message_dict = {
            "role": "user",
            "content": history_based_prompt.format(history_facts=message),
        }
    logger.info(f"[tool_data type] {tool_data['type']}")
    logger.info(f"[message_dict] {message_dict}")
    return tool_data, message_dict
