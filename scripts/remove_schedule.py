"""
Remove scheduled job from APScheduler
"""
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.scheduler import scheduler_instance

def remove_job(job_id: str):
    """특정 Job 제거"""
    try:
        # 스케줄러 시작 (JobStore 접근을 위해)
        scheduler_instance.start()

        # 모든 Job 조회
        jobs = scheduler_instance.get_all_jobs()
        print(f"현재 등록된 작업 {len(jobs)}개:")
        for job in jobs:
            print(f"  - {job['id']}: {job['name']}")

        # Job 제거
        if job_id:
            scheduler_instance.scheduler.remove_job(job_id)
            print(f"\n[SUCCESS] Job '{job_id}' 제거 완료")

        # 스케줄러 종료
        scheduler_instance.shutdown()

    except Exception as e:
        print(f"[ERROR] 작업 제거 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 계정 ID 1의 작업 제거
    remove_job("account_1")
