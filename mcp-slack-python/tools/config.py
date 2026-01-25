"""MCP 도구를 위한 설정 모듈"""

import logging
from pathlib import Path
from typing import Any

# mcp-slack-python 디렉토리의 logs.txt 경로 설정
current_dir = Path(__file__).parent.parent
log_file_path = current_dir / "logs.txt"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("mcp_tools")

# API 상수
SLACK_API_BASE = "https://slack.com/api"
