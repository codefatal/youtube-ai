"""
Phase 3: Draft Management API Router
Draft 생성, 조회, 수정, 최종 렌더링 (Human-in-the-Loop)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import json
import sys
import os

# 로컬 모듈 import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.database import get_db
from backend.models import Draft, DraftSegment, DraftStatus, Account
from core.planner import ContentPlanner
from core.asset_manager import AssetManager
from core.orchestrator import ContentOrchestrator
from core.models import VideoFormat, ContentPlan, ScriptSegment

router = APIRouter(prefix="/api/draft", tags=["Drafts"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateDraftRequest(BaseModel):
    """Draft 생성 요청"""
    topic: Optional[str] = None  # None이면 AI 자동 생성
    format: str = "shorts"  # shorts, landscape, square
    duration: int = 60
    account_id: Optional[int] = None
    style: str = "정보성"  # AI 스타일
    collect_assets: bool = True  # True면 에셋도 수집


class UpdateSegmentRequest(BaseModel):
    """세그먼트 업데이트 요청"""
    text: Optional[str] = None
    keyword: Optional[str] = None
    image_search_query: Optional[str] = None
    duration: Optional[float] = None


class FinalizeDraftRequest(BaseModel):
    """Draft 최종 렌더링 요청"""
    upload: bool = False
    template: Optional[str] = None
    bgm_settings: Optional[Dict[str, Any]] = None


class SegmentResponse(BaseModel):
    """세그먼트 응답"""
    segment_index: int
    text: str
    keyword: Optional[str]
    image_search_query: Optional[str]
    duration: Optional[float]

    # Assets
    video_url: Optional[str]
    video_local_path: Optional[str]
    video_provider: Optional[str]
    tts_local_path: Optional[str]
    tts_duration: Optional[float]

    class Config:
        from_attributes = True


class DraftResponse(BaseModel):
    """Draft 응답"""
    draft_id: str
    topic: str
    title: str
    description: Optional[str]
    tags: Optional[List[str]]
    format: str
    target_duration: int
    status: str
    segments: List[SegmentResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Helper Functions
# ============================================================================

def generate_draft_id() -> str:
    """Draft ID 생성 (draft_YYYYMMDD_HHMMSS)"""
    from datetime import datetime
    return f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def parse_tags(tags_str: Optional[str]) -> List[str]:
    """JSON 문자열을 리스트로 파싱"""
    if not tags_str:
        return []
    try:
        return json.loads(tags_str)
    except:
        return []


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/create", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(
    request: CreateDraftRequest,
    db: Session = Depends(get_db)
):
    """
    Phase 3: Draft 생성 API

    1. AI로 스크립트 생성 (Planner)
    2. (선택) 에셋 수집 (AssetManager)
    3. Draft + DraftSegment DB에 저장
    4. 프론트엔드에서 검토/수정 가능

    Args:
        request: CreateDraftRequest
            - topic: 주제 (None이면 AI 자동 생성)
            - format: shorts/landscape/square
            - duration: 목표 길이 (초)
            - collect_assets: True면 영상+TTS도 수집

    Returns:
        DraftResponse: 생성된 Draft 정보 (segments 포함)
    """
    try:
        print(f"\n[Draft API] ========== Draft 생성 시작 ==========")
        print(f"[Draft API] 주제: {request.topic or 'AI 자동 생성'}")
        print(f"[Draft API] 포맷: {request.format}, 길이: {request.duration}초")
        print(f"[Draft API] 에셋 수집: {request.collect_assets}")

        # 1. Planner로 스크립트 생성
        planner = ContentPlanner()

        topic = request.topic
        if not topic:
            # AI 자동 주제 생성
            topics = planner.generate_topic_ideas(category="트렌드", count=1)
            topic = topics[0] if topics else "AI 기술 소개"
            print(f"[Draft API] AI 생성 주제: {topic}")

        video_format = VideoFormat[request.format.upper()]
        content_plan = planner.create_script(
            topic=topic,
            format=video_format,
            target_duration=request.duration,
            tone=request.style
        )

        print(f"[Draft API] 스크립트 생성 완료: {len(content_plan.segments)}개 세그먼트")

        # 2. (선택) 에셋 수집
        asset_manager = None
        if request.collect_assets:
            print(f"[Draft API] 에셋 수집 시작...")
            asset_manager = AssetManager(bgm_enabled=False)  # Draft에서는 BGM 수집 안 함
            asset_bundle = asset_manager.collect_assets(content_plan)
            print(f"[Draft API] 에셋 수집 완료: 영상 {len(asset_bundle.videos)}개, TTS 생성됨")

        # 3. Draft DB에 저장
        draft_id = generate_draft_id()
        draft = Draft(
            draft_id=draft_id,
            account_id=request.account_id,
            topic=topic,
            title=content_plan.title,
            description=content_plan.description,
            tags=json.dumps(content_plan.tags, ensure_ascii=False),
            format=request.format,
            target_duration=request.duration,
            content_plan_json=content_plan.model_dump_json(),
            status=DraftStatus.ASSETS_READY if request.collect_assets else DraftStatus.EDITING
        )
        db.add(draft)
        db.flush()  # draft_id 생성

        # 4. DraftSegment 생성
        for i, segment in enumerate(content_plan.segments):
            # 에셋 정보 가져오기
            video_asset = asset_bundle.videos[i] if (asset_manager and i < len(asset_bundle.videos)) else None

            # Phase 3: segment_timings에서 TTS 경로 가져오기
            segment_timing = None
            if asset_manager and asset_bundle.segment_timings and i < len(asset_bundle.segment_timings):
                segment_timing = asset_bundle.segment_timings[i]

            draft_segment = DraftSegment(
                draft_id=draft_id,
                segment_index=i,
                text=segment.text,
                keyword=segment.keyword,
                image_search_query=segment.image_search_query,
                duration=segment.duration,

                # Assets (에셋 수집했을 경우)
                video_url=video_asset.url if video_asset else None,
                video_local_path=video_asset.local_path if video_asset else None,
                video_provider=video_asset.provider if video_asset else None,
                video_id=video_asset.id if video_asset else None,

                # Phase 3: segment_timings에서 TTS 경로 및 길이 가져오기
                tts_local_path=segment_timing.tts_local_path if segment_timing else None,
                tts_duration=segment_timing.tts_duration if segment_timing else segment.duration
            )
            db.add(draft_segment)

        db.commit()
        db.refresh(draft)

        print(f"[Draft API] Draft 저장 완료: {draft_id}")
        print(f"[Draft API] ==========================================\n")

        # 5. 응답 생성
        return _draft_to_response(draft)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Draft 생성 실패: {str(e)}"
        )


@router.get("/{draft_id}", response_model=DraftResponse)
def get_draft(
    draft_id: str,
    db: Session = Depends(get_db)
):
    """
    Phase 3: Draft 조회 API

    프론트엔드에서 Draft를 조회하여 세그먼트별 정보를 확인합니다.
    사용자는 이 정보를 보고 수정할 수 있습니다.

    Returns:
        - draft_id, topic, title, description, tags
        - segments: 세그먼트별 텍스트, 이미지 URL, TTS 경로 등
    """
    draft = db.query(Draft).filter(Draft.draft_id == draft_id).first()
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft '{draft_id}'를 찾을 수 없습니다."
        )

    return _draft_to_response(draft)


@router.post("/{draft_id}/update-segment/{segment_index}")
def update_segment(
    draft_id: str,
    segment_index: int,
    request: UpdateSegmentRequest,
    db: Session = Depends(get_db)
):
    """
    Phase 3: 세그먼트 업데이트 API

    사용자가 특정 세그먼트의 텍스트, 이미지 검색어 등을 수정합니다.

    Args:
        draft_id: Draft ID
        segment_index: 세그먼트 인덱스 (0부터 시작)
        request: 업데이트할 필드들 (text, keyword, image_search_query, duration)

    Returns:
        업데이트된 세그먼트 정보
    """
    try:
        # Draft 존재 확인
        draft = db.query(Draft).filter(Draft.draft_id == draft_id).first()
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Draft '{draft_id}'를 찾을 수 없습니다."
            )

        # Segment 조회
        segment = db.query(DraftSegment).filter(
            DraftSegment.draft_id == draft_id,
            DraftSegment.segment_index == segment_index
        ).first()

        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"세그먼트 {segment_index}를 찾을 수 없습니다."
            )

        # 업데이트
        if request.text is not None:
            segment.text = request.text
        if request.keyword is not None:
            segment.keyword = request.keyword
        if request.image_search_query is not None:
            segment.image_search_query = request.image_search_query
        if request.duration is not None:
            segment.duration = request.duration

        segment.updated_at = datetime.utcnow()
        draft.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(segment)

        print(f"[Draft API] 세그먼트 {segment_index} 업데이트 완료")

        return {
            "success": True,
            "data": SegmentResponse.model_validate(segment)
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세그먼트 업데이트 실패: {str(e)}"
        )


@router.post("/{draft_id}/finalize")
async def finalize_draft(
    draft_id: str,
    request: FinalizeDraftRequest,
    db: Session = Depends(get_db)
):
    """
    Phase 3: Draft 최종 렌더링 API

    사용자가 수정을 완료한 Draft를 최종 렌더링하여 JobHistory로 변환합니다.

    Workflow:
    1. Draft와 DraftSegment 조회
    2. ContentPlan 재구성
    3. Orchestrator로 영상 렌더링
    4. JobHistory에 기록
    5. Draft 상태를 FINALIZED로 변경

    Args:
        draft_id: Draft ID
        request: 렌더링 옵션 (upload, template, bgm_settings)

    Returns:
        job_id, output_video_path, youtube_url (업로드 시)
    """
    try:
        print(f"\n[Draft API] ========== Draft 최종 렌더링 시작 ==========")
        print(f"[Draft API] Draft ID: {draft_id}")

        # 1. Draft 조회
        draft = db.query(Draft).filter(Draft.draft_id == draft_id).first()
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Draft '{draft_id}'를 찾을 수 없습니다."
            )

        if draft.status == DraftStatus.FINALIZED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 렌더링된 Draft입니다."
            )

        # 2. DraftSegment 조회 및 ContentPlan 재구성
        segments = db.query(DraftSegment).filter(
            DraftSegment.draft_id == draft_id
        ).order_by(DraftSegment.segment_index).all()

        if not segments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="세그먼트가 없습니다."
            )

        # ContentPlan 재구성
        script_segments = [
            ScriptSegment(
                text=seg.text,
                keyword=seg.keyword or "nature landscape",
                image_search_query=seg.image_search_query,
                duration=seg.duration
            )
            for seg in segments
        ]

        content_plan = ContentPlan(
            title=draft.title,
            description=draft.description or "",
            tags=parse_tags(draft.tags),
            format=VideoFormat[draft.format.upper()],
            target_duration=draft.target_duration,
            segments=script_segments
        )

        print(f"[Draft API] ContentPlan 재구성 완료: {len(script_segments)}개 세그먼트")

        # 3. Orchestrator로 렌더링
        draft.status = DraftStatus.CONVERTING
        db.commit()

        orchestrator = ContentOrchestrator()

        import asyncio
        job = await asyncio.to_thread(
            orchestrator.create_content_from_plan,
            content_plan=content_plan,
            upload=request.upload,
            template=request.template
        )

        # 4. Draft 상태 업데이트
        draft.status = DraftStatus.FINALIZED
        draft.updated_at = datetime.utcnow()
        db.commit()

        print(f"[Draft API] 렌더링 완료: {job.job_id}")
        print(f"[Draft API] ==========================================\n")

        return {
            "success": True,
            "data": {
                "draft_id": draft_id,
                "job_id": job.job_id,
                "status": job.status.value,
                "output_video_path": job.output_video_path,
                "youtube_url": getattr(job.upload_result, 'url', None) if request.upload else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()

        # 실패 시 상태 복구
        draft.status = DraftStatus.ASSETS_READY
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"렌더링 실패: {str(e)}"
        )


@router.get("/", response_model=List[DraftResponse])
def list_drafts(
    skip: int = 0,
    limit: int = 20,
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Phase 3: Draft 목록 조회 API

    모든 Draft를 조회합니다. 계정별, 상태별 필터링 가능.

    Args:
        skip: 페이징 오프셋
        limit: 페이징 리미트
        account_id: 계정 ID 필터
        status: 상태 필터 (editing, assets_ready, converting, finalized)
    """
    query = db.query(Draft)

    if account_id is not None:
        query = query.filter(Draft.account_id == account_id)
    if status is not None:
        query = query.filter(Draft.status == DraftStatus[status.upper()])

    drafts = query.order_by(Draft.created_at.desc()).offset(skip).limit(limit).all()

    return [_draft_to_response(draft) for draft in drafts]


@router.delete("/{draft_id}")
def delete_draft(
    draft_id: str,
    db: Session = Depends(get_db)
):
    """
    Phase 3: Draft 삭제 API

    Draft와 관련된 모든 DraftSegment를 삭제합니다.
    """
    draft = db.query(Draft).filter(Draft.draft_id == draft_id).first()
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft '{draft_id}'를 찾을 수 없습니다."
        )

    db.delete(draft)  # cascade로 DraftSegment도 자동 삭제
    db.commit()

    return {
        "success": True,
        "message": f"Draft '{draft_id}'가 삭제되었습니다."
    }


# ============================================================================
# Helper Functions (Private)
# ============================================================================

def _draft_to_response(draft: Draft) -> DraftResponse:
    """Draft ORM을 DraftResponse로 변환"""
    return DraftResponse(
        draft_id=draft.draft_id,
        topic=draft.topic,
        title=draft.title,
        description=draft.description,
        tags=parse_tags(draft.tags),
        format=draft.format,
        target_duration=draft.target_duration,
        status=draft.status.value,
        segments=[
            SegmentResponse(
                segment_index=seg.segment_index,
                text=seg.text,
                keyword=seg.keyword,
                image_search_query=seg.image_search_query,
                duration=seg.duration,
                video_url=seg.video_url,
                video_local_path=seg.video_local_path,
                video_provider=seg.video_provider,
                tts_local_path=seg.tts_local_path,
                tts_duration=seg.tts_duration
            )
            for seg in sorted(draft.segments, key=lambda s: s.segment_index)
        ],
        created_at=draft.created_at,
        updated_at=draft.updated_at
    )
