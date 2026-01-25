"""메인 MCP 서버 애플리케이션"""
import os
from mcp.server.fastmcp import FastMCP

from tools import (
    list_slack_channels,
    send_slack_message,
    get_channel_messages,
    add_reaction,
    get_thread_replies,
    get_users,
    get_user_profile
)
from tools.config import logger

# 환경 변수에서 Slack 토큰 가져오기
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
if not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN 환경 변수가 필요합니다")

# FastMCP 서버 초기화
mcp = FastMCP("slack_mcp")


@mcp.tool()
async def slack_list_channels(limit: int = 100) -> str:
    """Slack 워크스페이스의 모든 채널 목록 조회

    Args:
        limit: 반환할 최대 채널 수 (기본값 100, 최대 1000)
    """
    return await list_slack_channels(SLACK_BOT_TOKEN, limit)


@mcp.tool()
async def slack_send_message(channel_id: str, text: str, thread_ts: str = None) -> str:
    """Slack 채널에 메시지 전송

    Args:
        channel_id: 메시지를 보낼 채널 ID
        text: 전송할 메시지 텍스트
        thread_ts: 스레드 타임스탬프 (스레드 답글인 경우, 선택사항)
    """
    return await send_slack_message(SLACK_BOT_TOKEN, channel_id, text, thread_ts)


@mcp.tool()
async def slack_get_messages(channel_id: str, limit: int = 50) -> str:
    """Slack 채널의 최근 메시지 조회

    Args:
        channel_id: 메시지를 가져올 채널 ID
        limit: 반환할 최대 메시지 수 (기본값 50, 최대 1000)
    """
    return await get_channel_messages(SLACK_BOT_TOKEN, channel_id, limit)


@mcp.tool()
async def slack_add_reaction(channel_id: str, timestamp: str, emoji: str) -> str:
    """메시지에 리액션 이모지 추가

    Args:
        channel_id: 메시지가 있는 채널 ID
        timestamp: 메시지 타임스탬프
        emoji: 추가할 이모지 이름 (콜론 없이, 예: 'thumbsup')
    """
    return await add_reaction(SLACK_BOT_TOKEN, channel_id, timestamp, emoji)


@mcp.tool()
async def slack_get_thread_replies(channel_id: str, thread_ts: str) -> str:
    """메시지 스레드의 모든 답글 조회

    Args:
        channel_id: 스레드가 있는 채널 ID
        thread_ts: 스레드의 부모 메시지 타임스탬프
    """
    return await get_thread_replies(SLACK_BOT_TOKEN, channel_id, thread_ts)


@mcp.tool()
async def slack_get_users(limit: int = 100) -> str:
    """워크스페이스의 모든 사용자 목록 조회

    Args:
        limit: 반환할 최대 사용자 수 (기본값 100, 최대 1000)
    """
    return await get_users(SLACK_BOT_TOKEN, limit)


@mcp.tool()
async def slack_get_user_profile(user_id: str) -> str:
    """특정 사용자의 상세 프로필 정보 조회

    Args:
        user_id: 조회할 사용자 ID
    """
    return await get_user_profile(SLACK_BOT_TOKEN, user_id)


if __name__ == "__main__":
    # 서버 초기화 및 실행
    logger.info("Starting FastMCP server...")
    mcp.run(transport='stdio')