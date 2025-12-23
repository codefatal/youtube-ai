# -*- coding: utf-8 -*-
"""
Uploader 모듈 테스트 스크립트
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

from core.uploader import YouTubeUploader
from core.models import YouTubeMetadata, VideoFormat
from datetime import datetime, timedelta


def test_uploader_import():
    """Uploader 모듈 import 테스트"""
    print("\n" + "="*60)
    print("[TEST 1] Uploader 모듈 import")
    print("="*60)

    try:
        uploader = YouTubeUploader(ai_provider="gemini")
        print(f"[SUCCESS] YouTubeUploader 초기화 완료: {uploader}")
    except Exception as e:
        print(f"[ERROR] YouTubeUploader 초기화 실패: {e}")
        import traceback
        traceback.print_exc()


def test_metadata_generation():
    """메타데이터 생성 테스트"""
    print("\n" + "="*60)
    print("[TEST 2] 메타데이터 생성")
    print("="*60)

    # API 키 확인
    if not os.getenv('GEMINI_API_KEY'):
        print("[SKIP] GEMINI_API_KEY가 설정되지 않음")
        return

    try:
        from core.planner import ContentPlanner

        # 1. 테스트용 ContentPlan 생성
        print("\n[1/2] 테스트용 스크립트 생성 중...")
        planner = ContentPlanner(ai_provider="gemini")

        content_plan = planner.create_script(
            topic="강아지 훈련 팁",
            format=VideoFormat.SHORTS,
            target_duration=30,
            tone="친근하고 유익한"
        )

        if not content_plan:
            print("[ERROR] 스크립트 생성 실패")
            return

        print(f"[SUCCESS] 스크립트 생성 완료: {content_plan.title}")

        # 2. 메타데이터 생성
        print("\n[2/2] 메타데이터 생성 중...")
        uploader = YouTubeUploader(ai_provider="gemini")

        metadata = uploader.generate_metadata(
            content_plan=content_plan,
            optimize_seo=True
        )

        print(f"\n[SUCCESS] 메타데이터 생성 완료!")
        print(f"  - 제목: {metadata.title}")
        print(f"  - 제목 길이: {len(metadata.title)}자")
        print(f"  - 설명 길이: {len(metadata.description)}자")
        print(f"  - 태그 수: {len(metadata.tags)}")
        print(f"  - 태그: {', '.join(metadata.tags[:5])}...")
        print(f"  - 카테고리 ID: {metadata.category_id}")
        print(f"  - 공개 상태: {metadata.privacy_status}")

    except Exception as e:
        print(f"[ERROR] 메타데이터 생성 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_youtube_metadata_model():
    """YouTubeMetadata 모델 테스트"""
    print("\n" + "="*60)
    print("[TEST 3] YouTubeMetadata 모델")
    print("="*60)

    try:
        # 기본 메타데이터
        metadata1 = YouTubeMetadata(
            title="테스트 영상 제목",
            description="테스트 영상 설명입니다.",
            tags=["테스트", "Python", "YouTube"],
            category_id="22",
            privacy_status="private"
        )
        print(f"[SUCCESS] 기본 메타데이터 생성: {metadata1.title}")

        # 예약 업로드 메타데이터
        publish_time = datetime.now() + timedelta(days=1)
        metadata2 = YouTubeMetadata(
            title="예약 업로드 영상",
            description="내일 공개될 영상입니다.",
            tags=["예약업로드"],
            category_id="22",
            privacy_status="private",
            publish_at=publish_time
        )
        print(f"[SUCCESS] 예약 업로드 메타데이터 생성")
        print(f"  - 공개 예정 시각: {metadata2.publish_at}")

    except Exception as e:
        print(f"[ERROR] 메타데이터 모델 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_authentication():
    """YouTube API 인증 테스트"""
    print("\n" + "="*60)
    print("[TEST 4] YouTube API 인증")
    print("="*60)

    try:
        uploader = YouTubeUploader(ai_provider="gemini")

        # client_secrets.json 파일 확인
        if not os.path.exists(uploader.credentials_path):
            print(f"[SKIP] {uploader.credentials_path} 파일이 없습니다.")
            print("[INFO] 실제 업로드를 위해서는 Google Cloud Console에서")
            print("       OAuth 2.0 클라이언트 ID를 생성하고 다운로드하세요.")
            print("       https://console.cloud.google.com/apis/credentials")
            return

        # 인증 시도
        success = uploader.authenticate()

        if success:
            print("[SUCCESS] YouTube API 인증 완료!")
            print(f"  - YouTube 서비스: {uploader.youtube}")
        else:
            print("[ERROR] 인증 실패")

    except Exception as e:
        print(f"[ERROR] 인증 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_seo_optimization():
    """SEO 최적화 테스트"""
    print("\n" + "="*60)
    print("[TEST 5] SEO 최적화")
    print("="*60)

    try:
        from core.planner import ContentPlanner

        uploader = YouTubeUploader(ai_provider="gemini")

        # 테스트 ContentPlan
        planner = ContentPlanner(ai_provider="gemini")

        # 쇼츠 포맷 테스트
        shorts_plan = planner.create_script(
            topic="고양이 귀여운 순간",
            format=VideoFormat.SHORTS,
            target_duration=20
        )

        if not shorts_plan:
            print("[SKIP] 스크립트 생성 실패")
            return

        # 메타데이터 최적화
        test_metadata = {
            "title": "짧은제목",  # 30자 미만
            "description": "짧은 설명",
            "tags": ["tag1"] * 20  # 15개 초과
        }

        optimized = uploader._optimize_seo(test_metadata, shorts_plan)

        print("[INFO] 최적화 테스트:")
        print(f"  - 제목 경고: {'예' if len(optimized['title']) < 30 else '아니오'}")
        print(f"  - 태그 제한: {len(optimized['tags'])}개 (최대 15개)")
        print(f"  - #Shorts 해시태그: {'포함' if '#Shorts' in optimized.get('description', '') else '미포함'}")

    except Exception as e:
        print(f"[ERROR] SEO 최적화 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_full_pipeline_simulation():
    """전체 파이프라인 시뮬레이션 (업로드 제외)"""
    print("\n" + "="*60)
    print("[TEST 6] 전체 파이프라인 시뮬레이션")
    print("="*60)

    if not os.getenv('GEMINI_API_KEY'):
        print("[SKIP] GEMINI_API_KEY가 설정되지 않음")
        return

    try:
        from core.planner import ContentPlanner
        from core.asset_manager import AssetManager
        from core.editor import VideoEditor

        print("\n[1/4] 스크립트 생성 중...")
        planner = ContentPlanner(ai_provider="gemini")
        content_plan = planner.create_script(
            topic="파이썬 초보자 팁",
            format=VideoFormat.SHORTS,
            target_duration=20
        )

        if not content_plan:
            print("[ERROR] 스크립트 생성 실패")
            return

        print(f"[SUCCESS] 스크립트: {content_plan.title}")

        print("\n[2/4] 메타데이터 생성 중...")
        uploader = YouTubeUploader(ai_provider="gemini")
        metadata = uploader.generate_metadata(content_plan, optimize_seo=True)

        print(f"[SUCCESS] 메타데이터: {metadata.title}")

        print("\n[3/4] 업로드 준비 완료")
        print(f"  - 제목: {metadata.title}")
        print(f"  - 태그: {', '.join(metadata.tags[:3])}...")

        print("\n[4/4] 실제 업로드는 client_secrets.json과 영상 파일이 필요합니다.")
        print("[INFO] 업로드 시뮬레이션 완료!")

    except Exception as e:
        print(f"[ERROR] 파이프라인 시뮬레이션 실패: {e}")
        import traceback
        traceback.print_exc()


def main():
    """메인 테스트 실행"""
    print("\n" + "="*60)
    print("Phase 5 Uploader 모듈 테스트 시작")
    print("="*60)

    try:
        # 1. Uploader import 테스트
        test_uploader_import()

        # 2. YouTubeMetadata 모델 테스트
        test_youtube_metadata_model()

        # 3. 메타데이터 생성 테스트
        test_metadata_generation()

        # 4. SEO 최적화 테스트
        test_seo_optimization()

        # 5. YouTube API 인증 테스트
        test_authentication()

        # 6. 전체 파이프라인 시뮬레이션
        test_full_pipeline_simulation()

        print("\n" + "="*60)
        print("[SUCCESS] 모든 테스트 완료!")
        print("="*60 + "\n")

        print("\n[참고] 실제 YouTube 업로드를 위해서는:")
        print("  1. Google Cloud Console에서 프로젝트 생성")
        print("  2. YouTube Data API v3 활성화")
        print("  3. OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)")
        print("  4. client_secrets.json 다운로드 및 프로젝트 루트에 배치")
        print("  5. uploader.upload_video() 메서드 호출")

    except Exception as e:
        print(f"\n[ERROR] 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
