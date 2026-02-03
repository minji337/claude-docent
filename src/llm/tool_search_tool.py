from anthropic import Anthropic
from typing import Literal, Optional, Dict, TypedDict
from pydantic import BaseModel, Field
from .llm import claude_4_5 as claude
import logging
from tavily import TavilyClient
from .prompt_templates import history_based_prompt, tool_system_prompt

logger = logging.getLogger(__name__)

client = Anthropic()
tavily = TavilyClient()


class Category(BaseModel):
    nationality: str = Field(description="예: 한국, 중국, 일본")
    period: str = Field(description="예: 신라, 고려, 조선. 단, 통일신라는 '신라'로 표기")
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
        "type": "tool_search_tool_regex_20251119",
        "name": "tool_search_tool_regex"
    },
    {
        "name": "search_relics_by_period_and_genre",
        "description": "사용자가 시대와 장르를 모두 명시하여 전시물 검색을 요청한 경우에만 사용",
        "input_schema": Category.model_json_schema(),
        "defer_loading": True,
    },
    {
        "name": "search_historical_facts",
        "description": "역사적 사실·배경 설명이 필요한 질문에 대해 웹 검색으로 보조 정보 수집",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "웹 검색 키워드"},
            },
            "required": ["query"],
        },
        "defer_loading": True,
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


def search_historical_facts(query) -> tuple[list, str]:
    tavily_response = tavily.search(
        query=query,
        include_domains=["ko.wikipedia.org", "encykorea.aks.ac.kr"],
        max_results=3,
        search_depth="advanced"
    )
    logger.info(f"[query] {query}")
    logger.info(f"[tavily_response] {tavily_response['answer']}")
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
    response = client.beta.messages.create(
        max_tokens=1024,
        temperature=0.0,        
        tools=tools,
        system=[
            {
                "type": "text",
                "text": tool_system_prompt,
            },
        ],
        messages=messages,
        model="claude-sonnet-4-5-20250929",
        betas=["advanced-tool-use-2025-11-20"],
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
