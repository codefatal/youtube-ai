# -*- coding: utf-8 -*-
"""
Asset Manager 모듈 테스트 스크립트
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

from core.asset_manager import AssetManager
from core.planner import ContentPlanner
from core.models import VideoFormat


def test_stock_providers():
    """스톡 영상 제공자 테스트"""
    print("\n" + "="*60)
    print("[TEST 1] 스톡 영상 제공자 초기화")
    print("="*60)

    # Pexels만 테스트 (API 키가 있는 경우)
    if os.getenv('PEXELS_API_KEY'):
        try:
            manager = AssetManager(stock_providers=['pexels'])
            print("[SUCCESS] Pexels 초기화 완료")
        except Exception as e:
            print(f"[ERROR] Pexels 초기화 실패: {e}")
    else:
        print("[SKIP] PEXELS_API_KEY가 설정되지 않음")

    # Pixabay만 테스트 (API 키가 있는 경우)
    if os.getenv('PIXABAY_API_KEY'):
        try:
            manager = AssetManager(stock_providers=['pixabay'])
            print("[SUCCESS] Pixabay 초기화 완료")
        except Exception as e:
            print(f"[ERROR] Pixabay 초기화 실패: {e}")
    else:
        print("[SKIP] PIXABAY_API_KEY가 설정되지 않음")


def test_video_search():
    """영상 검색 테스트"""
    print("\n" + "="*60)
    print("[TEST 2] 영상 검색")
    print("="*60)

    if not (os.getenv('PEXELS_API_KEY') or os.getenv('PIXABAY_API_KEY')):
        print("[SKIP] 스톡 영상 API 키가 설정되지 않음")
        return

    try:
        providers = []
        if os.getenv('PEXELS_API_KEY'):
            providers.append('pexels')
        if os.getenv('PIXABAY_API_KEY'):
            providers.append('pixabay')

        manager = AssetManager(
            stock_providers=providers,
            cache_enabled=False  # 테스트용으로 캐시 비활성화
        )

        # 간단한 키워드로 검색
        keyword = "happy dog"
        assets = manager._search_from_providers(keyword, per_page=2)

        print(f"\n[SUCCESS] '{keyword}' 검색 결과: {len(assets)}개")
        for i, asset in enumerate(assets[:3], 1):
            print(f"  {i}. [{asset.provider}] {asset.id} - {asset.duration}초")

    except Exception as e:
        print(f"[ERROR] 검색 실패: {e}")
        import traceback
        traceback.print_exc()


def test_tts_generation():
    """TTS 생성 테스트"""
    print("\n" + "="*60)
    print("[TEST 3] TTS 음성 생성")
    print("="*60)

    try:
        manager = AssetManager(tts_provider="gtts")

        # 간단한 텍스트로 TTS 생성
        text = "안녕하세요. 이것은 테스트 음성입니다."
        filepath = manager._generate_gtts(text)

        if filepath and os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / 1024  # KB
            print(f"[SUCCESS] TTS 생성 완료: {filepath}")
            print(f"[INFO] 파일 크기: {file_size:.2f} KB")
        else:
            print("[ERROR] TTS 생성 실패")

    except Exception as e:
        print(f"[ERROR] TTS 생성 실패: {e}")
        import traceback
        traceback.print_exc()


def test_full_pipeline():
    """전체 파이프라인 테스트"""
    print("\n" + "="*60)
    print("[TEST 4] 전체 파이프라인 (Planner + AssetManager)")
    print("="*60)

    if not os.getenv('GEMINI_API_KEY'):
        print("[SKIP] GEMINI_API_KEY가 설정되지 않음")
        return

    if not (os.getenv('PEXELS_API_KEY') or os.getenv('PIXABAY_API_KEY')):
        print("[SKIP] 스톡 영상 API 키가 설정되지 않음")
        return

    try:
        # 1. Planner로 스크립트 생성
        print("\n[1/3] 스크립트 생성 중...")
        planner = ContentPlanner(ai_provider="gemini")

        content_plan = planner.create_script(
            topic="강아지의 재미있는 습관",
            format=VideoFormat.SHORTS,
            target_duration=30,
            tone="친근하고 유쾌한"
        )

        if not content_plan:
            print("[ERROR] 스크립트 생성 실패")
            return

        print(f"[SUCCESS] 스크립트 생성 완료: {content_plan.title}")
        print(f"[INFO] 세그먼트 수: {len(content_plan.segments)}")

        # 2. AssetManager로 에셋 수집
        print("\n[2/3] 에셋 수집 중...")

        providers = []
        if os.getenv('PEXELS_API_KEY'):
            providers.append('pexels')
        if os.getenv('PIXABAY_API_KEY'):
            providers.append('pixabay')

        manager = AssetManager(
            stock_providers=providers,
            tts_provider="gtts",
            cache_enabled=True
        )

        # 테스트용으로 첫 번째 세그먼트만 처리
        print("\n[INFO] 테스트를 위해 첫 번째 세그먼트만 처리합니다...")
        if content_plan.segments:
            test_segment = content_plan.segments[0]
            print(f"[INFO] 키워드: {test_segment.keyword}")

            assets = manager._search_from_providers(test_segment.keyword, per_page=1)
            if assets:
                print(f"[SUCCESS] 영상 검색 완료: {len(assets)}개")
                # 실제 다운로드는 시간이 오래 걸리므로 스킵
                print("[INFO] 실제 다운로드는 생략합니다.")
            else:
                print("[WARNING] 영상 검색 결과 없음")

        # 3. TTS 생성
        print("\n[3/3] TTS 생성 중...")
        audio_asset = manager._generate_tts(content_plan)

        if audio_asset:
            print(f"[SUCCESS] TTS 생성 완료: {audio_asset.local_path}")
        else:
            print("[WARNING] TTS 생성 실패")

        print("\n[SUCCESS] 전체 파이프라인 테스트 완료!")

    except Exception as e:
        print(f"[ERROR] 파이프라인 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_cache_system():
    """캐시 시스템 테스트"""
    print("\n" + "="*60)
    print("[TEST 5] 캐시 시스템")
    print("="*60)

    try:
        manager = AssetManager(cache_enabled=True)

        # 캐시 디렉토리 확인
        if manager.cache_dir.exists():
            cache_files = list(manager.cache_dir.glob("*.json"))
            print(f"[INFO] 캐시 파일 수: {len(cache_files)}개")

            if cache_files:
                print("[INFO] 캐시 파일 예시:")
                for cache_file in cache_files[:3]:
                    print(f"  - {cache_file.name}")
        else:
            print("[INFO] 캐시 디렉토리가 비어있습니다.")

        # 캐시 삭제 테스트
        print("\n[INFO] 캐시 삭제 테스트...")
        manager.clear_cache()
        print("[SUCCESS] 캐시 삭제 완료")

    except Exception as e:
        print(f"[ERROR] 캐시 테스트 실패: {e}")


def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("Phase 3 Asset Manager 모듈 테스트 시작")
    print("="*60)

    try:
        # 1. 스톡 영상 제공자 초기화 테스트
        test_stock_providers()

        # 2. 영상 검색 테스트
        test_video_search()

        # 3. TTS 생성 테스트
        test_tts_generation()

        # 4. 전체 파이프라인 테스트
        test_full_pipeline()

        # 5. 캐시 시스템 테스트
        test_cache_system()

        print("\n" + "="*60)
        print("[SUCCESS] 모든 테스트 완료!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
