"""
Pydantic Schemas for API Request/Response
FastAPI 데이터 검증용
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from backend.models import ChannelType, JobStatus


# ============================================================================
# Account Schemas
# ============================================================================

class AccountBase(BaseModel):
    """Account 기본 스키마"""
    channel_name: str = Field(..., min_length=1, max_length=100)
    channel_type: ChannelType = ChannelType.INFO
    default_prompt_style: str = "정보성"
    upload_schedule: Optional[str] = None
    is_active: bool = True


class AccountCreate(AccountBase):
    """Account 생성 요청"""
    credentials_path: Optional[str] = None


class AccountUpdate(BaseModel):
    """Account 수정 요청 (부분 업데이트)"""
    channel_name: Optional[str] = None
    channel_type: Optional[ChannelType] = None
    default_prompt_style: Optional[str] = None
    upload_schedule: Optional[str] = None
    is_active: Optional[bool] = None


class AccountResponse(AccountBase):
    """Account 응답"""
    id: int
    channel_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2


# ============================================================================
# AccountSettings Schemas
# ============================================================================

class AccountSettingsBase(BaseModel):
    """AccountSettings 기본 스키마"""
    tts_provider: str = "gtts"
    tts_voice_id: Optional[str] = None
    tts_stability: float = Field(default=0.5, ge=0.0, le=1.0)
    tts_similarity_boost: float = Field(default=0.75, ge=0.0, le=1.0)
    tts_style: float = Field(default=0.0, ge=0.0, le=1.0)
    default_format: str = "shorts"
    default_duration: int = Field(default=60, ge=10, le=600)
    bgm_enabled: bool = False
    bgm_volume: float = Field(default=0.3, ge=0.0, le=1.0)


class AccountSettingsUpdate(AccountSettingsBase):
    """AccountSettings 수정 요청"""
    pass


class AccountSettingsResponse(AccountSettingsBase):
    """AccountSettings 응답"""
    id: int
    account_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# JobHistory Schemas
# ============================================================================

class JobHistoryResponse(BaseModel):
    """JobHistory 응답"""
    id: int
    job_id: str
    account_id: Optional[int] = None
    topic: str
    status: JobStatus
    format: str
    duration: int
    output_video_path: Optional[str] = None
    youtube_url: Optional[str] = None
    youtube_video_id: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Combined Responses
# ============================================================================

class AccountDetailResponse(AccountResponse):
    """Account 상세 정보 (설정 포함)"""
    settings: Optional[AccountSettingsResponse] = None
    jobs: List[JobHistoryResponse] = []
