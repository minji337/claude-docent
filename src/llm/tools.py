from anthropic import Anthropic
from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field
from .llm import claude_4 as claude


client = Anthropic()


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
]


def search_relics_by_period_and_genre(
    search_condition: dict, database: dict
) -> tuple[dict, str]:
    results = {}
    for relic_id, relic_data in database.items():
        relic_category: dict = relic_data["category"]
        if relic_category == search_condition:
            results[relic_id] = relic_data
            # results[relic_id]["is_presented"] = False
    message = (
        f"요청하신 전시물이 {len(results)}점 검색되었습니다. [다음] 버튼을 클릭해주세요."
        if len(results) > 0
        else "요청하신 전시물의 검색 결과가 없습니다."
    )
    return results, message


def use_tools(
    messages: list, database: dict
) -> tuple[Optional[dict], Optional[Dict[str, str]]]:
    response = claude.create_tool_response(
        messages=messages,
        tools=tools,
    )
    if response.stop_reason != "tool_use":
        return None, None
    tool_content = next(
        content for content in response.content if content.type == "tool_use"
    )
    data, message_dict = None, None
    if tool_content.name == "search_relics_by_period_and_genre":
        data, message = search_relics_by_period_and_genre(tool_content.input, database)
        message_dict = {"role": "assistant", "content": message}
    return data, message_dict
