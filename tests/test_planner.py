# -*- coding: utf-8 -*-
"""
Planner 모듈 테스트 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from core.planner import ContentPlanner
from core.models import VideoFormat
import re


def remove_emoji(text):
    """이모지 제거 (Windows 콘솔 호환성)"""
    # 더 포괄적인 이모지 제거
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F9FF"  # 확장된 범위
        u"\U0001FA00-\U0001FA6F"  # 추가 이모지
        u"\U0001FA70-\U0001FAFF"  # 추가 이모지
        u"\U00002600-\U000026FF"  # 기타 심볼
        u"\U00002300-\U000023FF"  # 기술 심볼
        "]+", flags=re.UNICODE)
    try:
        return emoji_pattern.sub(r'', text)
    except:
        # 인코딩 오류 시 ASCII만 남기기
        return ''.join(c if ord(c) < 128 else '' for c in text)


def test_topic_generation():
    """주제 생성 테스트"""
    print("\n" + "="*60)
    print("[TEST 1] 주제 아이디어 생성")
    print("="*60)

    planner = ContentPlanner(ai_provider="gemini")

    topics = planner.generate_topic_ideas(
        category="반려동물",
        count=3,
        tone="친근하고 활기찬"
    )

    print(f"\n[SUCCESS] 생성된 주제 ({len(topics)}개):")
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {remove_emoji(topic)}")

    return topics


def test_script_generation():
    """스크립트 생성 테스트"""
    print("\n" + "="*60)
    print("[TEST 2] 쇼츠 스크립트 생성")
    print("="*60)

    planner = ContentPlanner(ai_provider="gemini")

    content_plan = planner.create_script(
        topic="강아지가 주인의 감정을 인식하는 방법",
        format=VideoFormat.SHORTS,
        category="22",
        target_duration=60,
        tone="친근하고 활기찬"
    )

    if content_plan:
        print(f"\n[SUCCESS] 스크립트 생성 성공!")
        print(f"[INFO] 제목: {remove_emoji(content_plan.title)}")
        print(f"[INFO] 설명: {remove_emoji(content_plan.description[:100])}...")
        print(f"[INFO] 태그: {', '.join([remove_emoji(tag) for tag in content_plan.tags[:5]])}")
        print(f"\n[INFO] 스크립트 세그먼트:")

        for i, segment in enumerate(content_plan.segments, 1):
            print(f"\n  [{i}] {remove_emoji(segment.text)}")
            print(f"      키워드: {remove_emoji(segment.keyword)}")

        return content_plan
    else:
        print("[ERROR] 스크립트 생성 실패")
        return None


def test_keyword_extraction(content_plan):
    """키워드 추출 테스트"""
    print("\n" + "="*60)
    print("[TEST 3] 키워드 추출")
    print("="*60)

    if not content_plan:
        print("[SKIP] ContentPlan이 없어 테스트를 건너뜁니다")
        return

    planner = ContentPlanner(ai_provider="gemini")
    keywords = planner.extract_keywords(content_plan)

    print(f"\n[SUCCESS] 추출된 키워드 ({len(keywords)}개):")
    for i, keyword in enumerate(keywords, 1):
        print(f"  {i}. {remove_emoji(keyword)}")


def test_save_plan(content_plan):
    """기획안 저장 테스트"""
    print("\n" + "="*60)
    print("[TEST 4] 기획안 저장")
    print("="*60)

    if not content_plan:
        print("[SKIP] ContentPlan이 없어 테스트를 건너뜁니다")
        return

    planner = ContentPlanner(ai_provider="gemini")
    filepath = planner.save_plan(content_plan, output_dir="./output/plans")

    if filepath:
        print(f"[SUCCESS] 저장 성공: {filepath}")
    else:
        print("[ERROR] 저장 실패")


def test_usage_stats():
    """사용량 통계 테스트"""
    print("\n" + "="*60)
    print("[TEST 5] AI 사용량 통계")
    print("="*60)

    planner = ContentPlanner(ai_provider="gemini")
    stats = planner.get_usage_stats()

    print(f"\n[INFO] 사용량 통계:")
    print(f"  - 총 호출 횟수: {stats.get('total_calls', 0)}")
    print(f"  - 총 토큰 수: {stats.get('total_tokens', 0):,}")
    print(f"  - 프롬프트 토큰: {stats.get('prompt_tokens', 0):,}")
    print(f"  - 응답 토큰: {stats.get('response_tokens', 0):,}")
    print(f"  - 예상 비용: ${stats.get('estimated_cost', 0):.2f}")
    print(f"  - 모델: {stats.get('model', 'N/A')}")


def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("Phase 2 Planner 모듈 테스트 시작")
    print("="*60)

    try:
        # 1. 주제 생성 테스트
        topics = test_topic_generation()

        # 2. 스크립트 생성 테스트
        content_plan = test_script_generation()

        # 3. 키워드 추출 테스트
        test_keyword_extraction(content_plan)

        # 4. 기획안 저장 테스트
        test_save_plan(content_plan)

        # 5. 사용량 통계 테스트
        test_usage_stats()

        print("\n" + "="*60)
        print("[SUCCESS] 모든 테스트 완료!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
