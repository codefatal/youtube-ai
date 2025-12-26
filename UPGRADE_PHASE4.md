# Phase 4: 스케줄링 및 자동화 시스템

**작업 기간**: 1주 (2026-01-17 ~ 2026-01-23)
**담당 모듈**: `backend/scheduler.py`, `backend/workers.py`, `backend/main.py`
**우선순위**: ⭐⭐⭐⭐⭐ (최고)
**난이도**: 🔥🔥🔥🔥 (상)
**의존성**: Phase 1, 2 완료 필수

---

## 📋 개요

APScheduler를 도입하여 계정별로 설정된 스케줄에 따라 자동으로 영상을 생성하고 업로드하는 백그라운드 작업 시스템을 구축합니다. 이를 통해 완전 자동화된 YouTube 채널 운영이 가능해집니다.

### 목표
- ✅ APScheduler 도입 (백그라운드 작업)
- ✅ 계정별 스케줄 관리 (Cron 포맷)
- ✅ 자동 생성 및 업로드 Worker
- ✅ 작업 이력 DB 저장 (JobHistory 테이블)
- ✅ 에러 처리 및 재시도 로직
- ✅ 스케줄 모니터링 API

---

## 🗂️ 디렉토리 구조

```
youtube-ai/
├── backend/
│   ├── scheduler.py         # ✨ NEW - APScheduler 설정
│   ├── workers.py           # ✨ NEW - 자동화 Worker 함수
│   ├── main.py              # 🔧 MODIFY - 스케줄러 시작
│   └── routers/
│       └── scheduler.py     # ✨ NEW - 스케줄 관리 API
├── core/
│   └── orchestrator.py      # 🔧 MODIFY - account_id 연동
└── tests/
    └── test_scheduler.py    # ✨ NEW - 스케줄러 테스트
```

---

## 📦 필수 패키지 설치

`requirements.txt`에 추가:

```txt
# Scheduling (Phase 4)
apscheduler>=3.10.4
pytz>=2023.3
```

설치:
```bash
pip install apscheduler pytz
```

---

## 🏗️ 구현 단계

### Step 1: 스케줄러 모듈 생성 (`backend/scheduler.py`)

```python
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
```

---

### Step 2: Worker 함수 생성 (`backend/workers.py`)

```python
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
```

---

### Step 3: FastAPI 앱에 스케줄러 통합 (`backend/main.py`)

```python
# backend/main.py

from backend.scheduler import scheduler_instance

# ... 기존 코드 ...

@app.on_event("startup")
def startup_event():
    """앱 시작 시 실행"""
    # DB 초기화
    init_db()
    print("[FastAPI] 데이터베이스 초기화 완료")

    # ✨ 스케줄러 시작
    scheduler_instance.start()
    scheduler_instance.load_account_schedules()
    print("[FastAPI] 스케줄러 시작 완료")


@app.on_event("shutdown")
def shutdown_event():
    """앱 종료 시 실행"""
    # ✨ 스케줄러 종료
    scheduler_instance.shutdown()
    print("[FastAPI] 스케줄러 종료됨")
```

---

### Step 4: 스케줄 관리 API (`backend/routers/scheduler.py`)

```python
"""
Scheduler Management API
스케줄 조회 및 관리
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.scheduler import scheduler_instance

router = APIRouter(prefix="/api/scheduler", tags=["Scheduler"])


@router.get("/jobs")
def list_scheduled_jobs():
    """
    현재 등록된 모든 스케줄 조회
    """
    jobs = scheduler_instance.get_all_jobs()
    return {"jobs": jobs}


@router.post("/reload")
def reload_schedules():
    """
    DB에서 스케줄 다시 로드
    계정 설정 변경 시 호출
    """
    scheduler_instance.load_account_schedules()
    return {"message": "스케줄이 다시 로드되었습니다."}


@router.post("/trigger/{account_id}")
def trigger_manual_job(account_id: int):
    """
    특정 계정의 자동 작업을 즉시 실행 (테스트용)
    """
    from backend.workers import auto_generate_and_upload

    # 백그라운드에서 즉시 실행
    scheduler_instance.scheduler.add_job(
        func=auto_generate_and_upload,
        args=[account_id],
        id=f"manual_{account_id}",
        replace_existing=True
    )

    return {"message": f"계정 ID {account_id}의 작업이 실행 대기 중입니다."}


@router.delete("/jobs/{job_id}")
def remove_scheduled_job(job_id: str):
    """
    특정 Job 제거
    """
    try:
        scheduler_instance.scheduler.remove_job(job_id)
        return {"message": f"Job '{job_id}'가 제거되었습니다."}
    except Exception as e:
        return {"error": str(e)}
```

**라우터 등록** (`backend/main.py`):

```python
from backend.routers import accounts, tts, scheduler

app.include_router(accounts.router)
app.include_router(tts.router)
app.include_router(scheduler.router)  # ✨ NEW
```

---

### Step 5: Orchestrator 수정 - account_id 연동 (`core/orchestrator.py`)

```python
# core/orchestrator.py

class ContentOrchestrator:
    def create_content(
        self,
        topic: Optional[str] = None,
        video_format: VideoFormat = VideoFormat.SHORTS,
        target_duration: int = 60,
        upload: bool = False,
        account_id: Optional[int] = None  # ✨ NEW
    ) -> ContentJob:
        """
        전체 파이프라인 실행 (계정 ID 연동)
        """
        # ... 기존 코드 ...

        # ✨ AssetManager에 account_id 전달 (TTS 설정용)
        bundle = self.asset_manager.collect_assets(
            content_plan,
            account_id=account_id  # Phase 3에서 구현한 기능 사용
        )

        # ... 나머지 코드 ...
```

---

## ✅ 테스트 체크리스트

### 1. 스케줄러 시작 테스트

```bash
# 백엔드 서버 실행
python backend/main.py

# 로그 확인:
# - [Scheduler] APScheduler 초기화 완료
# - [Scheduler] 스케줄러 시작됨
# - [Scheduler] 활성 계정 N개 로드
```

### 2. 스케줄 등록 테스트

```python
# tests/test_scheduler.py
from backend.database import SessionLocal
from backend.models import Account, AccountSettings, ChannelType
from backend.scheduler import scheduler_instance

# 테스트 계정 생성
db = SessionLocal()

account = Account(
    channel_name="테스트 채널",
    channel_type=ChannelType.INFO,
    upload_schedule="*/5 * * * *",  # 매 5분마다 (테스트용)
    is_active=True
)
db.add(account)
db.flush()

# 기본 설정 추가
settings = AccountSettings(account_id=account.id)
db.add(settings)
db.commit()

# 스케줄 등록
scheduler_instance.add_account_schedule(account)

# Job 확인
jobs = scheduler_instance.get_all_jobs()
assert len(jobs) > 0
print(f"등록된 Job: {jobs[0]}")

db.close()
```

### 3. 수동 트리거 테스트

```bash
# 특정 계정의 작업 즉시 실행
curl -X POST "http://localhost:8000/api/scheduler/trigger/1"

# JobHistory 테이블 확인 (DB에 작업 기록됨)
```

### 4. 24시간 안정성 테스트

```bash
# 백엔드 서버를 24시간 실행
python backend/main.py

# 로그 모니터링:
# - 스케줄된 시간에 Worker 실행 확인
# - 에러 발생 시 JobHistory에 기록 확인
# - 메모리 누수 없는지 확인
```

---

## 📊 성공 기준

- [x] 스케줄러 24시간 안정 동작 (서버 재시작 없이)
- [x] 자동 업로드 100% 성공률 (에러 발생 시 DB 기록)
- [x] 작업 이력 DB 저장 확인 (JobHistory 테이블)
- [x] Cron 포맷 정확도 (±1분 이내 실행)
- [x] 스케줄 관리 API 작동 (조회, 재로드, 수동 트리거)

---

## 🔧 Cron 포맷 가이드

```
분 시 일 월 요일
│ │ │ │ │
│ │ │ │ └─ 0-6 (0=일요일)
│ │ │ └─── 1-12
│ │ └───── 1-31
│ └─────── 0-23
└───────── 0-59
```

**예시**:
- `0 9 * * *` - 매일 오전 9시
- `0 9,18 * * *` - 매일 오전 9시, 오후 6시
- `0 9 * * 1` - 매주 월요일 오전 9시
- `*/30 * * * *` - 30분마다
- `0 9 1 * *` - 매월 1일 오전 9시

---

## 🚀 커밋 전략

```bash
# Step 1
git add backend/scheduler.py
git commit -m "Phase 4: Add APScheduler module with account schedule loading"

# Step 2
git add backend/workers.py
git commit -m "Phase 4: Add auto generation and upload worker"

# Step 3
git add backend/main.py
git commit -m "Phase 4: Integrate scheduler into FastAPI startup/shutdown"

# Step 4
git add backend/routers/scheduler.py
git commit -m "Phase 4: Add scheduler management API"

# Step 5
git add core/orchestrator.py
git commit -m "Phase 4: Add account_id support to orchestrator"

# 테스트
git add tests/test_scheduler.py
git commit -m "Phase 4: Add scheduler tests"
```

---

## ⚠️ 주의사항

1. **타임존 설정**
   - `Asia/Seoul` 타임존 사용
   - 서버 시간과 Cron 시간이 일치하는지 확인

2. **동시 실행 방지**
   - `max_instances=1` 설정으로 중복 실행 방지
   - 이전 작업이 완료되지 않으면 대기

3. **에러 처리**
   - Worker 함수 내부에서 모든 예외 처리
   - JobHistory에 에러 메시지 기록

4. **스케줄 변경**
   - Account의 `upload_schedule` 변경 후 `/api/scheduler/reload` 호출 필요
   - 또는 서버 재시작

5. **테스트 시 주의**
   - 짧은 간격(`*/5 * * * *`)으로 테스트 시 API 호출 한도 주의
   - 프로덕션에서는 최소 1일 1회 권장

---

## 💡 활용 시나리오

### 시나리오 1: 다중 채널 자동화

```python
# 유머 채널: 매일 오전 9시
account1 = Account(
    channel_name="재미있는 이야기",
    channel_type=ChannelType.HUMOR,
    upload_schedule="0 9 * * *",
    is_active=True
)

# 정보 채널: 매일 오후 6시
account2 = Account(
    channel_name="유용한 정보",
    channel_type=ChannelType.INFO,
    upload_schedule="0 18 * * *",
    is_active=True
)

# 트렌드 채널: 매일 오전 10시, 오후 8시
account3 = Account(
    channel_name="핫한 트렌드",
    channel_type=ChannelType.TREND,
    upload_schedule="0 10,20 * * *",
    is_active=True
)
```

### 시나리오 2: 주말 특별 콘텐츠

```python
# 주말에만 업로드
weekend_account = Account(
    channel_name="주말 특집",
    upload_schedule="0 9 * * 0,6",  # 일요일, 토요일
    is_active=True
)
```

---

## 📚 다음 단계

Phase 4 완료 후:
- **Phase 5**: 프론트엔드 UI (스케줄 설정, 작업 모니터링)
- **Phase 6**: 통합 테스트 및 마무리

**Phase 5로 이동**: [UPGRADE_PHASE5.md](./UPGRADE_PHASE5.md)

---

**작성일**: 2025-12-26
**버전**: 1.0
**상태**: Ready for Implementation
