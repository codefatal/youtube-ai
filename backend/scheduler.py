"""
Scheduler Module
APScheduler 기반 자동화 작업 스케줄링
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from pytz import timezone
from typing import List
import logging

from backend.database import SessionLocal, SQLALCHEMY_DATABASE_URL
from backend.models import Account

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomationScheduler:
    """자동화 스케줄러"""

    def __init__(self):
        """
        APScheduler 초기화
        JobStore로 SQLite 사용 (영속성 보장)
        """
        # JobStore 설정 (스케줄 정보를 DB에 저장)
        jobstores = {
            'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URL)
        }

        # Executor 설정 (스레드 풀)
        executors = {
            'default': ThreadPoolExecutor(max_workers=5)
        }

        # Job 기본 설정
        job_defaults = {
            'coalesce': True,        # 누락된 작업 합치기
            'max_instances': 1,      # 동시 실행 방지
            'misfire_grace_time': 300  # 5분 이내 지연 허용
        }

        # 스케줄러 생성
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=timezone('Asia/Seoul')
        )

        logger.info("[Scheduler] APScheduler 초기화 완료")

    def start(self):
        """스케줄러 시작"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("[Scheduler] 스케줄러 시작됨")

    def shutdown(self):
        """스케줄러 종료"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("[Scheduler] 스케줄러 종료됨")

    def load_account_schedules(self):
        """
        DB에서 활성화된 계정들의 스케줄을 로드하여 등록

        모든 is_active=True 계정을 조회하고
        upload_schedule (Cron 포맷)에 따라 작업 등록
        """
        db = SessionLocal()
        try:
            # 활성화된 계정 조회
            active_accounts = db.query(Account).filter(
                Account.is_active == True,
                Account.upload_schedule.isnot(None)
            ).all()

            logger.info(f"[Scheduler] 활성 계정 {len(active_accounts)}개 로드")

            for account in active_accounts:
                self.add_account_schedule(account)

        finally:
            db.close()

    def add_account_schedule(self, account: Account):
        """
        특정 계정의 스케줄 등록

        Args:
            account: Account 객체
        """
        try:
            # Cron 포맷 파싱
            # 예: "0 9 * * *" = 매일 오전 9시
            cron_parts = account.upload_schedule.split()

            if len(cron_parts) != 5:
                logger.error(f"[Scheduler] 잘못된 Cron 포맷: {account.upload_schedule}")
                return

            minute, hour, day, month, day_of_week = cron_parts

            # CronTrigger 생성
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                timezone=timezone('Asia/Seoul')
            )

            # Worker 함수 import (순환 참조 방지)
            from backend.workers import auto_generate_and_upload

            # Job 등록
            job_id = f"account_{account.id}"
            self.scheduler.add_job(
                func=auto_generate_and_upload,
                trigger=trigger,
                args=[account.id],
                id=job_id,
                replace_existing=True,  # 기존 Job 교체
                name=f"Auto Upload - {account.channel_name}"
            )

            logger.info(
                f"[Scheduler] 계정 '{account.channel_name}' 스케줄 등록: {account.upload_schedule}"
            )

        except Exception as e:
            logger.error(f"[Scheduler] 스케줄 등록 실패 ({account.channel_name}): {e}")

    def remove_account_schedule(self, account_id: int):
        """
        특정 계정의 스케줄 제거

        Args:
            account_id: 계정 ID
        """
        job_id = f"account_{account_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"[Scheduler] 계정 ID {account_id} 스케줄 제거됨")
        except Exception as e:
            logger.warning(f"[Scheduler] 스케줄 제거 실패: {e}")

    def get_all_jobs(self) -> List[dict]:
        """
        등록된 모든 Job 조회

        Returns:
            Job 정보 리스트
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs


# 전역 스케줄러 인스턴스
scheduler_instance = AutomationScheduler()
