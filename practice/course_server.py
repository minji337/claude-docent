from fastmcp import FastMCP
import asyncio
import logging
from pathlib import Path
import json
from pydantic import Field
from typing import Literal

# 로그 파일 설정
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("course_server.log", encoding="utf-8"),
        logging.StreamHandler(),  # 콘솔 출력도 유지
    ],
)
logger = logging.getLogger(__name__)

mcp = FastMCP(name="ItCourseServer")


@mcp.resource(
    uri="file://course_catalog.txt",
    name="강의 카탈로그",
    description="강의 카탈로그를 제공합니다.",
    mime_type="text/plain",
)
def get_course_catalog() -> str:
    path = Path(__file__).resolve().parent / "course_catalog.txt"
    logger.info(f"Course catalog path: {path}")
    with open(path, encoding="utf-8", mode="r") as f:
        return f.read()


@mcp.tool(
    name="check_available_seats",
    description="주어진 강좌의 잔여석을 확인합니다.",
)
def check_available_seats(course_name: str = Field(description="강좌 이름")) -> str:
    course_data_path = Path(__file__).resolve().parent / "course_status.json"
    with open(course_data_path, encoding="utf-8", mode="r") as f:
        course_data = json.load(f)
        if course_name in course_data:
            return f"{course_name}: 잔여석 {course_data[course_name]['잔여석']}석"
        else:
            logger.warning(f"Course {course_name} not found in course data")
            return f"{course_name} 강좌 미존재"


@mcp.prompt(
    name="강의 추천 프롬프트 템플릿",
    description="직업과 관심사를 기반으로 강의 추천을 위한 프롬프트를 생성합니다.",
)
def get_course_prompt_template(
    job: Literal["학생", "직장인", "주부", "기타"], interest: str
) -> str:
    return f"현재 직업은 {job}에요. {interest}에 대해 관심이 많아요. 강의 추천해주세요."


if __name__ == "__main__":
    try:
        logger.info("Starting MCP server..............")
        #asyncio.run(mcp.run(transport="streamable-http"))
        #asyncio.run(mcp.run(transport="stdio"))
        asyncio.run(mcp.run(transport="sse", host="0.0.0.0", port=8000, path="/mcp"))    
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
