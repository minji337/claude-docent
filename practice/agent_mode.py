import asyncio
from claude_agent_sdk import query, ClaudeSDKClient, AssistantMessage, ResultMessage


from pathlib import Path

def extract_text(message):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if hasattr(block, "text"):
                return block.text
    return None


async def one_off_mode():
    print("=" * 50)
    print("[단일 요청 모드] query() 사용")
    print("=" * 50)

    print("첫 번째 요청: '내 이름은 홍길동이야'")
    async for message in query(
        prompt="내 이름은 홍길동이야. 알겠으면 '네, 홍길동님'이라고 대답해."
    ):
        text = extract_text(message)
        if text:
            print(f"응답: {text}")

    print("\n두 번째 요청: '내 이름이 뭐라고 했지?'")
    async for message in query(prompt="내 이름이 뭐라고 했지?"):
        text = extract_text(message)
        if text:
            print(f"응답: {text}")


async def continuous_mode():
    print("\n" + "=" * 50)
    print("[연속 대화 모드] ClaudeSDKClient 사용")
    print("=" * 50)

    async with ClaudeSDKClient() as client:
        print("첫 번째 요청: '내 이름은 홍길동이야'")
        await client.query(
            "내 이름은 홍길동이야. 알겠으면 '네, 홍길동님'이라고 대답해."
        )
        async for message in client.receive_response():
            text = extract_text(message)
            if text:
                print(f"응답: {text}")

        print("\n두 번째 요청: '내 이름이 뭐라고 했지?'")
        await client.query("내 이름이 뭐라고 했지?")
        async for message in client.receive_response():
            text = extract_text(message)
            if text:
                print(f"응답: {text}")


async def main():
    await one_off_mode()
    await continuous_mode()


if __name__ == "__main__":
    asyncio.run(main())
