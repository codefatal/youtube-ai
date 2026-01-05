# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**YouTube AI v4.0** - 완전 자동화된 AI 기반 유튜브 쇼츠 제작 시스템

듀얼 인터페이스 시스템:
- **Web UI** (Next.js frontend + FastAPI backend) - 주 인터페이스
- **CLI** (Python 기반) - 커맨드라인 인터페이스

AI(Gemini/Claude), TTS(gTTS/ElevenLabs), 스톡 영상, BGM, 템플릿 시스템을 결합하여 유튜브 영상을 자동으로 기획, 제작, 업로드하는 완전 자동화 시스템입니다.

**v4.0 주요 기능**:
- 멀티 계정 관리 (SQLAlchemy 기반 DB)
- BGM 시스템 (6가지 분위기별 자동 선택)
- 템플릿 시스템 (3종: basic, documentary, entertainment)
- ElevenLabs TTS 상세 제어 (stability, similarity_boost, style)
- 스케줄링 자동화 (APScheduler)
- 프론트엔드 UI/UX 전면 개편
- **Phase 6**: AI 영상 선택, Wholesome TTS, Vrew 통합

## Development Commands

### Backend Development

**Start Backend Server:**
```bash
cd backend
python main.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend Development

**Start Frontend:**
```bash
cd frontend
npm install  # First time only
npm run dev
# Web UI runs at http://localhost:3000
```

**Both servers must run simultaneously** - Backend on port 8000, Frontend on port 3000.

### Database Migration (Alembic)

```bash
# 가상환경 활성화
venv\Scripts\activate  # Windows

# 마이그레이션 생성
venv\Scripts\alembic.exe revision --autogenerate -m "설명"

# 마이그레이션 적용
venv\Scripts\alembic.exe upgrade head

# 마이그레이션 롤백
venv\Scripts\alembic.exe downgrade -1
```

### CLI 스크립트

```bash
# 수동 영상 업로드
python scripts/manual_upload.py --video output/video.mp4 --interactive

# BGM 설정
python scripts/setup_bgm.py --add music.mp3 --mood energetic --name "Track"
python scripts/setup_bgm.py --stats

# 자동 영상 생성 (Legacy)
python scripts/auto_create.py --topic "AI 기술" --format shorts --duration 60
```

## Architecture

### Core Modules (`core/`)

- **planner.py** - AI 기반 콘텐츠 기획 및 스크립트 생성
  - `create_script()` - AI 스크립트 생성 (세그먼트별 타이밍 포함)
  - `_validate_and_adjust_duration()` - **Phase 2**: 시간 제약 검증 및 조정 (±1초 정확도)
  - Gemini/Claude API 통합

- **asset_manager.py** - 에셋 수집 (영상, TTS, BGM)
  - `collect_assets()` - 전체 에셋 수집 (영상 + TTS + BGM)
  - `_generate_tts()` - **Phase 6**: Wholesome TTS 지원 (use_wholesome=True)
  - `_generate_tts_wholesome()` - **Phase 6**: 전체 대본 한 번에 생성, Whisper 타이밍 추출
  - `_select_best_video_with_ai()` - **Phase 6**: Gemini AI가 5-10개 후보 중 최적 영상 선택
  - `_auto_tune_tts_params()` - **Phase 6**: 대본 분석하여 TTS 파라미터 자동 조정
  - Pexels, Pixabay (영상) / gTTS, ElevenLabs (TTS)

- **bgm_manager.py** - **Phase 2 신규**: BGM 관리
  - `process_bgm()` - ffmpeg 기반 BGM 처리 (루프, 페이드, 볼륨)
  - `auto_select_mood()` - 주제/톤에서 분위기 자동 추론
  - 6가지 분위기: HAPPY, SAD, ENERGETIC, CALM, TENSE, MYSTERIOUS

- **editor.py** - MoviePy 기반 영상 편집
  - `create_video()` - 전체 영상 합성 (클립 + 자막 + TTS + BGM)
  - `_load_template()` - **Phase 2**: JSON 템플릿 로드 및 적용
  - `_load_audio_with_bgm()` - **Phase 2**: TTS + BGM CompositeAudioClip 믹싱
  - `export_srt()` - **Phase 6**: SRT 자막 파일 생성
  - `export_project_json()` - **Phase 6**: 프로젝트 메타데이터 JSON 생성
  - `export_vrew()` - **Phase 6**: Vrew 프로젝트 파일 (.vrew) 생성
  - 해상도: 1080x1920 (Shorts) or 1920x1080 (Landscape)

- **uploader.py** - YouTube 업로드 자동화
  - `upload_video()` - OAuth 2.0 기반 업로드
  - `generate_metadata()` - AI 생성 메타데이터

- **orchestrator.py** - 파이프라인 관리
  - `create_content()` - 전체 파이프라인: Plan → Assets → Edit → Upload
  - **Phase 4**: `account_id` 파라미터 추가 (계정별 설정 적용)
  - Job 진행 상황 추적 및 에러 처리

### Provider System (`providers/`)

**AI Providers** (`providers/ai/`):
- **gemini.py** - Google Gemini API (free, fast)
- **claude.py** - Anthropic Claude API (premium)

**Stock Video Providers** (`providers/stock/`):
- **pexels.py** - Pexels API (free, high quality)
- **pixabay.py** - Pixabay API (free, fallback)

**TTS Providers** (`providers/tts/`):
- **gtts_provider.py** - Google TTS (free, fast)
- **elevenlabs.py** - ElevenLabs (premium, natural)
- **google_cloud.py** - Google Cloud TTS (premium)

### Backend API (`backend/main.py`)

**Phase 1: Account 관리**:
- `POST /api/accounts/` - 계정 생성
- `GET /api/accounts/` - 계정 목록
- `GET /api/accounts/{id}` - 계정 상세 (설정 + 작업 이력 포함)
- `PUT /api/accounts/{id}/settings` - 계정 설정 업데이트

**Phase 3: Draft 관리**:
- `POST /api/draft/create` - Draft 생성 (스크립트 + 에셋 수집)
- `GET /api/draft/{id}` - Draft 조회
- `POST /api/draft/{id}/update-segment/{index}` - 세그먼트 수정
- `POST /api/draft/{id}/finalize` - 최종 렌더링

**Phase 6: Draft Export**:
- `GET /api/draft/{id}/export/srt` - SRT 자막 파일 다운로드
- `GET /api/draft/{id}/export/json` - 프로젝트 JSON 다운로드
- `GET /api/draft/{id}/export/vrew` - Vrew 프로젝트 파일 다운로드

**Phase 4: 스케줄러**:
- `GET /api/scheduler/jobs` - 등록된 스케줄 조회
- `POST /api/scheduler/reload` - 스케줄 재로드
- `POST /api/scheduler/trigger/{account_id}` - 즉시 실행
- `DELETE /api/scheduler/jobs/{job_id}` - 스케줄 삭제

**Legacy Endpoints**:
- `POST /api/videos/create` - 영상 생성 (전체 파이프라인)
- `POST /api/jobs/status` - Job 상태 확인
- `GET /api/jobs/recent` - 최근 작업 목록

**공통 응답 형식**:
```json
{
  "success": true,
  "data": { ... }
}
```

### Data Models

**Pydantic Models** (`core/models.py`):
- `ContentPlan` - 전체 콘텐츠 기획 (제목, 설명, 태그, 세그먼트)
- `ScriptSegment` - 스크립트 세그먼트 (텍스트, 키워드, 길이)
- `AssetBundle` - 에셋 번들 (영상 + TTS + **BGM**)
- `BGMAsset` - **Phase 2**: BGM 에셋 (name, mood, duration, volume)
- `TemplateConfig` - **Phase 2**: 템플릿 설정 (자막, 효과, BGM)

**SQLAlchemy ORM** (`backend/models.py`):
- `Account` - 유튜브 계정 정보 (channel_name, channel_type, upload_schedule)
- `AccountSettings` - 계정별 설정 (TTS provider, voice_id, stability, BGM)
- `JobHistory` - 작업 이력 (job_id, status, output_video_path, youtube_url)

**주요 Enums**:
- `VideoFormat` - SHORTS, LANDSCAPE, SQUARE
- `MoodType` - **Phase 2**: HAPPY, SAD, ENERGETIC, CALM, TENSE, MYSTERIOUS
- `ContentStatus` - PLANNING, COLLECTING_ASSETS, EDITING, UPLOADING, COMPLETED, FAILED
- `ChannelType` - HUMOR, TREND, INFO, REVIEW, NEWS, DAILY

## Environment Variables

Required `.env` file at project root:

```bash
# Required for basic functionality
GEMINI_API_KEY=AIza...          # From https://aistudio.google.com/apikey

# Stock Videos (at least one)
PEXELS_API_KEY=...              # From https://www.pexels.com/api/
PIXABAY_API_KEY=...             # From https://pixabay.com/api/docs/

# Optional
ANTHROPIC_API_KEY=sk-ant-...    # For Claude
ELEVENLABS_API_KEY=...          # For premium TTS
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json  # For Google Cloud TTS
YOUTUBE_API_KEY=...             # For trend analysis (optional)
```

**YouTube Upload** requires `client_secrets.json` for OAuth 2.0.

## 프로젝트 상태

### ✅ v4.0 완료된 Phase (1~6)

**Phase 1: 데이터베이스 인프라**
- SQLAlchemy + Alembic 통합
- Account, AccountSettings, JobHistory 모델
- Account CRUD API

**Phase 2: 미디어 엔진 고도화**
- BGM 시스템 (6가지 분위기, ffmpeg 처리)
- 템플릿 시스템 (3종 JSON)
- 시간 제약 강화 (±10초 → ±1초)
- 수동 업로드 스크립트

**Phase 3: ElevenLabs TTS 고도화**
- Stability, Similarity Boost, Style 파라미터 제어
- TTS 미리듣기 API
- 해시 기반 스마트 캐싱
- AccountSettings 연동

**Phase 4: 스케줄링 및 자동화**
- APScheduler 도입
- 계정별 Cron 스케줄
- 백그라운드 Worker (자동 생성 + 업로드)
- JobHistory 작업 이력 기록

**Phase 5: 프론트엔드 UI/UX 전면 개편**
- 멀티 계정 관리 사이드바
- 영상 생성 페이지 개선 (TTS, 템플릿, BGM 설정)
- 계정 관리 페이지 (CRUD, 스케줄)
- 다크 모드 디자인
- 모바일 반응형

**Phase 6: AI 고도화 및 Vrew 통합 (2025-01-05)**
- **AI 영상 선택**: Gemini가 5-10개 후보 중 최적 선택 (매칭률 +40%p)
- **Wholesome TTS**: 전체 대본 한 번에 생성, Whisper 타이밍 추출 (톤 일관성 +30%p)
- **Few-Shot Learning**: AI 프롬프트에 10개 성공 사례 추가 (키워드 구체성 +55%p)
- **TTS 자동 조정**: 대본 분석으로 파라미터 자동 조정 (감정 표현 +25%p)
- **Vrew Export**: SRT, JSON, .vrew 파일 자동 생성
- **프론트엔드 통합**: Export 버튼 UI, AI 고급 설정 UI 추가

**최근 버그 수정 (2025-12-29)**:
- 제목 텍스트 하단 잘림 해결 (interline=60, 패딩 비율 증가)
- 이모지 깨짐 방지 (포괄적인 유니코드 범위 제거)
- BGM 자동 다운로드 기본 활성화 (bgm_enabled=True)
- Gemini MAX_TOKENS 오류 자동 재시도 (16384 토큰, 1.5배 증가 재시도)
- TTS 대기 시간 처리 ("(3초 대기)" → 실제 무음 추가)

**영상 완성도 개선 (2025-12-30)**:
- **BGM 시스템 고도화**: 파일 검증 로직, MoviePy volumex/audio_loop 사용, 볼륨 0.25로 상향
- **시각 효과 추가**: Ken Burns Effect (줌 1.15배), Crossfade 전환 (0.3초)
- **검색 키워드 개선**: 추상적 명사 → 구체적 동작/사물 유도 프롬프트
- **자막 배경 옵션**: `SUBTITLE_BG_ENABLED` 설정으로 활성화/비활성화
- **버그 수정**: TemplateConfig.bgm_volume, MoviePy 2.x crossfade 호환

### 🔄 다음 Phase

**Phase 7: 고급 편집 기능**
- Vrew 양방향 연동 (역방향 import)
- Multi-Voice TTS
- Real-time Preview

## 일반적인 개발 패턴

### 계정별 영상 생성 (v4.0)

```python
from core.orchestrator import ContentOrchestrator
from core.models import VideoFormat
from backend.database import SessionLocal
from backend.models import Account

# DB에서 계정 조회
db = SessionLocal()
account = db.query(Account).filter(Account.channel_name == "내 채널").first()

# Orchestrator 생성
orchestrator = ContentOrchestrator()

# 계정별 설정을 반영한 영상 생성
job = orchestrator.create_content(
    topic="Python 프로그래밍 팁",
    video_format=VideoFormat.SHORTS,
    target_duration=60,
    upload=True,
    account_id=account.id  # AccountSettings 자동 적용
)

print(f"Video: {job.output_video_path}")
print(f"YouTube URL: {job.youtube_url}")
```

### BGM 및 템플릿 적용

```python
from core.editor import VideoEditor
from core.asset_manager import AssetManager

# BGM 활성화
asset_manager = AssetManager(bgm_enabled=True)

# 템플릿 적용
editor = VideoEditor(template_name="entertainment")  # basic, documentary, entertainment

# 에셋 수집 시 BGM 자동 선택됨
bundle = asset_manager.collect_assets(content_plan)

# 영상 생성 시 템플릿 스타일 자동 적용됨
video_path = editor.create_video(content_plan, bundle)
```

### ElevenLabs TTS 상세 제어 (Phase 3)

```python
from core.asset_manager import AssetManager

asset_manager = AssetManager()

# ElevenLabs 파라미터 직접 제어
audio_path = asset_manager._generate_elevenlabs(
    text="안녕하세요. 테스트 음성입니다.",
    voice_id="pNInz6obpgDQGcFmaJgB",  # Adam (남성 목소리)
    stability=0.5,           # 0.0 (감정 풍부) ~ 1.0 (일관성)
    similarity_boost=0.75,   # 0.0 ~ 1.0 (원본 목소리 유사도)
    style=0.0,              # 0.0 (자연스러움) ~ 1.0 (과장)
    use_speaker_boost=True  # 목소리 강화
)
```

### 스케줄링 자동화 (Phase 4)

```python
from backend.scheduler import scheduler_instance
from backend.models import Account
from backend.database import SessionLocal

db = SessionLocal()

# 계정 스케줄 등록 (매일 오전 10시)
account = db.query(Account).first()
account.upload_schedule = "0 10 * * *"  # Cron 포맷
db.commit()

# 스케줄러 재로드
scheduler_instance.load_account_schedules()

# 즉시 실행 (테스트용)
from backend.workers import auto_generate_and_upload
auto_generate_and_upload(account.id)
```

### Phase 6: AI 고급 기능 사용

```python
from core.asset_manager import AssetManager
from core.planner import ContentPlanner

# 1. AI 영상 선택 (자동 활성화됨)
asset_manager = AssetManager()
bundle = asset_manager.collect_assets(content_plan)
# → Gemini가 5-10개 후보 중 최적 영상 자동 선택

# 2. Wholesome TTS (기본값)
audio, timings = asset_manager._generate_tts(
    content_plan,
    use_wholesome=True  # 전체 대본 한 번에 생성
)
# → Whisper로 정확한 타이밍 추출

# 3. Vrew Export
from core.editor import VideoEditor

editor = VideoEditor()
editor.export_vrew(content_plan, bundle, "output/project.vrew")
# → .vrew 파일 생성 (SRT + JSON + manifest)
```

### Vrew 워크플로우

```
1. Frontend: Draft 생성 (/create)
2. Frontend: "🎬 Vrew" 버튼 클릭 (/projects)
3. Download: project.vrew 파일
4. Vrew: 프로젝트 열기 → 수동 편집
5. Vrew: 최종 영상 Export
6. YouTube: 업로드
```

## Testing Changes

**Backend changes:**
```bash
# Restart backend server (Ctrl+C, then)
python backend/main.py

# Test specific endpoint
curl -X POST http://localhost:8000/api/topics/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 3, "trending": true}'
```

**Frontend changes:**
- Next.js auto-reloads on file save
- Check browser console for errors
- Backend logs appear in backend terminal

**Run tests:**
```bash
# Integration tests
python tests/test_integration.py

# Error cases
python tests/test_error_cases.py

# Performance benchmark
python scripts/benchmark.py
```

## Git Workflow

- Commit messages in Korean (user preference)
- Push directly to main branch
- Phase summary documents (PHASE1_SUMMARY.md ~ PHASE8_SUMMARY.md) track progress

## 알려진 이슈 및 해결 방법

1. **ffmpeg 필수**: BGM 처리에 ffmpeg 필요 (Phase 2)
   - Windows: https://ffmpeg.org/download.html
   - PATH 환경변수에 추가 필수
   - 확인: `ffmpeg -version`

2. **ImageMagick 필수**: MoviePy 자막 렌더링
   - Windows: https://imagemagick.org/
   - `moviepy/config_defaults.py`에 경로 설정

3. **API 키 설정**: `.env` 파일 필수
   - 최소 요구: `GEMINI_API_KEY`, `PEXELS_API_KEY`
   - ElevenLabs: `ELEVENLABS_API_KEY` (Phase 3 TTS용)

4. **YouTube 업로드**: OAuth 2.0 설정
   - https://console.cloud.google.com/ 에서 프로젝트 생성
   - `client_secrets.json` 다운로드
   - 최초 업로드 시 브라우저에서 인증

5. **데이터베이스 초기화**: 최초 실행 시
   ```bash
   venv\Scripts\alembic.exe upgrade head
   ```

6. **Python 3.14 호환성**: 모든 의존성 업데이트됨
   - numpy >= 2.3.0
   - Pillow >= 11.0.0
   - SQLAlchemy >= 2.0.23

## 중요 구현 세부사항

### Phase 6: AI 영상 선택 (asset_manager.py:202-269)
- Gemini API로 5-10개 후보 중 최적 선택
- 대본과 영상의 semantic matching
- 자동 활성화됨 (비활성화 불가)

### Phase 6: Wholesome TTS (asset_manager.py:351-495)
- 전체 대본을 한 번에 생성 → 톤 일관성 보장
- Whisper 모델로 정확한 세그먼트 타이밍 추출
- Whisper 실패 시 텍스트 길이 기반 Fallback
- 기본값: `use_wholesome=True`

### Phase 6: Few-Shot Learning (templates/script_prompts/shorts_script.txt:77-382)
- 10개 카테고리 성공 사례 포함
- 키워드 생성 규칙: 주체 + 동작 + 대상 + 분위기
- 추상적 키워드 금지 ("성공", "행복" 등)

### Phase 6: TTS 자동 조정 (asset_manager.py:556-632)
- 대본 분석: 감정 표현, 격식체, 구어체, 긴급 단어
- ElevenLabs 파라미터 자동 조정 (stability, similarity_boost, style)
- Typecast 감정 자동 선택 (normal, happy, sad, angry)

### Phase 6: Vrew Export (editor.py:1053-1138)
- .vrew 파일 = ZIP (subtitle.srt + project.json + manifest.json)
- API: `GET /api/draft/{id}/export/vrew`
- Frontend: 프로젝트 목록 페이지에 "🎬 Vrew" 버튼

### TTS 대기 시간 구현
스크립트에 `(3초 대기)`, `(5초 기다림)` 등의 표현을 포함하면 해당 시간만큼 무음이 자동 추가됩니다.
**지원 표현**: `(N초 대기)`, `(N초 기다림)`, `(N초 멈춤)`, `(N초 정지)`
**구현 위치**: `core/asset_manager.py:_add_pause_to_audio()`

### 제목/자막 렌더링 주의사항
- **이모지 사용 금지**: Pillow와 MoviePy는 이모지를 렌더링할 수 없음
- 자동 제거: U+1F000~U+1FFFF 범위 및 특수 기호들이 자동 제거됨
- **제목 잘림 방지**: `interline=60`, 패딩 비율 3.0/2.2 적용으로 충분한 여백 확보

### Gemini API MAX_TOKENS 처리
- 기본 max_tokens: 16384
- MAX_TOKENS 도달 시 자동으로 1.5배 증가하여 재시도 (최대 2회)
- 재시도 시퀀스: 16384 → 24576 → 36864
- JSON 파싱 실패도 재시도 대상

### BGM 자동 다운로드
- 첫 실행 시 Bensound에서 6가지 분위기별 무료 BGM 자동 다운로드
- 저장 위치: `music/MOOD_NAME/` (예: `music/HAPPY/happy_upbeat.mp3`)
- 기본 활성화: `AssetManager(bgm_enabled=True)` (기본값)

## API Usage Examples

### Generate Topics

```bash
curl -X POST http://localhost:8000/api/topics/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 3, "trending": true}'
```

### Generate Script

```bash
curl -X POST http://localhost:8000/api/scripts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python 기초",
    "format": "shorts",
    "duration": 60,
    "style": "정보성"
  }'
```

### Create Video

```bash
curl -X POST http://localhost:8000/api/videos/create \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI 기술 소개",
    "format": "shorts",
    "duration": 60,
    "upload": false
  }'
```

### Check Job Status

```bash
curl -X POST http://localhost:8000/api/jobs/status \
  -H "Content-Type: application/json" \
  -d '{"job_id": "job_20251223_123456"}'
```

## 관련 문서

**계획 및 진행 상황**:
- `.claude/resume.md` - **다른 PC에서 작업 재개 시 필독**
- `PHASES_HISTORY.md` - 전체 Phase 작업 히스토리 (리팩토링 + 업그레이드)
- `UPGRADE_PLAN.md` - v4.0 업그레이드 전체 계획

**Phase별 상세 문서**:
- `UPGRADE_PHASE1.md` ~ `UPGRADE_PHASE6.md` - 각 Phase 상세 계획서

**Phase 6 문서** (2025-01-05):
- `PHASE6_VREW_INTEGRATION.md` - Phase 6 전체 구현 상세 가이드 (93KB)
- `PHASE6_QUICK_REFERENCE.md` - 빠른 참조 가이드 (13KB)
- `IMPLEMENTATION_SUMMARY_PHASE6.md` - Phase 1-6 종합 요약 (47KB)
- `FRONTEND_GUIDE_PHASE6.md` - 프론트엔드 UI 사용 가이드
- `ANALYSIS_AND_VREW_INTEGRATION.md` - 초기 분석 및 개선 방안

**가이드**:
- `README.md` - 프로젝트 개요 및 설치 가이드
- `MUSIC_GUIDE.md` - BGM 사용 가이드

**테스트 및 스크립트**:
- `tests/` - 통합 테스트, TTS 테스트, 스케줄러 테스트
- `scripts/` - 자동화 스크립트 (manual_upload.py, setup_bgm.py, setup_default_bgm.py)

## 레포지토리 URL

https://github.com/codefatal/youtube-ai

---

**작성일**: 2025-12-26
**버전**: v4.0 Phase 6
**최종 업데이트**: 2025-01-05 (Phase 6: AI 고도화 및 Vrew 통합 완료)
