"""Check Slack Bot Token information"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from tools.utils import make_slack_request

# 상위 디렉토리의 .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

async def main():
    print("Checking Slack Bot Token...\n")

    # Use auth.test to get token info
    data = await make_slack_request("auth.test", SLACK_BOT_TOKEN)

    if data and data.get("ok"):
        print("Token is VALID!")
        print(f"\nWorkspace: {data.get('team', 'Unknown')}")
        print(f"Team ID: {data.get('team_id', 'Unknown')}")
        print(f"Bot User: {data.get('user', 'Unknown')}")
        print(f"Bot User ID: {data.get('user_id', 'Unknown')}")
        print(f"URL: {data.get('url', 'Unknown')}")

        # Get team info
        team_data = await make_slack_request("team.info", SLACK_BOT_TOKEN)
        if team_data and team_data.get("ok"):
            team = team_data.get("team", {})
            print(f"\n=== Team Details ===")
            print(f"Team Name: {team.get('name', 'Unknown')}")
            print(f"Domain: {team.get('domain', 'Unknown')}")
            print(f"Email Domain: {team.get('email_domain', 'Unknown')}")
    else:
        error = data.get("error", "unknown error") if data else "unknown error"
        print(f"Token is INVALID: {error}")

if __name__ == "__main__":
    asyncio.run(main())
