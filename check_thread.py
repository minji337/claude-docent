#!/usr/bin/env python3
"""슬랙 스레드 댓글 조회 스크립트"""
import os
import sys
import json
import asyncio
sys.path.insert(0, '/home/runner/workspace/mcp-slack-python')

from tools.slack_tools import get_thread_replies

async def main():
    bot_token = os.environ.get('SLACK_BOT_TOKEN')
    if not bot_token:
        print("Error: SLACK_BOT_TOKEN not found", file=sys.stderr)
        sys.exit(1)

    channel_id = "C090FF9AJBU"
    thread_ts = "1771393312.005909"

    # 스레드 댓글 조회
    replies_json = await get_thread_replies(bot_token, channel_id, thread_ts)
    replies_data = json.loads(replies_json)

    print(json.dumps(replies_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
