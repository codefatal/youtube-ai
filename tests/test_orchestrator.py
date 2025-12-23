# -*- coding: utf-8 -*-
"""
Orchestrator 모듈 테스트 스크립트
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

from core.orchestrator import ContentOrchestrator
from core.models import (
    SystemConfig,
    ContentJob,
    VideoFormat,
    AIProvider,
    TTSProvider,
    ContentStatus
)


def test_orchestrator_import():
    """Orchestrator 모듈 import 테스트"""
    print("\n" + "="*60)
    print("[TEST 1] Orchestrator 모듈 import")
    print("="*60)

    try:
        orchestrator = ContentOrchestrator()
        print(f"[SUCCESS] Orchestrator 초기화 완료: {orchestrator}")
    except Exception as e:
        print(f"[ERROR] Orchestrator 초기화 실패: {e}")
        import traceback
        traceback.print_exc()


def test_system_config():
    """SystemConfig 테스트"""
    print("\n" + "="*60)
    print("[TEST 2] SystemConfig")
    print("="*60)

    try:
        # 기본 설정
        config1 = SystemConfig()
        print(f"[INFO] 기본 AI Provider: {config1.ai_provider}")
        print(f"[INFO] 기본 TTS Provider: {config1.tts_provider}")
        print(f"[INFO] 기본 포맷: {config1.default_format}")
        print(f"[INFO] 자동 업로드: {config1.auto_upload}")

        # 커스텀 설정
        config2 = SystemConfig(
            ai_provider=AIProvider.GEMINI,
            tts_provider=TTSProvider.GTTS,
            default_format=VideoFormat.SHORTS,
            default_duration=30,
            auto_upload=False
        )
        print(f"\n[SUCCESS] 커스텀 설정 생성 완료")
        print(f"  - AI: {config2.ai_provider}")
        print(f"  - TTS: {config2.tts_provider}")
        print(f"  - 포맷: {config2.default_format}")

        # Orchestrator에 설정 적용
        orchestrator = ContentOrchestrator(config=config2)
        print(f"[SUCCESS] 설정 적용된 Orchestrator 생성: {orchestrator}")

    except Exception as e:
        print(f"[ERROR] SystemConfig 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_progress_callback():
    """진행 상황 콜백 테스트"""
    print("\n" + "="*60)
    print("[TEST 3] 진행 상황 콜백")
    print("="*60)

    try:
        # 진행 상황 추적 함수
        def progress_tracker(message: str, progress: int):
            print(f"[CALLBACK] [{progress:3d}%] {message}")

        # Orchestrator 생성 (콜백 포함)
        orchestrator = ContentOrchestrator(
            progress_callback=progress_tracker,
            log_file="logs/test_orchestrator.log"
        )

        # 진행 상황 업데이트 테스트
        orchestrator._update_progress("테스트 시작", 0)
        orchestrator._update_progress("작업 진행 중", 50)
        orchestrator._update_progress("작업 완료", 100)

        print("[SUCCESS] 진행 상황 콜백 테스트 완료")

    except Exception as e:
        print(f"[ERROR] 콜백 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_job_queue():
    """작업 큐 테스트"""
    print("\n" + "="*60)
    print("[TEST 4] 작업 큐 관리")
    print("="*60)

    try:
        orchestrator = ContentOrchestrator()

        # 테스트 작업 생성
        job1 = ContentJob(job_id="test_job_1", status=ContentStatus.PLANNING)
        job2 = ContentJob(job_id="test_job_2", status=ContentStatus.PLANNING)
        job3 = ContentJob(job_id="test_job_3", status=ContentStatus.PLANNING)

        # 큐에 추가
        orchestrator.add_to_queue(job1)
        orchestrator.add_to_queue(job2)
        orchestrator.add_to_queue(job3)

        print(f"[INFO] 큐 크기: {orchestrator.job_queue.qsize()}")

        # 통계 조회
        stats = orchestrator.get_statistics()
        print(f"[INFO] 큐 크기 (통계): {stats['queue_size']}")

        print("[SUCCESS] 작업 큐 테스트 완료")

    except Exception as e:
        print(f"[ERROR] 작업 큐 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_job_history():
    """작업 히스토리 테스트"""
    print("\n" + "="*60)
    print("[TEST 5] 작업 히스토리")
    print("="*60)

    try:
        orchestrator = ContentOrchestrator()

        # 히스토리 정보
        print(f"[INFO] 총 작업 수: {orchestrator.history.total_jobs}")
        print(f"[INFO] 완료 작업: {orchestrator.history.completed_jobs}")
        print(f"[INFO] 실패 작업: {orchestrator.history.failed_jobs}")

        # 최근 작업 조회
        recent_jobs = orchestrator.get_recent_jobs(limit=5)
        print(f"[INFO] 최근 작업 수: {len(recent_jobs)}")

        if recent_jobs:
            print("\n[INFO] 최근 작업 목록:")
            for job in recent_jobs[:3]:
                print(f"  - {job.job_id}: {job.status.value}")

        # 통계 조회
        stats = orchestrator.get_statistics()
        print(f"\n[INFO] 통계:")
        print(f"  - 총 작업: {stats['total_jobs']}")
        print(f"  - 완료: {stats['completed_jobs']}")
        print(f"  - 실패: {stats['failed_jobs']}")
        print(f"  - 성공률: {stats['success_rate']:.1f}%")

        print("[SUCCESS] 작업 히스토리 테스트 완료")

    except Exception as e:
        print(f"[ERROR] 작업 히스토리 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_full_pipeline_simulation():
    """전체 파이프라인 시뮬레이션 (실제 실행 X)"""
    print("\n" + "="*60)
    print("[TEST 6] 전체 파이프라인 시뮬레이션")
    print("="*60)

    # API 키 확인
    if not os.getenv('GEMINI_API_KEY'):
        print("[SKIP] GEMINI_API_KEY가 설정되지 않음")
        return

    stock_keys = ['PEXELS_API_KEY', 'PIXABAY_API_KEY']
    if not any(os.getenv(key) for key in stock_keys):
        print("[SKIP] 스톡 영상 API 키가 설정되지 않음")
        print("[INFO] 실제 파이프라인 실행을 위해서는 Pexels 또는 Pixabay API 키가 필요합니다.")
        return

    try:
        # 진행 상황 추적
        def progress_callback(message: str, progress: int):
            print(f"[{progress:3d}%] {message}")

        # Orchestrator 생성
        config = SystemConfig(
            ai_provider=AIProvider.GEMINI,
            tts_provider=TTSProvider.GTTS,
            default_format=VideoFormat.SHORTS,
            auto_upload=False  # 테스트이므로 업로드 비활성화
        )

        orchestrator = ContentOrchestrator(
            config=config,
            progress_callback=progress_callback,
            log_file="logs/test_pipeline.log"
        )

        print("\n[INFO] 전체 파이프라인 실행 시작...")
        print("[WARNING] 이 테스트는 실제로 영상을 생성합니다 (약 3-5분 소요)")
        print("[INFO] 테스트를 건너뛰려면 Ctrl+C를 누르세요.")

        # 사용자 확인
        import time
        print("\n5초 후 자동으로 시작합니다...")
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n[SKIP] 사용자가 테스트를 취소했습니다.")
            return

        # 파이프라인 실행
        job = orchestrator.create_content(
            topic="파이썬 프로그래밍 팁",
            video_format=VideoFormat.SHORTS,
            target_duration=20,  # 테스트용으로 짧게
            upload=False  # 업로드 비활성화
        )

        print(f"\n[INFO] 작업 결과:")
        print(f"  - 작업 ID: {job.job_id}")
        print(f"  - 상태: {job.status.value}")
        print(f"  - 영상 경로: {job.output_video_path}")

        if job.status == ContentStatus.COMPLETED:
            print(f"\n[SUCCESS] 전체 파이프라인 시뮬레이션 성공!")
            if job.output_video_path:
                file_size = os.path.getsize(job.output_video_path) / (1024 * 1024)  # MB
                print(f"  - 파일 크기: {file_size:.2f} MB")
        elif job.status == ContentStatus.FAILED:
            print(f"\n[ERROR] 파이프라인 실행 실패")
            print(f"  - 에러 로그: {job.error_log}")
        else:
            print(f"\n[WARNING] 파이프라인이 완료되지 않았습니다: {job.status.value}")

        # 통계 확인
        stats = orchestrator.get_statistics()
        print(f"\n[INFO] 최종 통계:")
        print(f"  - 총 작업: {stats['total_jobs']}")
        print(f"  - 완료: {stats['completed_jobs']}")
        print(f"  - 실패: {stats['failed_jobs']}")

    except KeyboardInterrupt:
        print("\n[SKIP] 사용자가 테스트를 중단했습니다.")
    except Exception as e:
        print(f"[ERROR] 파이프라인 시뮬레이션 실패: {e}")
        import traceback
        traceback.print_exc()


def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("Phase 6 Orchestrator 모듈 테스트 시작")
    print("="*60)

    try:
        # 1. Orchestrator import 테스트
        test_orchestrator_import()

        # 2. SystemConfig 테스트
        test_system_config()

        # 3. 진행 상황 콜백 테스트
        test_progress_callback()

        # 4. 작업 큐 테스트
        test_job_queue()

        # 5. 작업 히스토리 테스트
        test_job_history()

        # 6. 전체 파이프라인 시뮬레이션
        test_full_pipeline_simulation()

        print("\n" + "="*60)
        print("[SUCCESS] 모든 테스트 완료!")
        print("="*60 + "\n")

        print("\n[사용 예시]")
        print("```python")
        print("from core.orchestrator import ContentOrchestrator")
        print("from core.models import VideoFormat")
        print("")
        print("# Orchestrator 생성")
        print("orchestrator = ContentOrchestrator()")
        print("")
        print("# 콘텐츠 생성 (전체 파이프라인)")
        print("job = orchestrator.create_content(")
        print("    topic='강아지 훈련 팁',")
        print("    video_format=VideoFormat.SHORTS,")
        print("    target_duration=60,")
        print("    upload=True  # YouTube 업로드")
        print(")")
        print("")
        print("print(f'완료: {job.output_video_path}')")
        print("```")

    except Exception as e:
        print(f"\n[ERROR] 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
