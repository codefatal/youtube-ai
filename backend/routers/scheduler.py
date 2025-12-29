"""
Scheduler Management API
스케줄 조회 및 관리
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.scheduler import scheduler_instance
from backend.schemas import SchedulerJobsResponse, MessageResponse

router = APIRouter(prefix="/api/scheduler", tags=["Scheduler"])


@router.get("/jobs", response_model=SchedulerJobsResponse)
def list_scheduled_jobs():
    """
    현재 등록된 모든 스케줄 조회
    """
    jobs = scheduler_instance.get_all_jobs()
    return {"jobs": jobs}


@router.post("/reload", response_model=MessageResponse)
def reload_schedules():
    """
    DB에서 스케줄 다시 로드
    계정 설정 변경 시 호출
    """
    scheduler_instance.load_account_schedules()
    return {"message": "스케줄이 다시 로드되었습니다."}


@router.post("/trigger/{account_id}", response_model=MessageResponse)
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


@router.delete("/jobs/{job_id}", response_model=MessageResponse)
def remove_scheduled_job(job_id: str):
    """
    특정 Job 제거
    """
    try:
        scheduler_instance.scheduler.remove_job(job_id)
        return {"message": f"Job '{job_id}'가 제거되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}'를 찾을 수 없습니다: {str(e)}")
