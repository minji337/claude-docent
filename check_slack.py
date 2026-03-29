#!/usr/bin/env python3
"""슬랙 채널 조회 스크립트"""
import os
import sys
import json
import asyncio
sys.path.insert(0, '/home/runner/workspace/mcp-slack-python')

from tools.slack_tools import list_slack_channels, get_channel_messages

async def main():
    bot_token = os.environ.get('SLACK_BOT_TOKEN')
    if not bot_token:
        print("Error: SLACK_BOT_TOKEN not found", file=sys.stderr)
        sys.exit(1)

    # 채널 목록 조회
    channels_json = await list_slack_channels(bot_token, limit=100)
    channels_data = json.loads(channels_json)

    print("=== 채널 목록 ===")
    if channels_data.get('ok'):
        for channel in channels_data.get('channels', []):
            print(f"ID: {channel['id']}, Name: {channel['name']}")

    # 첫 번째 채널의 메시지 조회 (또는 특정 채널 지정)
    if channels_data.get('ok') and channels_data.get('channels'):
        channel_id = channels_data['channels'][0]['id']
        print(f"\n=== 채널 {channel_id} 메시지 ===")
        messages_json = await get_channel_messages(bot_token, channel_id, limit=100)
        messages_data = json.loads(messages_json)

        if messages_data.get('ok'):
            for msg in messages_data.get('messages', []):
                print(json.dumps(msg, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
