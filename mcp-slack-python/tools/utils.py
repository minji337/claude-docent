"""MCP 도구를 위한 유틸리티 함수"""

from typing import Any

import httpx

from .config import logger, SLACK_API_BASE


async def make_slack_request(
    endpoint: str,
    bot_token: str,
    params: dict = None,
    json_data: dict = None,
    method: str = "GET",
) -> dict[str, Any] | None:
    """적절한 에러 처리와 함께 Slack API에 요청"""
    logger.debug(f"Making {method} request to Slack API: {endpoint}")
    headers = {
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    url = f"{SLACK_API_BASE}/{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(
                    url, headers=headers, params=params, timeout=30.0
                )
            else:  # POST
                response = await client.post(
                    url, headers=headers, json=json_data, timeout=30.0
                )
            response.raise_for_status()
            logger.debug(f"Successfully received response from Slack API: {endpoint}")
            return response.json()
        except Exception as e:
            logger.error(
                f"Error making request to Slack API: {endpoint} - Error: {str(e)}"
            )
            return None
