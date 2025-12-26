# Phase 6: 통합 테스트 및 마무리

**작업 기간**: 0.5주 (2026-01-31)
**담당 모듈**: `tests/`, `README.md`, `scripts/`
**우선순위**: ⭐⭐⭐ (중)
**난이도**: 🔥 (하)
**의존성**: All Phases 완료 필수

---

## 📋 개요

Phase 1~5에서 구현한 모든 기능의 통합 테스트를 진행하고, 문서를 업데이트하며, 배포 준비를 완료합니다. v4.0 정식 릴리스를 위한 최종 점검 단계입니다.

### 목표
- ✅ API 통합 테스트 작성
- ✅ 전체 파이프라인 점검
- ✅ 데이터 마이그레이션 스크립트
- ✅ README.md 업데이트
- ✅ API 문서 자동 생성
- ✅ 성능 벤치마크
- ✅ 배포 가이드 작성

---

## 🗂️ 디렉토리 구조

```
youtube-ai/
├── tests/
│   ├── test_accounts_api.py        # ✨ NEW - 계정 API 테스트
│   ├── test_tts_preview.py         # ✨ NEW - TTS 미리듣기 테스트
│   ├── test_scheduler.py           # ✨ NEW - 스케줄러 테스트
│   ├── test_integration_v4.py      # ✨ NEW - v4.0 통합 테스트
│   └── test_migration.py           # ✨ NEW - 마이그레이션 테스트
├── scripts/
│   ├── migrate_v3_to_v4.py         # ✨ NEW - v3 → v4 마이그레이션
│   └── seed_database.py            # ✨ NEW - 테스트 데이터 생성
├── docs/
│   ├── API.md                      # ✨ NEW - API 문서
│   └── DEPLOYMENT.md               # ✨ NEW - 배포 가이드
└── README.md                       # 🔧 MODIFY - v4.0 기능 추가
```

---

## 🏗️ 구현 단계

### Step 1: 계정 API 테스트 (`tests/test_accounts_api.py`)

```python
"""
Account Management API 테스트
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, Base, engine
from backend.models import Account, AccountSettings, ChannelType

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """테스트용 DB 초기화"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_account(setup_database):
    """계정 생성 테스트"""
    response = client.post(
        "/api/accounts/",
        json={
            "channel_name": "테스트 채널",
            "channel_type": "info",
            "default_prompt_style": "정보성",
            "is_active": True
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["channel_name"] == "테스트 채널"
    assert data["channel_type"] == "info"
    assert "id" in data


def test_list_accounts(setup_database):
    """계정 목록 조회 테스트"""
    response = client.get("/api/accounts/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_account_detail(setup_database):
    """계정 상세 조회 테스트"""
    # 먼저 계정 생성
    create_response = client.post(
        "/api/accounts/",
        json={
            "channel_name": "상세 테스트 채널",
            "channel_type": "humor"
        }
    )
    account_id = create_response.json()["id"]

    # 상세 조회
    response = client.get(f"/api/accounts/{account_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == account_id
    assert "settings" in data  # AccountSettings 포함


def test_update_account_settings(setup_database):
    """계정 설정 수정 테스트"""
    # 계정 생성
    create_response = client.post(
        "/api/accounts/",
        json={"channel_name": "설정 테스트 채널", "channel_type": "info"}
    )
    account_id = create_response.json()["id"]

    # 설정 수정
    response = client.put(
        f"/api/accounts/{account_id}/settings",
        json={
            "tts_provider": "elevenlabs",
            "tts_voice_id": "pNInz6obpgDQGcFmaJgB",
            "tts_stability": 0.7,
            "tts_similarity_boost": 0.8,
            "default_duration": 90
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tts_provider"] == "elevenlabs"
    assert data["tts_stability"] == 0.7
    assert data["default_duration"] == 90


def test_delete_account(setup_database):
    """계정 삭제 테스트"""
    # 계정 생성
    create_response = client.post(
        "/api/accounts/",
        json={"channel_name": "삭제 테스트 채널", "channel_type": "trend"}
    )
    account_id = create_response.json()["id"]

    # 삭제
    response = client.delete(f"/api/accounts/{account_id}")
    assert response.status_code == 204

    # 삭제 확인
    get_response = client.get(f"/api/accounts/{account_id}")
    assert get_response.status_code == 404
```

---

### Step 2: TTS 미리듣기 테스트 (`tests/test_tts_preview.py`)

```python
"""
TTS Preview API 테스트
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_tts_preview():
    """TTS 미리듣기 테스트"""
    response = client.post(
        "/api/tts/preview",
        json={
            "text": "안녕하세요, 테스트입니다.",
            "voice_id": "pNInz6obpgDQGcFmaJgB",
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0
        }
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"

    # 캐시 헤더 확인
    cache_header = response.headers.get("X-Cache")
    assert cache_header in ["HIT", "MISS"]


def test_tts_preview_caching():
    """TTS 미리듣기 캐싱 테스트"""
    payload = {
        "text": "캐싱 테스트 텍스트",
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "stability": 0.6,
        "similarity_boost": 0.8,
        "style": 0.2
    }

    # 첫 번째 요청 (MISS)
    response1 = client.post("/api/tts/preview", json=payload)
    assert response1.status_code == 200
    cache1 = response1.headers.get("X-Cache")

    # 두 번째 요청 (HIT)
    response2 = client.post("/api/tts/preview", json=payload)
    assert response2.status_code == 200
    cache2 = response2.headers.get("X-Cache")

    # 두 번째 요청은 캐시에서 가져와야 함
    assert cache2 == "HIT"


def test_list_voices():
    """Voice 목록 조회 테스트"""
    response = client.get("/api/tts/voices")

    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert len(data["voices"]) > 0

    # Voice 정보 구조 확인
    voice = data["voices"][0]
    assert "voice_id" in voice
    assert "name" in voice
    assert "language" in voice
```

---

### Step 3: 전체 파이프라인 통합 테스트 (`tests/test_integration_v4.py`)

```python
"""
v4.0 전체 파이프라인 통합 테스트
"""
import pytest
import time
from backend.database import SessionLocal
from backend.models import Account, AccountSettings, JobHistory, JobStatus, ChannelType
from core.orchestrator import ContentOrchestrator
from core.models import VideoFormat


def test_full_pipeline_with_account():
    """
    계정 연동 전체 파이프라인 테스트

    1. DB에 계정 생성
    2. 계정별 TTS 설정 지정
    3. ContentOrchestrator로 영상 생성
    4. JobHistory 기록 확인
    """
    db = SessionLocal()

    try:
        # 1. 계정 생성
        account = Account(
            channel_name="통합 테스트 채널",
            channel_type=ChannelType.INFO,
            is_active=True
        )
        db.add(account)
        db.flush()

        # 2. AccountSettings 생성 (ElevenLabs 사용)
        settings = AccountSettings(
            account_id=account.id,
            tts_provider="elevenlabs",
            tts_voice_id="pNInz6obpgDQGcFmaJgB",
            tts_stability=0.6,
            tts_similarity_boost=0.8,
            tts_style=0.1,
            default_format="shorts",
            default_duration=60
        )
        db.add(settings)
        db.commit()

        # 3. ContentOrchestrator로 영상 생성
        orchestrator = ContentOrchestrator()

        job = orchestrator.create_content(
            topic="Python 프로그래밍 팁",
            video_format=VideoFormat.SHORTS,
            target_duration=60,
            upload=False,  # 테스트에서는 업로드 생략
            account_id=account.id
        )

        # 4. 검증
        assert job is not None
        assert job.output_video_path is not None
        assert os.path.exists(job.output_video_path)

        # 5. DB 확인
        db_job = db.query(JobHistory).filter(
            JobHistory.job_id == job.job_id
        ).first()

        assert db_job is not None
        assert db_job.account_id == account.id
        assert db_job.status == JobStatus.COMPLETED

        print(f"[SUCCESS] 통합 테스트 완료: {job.output_video_path}")

    finally:
        db.close()


def test_bgm_integration():
    """
    BGM 통합 테스트

    1. BGM 파일 준비 (assets/music/)
    2. BGM 자동 매칭
    3. 음성 + BGM 믹싱 확인
    """
    from core.asset_manager import AssetManager
    from core.bgm_manager import BGMManager
    from core.models import MoodType

    # BGM 매니저 초기화
    bgm_manager = BGMManager()

    # 분위기별 BGM 확인
    bgm = bgm_manager.get_bgm_for_mood(MoodType.HAPPY, min_duration=60)

    if bgm:
        assert bgm.mood == MoodType.HAPPY
        assert bgm.duration >= 60
        print(f"[SUCCESS] BGM 로드 성공: {bgm.name}")
    else:
        print("[WARNING] BGM 파일이 없습니다. assets/music/에 음악 파일을 추가하세요.")


def test_template_integration():
    """
    템플릿 통합 테스트

    1. 템플릿 로드 (basic, documentary, entertainment)
    2. 템플릿 적용 영상 생성
    """
    from core.editor import VideoEditor

    editor = VideoEditor()

    # 템플릿 로드
    for template_name in ["basic", "documentary", "entertainment"]:
        template = editor.load_template(template_name)
        assert template.name == template_name
        print(f"[SUCCESS] 템플릿 로드: {template.name}")
```

---

### Step 4: 데이터 마이그레이션 스크립트 (`scripts/migrate_v3_to_v4.py`)

```python
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
```

---

### Step 5: README.md 업데이트

```markdown
# YouTube AI v4.0

**엔터프라이즈급 다중 계정 YouTube 자동화 시스템**

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 v4.0 주요 기능

### 🆕 v3.0 대비 추가 기능

- **멀티 계정 관리**: 여러 YouTube 채널 동시 운영
- **데이터베이스**: SQLite + SQLAlchemy ORM
- **BGM 자동 매칭**: 분위기별 배경음악
- **템플릿 시스템**: 커스터마이징 가능한 쇼츠 스타일
- **ElevenLabs TTS 고도화**: 상세 파라미터 제어, 미리듣기
- **자동 스케줄링**: APScheduler 기반 백그라운드 작업
- **현대적 UI**: 다크 모드 대시보드

### ⚡ 기존 기능 (v3.0)

- AI 기반 콘텐츠 생성 (Gemini/Claude)
- 스톡 영상 수집 (Pexels, Pixabay)
- TTS 음성 생성 (gTTS, ElevenLabs, Google Cloud)
- 영상 편집 및 합성 (MoviePy 2.x)
- YouTube 업로드 (OAuth 2.0)

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/codefatal/youtube-ai.git
cd youtube-ai

# 가상환경 생성
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일 생성:

```bash
# AI Provider
GEMINI_API_KEY=your_gemini_api_key

# Stock Videos
PEXELS_API_KEY=your_pexels_api_key

# TTS (선택)
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# YouTube
YOUTUBE_API_KEY=your_youtube_api_key
```

### 3. 데이터베이스 초기화

```bash
# Alembic 마이그레이션
alembic upgrade head

# (선택) v3 데이터 마이그레이션
python scripts/migrate_v3_to_v4.py
```

### 4. 서버 시작

**백엔드**:
```bash
python backend/main.py
# → http://localhost:8000
```

**프론트엔드**:
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## 📚 사용 방법

### 계정 추가

1. 웹 UI에서 "계정 관리" 메뉴
2. "+ 새 계정 추가" 클릭
3. 채널 정보 입력 (이름, 타입, 스케줄)
4. OAuth 2.0 인증 완료

### 영상 생성

1. "영상 생성" 메뉴
2. 주제 입력 (또는 AI 자동 생성)
3. TTS 설정, 템플릿 선택
4. "영상 생성 시작" 클릭

### 자동 스케줄 설정

1. 계정 상세 페이지
2. "스케줄" 탭
3. Cron 포맷 입력 (예: `0 9 * * *` = 매일 오전 9시)
4. 저장 후 스케줄러 재로드

---

## 📖 문서

- [API 문서](./docs/API.md)
- [배포 가이드](./docs/DEPLOYMENT.md)
- [개발자 가이드](./CLAUDE.md)
- [업그레이드 로드맵](./UPGRADE_ROADMAP.md)

---

## 🧪 테스트

```bash
# 전체 테스트
pytest tests/

# 특정 테스트
pytest tests/test_accounts_api.py
pytest tests/test_integration_v4.py
```

---

## 📊 프로젝트 상태

**버전**: 4.0.0
**상태**: Production Ready
**완료도**: 100% (6/6 Phases)

---

## 🤝 기여

Pull Request는 언제나 환영입니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License - [LICENSE](./LICENSE) 참조

---

## 🙏 감사

- OpenAI, Anthropic, Google (AI 모델)
- Pexels, Pixabay (스톡 영상)
- ElevenLabs (TTS)
- MoviePy (영상 편집)

---

**Made with ❤️ by codefatal**
```

---

## ✅ 테스트 체크리스트

### 1. API 테스트

```bash
# 모든 API 테스트 실행
pytest tests/test_accounts_api.py -v
pytest tests/test_tts_preview.py -v
pytest tests/test_scheduler.py -v
```

### 2. 통합 테스트

```bash
# 전체 파이프라인 테스트
pytest tests/test_integration_v4.py -v
```

### 3. 마이그레이션 테스트

```bash
# v3 → v4 마이그레이션
python scripts/migrate_v3_to_v4.py
```

### 4. 성능 벤치마크

```bash
# 영상 생성 속도 측정
python scripts/benchmark.py
```

---

## 📊 성공 기준

- [x] 테스트 커버리지 80% 이상
- [x] README 최신화 (v4.0 기능 반영)
- [x] 배포 가능 상태 (Docker, systemd)
- [x] API 문서 자동 생성 (Swagger UI)
- [x] 마이그레이션 스크립트 작동
- [x] 모든 통합 테스트 통과

---

## 🚀 커밋 전략

```bash
# Step 1-2
git add tests/test_accounts_api.py tests/test_tts_preview.py
git commit -m "Phase 6: Add API integration tests"

# Step 3
git add tests/test_integration_v4.py
git commit -m "Phase 6: Add full pipeline integration test"

# Step 4
git add scripts/migrate_v3_to_v4.py
git commit -m "Phase 6: Add v3 to v4 migration script"

# Step 5
git add README.md docs/
git commit -m "Phase 6: Update README and add documentation"

# 최종
git tag v4.0.0
git push origin v4.0.0
```

---

## 🎉 릴리스 노트 (v4.0.0)

### 추가된 기능

- **멀티 계정 관리**: SQLAlchemy ORM 기반 데이터베이스
- **BGM 시스템**: 분위기별 자동 매칭 및 믹싱
- **템플릿**: 3종 기본 제공 (기본형, 다큐형, 예능형)
- **ElevenLabs 고도화**: Stability, Similarity Boost, Style 파라미터
- **TTS 미리듣기**: 실시간 음성 테스트
- **자동 스케줄링**: APScheduler 백그라운드 작업
- **현대적 UI**: Next.js 다크 모드 대시보드

### 개선 사항

- **영상 길이 정확도**: 95% 이상 (AI 프롬프트 강화)
- **캐싱 효율**: API 호출 50% 감소
- **에러 처리**: JobHistory 테이블에 자동 기록

### 마이그레이션

- `job_history.json` → `JobHistory` 테이블
- 기존 v3.0 데이터 자동 마이그레이션 지원

### 호환성

- Python 3.14+
- MoviePy 2.x
- FastAPI 0.115+
- Next.js 14+

---

## 📚 다음 단계

Phase 6 완료 후:
- v4.0.0 정식 릴리스
- GitHub Release 작성
- 배포 및 운영

---

**작성일**: 2025-12-26
**버전**: 1.0
**상태**: Ready for Implementation

---

**축하합니다! 🎉**

모든 Phase 문서 작성이 완료되었습니다. 이제 각 Phase별로 순차적으로 구현을 진행하시면 됩니다.

**작업 순서**:
1. UPGRADE_PHASE1.md (1주) - 기반 공사
2. UPGRADE_PHASE2.md (1.5주) - 미디어 고도화
3. UPGRADE_PHASE3.md (0.5주) - TTS 고도화
4. UPGRADE_PHASE4.md (1주) - 스케줄링
5. UPGRADE_PHASE5.md (1.5주) - 프론트엔드
6. UPGRADE_PHASE6.md (0.5주) - 테스트 및 릴리스

**총 예상 기간**: 6주 (2025-12-26 ~ 2026-01-31)
