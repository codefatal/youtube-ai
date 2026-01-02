"""
Database ORM Models
Account, AccountSettings, JobHistory 테이블 정의
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime, Enum, ForeignKey, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.database import Base


class ChannelType(str, enum.Enum):
    """채널 성격"""
    HUMOR = "humor"         # 유머/예능
    TREND = "trend"         # 트렌드/핫이슈
    INFO = "info"           # 정보/교육
    REVIEW = "review"       # 리뷰/분석
    NEWS = "news"           # 뉴스/시사
    DAILY = "daily"         # 일상/브이로그


class JobStatus(str, enum.Enum):
    """작업 상태"""
    PENDING = "pending"
    PLANNING = "planning"
    COLLECTING_ASSETS = "collecting_assets"
    EDITING = "editing"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


class DraftStatus(str, enum.Enum):
    """Phase 3: Draft 상태"""
    EDITING = "editing"              # 편집 중 (사용자 수정 가능)
    ASSETS_READY = "assets_ready"    # 에셋 수집 완료
    CONVERTING = "converting"        # 렌더링 중 (Draft → Job 변환)
    FINALIZED = "finalized"          # 최종 완료 (Job으로 변환됨)


class Account(Base):
    """
    유튜브 계정 테이블
    여러 채널을 관리할 수 있도록 설계
    """
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String(100), unique=True, nullable=False, index=True)
    channel_id = Column(String(50), unique=True, nullable=True)  # YouTube Channel ID

    # 인증 정보
    credentials_path = Column(String(255), nullable=True)  # client_secrets.json 경로
    token_path = Column(String(255), nullable=True)        # OAuth token 경로

    # 채널 설정
    channel_type = Column(Enum(ChannelType), default=ChannelType.INFO)
    default_prompt_style = Column(String(50), default="정보성")  # AI 프롬프트 스타일

    # 스케줄링
    upload_schedule = Column(String(100), nullable=True)  # Cron 포맷 (예: "0 9 * * *")
    is_active = Column(Boolean, default=True)             # 스케줄 활성화 여부

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 (1:1)
    settings = relationship("AccountSettings", back_populates="account", uselist=False, cascade="all, delete-orphan")

    # 관계 (1:N)
    jobs = relationship("JobHistory", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.channel_name}', type={self.channel_type})>"


class AccountSettings(Base):
    """
    계정별 설정 테이블 (1:1 관계)
    TTS, 영상 스타일 등 계정마다 다른 설정
    """
    __tablename__ = "account_settings"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), unique=True, nullable=False)

    # TTS 설정
    tts_provider = Column(String(50), default="gtts")  # gtts, elevenlabs, google_cloud
    tts_voice_id = Column(String(100), nullable=True)  # ElevenLabs Voice ID
    tts_stability = Column(Float, default=0.5)         # ElevenLabs: 0.0 ~ 1.0
    tts_similarity_boost = Column(Float, default=0.75) # ElevenLabs: 0.0 ~ 1.0
    tts_style = Column(Float, default=0.0)             # ElevenLabs: 0.0 ~ 1.0

    # 영상 설정
    default_format = Column(String(20), default="shorts")  # shorts, landscape, square
    default_duration = Column(Integer, default=60)         # 기본 영상 길이 (초)
    default_template = Column(String(50), nullable=True)   # 템플릿 이름 (Phase 2)

    # BGM 설정 (Phase 2)
    bgm_enabled = Column(Boolean, default=False)
    bgm_volume = Column(Float, default=0.3)  # 0.0 ~ 1.0

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    account = relationship("Account", back_populates="settings")

    def __repr__(self):
        return f"<AccountSettings(account_id={self.account_id}, tts={self.tts_provider})>"


class JobHistory(Base):
    """
    작업 이력 테이블
    기존 job_history.json을 대체
    """
    __tablename__ = "job_history"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, nullable=False, index=True)  # job_20251226_123456
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # NULL = 수동 실행

    # 작업 정보
    topic = Column(String(200), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)

    # 영상 정보
    format = Column(String(20), nullable=False)  # shorts, landscape, square
    duration = Column(Integer, nullable=False)   # 목표 길이 (초)

    # 결과
    output_video_path = Column(String(500), nullable=True)
    youtube_url = Column(String(200), nullable=True)
    youtube_video_id = Column(String(50), nullable=True)

    # 에러 정보
    error_message = Column(Text, nullable=True)

    # 메타데이터
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # 관계
    account = relationship("Account", back_populates="jobs")

    def __repr__(self):
        return f"<JobHistory(id='{self.job_id}', status={self.status})>"


# ============================================================
# Phase 3: Draft Models (Human-in-the-Loop)
# ============================================================

class Draft(Base):
    """
    Phase 3: 영상 Draft 테이블

    사용자가 스크립트와 에셋을 검토/수정한 후 렌더링할 수 있도록
    중간 단계의 데이터를 저장합니다.

    Workflow:
    1. POST /api/draft/create → Draft 생성 (스크립트 + 에셋 수집)
    2. GET /api/draft/{id} → Draft 조회 (프론트엔드에서 검토)
    3. POST /api/draft/{id}/update-segment → 세그먼트 수정
    4. POST /api/draft/{id}/finalize → 최종 렌더링 (JobHistory 생성)
    """
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(String(50), unique=True, nullable=False, index=True)  # draft_20260102_123456
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # NULL = 수동 실행

    # 기본 정보
    topic = Column(String(200), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array string

    # 영상 설정
    format = Column(String(20), nullable=False)  # shorts, landscape, square
    target_duration = Column(Integer, nullable=False)  # 목표 길이 (초)

    # ContentPlan JSON (전체 구조 저장)
    content_plan_json = Column(Text, nullable=True)  # JSON string

    # Status
    status = Column(Enum(DraftStatus), default=DraftStatus.EDITING)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    account = relationship("Account")
    segments = relationship("DraftSegment", back_populates="draft", cascade="all, delete-orphan", order_by="DraftSegment.segment_index")

    def __repr__(self):
        return f"<Draft(id='{self.draft_id}', topic='{self.topic}', status={self.status})>"


class DraftSegment(Base):
    """
    Phase 3: Draft 세그먼트 테이블

    각 Draft의 세그먼트를 정규화하여 저장합니다.
    사용자가 개별 세그먼트의 텍스트, 이미지, TTS를 수정할 수 있습니다.
    """
    __tablename__ = "draft_segments"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(String(50), ForeignKey("drafts.draft_id"), nullable=False, index=True)
    segment_index = Column(Integer, nullable=False)  # 순서 (0부터 시작)

    # Segment 데이터
    text = Column(Text, nullable=False)  # 대사 텍스트
    keyword = Column(String(200), nullable=True)  # 하위 호환성
    image_search_query = Column(String(500), nullable=True)  # Phase 2: 구체적 시각 묘사
    duration = Column(Float, nullable=True)  # 예상 길이 (초)

    # Assets (수집된 에셋 정보)
    video_url = Column(String(500), nullable=True)  # Pexels/Pixabay URL
    video_local_path = Column(String(500), nullable=True)  # 다운로드된 로컬 경로
    video_provider = Column(String(50), nullable=True)  # pexels, pixabay
    video_id = Column(String(100), nullable=True)  # 영상 ID

    tts_local_path = Column(String(500), nullable=True)  # TTS 오디오 경로
    tts_duration = Column(Float, nullable=True)  # 실제 TTS 길이 (초)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    draft = relationship("Draft", back_populates="segments")

    def __repr__(self):
        return f"<DraftSegment(draft_id='{self.draft_id}', index={self.segment_index}, text='{self.text[:30]}...')>"