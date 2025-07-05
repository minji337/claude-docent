import asyncio
from fastmcp import Client
from pprint import pprint

# client = Client("http://127.0.0.1:8000/mcp")
client = Client("practice/course_server.py")


async def call_mcp():

    async with client:

        resources_list = await client.list_resources()
        print("[리소스 리스트]:")
        pprint(resources_list[0].model_dump())

        course_catalog = await client.read_resource(uri="file://course_catalog.txt")
        print("\n[리소스 호출 결과]:")
        pprint(course_catalog[0].model_dump())

        tools_list = await client.list_tools()
        print("\n[툴 리스트]:")
        pprint(tools_list[0].model_dump())

        tool_call_result = await client.call_tool(
            name="check_available_seats",
            arguments={"course_name": "파이썬 데이터 분석 입문"},
        )
        print("\n[툴 호출 결과]:")
        pprint(tool_call_result[0].model_dump())

        prompts_list = await client.list_prompts()
        print("\n[프롬프트 리스트]:")
        pprint(prompts_list[0].model_dump())

        prompt_result = await client.get_prompt(
            name="강의 추천 프롬프트 템플릿",
            arguments={"job": "직장인", "interest": "파이썬"},
        )
        print("\n[프롬프트 호출 결과]:")
        pprint(prompt_result.model_dump())


asyncio.run(call_mcp())
