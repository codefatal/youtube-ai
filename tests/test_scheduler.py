# tests/test_scheduler.py
from backend.database import SessionLocal
from backend.models import Account, AccountSettings, ChannelType
from backend.scheduler import scheduler_instance
import time

# 테스트 계정 생성
db = SessionLocal()

# 기존에 있을 수 있는 테스트 계정 삭제 (클린업)
db.query(Account).filter(Account.channel_name == "테스트 채널").delete()
db.commit()

account = Account(
    channel_name="테스트 채널",
    channel_type=ChannelType.INFO,
    upload_schedule="*/1 * * * *",  # 매 1분마다 (테스트용)
    is_active=True
)
db.add(account)
db.flush()  # account.id를 얻기 위해 flush

# 기본 설정 추가 (AccountSettings는 Account에 종속)
settings = AccountSettings(
    account_id=account.id,
    default_format="shorts",
    default_duration=60,
    tts_provider="elevenlabs",
    tts_voice_id="pNInz6obpgDQGcFmaJgB",
    tts_stability=0.5,
    tts_similarity_boost=0.75,
    tts_style=0.0
)
db.add(settings)
db.commit()

print(f"테스트 계정 생성됨 (ID: {account.id})")

# 스케줄러 인스턴스 확인
if not scheduler_instance.scheduler.running:
    scheduler_instance.start()

# 스케줄 등록
scheduler_instance.add_account_schedule(account)

# Job 확인
jobs = scheduler_instance.get_all_jobs()
assert len(jobs) > 0, "스케줄 Job이 등록되지 않았습니다."
print(f"등록된 Job: {jobs[0]}")

# 다음 실행 시간 확인
initial_next_run_time = jobs[0].get("next_run_time")
print(f"초기 다음 실행 시간: {initial_next_run_time}")

# 1분 대기 (작업 실행 확인)
print("1분 대기 중... (실제 작업 실행까지 기다림)")
time.sleep(65) # APScheduler의 misfire_grace_time과 안전 마진 고려

# JobHistory 확인 (worker 함수가 실행되었는지 간접 확인)
from backend.models import JobHistory, JobStatus
from datetime import datetime, timedelta

# 최근 2분 이내의 JobHistory 레코드 조회
recent_jobs = db.query(JobHistory).filter(
    JobHistory.account_id == account.id,
    JobHistory.created_at >= datetime.utcnow() - timedelta(minutes=2)
).all()

assert len(recent_jobs) > 0, "JobHistory에 작업 기록이 없습니다. Worker가 실행되지 않았을 수 있습니다."
print(f"JobHistory에 기록된 작업 수: {len(recent_jobs)}")
print(f"최근 JobHistory: ID={recent_jobs[0].job_id}, Status={recent_jobs[0].status}")
assert recent_jobs[0].status in [JobStatus.PENDING, JobStatus.PLANNING, JobStatus.FAILED, JobStatus.COMPLETED], \
    f"예상치 못한 Job Status: {recent_jobs[0].status}"

# 스케줄러 종료 (테스트 후 정리)
scheduler_instance.remove_account_schedule(account.id)
jobs_after_remove = scheduler_instance.get_all_jobs()
assert all(job["id"] != f"account_{account.id}" for job in jobs_after_remove), "스케줄 Job이 제거되지 않았습니다."
print(f"테스트 계정 스케줄 제거 완료.")

scheduler_instance.shutdown()
db.close()

print("\n스케줄러 테스트 성공!")
