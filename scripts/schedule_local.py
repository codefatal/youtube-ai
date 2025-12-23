#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
로컬 스케줄링 스크립트
schedule 라이브러리를 사용하여 정기적으로 콘텐츠 생성
"""
import sys
import os
import time
import schedule
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from core.orchestrator import ContentOrchestrator
from core.models import (
    SystemConfig,
    VideoFormat,
    AIProvider,
    TTSProvider,
    ContentStatus
)


def daily_content_job():
    """매일 실행될 콘텐츠 생성 작업"""
    print(f"\n{'='*60}")
    print(f"스케줄 작업 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    try:
        # 시스템 설정
        config = SystemConfig(
            ai_provider=AIProvider.GEMINI,
            tts_provider=TTSProvider.GTTS,
            default_format=VideoFormat.SHORTS,
            default_duration=60,
            auto_upload=True  # 자동 업로드 활성화
        )

        # Orchestrator 생성
        orchestrator = ContentOrchestrator(
            config=config,
            log_file=f"logs/scheduled_{datetime.now().strftime('%Y%m%d')}.log"
        )

        # AI로 주제 생성
        from core.planner import ContentPlanner
        planner = ContentPlanner(ai_provider="gemini")

        ideas = planner.generate_topic_ideas(
            category="general",
            count=1,
            trending=True
        )

        topic = ideas[0].title if ideas else "오늘의 유용한 팁"

        print(f"[INFO] 생성 주제: {topic}\n")

        # 콘텐츠 생성
        job = orchestrator.create_content(
            topic=topic,
            video_format=VideoFormat.SHORTS,
            target_duration=60,
            upload=True
        )

        # 결과 출력
        if job.status == ContentStatus.COMPLETED:
            print(f"\n[SUCCESS] 작업 완료!")
            print(f"  - 작업 ID: {job.job_id}")
            print(f"  - 영상: {job.output_video_path}")
            if job.upload_result and job.upload_result.success:
                print(f"  - YouTube: {job.upload_result.url}")
        else:
            print(f"\n[ERROR] 작업 실패: {job.status.value}")
            if job.error_log:
                print(f"  - 에러: {job.error_log[-1]}")

    except Exception as e:
        print(f"\n[ERROR] 스케줄 작업 실패: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"스케줄 작업 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")


def main():
    print("="*60)
    print("YouTube AI 로컬 스케줄러 시작")
    print("="*60)
    print("\n[설정]")
    print("  - 실행 시각: 매일 오전 9시")
    print("  - 포맷: Shorts")
    print("  - 길이: 60초")
    print("  - 자동 업로드: 활성화")
    print("\n[INFO] Ctrl+C를 눌러 종료할 수 있습니다.")
    print("="*60 + "\n")

    # 환경 변수 확인
    if not os.getenv('GEMINI_API_KEY'):
        print("[ERROR] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)

    # 스케줄 설정: 매일 오전 9시
    schedule.every().day.at("09:00").do(daily_content_job)

    # 테스트 실행 (옵션)
    if "--test" in sys.argv:
        print("[TEST] 테스트 모드: 즉시 실행합니다...\n")
        daily_content_job()
        return

    # 첫 실행 예정 시각 표시
    next_run = schedule.next_run()
    print(f"[INFO] 다음 실행 예정: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    print("[INFO] 스케줄러 대기 중...\n")

    # 스케줄 루프
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

    except KeyboardInterrupt:
        print("\n\n[INFO] 스케줄러를 종료합니다.")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ERROR] 스케줄러 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
