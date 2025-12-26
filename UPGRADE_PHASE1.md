# Phase 1: 백엔드 구조 개편 및 DB 도입

**작업 기간**: 1주 (2025-12-26 ~ 2026-01-02)
**담당 모듈**: `backend/`, `config/`, `data/`
**우선순위**: ⭐⭐⭐⭐⭐ (최고)
**난이도**: 🔥🔥🔥 (중상)

---

## 📋 개요

현재 `job_history.json` 파일 기반으로 작동하는 시스템을 **SQLite + SQLAlchemy ORM** 기반의 관계형 데이터베이스로 전환합니다. 이를 통해 다중 YouTube 채널 관리, 계정별 설정 저장, 작업 이력 추적이 가능한 엔터프라이즈급 시스템의 기반을 마련합니다.

### 목표
- ✅ 파일 기반(`job_history.json`) 시스템 제거
- ✅ SQLite + SQLAlchemy ORM 도입
- ✅ 멀티 계정(Multi-Account) 관리 기능
- ✅ 계정별 설정(Settings) 분리
- ✅ 작업 이력(Job History) DB 저장
- ✅ REST API 엔드포인트 추가 (CRUD)
- ✅ Alembic 마이그레이션 시스템

---

## 🗂️ 디렉토리 구조

```
youtube-ai/
├── backend/
│   ├── database.py          # ✨ NEW - DB 연결 및 세션 관리
│   ├── models.py            # ✨ NEW - ORM 모델 정의
│   ├── schemas.py           # ✨ NEW - Pydantic 스키마
│   ├── routers/
│   │   ├── __init__.py
│   │   └── accounts.py      # ✨ NEW - 계정 관리 API
│   ├── main.py              # 🔧 MODIFY - 라우터 추가
│   └── ...
├── alembic/                 # ✨ NEW - DB 마이그레이션
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── data/
│   ├── youtube_ai.db        # ✨ NEW - SQLite DB 파일
│   └── job_history.json     # ⚠️ DEPRECATED (백업 후 삭제 예정)
└── requirements.txt         # 🔧 MODIFY - 새 패키지 추가
```

---

## 📦 필수 패키지 설치

`requirements.txt`에 다음 패키지를 추가하세요:

```txt
# Database (Phase 1)
sqlalchemy>=2.0.23
alembic>=1.13.1
pydantic>=2.5.0
pydantic-settings>=2.1.0
```

설치:
```bash
pip install sqlalchemy alembic pydantic pydantic-settings
```

---

## 🏗️ 구현 단계

### Step 1: Database 모듈 생성 (`backend/database.py`)

SQLAlchemy 엔진 및 세션 설정을 담당합니다.

```python
"""
Database Connection Module
SQLite + SQLAlchemy 기반 DB 연결 관리
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

# DB 파일 경로
DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "youtube_ai.db"

# SQLite 연결 URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 멀티스레드 지원
    echo=False  # SQL 쿼리 로깅 (개발 시 True로 설정)
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM Base 클래스
Base = declarative_base()


def get_db() -> Session:
    """
    FastAPI Dependency Injection용 DB 세션 제공

    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    데이터베이스 초기화 (테이블 생성)
    앱 시작 시 호출
    """
    from backend.models import Account, AccountSettings, JobHistory
    Base.metadata.create_all(bind=engine)
    print(f"[Database] 초기화 완료: {DB_PATH}")
```

---

### Step 2: ORM 모델 정의 (`backend/models.py`)

3개의 핵심 테이블을 정의합니다.

```python
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
```

---

### Step 3: Pydantic 스키마 생성 (`backend/schemas.py`)

API 요청/응답용 데이터 검증 스키마입니다.

```python
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
    channel_id: Optional[str]
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
    account_id: Optional[int]
    topic: str
    status: JobStatus
    format: str
    duration: int
    output_video_path: Optional[str]
    youtube_url: Optional[str]
    youtube_video_id: Optional[str]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# Combined Responses
# ============================================================================

class AccountDetailResponse(AccountResponse):
    """Account 상세 정보 (설정 포함)"""
    settings: Optional[AccountSettingsResponse] = None
    jobs: List[JobHistoryResponse] = []
```

---

### Step 4: Account API 라우터 생성 (`backend/routers/accounts.py`)

CRUD API 엔드포인트를 구현합니다.

```python
"""
Account Management API Router
계정 생성, 조회, 수정, 삭제 (CRUD)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Account, AccountSettings
from backend.schemas import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountDetailResponse,
    AccountSettingsUpdate,
    AccountSettingsResponse
)

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


# ============================================================================
# Account CRUD
# ============================================================================

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 YouTube 계정 생성
    자동으로 기본 설정(AccountSettings)도 생성됩니다.
    """
    # 중복 확인
    existing = db.query(Account).filter(Account.channel_name == account.channel_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"채널명 '{account.channel_name}'이 이미 존재합니다."
        )

    # Account 생성
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.flush()  # ID 생성을 위해 flush

    # 기본 AccountSettings 생성
    db_settings = AccountSettings(account_id=db_account.id)
    db.add(db_settings)

    db.commit()
    db.refresh(db_account)

    return db_account


@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    모든 계정 목록 조회
    """
    accounts = db.query(Account).offset(skip).limit(limit).all()
    return accounts


@router.get("/{account_id}", response_model=AccountDetailResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 계정 상세 조회 (설정 및 작업 이력 포함)
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}를 찾을 수 없습니다."
        )

    return account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db)
):
    """
    계정 정보 수정 (부분 업데이트)
    """
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}를 찾을 수 없습니다."
        )

    # 부분 업데이트
    update_data = account_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_account, key, value)

    db.commit()
    db.refresh(db_account)

    return db_account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    계정 삭제 (설정 및 작업 이력도 함께 삭제)
    """
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}를 찾을 수 없습니다."
        )

    db.delete(db_account)
    db.commit()

    return None


# ============================================================================
# AccountSettings CRUD
# ============================================================================

@router.get("/{account_id}/settings", response_model=AccountSettingsResponse)
def get_account_settings(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    계정 설정 조회
    """
    settings = db.query(AccountSettings).filter(
        AccountSettings.account_id == account_id
    ).first()

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}의 설정을 찾을 수 없습니다."
        )

    return settings


@router.put("/{account_id}/settings", response_model=AccountSettingsResponse)
def update_account_settings(
    account_id: int,
    settings_update: AccountSettingsUpdate,
    db: Session = Depends(get_db)
):
    """
    계정 설정 수정
    """
    db_settings = db.query(AccountSettings).filter(
        AccountSettings.account_id == account_id
    ).first()

    if not db_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}의 설정을 찾을 수 없습니다."
        )

    # 업데이트
    update_data = settings_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_settings, key, value)

    db.commit()
    db.refresh(db_settings)

    return db_settings
```

---

### Step 5: FastAPI 메인 앱에 라우터 추가 (`backend/main.py`)

기존 `main.py`를 수정하여 DB 초기화 및 라우터를 추가합니다.

```python
# backend/main.py 상단에 추가

from backend.database import init_db
from backend.routers import accounts

# ... 기존 코드 ...

# FastAPI 앱 생성 후
app = FastAPI(title="YouTube AI v3.0", version="3.0.0")

# ✨ NEW: DB 초기화
@app.on_event("startup")
def startup_event():
    """앱 시작 시 DB 초기화"""
    init_db()
    print("[FastAPI] 데이터베이스 초기화 완료")

# ✨ NEW: 계정 관리 라우터 추가
app.include_router(accounts.router)

# ... 나머지 기존 라우터들 ...
```

---

### Step 6: Alembic 마이그레이션 설정

Alembic을 사용하여 DB 스키마 변경을 버전 관리합니다.

**1. Alembic 초기화**

```bash
alembic init alembic
```

**2. `alembic.ini` 수정**

```ini
# alembic.ini (54번째 줄 근처)
sqlalchemy.url = sqlite:///./data/youtube_ai.db
```

**3. `alembic/env.py` 수정**

```python
# alembic/env.py

from backend.database import Base
from backend.models import Account, AccountSettings, JobHistory

target_metadata = Base.metadata

# ... 나머지는 기본값 유지 ...
```

**4. 첫 마이그레이션 생성**

```bash
alembic revision --autogenerate -m "Initial migration: Account, AccountSettings, JobHistory"
```

**5. 마이그레이션 적용**

```bash
alembic upgrade head
```

---

## ✅ 테스트 체크리스트

### 1. DB 생성 확인

```bash
# 백엔드 서버 실행
python backend/main.py

# 확인 사항:
# - "[FastAPI] 데이터베이스 초기화 완료" 메시지 출력
# - data/youtube_ai.db 파일 생성됨
```

### 2. API 테스트 (curl 또는 Swagger UI)

**Swagger UI**: http://localhost:8000/docs

**1) 계정 생성**

```bash
curl -X POST "http://localhost:8000/api/accounts/" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_name": "테스트 채널",
    "channel_type": "info",
    "default_prompt_style": "정보성",
    "is_active": true
  }'
```

**2) 계정 목록 조회**

```bash
curl -X GET "http://localhost:8000/api/accounts/"
```

**3) 계정 상세 조회**

```bash
curl -X GET "http://localhost:8000/api/accounts/1"
```

**4) 설정 수정**

```bash
curl -X PUT "http://localhost:8000/api/accounts/1/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "tts_provider": "elevenlabs",
    "tts_voice_id": "pNInz6obpgDQGcFmaJgB",
    "tts_stability": 0.7,
    "default_duration": 58
  }'
```

**5) 계정 삭제**

```bash
curl -X DELETE "http://localhost:8000/api/accounts/1"
```

### 3. 마이그레이션 테스트

```bash
# 현재 버전 확인
alembic current

# 업그레이드
alembic upgrade head

# 다운그레이드 (롤백)
alembic downgrade -1
```

---

## 🔧 기존 코드 통합

### `core/orchestrator.py` 수정

기존 `job_history.json` 대신 DB에 작업 이력을 저장하도록 수정합니다.

```python
# core/orchestrator.py

from backend.database import SessionLocal
from backend.models import JobHistory, JobStatus

class ContentOrchestrator:
    def __init__(self, ...):
        # ... 기존 코드 ...
        self.db = SessionLocal()  # ✨ DB 세션 추가

    def create_content(self, topic, video_format, target_duration, upload=False, account_id=None):
        # Job ID 생성
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # ✨ DB에 작업 기록 생성
        db_job = JobHistory(
            job_id=job_id,
            account_id=account_id,
            topic=topic or "AI 생성 주제",
            status=JobStatus.PENDING,
            format=video_format.value,
            duration=target_duration
        )
        self.db.add(db_job)
        self.db.commit()

        try:
            # 1. Planning
            db_job.status = JobStatus.PLANNING
            self.db.commit()
            plan = self.planner.generate_content_plan(...)

            # 2. Asset Collection
            db_job.status = JobStatus.COLLECTING_ASSETS
            self.db.commit()
            bundle = self.asset_manager.collect_assets(plan)

            # 3. Editing
            db_job.status = JobStatus.EDITING
            self.db.commit()
            video_path = self.editor.create_video(plan, bundle)

            # 4. Upload
            if upload:
                db_job.status = JobStatus.UPLOADING
                self.db.commit()
                youtube_url = self.uploader.upload_video(video_path, ...)
                db_job.youtube_url = youtube_url

            # 5. Complete
            db_job.status = JobStatus.COMPLETED
            db_job.output_video_path = video_path
            db_job.completed_at = datetime.utcnow()
            self.db.commit()

        except Exception as e:
            db_job.status = JobStatus.FAILED
            db_job.error_message = str(e)
            db_job.completed_at = datetime.utcnow()
            self.db.commit()
            raise

        return db_job
```

---

## 📊 성공 기준

- [x] `data/youtube_ai.db` 파일 생성 확인
- [x] Account CRUD API 모두 정상 작동 (POST, GET, PUT, DELETE)
- [x] AccountSettings 수정 API 정상 작동
- [x] Alembic 마이그레이션 성공 (`alembic upgrade head`)
- [x] Swagger UI에서 모든 엔드포인트 확인 가능
- [x] 기존 파이프라인에서 JobHistory DB 저장 확인

---

## 🚀 커밋 전략

각 단계별로 커밋하여 롤백 가능하도록 합니다:

```bash
# Step 1-2
git add backend/database.py backend/models.py
git commit -m "Phase 1: Add SQLAlchemy database and ORM models"

# Step 3-4
git add backend/schemas.py backend/routers/accounts.py
git commit -m "Phase 1: Add Account API endpoints (CRUD)"

# Step 5
git add backend/main.py
git commit -m "Phase 1: Integrate account router into FastAPI app"

# Step 6
git add alembic/ alembic.ini
git commit -m "Phase 1: Setup Alembic migrations"

# 통합
git add core/orchestrator.py
git commit -m "Phase 1: Integrate JobHistory DB into orchestrator"

# 최종
git add requirements.txt
git commit -m "Phase 1: Update requirements.txt"
```

---

## ⚠️ 주의사항

1. **기존 데이터 백업**
   ```bash
   cp data/job_history.json data/job_history.json.backup
   ```

2. **하위 호환성**
   - Phase 1 완료 후에도 `job_history.json`은 백업용으로 유지
   - Phase 6에서 마이그레이션 스크립트 제공 예정

3. **환경변수**
   - `.env` 파일에 DB 경로 추가 가능 (선택사항):
     ```
     DATABASE_URL=sqlite:///./data/youtube_ai.db
     ```

4. **SQLite 제한사항**
   - 멀티스레드 환경에서 `check_same_thread=False` 필수
   - 프로덕션 환경에서는 PostgreSQL/MySQL 권장

---

## 📚 다음 단계

Phase 1 완료 후:
- **Phase 2**: 미디어 엔진 고도화 (BGM, 템플릿)
- **Phase 3**: ElevenLabs TTS 고도화 (DB 설정 연동)
- **Phase 4**: 스케줄링 시스템 (Account 테이블 활용)

**Phase 2로 이동**: [UPGRADE_PHASE2.md](./UPGRADE_PHASE2.md)

---

**작성일**: 2025-12-26
**버전**: 1.0
**상태**: Ready for Implementation
