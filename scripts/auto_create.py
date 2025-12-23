#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
자동 콘텐츠 생성 스크립트
GitHub Actions 또는 로컬 스케줄러에서 실행
"""
import sys
import os
import argparse
from pathlib import Path

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
    TTSProvider
)


def generate_topic_from_ai():
    """AI로 트렌디한 주제 생성"""
    from core.planner import ContentPlanner

    planner = ContentPlanner(ai_provider="gemini")

    # 트렌디한 주제 아이디어 생성
    ideas = planner.generate_topic_ideas(
        category="general",
        count=1,
        trending=True
    )

    if ideas:
        return ideas[0].title
    else:
        # 폴백: 기본 주제
        return "오늘의 유용한 팁"


def progress_callback(message: str, progress: int):
    """진행 상황 출력"""
    print(f"[{progress:3d}%] {message}", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="자동 YouTube 콘텐츠 생성"
    )

    parser.add_argument(
        '--topic',
        type=str,
        default='',
        help='영상 주제 (비워두면 AI가 자동 생성)'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['shorts', 'landscape', 'square'],
        default='shorts',
        help='영상 포맷 (기본: shorts)'
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='목표 길이 (초, 기본: 60)'
    )

    parser.add_argument(
        '--upload',
        action='store_true',
        default=False,
        help='YouTube 업로드 활성화'
    )

    parser.add_argument(
        '--no-upload',
        action='store_false',
        dest='upload',
        help='YouTube 업로드 비활성화 (기본)'
    )

    parser.add_argument(
        '--ai-provider',
        type=str,
        choices=['gemini', 'claude', 'openai'],
        default='gemini',
        help='AI 제공자 (기본: gemini)'
    )

    parser.add_argument(
        '--tts-provider',
        type=str,
        choices=['gtts', 'elevenlabs', 'google_cloud'],
        default='gtts',
        help='TTS 제공자 (기본: gtts)'
    )

    args = parser.parse_args()

    # 환경 변수 확인
    if not os.getenv('GEMINI_API_KEY'):
        print("[ERROR] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    # 주제 결정
    topic = args.topic.strip()
    if not topic:
        print("[INFO] 주제가 제공되지 않아 AI가 자동으로 생성합니다...")
        try:
            topic = generate_topic_from_ai()
            print(f"[INFO] AI 생성 주제: {topic}")
        except Exception as e:
            print(f"[ERROR] 주제 생성 실패: {e}", file=sys.stderr)
            sys.exit(1)

    # 영상 포맷 변환
    video_format_map = {
        'shorts': VideoFormat.SHORTS,
        'landscape': VideoFormat.LANDSCAPE,
        'square': VideoFormat.SQUARE
    }
    video_format = video_format_map.get(args.format, VideoFormat.SHORTS)

    # AI Provider 변환
    ai_provider_map = {
        'gemini': AIProvider.GEMINI,
        'claude': AIProvider.CLAUDE,
        'openai': AIProvider.OPENAI
    }
    ai_provider = ai_provider_map.get(args.ai_provider, AIProvider.GEMINI)

    # TTS Provider 변환
    tts_provider_map = {
        'gtts': TTSProvider.GTTS,
        'elevenlabs': TTSProvider.ELEVENLABS,
        'google_cloud': TTSProvider.GOOGLE_CLOUD
    }
    tts_provider = tts_provider_map.get(args.tts_provider, TTSProvider.GTTS)

    # 시스템 설정
    config = SystemConfig(
        ai_provider=ai_provider,
        tts_provider=tts_provider,
        default_format=video_format,
        default_duration=args.duration,
        auto_upload=args.upload
    )

    print("\n" + "="*60)
    print("자동 YouTube 콘텐츠 생성 시작")
    print("="*60)
    print(f"주제: {topic}")
    print(f"포맷: {args.format}")
    print(f"길이: {args.duration}초")
    print(f"업로드: {'예' if args.upload else '아니오'}")
    print(f"AI: {args.ai_provider}")
    print(f"TTS: {args.tts_provider}")
    print("="*60 + "\n")

    # Orchestrator 생성
    try:
        orchestrator = ContentOrchestrator(
            config=config,
            log_file="logs/orchestrator.log",
            progress_callback=progress_callback
        )

        # 콘텐츠 생성
        job = orchestrator.create_content(
            topic=topic,
            video_format=video_format,
            target_duration=args.duration,
            upload=args.upload
        )

        # 결과 출력
        print("\n" + "="*60)
        print("작업 완료")
        print("="*60)
        print(f"작업 ID: {job.job_id}")
        print(f"상태: {job.status.value}")

        if job.output_video_path:
            print(f"영상 경로: {job.output_video_path}")

            # 파일 크기 확인
            if os.path.exists(job.output_video_path):
                file_size = os.path.getsize(job.output_video_path) / (1024 * 1024)  # MB
                print(f"파일 크기: {file_size:.2f} MB")

        if job.upload_result:
            if job.upload_result.success:
                print(f"YouTube URL: {job.upload_result.url}")
                print(f"영상 ID: {job.upload_result.video_id}")
            else:
                print(f"업로드 실패: {job.upload_result.error}")

        if job.error_log:
            print(f"\n에러 로그:")
            for error in job.error_log:
                print(f"  - {error}")

        # 통계 출력
        stats = orchestrator.get_statistics()
        print(f"\n통계:")
        print(f"  - 총 작업: {stats['total_jobs']}")
        print(f"  - 완료: {stats['completed_jobs']}")
        print(f"  - 실패: {stats['failed_jobs']}")
        print(f"  - 성공률: {stats['success_rate']:.1f}%")
        print("="*60 + "\n")

        # 성공 여부에 따라 종료 코드 반환
        from core.models import ContentStatus
        if job.status == ContentStatus.COMPLETED:
            print("[SUCCESS] 모든 작업이 성공적으로 완료되었습니다!")
            sys.exit(0)
        elif job.status == ContentStatus.FAILED:
            print("[ERROR] 작업이 실패했습니다.", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"[WARNING] 작업이 완료되지 않았습니다: {job.status.value}", file=sys.stderr)
            sys.exit(2)

    except KeyboardInterrupt:
        print("\n[INFO] 사용자가 작업을 중단했습니다.", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"\n[ERROR] 예상치 못한 오류 발생: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
