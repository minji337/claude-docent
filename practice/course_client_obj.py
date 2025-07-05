import asyncio
from fastmcp import Client
from contextlib import AsyncExitStack
import traceback


class CourseClient:

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.tools: list[dict] = []
        self.resource_map: dict[str, str] = {}
        self.prompt_map: dict[str, list[str]] = {}

    async def connect_server(self):
        try:
            self.session = await self.exit_stack.enter_async_context(
                Client("http://127.0.0.1:8000/mcp")
            )
            print("MCP 서버 연결 완료")
        except Exception as e:
            print(f"MCP 서버 연결 실패: {e}")
            traceback.print_exc()
            raise e

    async def setup_context(self):
        mcp_tools = await self.session.list_tools()
        self.tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in mcp_tools
        ]
        print(f"도구 목록: {[tool['name'] for tool in self.tools]}")

        mcp_resources = await self.session.list_resources()
        self.resource_map = {
            resource.name: str(resource.uri) for resource in mcp_resources
        }

        mcp_prompts = await self.session.list_prompts()
        for prompt in mcp_prompts:
            self.prompt_map[prompt.name] = []
            for argument in prompt.arguments:
                self.prompt_map[prompt.name].append(argument.name)

    async def read_resource(self, uri: str) -> str:
        resource = await self.session.read_resource(uri=uri)
        return resource[0].text

    async def call_tool(self, tool_name: str, tool_input: dict) -> str:
        tool = await self.session.call_tool(name=tool_name, arguments=tool_input)
        return tool[0].text

    async def get_prompt(self, name: str, arguments: dict) -> str:
        template = await self.session.get_prompt(name=name, arguments=arguments)
        return template.messages[0].content.text

    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
            print("MCP 서버 연결 해제")
        except Exception as e:
            print(f"정리 중 오류 발생: {e}")
            traceback.print_exc()
            raise e


async def main():
    client = CourseClient()
    await client.connect_server()


if __name__ == "__main__":
    asyncio.run(main())
