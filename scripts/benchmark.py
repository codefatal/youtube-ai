# -*- coding: utf-8 -*-
"""
Phase 8 성능 벤치마크 - 파이프라인 성능 측정
"""
import sys
import os
from pathlib import Path
import time
from datetime import datetime
import json
import psutil  # pip install psutil

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
from core.models import (
    SystemConfig,
    VideoFormat,
    AIProvider,
    TTSProvider
)


class BenchmarkResult:
    """벤치마크 결과 클래스"""
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = 0.0
        self.memory_before = 0
        self.memory_after = 0
        self.memory_peak = 0
        self.cpu_percent = 0.0
        self.success = False
        self.error = None
        self.details = {}

    def start(self):
        """벤치마크 시작"""
        self.start_time = time.time()
        process = psutil.Process()
        self.memory_before = process.memory_info().rss / 1024 / 1024  # MB
        self.cpu_percent = psutil.cpu_percent(interval=0.1)

    def stop(self):
        """벤치마크 종료"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        process = psutil.Process()
        self.memory_after = process.memory_info().rss / 1024 / 1024  # MB
        self.memory_peak = max(self.memory_before, self.memory_after)

    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            "name": self.name,
            "duration": round(self.duration, 2),
            "memory_before_mb": round(self.memory_before, 2),
            "memory_after_mb": round(self.memory_after, 2),
            "memory_delta_mb": round(self.memory_after - self.memory_before, 2),
            "cpu_percent": round(self.cpu_percent, 2),
            "success": self.success,
            "error": self.error,
            "details": self.details
        }


def print_header(title: str):
    """헤더 출력"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_result(result: BenchmarkResult):
    """결과 출력"""
    status = "✅ SUCCESS" if result.success else "❌ FAILED"
    print(f"\n{status} {result.name}")
    print(f"  ⏱️  소요 시간: {result.duration:.2f}초")
    print(f"  🧠 메모리 사용: {result.memory_before:.1f} MB → {result.memory_after:.1f} MB (Δ {result.memory_after - result.memory_before:+.1f} MB)")
    print(f"  💻 CPU 사용률: {result.cpu_percent:.1f}%")

    if result.error:
        print(f"  ❌ 에러: {result.error}")

    for key, value in result.details.items():
        print(f"  📊 {key}: {value}")


def benchmark_planner() -> BenchmarkResult:
    """Planner 벤치마크"""
    result = BenchmarkResult("Planner (주제 생성 + 스크립트 생성)")

    if not os.getenv('GEMINI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        result.error = "API 키 없음 (SKIP)"
        return result

    try:
        result.start()

        planner = Planner()

        # 주제 생성
        topic_start = time.time()
        topics = planner.generate_topic_ideas(count=1, trending=False)
        topic_duration = time.time() - topic_start

        # 스크립트 생성
        script_start = time.time()
        plan = planner.generate_content_plan(
            topic=topics[0],
            format=VideoFormat.SHORTS,
            target_duration=30,
            style="정보성"
        )
        script_duration = time.time() - script_start

        result.stop()
        result.success = True
        result.details = {
            "주제 생성 시간": f"{topic_duration:.2f}초",
            "스크립트 생성 시간": f"{script_duration:.2f}초",
            "세그먼트 수": len(plan.segments)
        }

    except Exception as e:
        result.stop()
        result.error = str(e)
        result.success = False

    return result


def benchmark_asset_manager(short: bool = True) -> BenchmarkResult:
    """AssetManager 벤치마크"""
    duration = 20 if short else 60
    result = BenchmarkResult(f"AssetManager ({duration}초 영상)")

    if not os.getenv('GEMINI_API_KEY'):
        result.error = "GEMINI_API_KEY 없음 (SKIP)"
        return result

    try:
        result.start()

        # Planner로 계획 생성
        planner = Planner()
        plan = planner.generate_content_plan(
            topic="테스트 주제",
            format=VideoFormat.SHORTS,
            target_duration=duration,
            style="정보성"
        )

        # AssetManager로 에셋 수집 (TTS만, 스톡 영상 제외)
        asset_start = time.time()
        asset_manager = AssetManager()
        bundle = asset_manager.collect_assets(plan, videos_per_segment=0)
        asset_duration = time.time() - asset_start

        result.stop()
        result.success = True
        result.details = {
            "에셋 수집 시간": f"{asset_duration:.2f}초",
            "오디오 길이": f"{bundle.audio.duration:.1f}초" if bundle.audio else "N/A",
            "영상 개수": len(bundle.videos)
        }

    except Exception as e:
        result.stop()
        result.error = str(e)
        result.success = False

    return result


def benchmark_full_pipeline(duration: int = 20) -> BenchmarkResult:
    """전체 파이프라인 벤치마크"""
    result = BenchmarkResult(f"전체 파이프라인 ({duration}초 Shorts)")

    # API 키 확인
    if not os.getenv('GEMINI_API_KEY'):
        result.error = "GEMINI_API_KEY 없음 (SKIP)"
        return result

    try:
        result.start()

        # 단계별 시간 측정
        timings = {}

        # Orchestrator 생성
        config = SystemConfig(
            ai_provider=AIProvider.GEMINI,
            tts_provider=TTSProvider.GTTS,
            default_format=VideoFormat.SHORTS,
            auto_upload=False
        )

        def progress_callback(message: str, progress: int):
            # 진행 상황만 출력 (벤치마크 결과와 분리)
            pass

        orchestrator = ContentOrchestrator(
            config=config,
            progress_callback=progress_callback,
            log_file="logs/benchmark.log"
        )

        # 전체 파이프라인 실행
        pipeline_start = time.time()
        job = orchestrator.create_content(
            topic="Python 프로그래밍 팁",
            video_format=VideoFormat.SHORTS,
            target_duration=duration,
            upload=False
        )
        pipeline_duration = time.time() - pipeline_start

        result.stop()

        if job.status.value == "completed":
            result.success = True

            # 파일 크기 확인
            file_size_mb = 0
            if job.output_video_path and os.path.exists(job.output_video_path):
                file_size_mb = os.path.getsize(job.output_video_path) / 1024 / 1024

            result.details = {
                "파이프라인 시간": f"{pipeline_duration:.2f}초",
                "작업 ID": job.job_id[:20] + "...",
                "파일 크기": f"{file_size_mb:.2f} MB",
                "초당 처리 속도": f"{duration / pipeline_duration:.2f}초/초"
            }
        else:
            result.success = False
            result.error = f"상태: {job.status.value}"

    except Exception as e:
        result.stop()
        result.error = str(e)
        result.success = False
        import traceback
        traceback.print_exc()

    return result


def run_benchmarks():
    """벤치마크 실행"""
    print_header("Phase 8 성능 벤치마크 시작")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python 버전: {sys.version}")
    print(f"Platform: {sys.platform}")

    # 시스템 정보
    print(f"\n시스템 정보:")
    print(f"  CPU 코어: {psutil.cpu_count(logical=False)}개 (논리적: {psutil.cpu_count()}개)")
    print(f"  총 메모리: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f} GB")
    print(f"  사용 가능 메모리: {psutil.virtual_memory().available / 1024 / 1024 / 1024:.1f} GB")

    results = []

    # 1. Planner 벤치마크
    print_header("1/4: Planner 벤치마크")
    result = benchmark_planner()
    results.append(result)
    print_result(result)

    # 2. AssetManager 벤치마크 (짧은 영상)
    print_header("2/4: AssetManager 벤치마크 (20초)")
    result = benchmark_asset_manager(short=True)
    results.append(result)
    print_result(result)

    # 3. AssetManager 벤치마크 (긴 영상)
    print_header("3/4: AssetManager 벤치마크 (60초)")
    result = benchmark_asset_manager(short=False)
    results.append(result)
    print_result(result)

    # 4. 전체 파이프라인 벤치마크
    print_header("4/4: 전체 파이프라인 벤치마크")

    # 사용자 확인 (선택사항)
    run_full = os.getenv('RUN_FULL_BENCHMARK', 'false').lower() == 'true'

    if run_full:
        print("\n⚠️  전체 파이프라인 벤치마크 실행 (약 3-5분 소요)")
        result = benchmark_full_pipeline(duration=20)
        results.append(result)
        print_result(result)
    else:
        print("\n⏭️  전체 파이프라인 벤치마크 SKIP")
        print("    실행하려면: RUN_FULL_BENCHMARK=true python scripts/benchmark.py")

    # 결과 요약
    print_header("벤치마크 결과 요약")

    success_count = sum(1 for r in results if r.success)
    total_count = len(results)
    total_duration = sum(r.duration for r in results if r.success)

    print(f"\n📊 전체 결과: {success_count}/{total_count} 성공")
    print(f"⏱️  총 소요 시간: {total_duration:.2f}초")

    print("\n📋 벤치마크별 결과:")
    for r in results:
        status_icon = "✅" if r.success else "❌"
        print(f"  {status_icon} {r.name}: {r.duration:.2f}초")

    # JSON 파일로 저장
    output_dir = project_root / "logs"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"benchmark_{timestamp}.json"

    benchmark_data = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "platform": sys.platform,
            "python_version": sys.version
        },
        "results": [r.to_dict() for r in results],
        "summary": {
            "total_tests": total_count,
            "successful": success_count,
            "total_duration": round(total_duration, 2)
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(benchmark_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 벤치마크 결과 저장: {output_file}")

    print_header("벤치마크 완료")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 권장 사항
    print("\n[성능 최적화 권장 사항]")
    print("1. AI API 응답 시간이 가장 큰 병목 구간입니다")
    print("2. 스톡 영상 다운로드 시간은 네트워크 속도에 의존합니다")
    print("3. TTS 생성은 로컬(gTTS)이므로 빠릅니다")
    print("4. 영상 편집(MoviePy)은 CPU/GPU 성능에 의존합니다")
    print("5. 병렬 처리를 통해 성능 개선 가능 (추후 개선 예정)")


if __name__ == "__main__":
    try:
        run_benchmarks()
    except KeyboardInterrupt:
        print("\n\n⏸️  사용자가 벤치마크를 중단했습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 벤치마크 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
