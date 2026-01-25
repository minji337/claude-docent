"""MCP Client to test the Slack MCP Server"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os

async def main():
    # Server parameters - path to main.py
    server_params = StdioServerParameters(
        command="python",
        args=["main.py"],
        env={
            "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
        }
    )

    print("=== MCP Client Test ===\n")
    print("Connecting to MCP server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("[OK] Connected to MCP server\n")

            # 1. List available tools
            print("1. Listing available tools...")
            tools = await session.list_tools()
            print(f"Found {len(tools.tools)} tools:\n")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print("\n" + "="*50 + "\n")

            # 2. Call slack_list_channels
            print("2. Calling slack_list_channels tool...")
            result = await session.call_tool("slack_list_channels", arguments={"limit": 10})
            print("Result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    print(content.text)
            print("\n" + "="*50 + "\n")

            print("[OK] MCP Client test completed!")

if __name__ == "__main__":
    asyncio.run(main())
