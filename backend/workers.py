"""
Background Worker Functions
자동 영상 생성 및 업로드 작업
"""
import logging
from datetime import datetime

from backend.database import SessionLocal
from backend.models import Account, JobHistory, JobStatus, ChannelType
from core.orchestrator import ContentOrchestrator
from core.models import VideoFormat

logger = logging.getLogger(__name__)


def auto_generate_and_upload(account_id: int):
    """
    자동 영상 생성 및 업로드 Worker

    Args:
        account_id: 계정 ID

    이 함수는 APScheduler에 의해 백그라운드에서 실행됩니다.
    """
    db = SessionLocal()
    job_id = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        # 계정 조회
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            logger.error(f"[Worker] 계정 ID {account_id}를 찾을 수 없음")
            return

        logger.info(f"[Worker] 자동 작업 시작: {account.channel_name}")

        # JobHistory 레코드 생성
        db_job = JobHistory(
            job_id=job_id,
            account_id=account_id,
            topic="",  # 아래에서 생성
            status=JobStatus.PENDING,
            format=account.settings.default_format if account.settings else "shorts",
            duration=account.settings.default_duration if account.settings else 60
        )
        db.add(db_job)
        db.commit()

        # ContentOrchestrator 생성
        orchestrator = ContentOrchestrator()

        # 주제 선정 (채널 타입 기반)
        topic = _generate_topic_for_channel_type(account.channel_type)
        db_job.topic = topic
        db.commit()

        logger.info(f"[Worker] 주제 선정: {topic}")

        # 영상 형식 설정
        video_format = VideoFormat(db_job.format)

        # 전체 파이프라인 실행
        db_job.status = JobStatus.PLANNING
        db.commit()

        result_job = orchestrator.create_content(
            topic=topic,
            video_format=video_format,
            target_duration=db_job.duration,
            upload=True,  # 자동 업로드
            account_id=account_id
        )

        # 결과 업데이트
        if result_job.youtube_url:
            db_job.status = JobStatus.COMPLETED
            db_job.output_video_path = result_job.output_video_path
            db_job.youtube_url = result_job.youtube_url
            db_job.youtube_video_id = result_job.youtube_video_id
            db_job.completed_at = datetime.utcnow()

            logger.info(f"[Worker] 작업 완료: {result_job.youtube_url}")
        else:
            raise Exception("YouTube 업로드 실패")

    except Exception as e:
        logger.error(f"[Worker] 작업 실패 ({account_id}): {e}")

        # 에러 기록
        db_job.status = JobStatus.FAILED
        db_job.error_message = str(e)
        db_job.completed_at = datetime.utcnow()

    finally:
        db.commit()
        db.close()


def _generate_topic_for_channel_type(channel_type: ChannelType) -> str:
    """
    채널 타입에 맞는 주제 생성

    Args:
        channel_type: ChannelType Enum

    Returns:
        생성된 주제
    """
    from core.planner import Planner

    planner = Planner()

    # 채널 타입별 카테고리 매핑
    category_map = {
        ChannelType.HUMOR: "유머",
        ChannelType.TREND: "트렌드",
        ChannelType.INFO: "정보",
        ChannelType.REVIEW: "리뷰",
        ChannelType.NEWS: "뉴스",
        ChannelType.DAILY: "일상"
    }

    category = category_map.get(channel_type, "트렌드")

    # AI로 주제 생성
    topics = planner.generate_topic_ideas(category=category, count=1)

    if topics:
        return topics[0]
    else:
        return f"{category} 관련 흥미로운 이야기"