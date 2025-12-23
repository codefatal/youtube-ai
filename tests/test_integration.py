# -*- coding: utf-8 -*-
"""
Phase 8 통합 테스트 - 완전한 End-to-End 파이프라인 테스트
"""
import sys
import os
from pathlib import Path
import time
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from core.orchestrator import ContentOrchestrator
from core.planner import Planner
from core.asset_manager import AssetManager
from core.editor import Editor
from core.uploader import Uploader
from core.models import (
    SystemConfig,
    VideoFormat,
    AIProvider,
    TTSProvider,
    ContentStatus
)


class TestResult:
    """테스트 결과 클래스"""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.duration = 0.0
        self.details = {}


def print_header(title: str):
    """헤더 출력"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test_result(result: TestResult):
    """테스트 결과 출력"""
    status = "✅ PASS" if result.passed else "❌ FAIL"
    print(f"\n{status} {result.name} ({result.duration:.2f}초)")
    if result.error:
        print(f"  Error: {result.error}")
    for key, value in result.details.items():
        print(f"  {key}: {value}")


def test_environment_setup() -> TestResult:
    """환경 변수 설정 테스트"""
    result = TestResult("환경 변수 설정 확인")
    start_time = time.time()

    try:
        # 필수 API 키 확인
        required_keys = ['GEMINI_API_KEY']
        optional_keys = ['PEXELS_API_KEY', 'PIXABAY_API_KEY', 'ANTHROPIC_API_KEY']

        missing_required = [key for key in required_keys if not os.getenv(key)]
        available_optional = [key for key in optional_keys if os.getenv(key)]

        if missing_required:
            result.error = f"필수 키 누락: {', '.join(missing_required)}"
            result.passed = False
        else:
            result.passed = True
            result.details = {
                "필수 키": "모두 설정됨",
                "선택 키": f"{len(available_optional)}/{len(optional_keys)} 설정됨"
            }

    except Exception as e:
        result.error = str(e)
        result.passed = False

    result.duration = time.time() - start_time
    return result


def test_module_imports() -> TestResult:
    """모듈 import 테스트"""
    result = TestResult("모듈 Import 확인")
    start_time = time.time()

    try:
        # 모든 핵심 모듈 import 확인
        modules = {
            "Planner": Planner,
            "AssetManager": AssetManager,
            "Editor": Editor,
            "Uploader": Uploader,
            "Orchestrator": ContentOrchestrator
        }

        for name, module_class in modules.items():
            try:
                # 기본 초기화 테스트
                if name == "Orchestrator":
                    instance = module_class()
                else:
                    instance = module_class()
                result.details[name] = "✓"
            except Exception as e:
                result.details[name] = f"✗ ({str(e)[:30]})"
                raise

        result.passed = True

    except Exception as e:
        result.error = str(e)
        result.passed = False

    result.duration = time.time() - start_time
    return result


def test_planner_only() -> TestResult:
    """Planner 모듈 단독 테스트"""
    result = TestResult("Planner 모듈 단독")
    start_time = time.time()

    if not os.getenv('GEMINI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        result.error = "AI API 키 없음 (SKIP)"
        result.passed = False
        result.duration = time.time() - start_time
        return result

    try:
        planner = Planner()

        # 주제 생성 테스트
        topics = planner.generate_topic_ideas(count=3, trending=False)

        if not topics or len(topics) == 0:
            raise ValueError("주제 생성 실패")

        # 콘텐츠 기획 테스트
        plan = planner.generate_content_plan(
            topic=topics[0],
            format=VideoFormat.SHORTS,
            target_duration=20,  # 테스트용 짧게
            style="정보성"
        )

        result.passed = True
        result.details = {
            "생성된 주제": topics[0][:50] + "...",
            "세그먼트 수": len(plan.segments),
            "제목": plan.title[:50] + "..."
        }

    except Exception as e:
        result.error = str(e)
        result.passed = False

    result.duration = time.time() - start_time
    return result


def test_asset_manager_only() -> TestResult:
    """AssetManager 모듈 단독 테스트 (TTS만)"""
    result = TestResult("AssetManager 모듈 (TTS만)")
    start_time = time.time()

    if not os.getenv('GEMINI_API_KEY'):
        result.error = "GEMINI_API_KEY 없음 (SKIP)"
        result.passed = False
        result.duration = time.time() - start_time
        return result

    try:
        # Planner로 간단한 계획 생성
        planner = Planner()
        plan = planner.generate_content_plan(
            topic="테스트 주제",
            format=VideoFormat.SHORTS,
            target_duration=10,
            style="정보성"
        )

        # AssetManager로 TTS만 생성 (영상 제외)
        asset_manager = AssetManager()
        bundle = asset_manager.collect_assets(
            plan=plan,
            videos_per_segment=0  # 영상 제외
        )

        result.passed = True
        result.details = {
            "오디오 생성": "✓" if bundle.audio else "✗",
            "오디오 길이": f"{bundle.audio.duration:.1f}초" if bundle.audio else "N/A",
            "영상 개수": len(bundle.videos)
        }

    except Exception as e:
        result.error = str(e)
        result.passed = False

    result.duration = time.time() - start_time
    return result


def test_full_pipeline_shorts() -> TestResult:
    """전체 파이프라인 테스트 (Shorts, 업로드 제외)"""
    result = TestResult("전체 파이프라인 (Shorts 20초)")
    start_time = time.time()

    # API 키 확인
    if not os.getenv('GEMINI_API_KEY'):
        result.error = "GEMINI_API_KEY 없음 (SKIP)"
        result.passed = False
        result.duration = time.time() - start_time
        return result

    try:
        # 진행 상황 추적
        progress_log = []
        def progress_callback(message: str, progress: int):
            progress_log.append(f"[{progress:3d}%] {message}")
            print(f"  [{progress:3d}%] {message}")

        # Orchestrator 생성
        config = SystemConfig(
            ai_provider=AIProvider.GEMINI,
            tts_provider=TTSProvider.GTTS,
            default_format=VideoFormat.SHORTS,
            auto_upload=False
        )

        orchestrator = ContentOrchestrator(
            config=config,
            progress_callback=progress_callback,
            log_file="logs/test_integration.log"
        )

        # 콘텐츠 생성 (20초 Shorts)
        job = orchestrator.create_content(
            topic="Python 프로그래밍 기초",
            video_format=VideoFormat.SHORTS,
            target_duration=20,
            upload=False
        )

        # 결과 확인
        if job.status == ContentStatus.COMPLETED:
            result.passed = True
            result.details = {
                "작업 ID": job.job_id[:20] + "...",
                "영상 경로": os.path.basename(job.output_video_path) if job.output_video_path else "없음",
                "파일 크기": f"{os.path.getsize(job.output_video_path) / (1024*1024):.2f} MB" if job.output_video_path and os.path.exists(job.output_video_path) else "N/A",
                "진행 단계": len(progress_log)
            }
        else:
            result.passed = False
            result.error = f"상태: {job.status.value}, 에러: {job.error_log[:100] if job.error_log else '없음'}"

    except Exception as e:
        result.error = str(e)
        result.passed = False
        import traceback
        traceback.print_exc()

    result.duration = time.time() - start_time
    return result


def test_concurrent_jobs() -> TestResult:
    """동시 작업 처리 테스트"""
    result = TestResult("동시 작업 처리 (큐 관리)")
    start_time = time.time()

    try:
        orchestrator = ContentOrchestrator()

        # 테스트 작업 3개 생성
        from core.models import ContentJob
        jobs = [
            ContentJob(job_id=f"test_job_{i}", status=ContentStatus.PLANNING)
            for i in range(3)
        ]

        # 큐에 추가
        for job in jobs:
            orchestrator.add_to_queue(job)

        # 큐 크기 확인
        queue_size = orchestrator.job_queue.qsize()

        # 통계 확인
        stats = orchestrator.get_statistics()

        result.passed = (queue_size == 3)
        result.details = {
            "큐 크기": queue_size,
            "예상 큐 크기": 3,
            "통계 큐 크기": stats['queue_size']
        }

        if queue_size != 3:
            result.error = f"큐 크기 불일치: {queue_size} != 3"

    except Exception as e:
        result.error = str(e)
        result.passed = False

    result.duration = time.time() - start_time
    return result


def test_error_handling() -> TestResult:
    """에러 핸들링 테스트"""
    result = TestResult("에러 핸들링")
    start_time = time.time()

    try:
        # 잘못된 API 키로 초기화 시도
        original_key = os.getenv('GEMINI_API_KEY')
        os.environ['GEMINI_API_KEY'] = 'invalid_key_test'

        try:
            planner = Planner()
            # 실제 API 호출은 실패할 것으로 예상
            # 하지만 초기화는 성공해야 함
            result.passed = True
            result.details = {
                "초기화": "성공 (예상대로)",
                "에러 핸들링": "정상"
            }
        except Exception as e:
            # 초기화 단계에서는 실패하지 않아야 함
            result.error = f"초기화 실패 (예상치 못함): {str(e)}"
            result.passed = False
        finally:
            # 원래 키 복원
            if original_key:
                os.environ['GEMINI_API_KEY'] = original_key

    except Exception as e:
        result.error = str(e)
        result.passed = False

    result.duration = time.time() - start_time
    return result


def main():
    """메인 테스트 실행"""
    print_header("Phase 8 통합 테스트 시작")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 테스트 실행
    tests = [
        test_environment_setup,
        test_module_imports,
        test_planner_only,
        test_asset_manager_only,
        test_concurrent_jobs,
        test_error_handling,
    ]

    results = []
    for test_func in tests:
        print_header(f"실행 중: {test_func.__doc__ or test_func.__name__}")
        result = test_func()
        results.append(result)
        print_test_result(result)

    # 전체 파이프라인 테스트 (선택사항)
    print_header("전체 파이프라인 테스트 (선택)")
    print("\n⚠️  이 테스트는 실제로 영상을 생성합니다 (약 2-3분 소요)")
    print("⚠️  API 호출 비용이 발생할 수 있습니다.")

    # 자동으로 전체 파이프라인 테스트 실행 (CI/CD 환경에서는 건너뛰기)
    run_full_test = os.getenv('RUN_FULL_INTEGRATION_TEST', 'false').lower() == 'true'

    if run_full_test:
        print("\n[INFO] RUN_FULL_INTEGRATION_TEST=true, 전체 파이프라인 테스트 실행")
        result = test_full_pipeline_shorts()
        results.append(result)
        print_test_result(result)
    else:
        print("\n[SKIP] 전체 파이프라인 테스트 건너뛰기")
        print("[INFO] 실행하려면 RUN_FULL_INTEGRATION_TEST=true 설정")

    # 결과 요약
    print_header("테스트 결과 요약")

    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)
    total_duration = sum(r.duration for r in results)

    print(f"\n📊 전체 결과: {passed_count}/{total_count} 통과 ({passed_count/total_count*100:.1f}%)")
    print(f"⏱️  총 소요 시간: {total_duration:.2f}초")

    print("\n📋 테스트별 결과:")
    for r in results:
        status_icon = "✅" if r.passed else "❌"
        print(f"  {status_icon} {r.name} ({r.duration:.2f}초)")

    # 실패한 테스트가 있으면 상세 정보 출력
    failed_tests = [r for r in results if not r.passed]
    if failed_tests:
        print("\n❌ 실패한 테스트 상세:")
        for r in failed_tests:
            print(f"\n  {r.name}:")
            print(f"    Error: {r.error}")

    print_header("테스트 완료")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 종료 코드 반환
    sys.exit(0 if passed_count == total_count else 1)


if __name__ == "__main__":
    main()
