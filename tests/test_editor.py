# -*- coding: utf-8 -*-
"""
Editor 모듈 테스트 스크립트
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

from core.editor import VideoEditor
from core.models import EditConfig, VideoFormat


def test_editor_import():
    """Editor 모듈 import 테스트"""
    print("\n" + "="*60)
    print("[TEST 1] Editor 모듈 import")
    print("="*60)

    try:
        editor = VideoEditor()
        print(f"[SUCCESS] VideoEditor 초기화 완료: {editor}")
    except Exception as e:
        print(f"[ERROR] VideoEditor 초기화 실패: {e}")
        import traceback
        traceback.print_exc()


def test_editor_config():
    """EditConfig 테스트"""
    print("\n" + "="*60)
    print("[TEST 2] EditConfig 설정")
    print("="*60)

    try:
        # 기본 설정
        config = EditConfig()
        print(f"[INFO] 기본 해상도: {config.resolution}")
        print(f"[INFO] FPS: {config.fps}")
        print(f"[INFO] 트랜지션: {config.enable_transitions}")
        print(f"[INFO] 자막 애니메이션: {config.enable_subtitle_animation}")

        # 커스텀 설정
        custom_config = EditConfig(
            resolution=(1920, 1080),
            fps=60,
            enable_transitions=False
        )
        print(f"\n[INFO] 커스텀 해상도: {custom_config.resolution}")
        print(f"[INFO] 커스텀 FPS: {custom_config.fps}")

        editor = VideoEditor(config=custom_config)
        print(f"[SUCCESS] 커스텀 설정 적용 완료")

    except Exception as e:
        print(f"[ERROR] 설정 테스트 실패: {e}")


def test_full_pipeline():
    """전체 파이프라인 테스트 (Planner + AssetManager + Editor)"""
    print("\n" + "="*60)
    print("[TEST 3] 전체 파이프라인 (통합 테스트)")
    print("="*60)

    # API 키 확인
    required_keys = ['GEMINI_API_KEY']
    stock_keys = ['PEXELS_API_KEY', 'PIXABAY_API_KEY']

    if not os.getenv('GEMINI_API_KEY'):
        print("[SKIP] GEMINI_API_KEY가 설정되지 않음")
        return

    if not any(os.getenv(key) for key in stock_keys):
        print("[SKIP] 스톡 영상 API 키가 설정되지 않음")
        print("[INFO] 이 테스트는 실제 영상 생성을 위해 Pexels 또는 Pixabay API 키가 필요합니다.")
        return

    try:
        from core.planner import ContentPlanner
        from core.asset_manager import AssetManager
        from core.editor import VideoEditor

        # 1. 스크립트 생성
        print("\n[1/4] 스크립트 생성 중...")
        planner = ContentPlanner(ai_provider="gemini")

        content_plan = planner.create_script(
            topic="강아지의 귀여운 행동",
            format=VideoFormat.SHORTS,
            target_duration=20,  # 테스트용으로 짧게 (20초)
            tone="친근하고 유쾌한"
        )

        if not content_plan:
            print("[ERROR] 스크립트 생성 실패")
            return

        print(f"[SUCCESS] 스크립트 생성 완료: {content_plan.title}")
        print(f"[INFO] 세그먼트 수: {len(content_plan.segments)}")

        # 2. 에셋 수집
        print("\n[2/4] 에셋 수집 중...")

        # 사용 가능한 스톡 제공자 확인
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

        # 테스트용으로 영상은 1개만 다운로드
        print("[INFO] 테스트를 위해 첫 번째 세그먼트만 처리합니다...")

        # 첫 번째 세그먼트의 키워드로 영상 검색
        test_keyword = content_plan.segments[0].keyword if content_plan.segments else "cute dog"
        print(f"[INFO] 검색 키워드: {test_keyword}")

        assets = manager._search_from_providers(test_keyword, per_page=1)

        if not assets:
            print("[ERROR] 영상 검색 결과 없음")
            return

        # 영상 다운로드
        print(f"[INFO] 영상 다운로드 중: {assets[0].id}")
        filepath = manager._download_video(assets[0])

        if filepath:
            assets[0].local_path = filepath
            assets[0].downloaded = True
            print(f"[SUCCESS] 영상 다운로드 완료: {filepath}")
        else:
            print("[ERROR] 영상 다운로드 실패")
            return

        # TTS 생성
        print("\n[3/4] TTS 생성 중...")
        audio_asset = manager._generate_tts(content_plan)

        if not audio_asset:
            print("[WARNING] TTS 생성 실패, 오디오 없이 계속 진행")

        # AssetBundle 생성
        from core.models import AssetBundle
        bundle = AssetBundle(
            videos=[assets[0]],
            audio=audio_asset
        )

        print(f"[SUCCESS] AssetBundle 생성 완료")

        # 3. 영상 편집
        print("\n[4/4] 영상 편집 중...")
        editor = VideoEditor()

        output_path = editor.create_video(
            content_plan=content_plan,
            asset_bundle=bundle,
            output_filename="test_video.mp4"
        )

        if output_path:
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            print(f"\n[SUCCESS] 전체 파이프라인 테스트 완료!")
            print(f"[INFO] 출력 파일: {output_path}")
            print(f"[INFO] 파일 크기: {file_size:.2f} MB")
        else:
            print("[ERROR] 영상 생성 실패")

    except Exception as e:
        print(f"[ERROR] 파이프라인 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("Phase 4 Editor 모듈 테스트 시작")
    print("="*60)

    try:
        # 1. Editor import 테스트
        test_editor_import()

        # 2. EditConfig 테스트
        test_editor_config()

        # 3. 전체 파이프라인 테스트
        test_full_pipeline()

        print("\n" + "="*60)
        print("[SUCCESS] 모든 테스트 완료!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
