"""
FastAPI Backend Server for YouTube AI v3.0
AI-Powered Original Content Creation System
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import shutil

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# 로컬 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.orchestrator import ContentOrchestrator
from core.planner import ContentPlanner
from core.asset_manager import AssetManager
from core.editor import VideoEditor
from core.uploader import YouTubeUploader
from core.models import (
    SystemConfig,
    VideoFormat,
    AIProvider,
    TTSProvider,
    ContentStatus
)

# Phase 1: Database and API Routers
from backend.database import init_db, SessionLocal
from backend.models import JobHistory as DBJobHistory, JobStatus
from backend.routers import accounts, tts, scheduler, bgm  # Phase 5: BGM 라우터 추가
from backend.scheduler import scheduler_instance  # ✨ NEW
from sqlalchemy import func

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    init_db()
    print("[FastAPI] 데이터베이스 초기화 완료")
    scheduler_instance.start()
    scheduler_instance.load_account_schedules()
    print("[FastAPI] 스케줄러 시작 완료")
    yield
    # 종료 시 실행
    scheduler_instance.shutdown()
    print("[FastAPI] 스케줄러 종료됨")

app = FastAPI(
    title="YouTube AI v4.0 API",
    description="AI-Powered Original Content Creation System",
    version="4.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 라우터 등록 ====================

app.include_router(accounts.router)
app.include_router(tts.router)
app.include_router(scheduler.router)
app.include_router(bgm.router)  # Phase 5: BGM API


# 전역 Orchestrator (싱글톤 패턴)
_orchestrator = None

def get_orchestrator() -> ContentOrchestrator:
    """Orchestrator 싱글톤 인스턴스 반환"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ContentOrchestrator(log_file="logs/backend_orchestrator.log")
    return _orchestrator


# ==================== Request/Response 모델 ====================

class GenerateTopicsRequest(BaseModel):
    count: int = 3
    trending: bool = True


class GenerateScriptRequest(BaseModel):
    topic: str
    format: str = "shorts"  # shorts, landscape, square
    duration: int = 60
    style: str = "정보성"  # 힐링, 정보성, 유머


class CreateVideoRequest(BaseModel):
    topic: Optional[str] = None  # None이면 AI가 자동 생성
    format: str = "shorts"
    duration: int = 60
    upload: bool = False
    template: Optional[str] = None  # ✨ NEW: 템플릿 필드
    ai_provider: Optional[str] = None  # gemini, claude, openai
    tts_provider: Optional[str] = None  # gtts, elevenlabs, google_cloud
    tts_settings: Optional[Dict[str, Any]] = None  # ✨ NEW: TTS 상세 설정
    bgm_settings: Optional[Dict[str, Any]] = None  # Phase 5: BGM 설정 (enabled, mood, volume)


class GetJobStatusRequest(BaseModel):
    job_id: str


class StatsResponse(BaseModel):
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    success_rate: float
    queue_size: int


# ==================== API 엔드포인트 ====================

@app.get("/")
async def root():
    """API 루트"""
    return {
        "name": "YouTube AI v3.0 API",
        "version": "3.0.0",
        "status": "running",
        "system": "AI-Powered Original Content Creation"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/topics/generate")
async def generate_topics(request: GenerateTopicsRequest):
    """AI 주제 생성"""
    try:
        planner = ContentPlanner()

        # trending이 True면 "트렌드" 카테고리, False면 "일반" 카테고리 사용
        category = "트렌드" if request.trending else "일반"
        topics = planner.generate_topic_ideas(
            category=category,
            count=request.count
        )

        return {
            "success": True,
            "data": {
                "topics": topics,
                "count": len(topics)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주제 생성 실패: {str(e)}")


@app.post("/api/scripts/generate")
async def generate_script(request: GenerateScriptRequest):
    """AI 스크립트 생성"""
    try:
        planner = ContentPlanner()

        # 포맷 변환
        video_format = VideoFormat[request.format.upper()]

        plan = planner.create_script(
            topic=request.topic,
            format=video_format,
            target_duration=request.duration,
            tone=request.style
        )

        return {
            "success": True,
            "data": {
                "title": plan.title,
                "description": plan.description,
                "tags": plan.tags,
                "segments": [
                    {
                        "text": seg.text,
                        "keyword": seg.keyword,
                        "duration": seg.duration
                    }
                    for seg in plan.segments
                ],
                "total_duration": plan.target_duration
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스크립트 생성 실패: {str(e)}")


@app.post("/api/videos/create")
async def create_video(request: CreateVideoRequest, background_tasks: BackgroundTasks):
    """영상 생성 (백그라운드 작업)"""
    try:
        orchestrator = get_orchestrator()

        # 설정 생성
        config = SystemConfig()

        # Provider 설정
        if request.ai_provider:
            config.ai_provider = AIProvider[request.ai_provider.upper()]
        if request.tts_provider:
            config.tts_provider = TTSProvider[request.tts_provider.upper()]

        # 포맷 변환
        video_format = VideoFormat[request.format.upper()]

        # 주제가 없으면 AI가 자동 생성
        topic = request.topic
        if not topic:
            planner = ContentPlanner()
            topics = planner.generate_topic_ideas(category="트렌드", count=1)
            topic = topics[0] if topics else "AI 기술 소개"

        # 영상 생성 (비동기)
        job = await asyncio.to_thread(
            orchestrator.create_content,
            topic=topic,
            video_format=video_format,
            target_duration=request.duration,
            upload=request.upload,
            template=request.template,  # ✨ NEW
            tts_settings=request.tts_settings  # ✨ NEW
        )

        return {
            "success": True,
            "data": {
                "job_id": job.job_id,
                "status": job.status.value,
                "topic": topic,
                "format": request.format,
                "duration": request.duration,
                "message": "영상 생성이 시작되었습니다. job_id로 진행 상황을 확인하세요."
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"영상 생성 실패: {str(e)}")


@app.post("/api/jobs/status")
async def get_job_status(request: GetJobStatusRequest):
    """작업 상태 조회"""
    try:
        db = SessionLocal()
        try:
            job = db.query(DBJobHistory).filter(DBJobHistory.job_id == request.job_id).first()

            if not job:
                raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")

            return {
                "success": True,
                "data": {
                    "job_id": job.job_id,
                    "status": job.status.value,
                    "topic": job.topic,
                    "format": job.format,
                    "output_video_path": job.output_video_path,
                    "youtube_url": job.youtube_url,
                    "error_log": job.error_message or "",
                    "created_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None
                }
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")


@app.get("/api/jobs/recent")
async def get_recent_jobs(page: int = 1, limit: int = 10):
    """
    Phase 6: 최근 작업 목록 조회 (페이징 지원)

    Args:
        page: 페이지 번호 (1부터 시작)
        limit: 페이지당 항목 수 (기본 10개)
    """
    try:
        db = SessionLocal()
        try:
            # 페이징 계산
            offset = (page - 1) * limit

            # 전체 개수 조회
            total = db.query(func.count(DBJobHistory.id)).scalar()

            # 페이징된 데이터 조회
            jobs = db.query(DBJobHistory).order_by(DBJobHistory.started_at.desc()).offset(offset).limit(limit).all()

            # 전체 페이지 수 계산
            total_pages = (total + limit - 1) // limit if total > 0 else 1

            return {
                "success": True,
                "data": {
                    "jobs": [
                        {
                            "job_id": job.job_id,
                            "status": job.status.value,
                            "topic": job.topic,
                            "format": job.format,
                            "created_at": job.started_at.isoformat() if job.started_at else None,
                            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                            "output_video_path": job.output_video_path,
                            "youtube_url": job.youtube_url,
                            "error_log": job.error_log
                        }
                        for job in jobs
                    ],
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "total_pages": total_pages,
                    "count": len(jobs)
                }
            }
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 목록 조회 실패: {str(e)}")


@app.get("/api/stats")
async def get_statistics():
    """통계 조회"""
    try:
        db = SessionLocal()
        try:
            total_jobs = db.query(func.count(DBJobHistory.id)).scalar() or 0
            completed_jobs = db.query(func.count(DBJobHistory.id)).filter(
                DBJobHistory.status == JobStatus.COMPLETED
            ).scalar() or 0
            failed_jobs = db.query(func.count(DBJobHistory.id)).filter(
                DBJobHistory.status == JobStatus.FAILED
            ).scalar() or 0

            success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0.0

            return {
                "success": True,
                "data": {
                    "total_jobs": total_jobs,
                    "completed_jobs": completed_jobs,
                    "failed_jobs": failed_jobs,
                    "success_rate": round(success_rate, 2),
                    "queue_size": 0  # DB 모드에서는 큐 사이즈 없음
                }
            }
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@app.get("/api/config")
async def get_config():
    """현재 설정 조회"""
    try:
        config = SystemConfig()

        return {
            "success": True,
            "data": {
                "ai_provider": config.ai_provider.value,
                "tts_provider": config.tts_provider.value,
                "default_format": config.default_format.value,
                "default_duration": config.default_duration,
                "auto_upload": config.auto_upload
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"설정 조회 실패: {str(e)}")


# ==================== 테스트 API ====================

class TestVideoRequest(BaseModel):
    """테스트 영상 생성 요청"""
    duration: int = 10  # 영상 길이 (초)
    subtitles: List[str] = ["테스트 자막 1", "테스트 자막 2", "테스트 자막 3"]
    title: str = "테스트 영상"

@app.post("/api/test/video")
async def create_test_video(request: TestVideoRequest):
    """
    테스트용 간단한 영상 생성 (10초 기본)
    - 사용자가 입력한 자막으로 영상 생성
    - 스톡 영상 사용
    """
    try:
        from core.models import ContentPlan, ScriptSegment, VideoFormat

        # 자막당 시간 계산
        segment_duration = request.duration / len(request.subtitles)

        # ContentPlan 생성
        segments = [
            ScriptSegment(
                text=subtitle,
                keyword="nature landscape",  # 고정 키워드
                duration=segment_duration
            )
            for subtitle in request.subtitles
        ]

        content_plan = ContentPlan(
            title=request.title,
            description="테스트 영상입니다",
            tags=["테스트"],
            format=VideoFormat.SHORTS,
            target_duration=request.duration,
            segments=segments
        )

        # Orchestrator로 영상 생성
        orchestrator = ContentOrchestrator()
        job = await asyncio.to_thread(
            orchestrator.create_content_from_plan,
            content_plan=content_plan,
            upload=False
        )

        if job.status == ContentStatus.COMPLETED:
            return {
                "success": True,
                "video_path": job.output_video_path,
                "duration": request.duration,
                "subtitles": request.subtitles
            }
        else:
            return {
                "success": False,
                "error": "영상 생성 실패"
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"테스트 영상 생성 실패: {str(e)}")


# ==================== BGM API ====================

@app.post("/api/bgm/upload")
async def upload_bgm(
    file: UploadFile = File(...),
    mood: str = Form(...),
    name: str = Form(...)
):
    """
    BGM 파일 업로드

    Args:
        file: mp3 파일
        mood: 분위기 (HAPPY, SAD, ENERGETIC, CALM, TENSE, MYSTERIOUS)
        name: BGM 이름
    """
    try:
        # mood 검증
        valid_moods = ["HAPPY", "SAD", "ENERGETIC", "CALM", "TENSE", "MYSTERIOUS"]
        mood_upper = mood.upper()
        if mood_upper not in valid_moods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mood. Must be one of: {', '.join(valid_moods)}"
            )

        # 파일 확장자 확인
        if not file.filename.endswith('.mp3'):
            raise HTTPException(status_code=400, detail="Only .mp3 files are allowed")

        # music/MOOD/ 폴더 생성
        music_dir = os.path.join(os.path.dirname(__file__), '..', 'music', mood_upper)
        os.makedirs(music_dir, exist_ok=True)

        # 파일명 정리 (공백 → 언더스코어)
        clean_name = name.replace(' ', '_')
        filepath = os.path.join(music_dir, f"{clean_name}.mp3")

        # 파일 저장
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        print(f"[BGM] 업로드 완료: {filepath}")

        return {
            "success": True,
            "message": f"BGM uploaded successfully",
            "filepath": filepath,
            "mood": mood_upper,
            "name": name
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"BGM upload failed: {str(e)}")


@app.get("/api/bgm/list")
async def list_bgm():
    """music 폴더의 모든 BGM 파일 목록"""
    try:
        music_root = os.path.join(os.path.dirname(__file__), '..', 'music')
        bgm_list = []

        if os.path.exists(music_root):
            for mood_folder in os.listdir(music_root):
                mood_path = os.path.join(music_root, mood_folder)
                if os.path.isdir(mood_path):
                    for file in os.listdir(mood_path):
                        if file.endswith('.mp3'):
                            bgm_list.append({
                                "mood": mood_folder,
                                "name": file.replace('.mp3', ''),
                                "filepath": os.path.join(mood_path, file)
                            })

        return {
            "success": True,
            "bgm_count": len(bgm_list),
            "bgm_list": bgm_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BGM list failed: {str(e)}")


# ==================== 서버 실행 ====================

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("YouTube AI v3.0 Backend Server")
    print("=" * 70)
    print(f"API 문서: http://localhost:8000/docs")
    print(f"프론트엔드: http://localhost:3000")
    print("=" * 70)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
