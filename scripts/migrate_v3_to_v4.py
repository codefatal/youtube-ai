"""
v3.0 → v4.0 데이터 마이그레이션 스크립트

job_history.json → JobHistory 테이블
"""
import json
from pathlib import Path
from datetime import datetime

from backend.database import SessionLocal
from backend.models import JobHistory, JobStatus


def migrate_job_history():
    """
    job_history.json의 데이터를 JobHistory 테이블로 마이그레이션
    """
    json_path = Path("./data/job_history.json")

    if not json_path.exists():
        print("[INFO] job_history.json이 없습니다. 마이그레이션 건너뜀.")
        return

    # JSON 로드
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    db = SessionLocal()

    try:
        migrated_count = 0

        for job_id, job_data in data.items():
            # 이미 존재하는지 확인
            existing = db.query(JobHistory).filter(
                JobHistory.job_id == job_id
            ).first()

            if existing:
                print(f"[SKIP] {job_id} - 이미 존재함")
                continue

            # JobHistory 레코드 생성
            db_job = JobHistory(
                job_id=job_id,
                account_id=None,  # v3에서는 account_id 없음
                topic=job_data.get("topic", "Unknown"),
                status=JobStatus(job_data.get("status", "completed")),
                format=job_data.get("format", "shorts"),
                duration=job_data.get("duration", 60),
                output_video_path=job_data.get("output_video_path"),
                youtube_url=job_data.get("youtube_url"),
                youtube_video_id=job_data.get("youtube_video_id"),
                started_at=datetime.fromisoformat(job_data.get("started_at")),
                completed_at=datetime.fromisoformat(job_data.get("completed_at")) if job_data.get("completed_at") else None
            )

            db.add(db_job)
            migrated_count += 1

        db.commit()
        print(f"[SUCCESS] {migrated_count}개 작업 마이그레이션 완료")

        # 백업
        backup_path = json_path.with_suffix('.json.backup')
        json_path.rename(backup_path)
        print(f"[BACKUP] {backup_path}로 백업됨")

    except Exception as e:
        print(f"[ERROR] 마이그레이션 실패: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    migrate_job_history()
