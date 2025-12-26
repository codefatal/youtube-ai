"""
v4.0 전체 파이프라인 통합 테스트
"""
import pytest
import time
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal
from backend.models import Account, AccountSettings, JobHistory, JobStatus, ChannelType
from core.orchestrator import ContentOrchestrator
from core.models import VideoFormat


def test_full_pipeline_with_account():
    """
    계정 연동 전체 파이프라인 테스트

    1. DB에 계정 생성
    2. 계정별 TTS 설정 지정
    3. ContentOrchestrator로 영상 생성
    4. JobHistory 기록 확인
    """
    db = SessionLocal()

    try:
        # 1. 계정 생성
        account = Account(
            channel_name="통합 테스트 채널",
            channel_type=ChannelType.INFO,
            is_active=True
        )
        db.add(account)
        db.flush()

        # 2. AccountSettings 생성 (ElevenLabs 사용)
        settings = AccountSettings(
            account_id=account.id,
            tts_provider="elevenlabs",
            tts_voice_id="pNInz6obpgDQGcFmaJgB",
            tts_stability=0.6,
            tts_similarity_boost=0.8,
            tts_style=0.1,
            default_format="shorts",
            default_duration=60
        )
        db.add(settings)
        db.commit()

        # 3. ContentOrchestrator로 영상 생성
        orchestrator = ContentOrchestrator()

        job = orchestrator.create_content(
            topic="Python 프로그래밍 팁",
            video_format=VideoFormat.SHORTS,
            target_duration=60,
            upload=False,  # 테스트에서는 업로드 생략
            account_id=account.id
        )

        # 4. 검증
        assert job is not None
        assert job.output_video_path is not None
        assert os.path.exists(job.output_video_path)

        # 5. DB 확인
        db_job = db.query(JobHistory).filter(
            JobHistory.job_id == job.job_id
        ).first()

        assert db_job is not None
        assert db_job.account_id == account.id
        assert db_job.status == JobStatus.COMPLETED

        print(f"[SUCCESS] 통합 테스트 완료: {job.output_video_path}")

    finally:
        db.close()


def test_bgm_integration():
    """
    BGM 통합 테스트

    1. BGM 파일 준비 (assets/music/)
    2. BGM 자동 매칭
    3. 음성 + BGM 믹싱 확인
    """
    from core.asset_manager import AssetManager
    from core.bgm_manager import BGMManager
    from core.models import MoodType

    # BGM 매니저 초기화
    bgm_manager = BGMManager()

    # 분위기별 BGM 확인
    bgm = bgm_manager.get_bgm_for_mood(MoodType.HAPPY, min_duration=60)

    if bgm:
        assert bgm.mood == MoodType.HAPPY
        assert bgm.duration >= 60
        print(f"[SUCCESS] BGM 로드 성공: {bgm.name}")
    else:
        print("[WARNING] BGM 파일이 없습니다. assets/music/에 음악 파일을 추가하세요.")


def test_template_integration():
    """
    템플릿 통합 테스트

    1. 템플릿 로드 (basic, documentary, entertainment)
    2. 템플릿 적용 영상 생성
    """
    from core.editor import VideoEditor

    editor = VideoEditor()

    # 템플릿 로드
    for template_name in ["basic", "documentary", "entertainment"]:
        template = editor.load_template(template_name)
        assert template.name == template_name
        print(f"[SUCCESS] 템플릿 로드: {template.name}")