"""
Preview API Router (Phase 3)
영상 프리뷰 생성 및 조정 API
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import json
from pathlib import Path

router = APIRouter(prefix="/api/preview", tags=["Preview"])

# 프리뷰 저장 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent.parent
PREVIEW_DIR = PROJECT_ROOT / "output" / "preview"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

# 프리뷰 작업 상태 저장 (메모리)
preview_jobs: Dict[str, Dict[str, Any]] = {}


# ==================== Request/Response 모델 ====================

class PreviewGenerateRequest(BaseModel):
    """프리뷰 생성 요청"""
    topic: str = Field(..., description="영상 주제")
    format: str = Field(default="shorts", description="영상 포맷 (shorts, landscape)")
    duration: int = Field(default=60, ge=15, le=180, description="목표 길이 (초)")
    template_name: str = Field(default="basic", description="템플릿 이름")
    account_id: Optional[int] = Field(None, description="계정 ID")
    tts_settings: Optional[Dict[str, Any]] = Field(None, description="TTS 설정 오버라이드")
    low_resolution: bool = Field(default=True, description="저해상도 프리뷰 (540p)")


class PreviewAdjustRequest(BaseModel):
    """프리뷰 조정 요청"""
    job_id: str = Field(..., description="작업 ID")
    adjustments: Dict[str, Any] = Field(..., description="조정 내용")


class SegmentAdjustment(BaseModel):
    """세그먼트 조정"""
    segment_index: int = Field(..., description="세그먼트 인덱스")
    new_keyword: Optional[str] = Field(None, description="새 영상 검색 키워드")
    timing_offset: Optional[float] = Field(None, description="타이밍 조정 (초)")
    subtitle_text: Optional[str] = Field(None, description="수정된 자막 텍스트")


class PreviewFinalizeRequest(BaseModel):
    """최종 렌더링 요청"""
    job_id: str = Field(..., description="작업 ID")
    upload: bool = Field(default=False, description="업로드 여부")


class PreviewStatus(BaseModel):
    """프리뷰 상태"""
    job_id: str
    status: str  # pending, generating, completed, failed
    progress: int = 0  # 0-100
    preview_path: Optional[str] = None
    segments: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ==================== API 엔드포인트 ====================

@router.post("/generate", response_model=Dict[str, Any])
async def generate_preview(request: PreviewGenerateRequest, background_tasks: BackgroundTasks):
    """
    프리뷰 영상 생성 시작

    저해상도(540p) 또는 짧은 버전의 프리뷰를 생성합니다.
    백그라운드에서 비동기로 처리됩니다.
    """
    import uuid

    # 작업 ID 생성
    job_id = f"preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

    # 초기 상태 저장
    preview_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "request": request.model_dump(),
        "preview_path": None,
        "segments": None,
        "metadata": None,
        "error": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    # 백그라운드 작업 시작
    background_tasks.add_task(_generate_preview_task, job_id, request)

    return {
        "success": True,
        "job_id": job_id,
        "message": "프리뷰 생성이 시작되었습니다.",
        "status_url": f"/api/preview/{job_id}"
    }


@router.get("/{job_id}", response_model=PreviewStatus)
async def get_preview_status(job_id: str):
    """
    프리뷰 작업 상태 조회
    """
    if job_id not in preview_jobs:
        raise HTTPException(status_code=404, detail=f"작업을 찾을 수 없습니다: {job_id}")

    job = preview_jobs[job_id]
    return PreviewStatus(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        preview_path=job["preview_path"],
        segments=job["segments"],
        metadata=job["metadata"],
        error=job["error"],
        created_at=job["created_at"],
        updated_at=job["updated_at"]
    )


@router.get("/{job_id}/video")
async def get_preview_video(job_id: str):
    """
    프리뷰 영상 파일 다운로드
    """
    if job_id not in preview_jobs:
        raise HTTPException(status_code=404, detail=f"작업을 찾을 수 없습니다: {job_id}")

    job = preview_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"프리뷰가 아직 완료되지 않았습니다. 상태: {job['status']}")

    if not job["preview_path"] or not os.path.exists(job["preview_path"]):
        raise HTTPException(status_code=404, detail="프리뷰 파일을 찾을 수 없습니다.")

    return FileResponse(
        job["preview_path"],
        media_type="video/mp4",
        filename=f"preview_{job_id}.mp4"
    )


@router.post("/adjust", response_model=Dict[str, Any])
async def adjust_preview(request: PreviewAdjustRequest, background_tasks: BackgroundTasks):
    """
    프리뷰 파라미터 조정 및 재생성

    세그먼트별 타이밍, 영상 클립, 자막 등을 조정합니다.
    """
    if request.job_id not in preview_jobs:
        raise HTTPException(status_code=404, detail=f"작업을 찾을 수 없습니다: {request.job_id}")

    job = preview_jobs[request.job_id]

    if job["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="프리뷰가 완료된 후에만 조정할 수 있습니다.")

    # 상태 업데이트
    job["status"] = "adjusting"
    job["progress"] = 0
    job["updated_at"] = datetime.now()
    job["adjustments"] = request.adjustments

    # 백그라운드에서 조정된 프리뷰 재생성
    background_tasks.add_task(_adjust_preview_task, request.job_id, request.adjustments)

    return {
        "success": True,
        "job_id": request.job_id,
        "message": "조정이 적용되고 있습니다."
    }


@router.post("/finalize", response_model=Dict[str, Any])
async def finalize_preview(request: PreviewFinalizeRequest, background_tasks: BackgroundTasks):
    """
    최종 렌더링 (고해상도)

    프리뷰 조정이 완료되면 최종 고해상도 버전을 렌더링합니다.
    """
    if request.job_id not in preview_jobs:
        raise HTTPException(status_code=404, detail=f"작업을 찾을 수 없습니다: {request.job_id}")

    job = preview_jobs[request.job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="프리뷰가 완료된 후에만 최종 렌더링할 수 있습니다.")

    # 상태 업데이트
    job["status"] = "finalizing"
    job["progress"] = 0
    job["updated_at"] = datetime.now()

    # 백그라운드에서 최종 렌더링
    background_tasks.add_task(_finalize_preview_task, request.job_id, request.upload)

    return {
        "success": True,
        "job_id": request.job_id,
        "message": "최종 렌더링이 시작되었습니다."
    }


@router.get("/list/recent", response_model=Dict[str, Any])
async def list_recent_previews(limit: int = 10):
    """
    최근 프리뷰 목록 조회
    """
    # 최신순 정렬
    sorted_jobs = sorted(
        preview_jobs.values(),
        key=lambda x: x["created_at"],
        reverse=True
    )[:limit]

    return {
        "success": True,
        "count": len(sorted_jobs),
        "previews": [
            {
                "job_id": j["job_id"],
                "status": j["status"],
                "progress": j["progress"],
                "created_at": j["created_at"].isoformat(),
                "topic": j["request"].get("topic", "Unknown") if j["request"] else "Unknown"
            }
            for j in sorted_jobs
        ]
    }


# ==================== 백그라운드 작업 함수 ====================

async def _generate_preview_task(job_id: str, request: PreviewGenerateRequest):
    """
    프리뷰 생성 백그라운드 작업
    """
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))

    try:
        preview_jobs[job_id]["status"] = "generating"
        preview_jobs[job_id]["progress"] = 10
        preview_jobs[job_id]["updated_at"] = datetime.now()

        from core.orchestrator import ContentOrchestrator
        from core.models import VideoFormat

        # Orchestrator 생성
        orchestrator = ContentOrchestrator()

        # 프리뷰용 설정
        video_format = VideoFormat.SHORTS if request.format == "shorts" else VideoFormat.LANDSCAPE

        preview_jobs[job_id]["progress"] = 20

        # 1. 콘텐츠 기획
        print(f"[Preview {job_id}] 콘텐츠 기획 중...")
        content_plan = orchestrator.planner.create_script(
            topic=request.topic,
            video_format=video_format,
            target_duration=request.duration
        )

        if not content_plan:
            raise Exception("콘텐츠 기획 실패")

        preview_jobs[job_id]["progress"] = 40

        # 세그먼트 정보 저장
        preview_jobs[job_id]["segments"] = [
            {
                "index": i,
                "text": seg.text,
                "keyword": seg.keyword,
                "duration": seg.duration
            }
            for i, seg in enumerate(content_plan.segments)
        ]

        # 2. 에셋 수집
        print(f"[Preview {job_id}] 에셋 수집 중...")
        asset_bundle = orchestrator.asset_manager.collect_assets(
            content_plan,
            account_id=request.account_id,
            tts_settings_override=request.tts_settings
        )

        if not asset_bundle:
            raise Exception("에셋 수집 실패")

        preview_jobs[job_id]["progress"] = 60

        # 3. 영상 편집 (저해상도)
        print(f"[Preview {job_id}] 프리뷰 렌더링 중...")
        from core.editor import VideoEditor
        from core.models import EditConfig

        # 저해상도 설정
        if request.low_resolution:
            preview_config = EditConfig(
                resolution=(540, 960),  # 절반 해상도
                fps=24  # 낮은 FPS
            )
        else:
            preview_config = EditConfig()

        editor = VideoEditor(config=preview_config)

        preview_filename = f"preview_{job_id}.mp4"
        output_path = editor.create_video(
            content_plan,
            asset_bundle,
            output_filename=preview_filename,
            template_name=request.template_name
        )

        if not output_path:
            raise Exception("프리뷰 렌더링 실패")

        preview_jobs[job_id]["progress"] = 100
        preview_jobs[job_id]["status"] = "completed"
        preview_jobs[job_id]["preview_path"] = output_path
        preview_jobs[job_id]["metadata"] = {
            "title": content_plan.title,
            "description": content_plan.description,
            "tags": content_plan.tags,
            "duration": content_plan.target_duration,
            "segment_count": len(content_plan.segments),
            "resolution": "540x960" if request.low_resolution else "1080x1920"
        }
        preview_jobs[job_id]["updated_at"] = datetime.now()

        print(f"[Preview {job_id}] 프리뷰 생성 완료: {output_path}")

    except Exception as e:
        import traceback
        preview_jobs[job_id]["status"] = "failed"
        preview_jobs[job_id]["error"] = str(e)
        preview_jobs[job_id]["updated_at"] = datetime.now()
        print(f"[Preview {job_id}] 오류: {e}")
        traceback.print_exc()


async def _adjust_preview_task(job_id: str, adjustments: Dict[str, Any]):
    """
    프리뷰 조정 백그라운드 작업
    """
    try:
        preview_jobs[job_id]["status"] = "adjusting"
        preview_jobs[job_id]["progress"] = 50
        preview_jobs[job_id]["updated_at"] = datetime.now()

        # TODO: 조정 로직 구현
        # - 세그먼트별 타이밍 조정
        # - 영상 클립 교체
        # - 자막 수정
        # 현재는 기본 구현만

        import asyncio
        await asyncio.sleep(2)  # 시뮬레이션

        preview_jobs[job_id]["progress"] = 100
        preview_jobs[job_id]["status"] = "completed"
        preview_jobs[job_id]["updated_at"] = datetime.now()

        print(f"[Preview {job_id}] 조정 완료")

    except Exception as e:
        preview_jobs[job_id]["status"] = "failed"
        preview_jobs[job_id]["error"] = str(e)
        preview_jobs[job_id]["updated_at"] = datetime.now()


async def _finalize_preview_task(job_id: str, upload: bool):
    """
    최종 렌더링 백그라운드 작업
    """
    try:
        preview_jobs[job_id]["status"] = "finalizing"
        preview_jobs[job_id]["progress"] = 50
        preview_jobs[job_id]["updated_at"] = datetime.now()

        # TODO: 고해상도 렌더링 구현
        # - 원본 설정으로 재렌더링
        # - 업로드 옵션 처리

        import asyncio
        await asyncio.sleep(3)  # 시뮬레이션

        preview_jobs[job_id]["progress"] = 100
        preview_jobs[job_id]["status"] = "finalized"
        preview_jobs[job_id]["updated_at"] = datetime.now()

        print(f"[Preview {job_id}] 최종 렌더링 완료")

    except Exception as e:
        preview_jobs[job_id]["status"] = "failed"
        preview_jobs[job_id]["error"] = str(e)
        preview_jobs[job_id]["updated_at"] = datetime.now()
