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