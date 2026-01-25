"""Slack 관련 MCP 도구들"""

import json
from typing import Any
from datetime import datetime

from .config import logger
from .utils import make_slack_request


async def list_slack_channels(bot_token: str, limit: int = 100) -> str:
    """워크스페이스의 모든 채널 목록 조회

    Args:
        bot_token: Slack 봇 토큰
        limit: 반환할 최대 채널 수 (기본값 100, 최대 1000)

    Returns:
        Slack API 원본 응답 JSON 문자열
    """
    logger.info(f"Listing Slack channels with limit: {limit}")
    params = {"limit": min(limit, 1000), "exclude_archived": True}

    data = await make_slack_request("conversations.list", bot_token, params=params)

    logger.info(f"API Response: {data}")
    return json.dumps(data, ensure_ascii=False, indent=2)


async def send_slack_message(
    bot_token: str, channel_id: str, text: str, thread_ts: str = None
) -> str:
    """Slack 채널에 메시지 전송

    Args:
        bot_token: Slack 봇 토큰
        channel_id: 메시지를 보낼 채널 ID
        text: 전송할 메시지 텍스트
        thread_ts: 스레드 타임스탬프 (스레드 답글인 경우)

    Returns:
        Slack API 원본 응답 JSON 문자열
    """
    logger.info(f"Sending message to channel: {channel_id}")
    json_data = {"channel": channel_id, "text": text}
    if thread_ts:
        json_data["thread_ts"] = thread_ts

    data = await make_slack_request(
        "chat.postMessage", bot_token, json_data=json_data, method="POST"
    )

    logger.info(f"API Response: {data}")
    return json.dumps(data, ensure_ascii=False, indent=2)


async def get_channel_messages(bot_token: str, channel_id: str, limit: int = 50) -> str:
    """Slack 채널의 최근 메시지 조회

    Args:
        bot_token: Slack 봇 토큰
        channel_id: 메시지를 가져올 채널 ID
        limit: 반환할 최대 메시지 수 (기본값 50, 최대 1000)

    Returns:
        Slack API 원본 응답 JSON 문자열
    """
    logger.info(f"Getting messages from channel: {channel_id}")
    params = {
        "channel": channel_id,
        "limit": min(limit, 1000),
        "inclusive": True,
        "include_all_metadata": True,
    }

    data = await make_slack_request("conversations.history", bot_token, params=params)

    logger.info(f"API Response: {data}")
    return json.dumps(data, ensure_ascii=False, indent=2)


async def add_reaction(
    bot_token: str, channel_id: str, timestamp: str, emoji: str
) -> str:
    """메시지에 리액션 이모지 추가

    Args:
        bot_token: Slack 봇 토큰
        channel_id: 메시지가 있는 채널 ID
        timestamp: 메시지 타임스탬프
        emoji: 추가할 이모지 이름 (콜론 없이, 예: 'thumbsup')

    Returns:
        Slack API 원본 응답 JSON 문자열
    """
    logger.info(
        f"Adding reaction :{emoji}: to message {timestamp} in channel {channel_id}"
    )
    json_data = {"channel": channel_id, "timestamp": timestamp, "name": emoji}

    data = await make_slack_request(
        "reactions.add", bot_token, json_data=json_data, method="POST"
    )

    logger.info(f"API Response: {data}")
    return json.dumps(data, ensure_ascii=False, indent=2)


async def get_thread_replies(bot_token: str, channel_id: str, thread_ts: str) -> str:
    """메시지 스레드의 모든 답글 조회

    Args:
        bot_token: Slack 봇 토큰
        channel_id: 스레드가 있는 채널 ID
        thread_ts: 스레드의 부모 메시지 타임스탬프

    Returns:
        Slack API 원본 응답 JSON 문자열
    """
    logger.info(f"Getting thread replies for {thread_ts} in channel {channel_id}")
    params = {"channel": channel_id, "ts": thread_ts}

    data = await make_slack_request("conversations.replies", bot_token, params=params)

    logger.info(f"API Response: {data}")
    return json.dumps(data, ensure_ascii=False, indent=2)


async def get_users(bot_token: str, limit: int = 100) -> str:
    """워크스페이스의 모든 사용자 목록 조회

    Args:
        bot_token: Slack 봇 토큰
        limit: 반환할 최대 사용자 수 (기본값 100, 최대 1000)

    Returns:
        Slack API 원본 응답 JSON 문자열
    """
    logger.info(f"Getting users with limit: {limit}")
    params = {"limit": min(limit, 1000)}

    data = await make_slack_request("users.list", bot_token, params=params)

    logger.info(f"API Response: {data}")
    return json.dumps(data, ensure_ascii=False, indent=2)


async def get_user_profile(bot_token: str, user_id: str) -> str:
    """특정 사용자의 상세 프로필 정보 조회

    Args:
        bot_token: Slack 봇 토큰
        user_id: 조회할 사용자 ID

    Returns:
        Slack API 원본 응답 JSON 문자열
    """
    logger.info(f"Getting user profile for: {user_id}")
    params = {"user": user_id}

    data = await make_slack_request("users.info", bot_token, params=params)

    logger.info(f"API Response: {data}")
    return json.dumps(data, ensure_ascii=False, indent=2)
