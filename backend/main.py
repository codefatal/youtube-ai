"""
FastAPI Backend Server for YouTube AI v3.0
AI-Powered Original Content Creation System
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# 로컬 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.orchestrator import ContentOrchestrator
from core.planner import ContentPlanner
from core.asset_manager import AssetManager
from core.editor import Editor
from core.uploader import Uploader
from core.models import (
    SystemConfig,
    VideoFormat,
    AIProvider,
    TTSProvider,
    ContentStatus,
    StockProvider
)

app = FastAPI(
    title="YouTube AI v3.0 API",
    description="AI-Powered Original Content Creation System",
    version="3.0.0"
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
    ai_provider: Optional[str] = None  # gemini, claude, openai
    tts_provider: Optional[str] = None  # gtts, elevenlabs, google_cloud


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

        topics = await planner.generate_topic_ideas(
            count=request.count,
            trending=request.trending
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

        plan = await planner.generate_content_plan(
            topic=request.topic,
            format=video_format,
            target_duration=request.duration,
            style=request.style
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
            planner = Planner()
            topics = await planner.generate_topic_ideas(count=1, trending=True)
            topic = topics[0] if topics else "AI 기술 소개"

        # 영상 생성 (비동기)
        job = await asyncio.to_thread(
            orchestrator.create_content,
            topic=topic,
            video_format=video_format,
            target_duration=request.duration,
            upload=request.upload
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
        orchestrator = get_orchestrator()

        # 작업 히스토리에서 조회
        job = orchestrator.history.get_job(request.job_id)

        if not job:
            raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")

        return {
            "success": True,
            "data": {
                "job_id": job.job_id,
                "status": job.status.value,
                "topic": job.metadata.get("topic", ""),
                "format": job.metadata.get("format", ""),
                "output_video_path": job.output_video_path,
                "youtube_url": job.youtube_url,
                "error_log": job.error_log,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")


@app.get("/api/jobs/recent")
async def get_recent_jobs(limit: int = 10):
    """최근 작업 목록 조회"""
    try:
        orchestrator = get_orchestrator()

        recent_jobs = orchestrator.get_recent_jobs(limit=limit)

        return {
            "success": True,
            "data": {
                "jobs": [
                    {
                        "job_id": job.job_id,
                        "status": job.status.value,
                        "topic": job.metadata.get("topic", ""),
                        "format": job.metadata.get("format", ""),
                        "created_at": job.created_at.isoformat() if job.created_at else None,
                        "completed_at": job.completed_at.isoformat() if job.completed_at else None
                    }
                    for job in recent_jobs
                ],
                "count": len(recent_jobs)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업 목록 조회 실패: {str(e)}")


@app.get("/api/stats")
async def get_statistics():
    """통계 조회"""
    try:
        orchestrator = get_orchestrator()

        stats = orchestrator.get_statistics()

        return {
            "success": True,
            "data": stats
        }
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
                "stock_provider": config.stock_provider.value if hasattr(config, 'stock_provider') else "pexels",
                "default_format": config.default_format.value,
                "default_duration": config.default_duration,
                "auto_upload": config.auto_upload
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"설정 조회 실패: {str(e)}")


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
