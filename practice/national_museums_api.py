import argparse
from anthropic import Anthropic
from pathlib import Path
from anthropic.lib import files_from_dir

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).cwd()
print(f"프로젝트 루트: {PROJECT_ROOT}")

## 스킬 디렉토리 경로
SKILL_DIR = PROJECT_ROOT / ".claude" / "skills" / "national-museums"

client = Anthropic()

def upload_skill(display_title: str) -> str:
    skill = client.beta.skills.create(
        display_title=display_title,
        files=files_from_dir(str(SKILL_DIR)),
        betas=["skills-2025-10-02"],
    )

    print(f"스킬 업로드 완료!")
    print(f"  - Skill ID: {skill.id}")
    print(f"  - Version: {skill.latest_version}")

    return skill.id


def update_skill(skill_id: str) -> str:
    print(f"스킬 업데이트 중: {SKILL_DIR}")
    print(f"  - Skill ID: {skill_id}")

    new_version = client.beta.skills.versions.create(
        skill_id=skill_id,
        files=files_from_dir(str(SKILL_DIR)),
        betas=["skills-2025-10-02"],
    )

    print(f"스킬 업데이트 완료!")
    print(f"  - New Version: {new_version.version}")

    return new_version.version

    
def delete_skill(skill_id: str):
    """스킬 삭제 (모든 버전 삭제 후 스킬 삭제)"""
    print(f"스킬 삭제 중: {skill_id}")

    # Step 1: 모든 버전 삭제
    print("  버전 목록 조회 중...")
    versions = client.beta.skills.versions.list(
        skill_id=skill_id, betas=["skills-2025-10-02"]
    )

    version_count = len(versions.data)
    print(f"  {version_count}개의 버전 발견")

    for version in versions.data:
        print(f"    버전 삭제: {version.version}")
        client.beta.skills.versions.delete(
            skill_id=skill_id, version=version.version
        )

    # Step 2: 스킬 삭제
    print("  스킬 삭제 중...")
    client.beta.skills.delete(skill_id=skill_id, betas=["skills-2025-10-02"])

    print(f"스킬 삭제 완료: {skill_id}")

def list_skills():

    skills = client.beta.skills.list(source="anthropic", betas=["skills-2025-10-02"])

    print("\n=== 사전구축 스킬 목록 ===")
    for skill in skills.data:
        print(f"  - {skill.display_title}")
        print(f"    ID: {skill.id}")
        print(f"    Version: {skill.latest_version}")
        print()

    skills = client.beta.skills.list(source="custom", betas=["skills-2025-10-02"])

    print("\n=== 커스텀 스킬 목록 ===")
    for skill in skills.data:
        print(f"  - {skill.display_title}")
        print(f"    ID: {skill.id}")
        print(f"    Version: {skill.latest_version}")
        print()


def find_existing_skill(display_title: str) -> str | None:
    """기존 스킬 찾기"""
    skills = client.beta.skills.list(source="custom", betas=["skills-2025-10-02"])

    for skill in skills.data:
        if skill.display_title == display_title:
            return skill.id
    return None


    return True


def ask_museum_simple(skill_id: str, question: str) -> str:

    print(f"[기본 실행] 질문: {question}, {skill_id}")

    messages = [{"role": "user", "content": question}]

    response = client.beta.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        betas=["code-execution-2025-08-25", "skills-2025-10-02"],
        container={
            "skills": [{"type": "custom", "skill_id": skill_id, "version": "latest"}]
        },
        messages=messages,
        tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    )

    # 응답에서 텍스트 추출
    result_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            result_text += block.text

    print(f"[기본 실행] 응답 완료")
    print(f"[기본 실행] stop_reason: {response.stop_reason}")
    print(f"[기본 실행] 결과:\n{result_text}")

    return result_text


def ask_museum_multi_turn(skill_id: str, questions: list[str]) -> str:
    """박물관 관련 다중 턴 대화"""
    print(f"[다중 턴] 질문 수: {len(questions)}")

    # 첫 번째 요청 - 컨테이너 생성
    print(f"[다중 턴] 1번째 질문: {questions[0]}")
    messages = [{"role": "user", "content": questions[0]}]

    response = client.beta.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        betas=["code-execution-2025-08-25", "skills-2025-10-02"],
        container={
            "skills": [{"type": "custom", "skill_id": skill_id, "version": "latest"}]
        },
        messages=messages,
        tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    )
    container_id = response.container.id
    print(f"[다중 턴] 컨테이너 ID 생성: {container_id}")
    print(f"[다중 턴] 1번째 응답 완료")
    # 최종 응답에서 텍스트 추출
    result_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            result_text += block.text
    print(f"[다중 턴] 최종 결과:\n{result_text}")

    # 후속 질문들 처리
    for i, question in enumerate(questions[1:], start=2):
        print(f"[다중 턴] {i}번째 질문: {question}")

        # 이전 응답을 메시지에 추가
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": question})

        response = client.beta.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            betas=["code-execution-2025-08-25", "skills-2025-10-02"],
            container={
                "id": container_id,  # 컨테이너 ID 재사용
                "skills": [
                    {"type": "custom", "skill_id": skill_id, "version": "latest"}
                ],
            },
            messages=messages,
            tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
        )
        print(f"[다중 턴] {i}번째 응답 완료")
        # 최종 응답에서 텍스트 추출
        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text
        print(f"[다중 턴] 최종 결과:\n{result_text}")

    print(f"[다중 턴] 대화 완료")

    return result_text


def ask_museum_long_running(skill_id: str, question: str, max_retries: int = 10) -> str:
    """박물관 관련 질문하기 - 장기 실행 작업 처리 (pause_turn)"""
    print(f"[장기 실행] 질문: {question}")
    print(f"[장기 실행] 최대 재시도 횟수: {max_retries}")

    messages = [{"role": "user", "content": question}]

    response = client.beta.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        betas=["code-execution-2025-08-25", "skills-2025-10-02"],
        container={
            "skills": [{"type": "custom", "skill_id": skill_id, "version": "latest"}]
        },
        messages=messages,
        tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    )

    print(f"[장기 실행] 초기 응답 stop_reason: {response.stop_reason}")

    # pause_turn 처리 루프
    retry_count = 0
    while response.stop_reason == "pause_turn" and retry_count < max_retries:
        retry_count += 1
        print(f"[장기 실행] pause_turn 감지 - 재시도 {retry_count}/{max_retries}")

        # 이전 응답을 메시지에 추가하고 계속 진행
        messages.append({"role": "assistant", "content": response.content})

        response = client.beta.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            betas=["code-execution-2025-08-25", "skills-2025-10-02"],
            container={
                "id": response.container.id,
                "skills": [
                    {"type": "custom", "skill_id": skill_id, "version": "latest"}
                ],
            },
            messages=messages,
            tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
        )
        print(f"[장기 실행] 재시도 후 stop_reason: {response.stop_reason}")

    # 응답에서 텍스트 추출
    result_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            result_text += block.text

    print(f"[장기 실행] 작업 완료 (총 {retry_count}회 재시도)")
    print(f"[장기 실행] 결과:\n{result_text}")

    return result_text


def main():
    parser = argparse.ArgumentParser(description="스킬 API 실행")
    parser.add_argument("--list", action="store_true", help="스킬 목록 조회")
    parser.add_argument("--upload", action="store_true", help="스킬 새로 업로드")
    parser.add_argument(
        "--title",
        default="지역 국립박물관 안내",
        help="스킬 display_title (기본값: 지역 국립박물관 안내)",
    )
    parser.add_argument("--skill-id", help="사용할 스킬 ID (없으면 자동 검색/업로드)")
    parser.add_argument(
        "--update", action="store_true", help="기존 스킬 업데이트 (새 버전)"
    )
    parser.add_argument("--delete", action="store_true", help="스킬 삭제")

    # 스킬 실행 모드
    parser.add_argument("--simple", action="store_true", help="기본 실행 모드")
    parser.add_argument("--multi-turn", action="store_true", help="다중 턴 대화 모드")
    parser.add_argument("--long-running", action="store_true", help="장기 실행 모드")
    parser.add_argument("--question", "-q", help="박물관 관련 질문")

    args = parser.parse_args()

    # 스킬 목록 조회
    if args.list:
        list_skills()
        return

    # 스킬 새로 업로드
    if args.upload:
        upload_skill(args.title)
        return

    skill_id = args.skill_id or find_existing_skill(args.title)
    if not skill_id:
        print("오류: 사용할 스킬이 없습니다. --upload로 먼저 생성하세요.")
        return

    # # 기존 스킬 업데이트 (새 버전)
    if args.update:
        skill_id = args.skill_id or find_existing_skill(args.title)
        if not skill_id:
            print("오류: 업데이트할 스킬이 없습니다. --upload로 먼저 생성하세요.")
            return
        update_skill(skill_id)
        return

    # # 스킬 삭제
    if args.delete:
        skill_id = args.skill_id or find_existing_skill(args.title)
        if not skill_id:
            print("오류: 삭제할 스킬이 없습니다.")
            return
        delete_skill(skill_id)
        return

    if args.simple:
        question = args.question or "공주박물관의 대표 유물은 무엇인가요?"
        ask_museum_simple(skill_id, question)
        return

    if args.multi_turn:
        questions = [
            "공주박물관의 대표 유물은 무엇인가요?",
            "그 유물의 역사적 의의는 무엇인가요?",
            "관람 시간은 어떻게 되나요?",
        ]
        ask_museum_multi_turn(skill_id, questions)
        return

    if args.long_running:
        question = (
            # args.question or "전국 13개 국립박물관의 운영 정보를 모두 정리해주세요."
            args.question
            or "공주와 제주 국립박물관의 운영 정보를 모두 정리해주세요."
        )
        ask_museum_long_running(skill_id, question)
        return

    # 기본 도움말
    print("사용법:")
    print(
        "  python national_museums_api2.py --list                        # 스킬 목록 조회"
    )
    print(
        "  python national_museums_api2.py --upload                      # 스킬 업로드 (기본 title)"
    )
    print(
        "  python national_museums_api2.py --upload --title '스킬명'     # 스킬 업로드 (커스텀 title)"
    )
    print(
        "  python national_museums_api2.py --update                      # 스킬 업데이트"
    )
    print("  python national_museums_api2.py --delete                      # 스킬 삭제")
    print(
        "  python national_museums_api2.py --delete --title '스킬명'     # 특정 스킬 삭제"
    )
    print("  python national_museums_api2.py --simple                      # 기본 실행")
    print(
        "  python national_museums_api2.py --multi-turn                  # 다중 턴 대화"
    )
    print("  python national_museums_api2.py --long-running                # 장기 실행")
    print(
        "  python national_museums_api2.py --simple -q '질문'            # 커스텀 질문"
    )


if __name__ == "__main__":
    main()
