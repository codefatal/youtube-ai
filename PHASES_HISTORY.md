# YouTube AI 개발 히스토리

프로젝트의 모든 Phase 작업 기록을 통합한 문서입니다.

---

## 📅 타임라인

- **2025-12-22~23**: 리팩토링 프로젝트 (Phase 1~8)
- **2025-12-26**: v4.0 업그레이드 (Phase 1~2)

---

# 🔧 리팩토링 프로젝트 (v3.0 → v4.0 기반)

## Phase 1: 프로젝트 구조 재설계

**완료 일시**: 2025-12-22
**토큰 사용**: 56.5% (113,000/200,000)

### 완료된 작업

#### 1. 리팩토링 계획 수립
- `REFACTOR_PLAN.md` - 전체 마스터 플랜
- `QUICK_REFACTOR_GUIDE.md` - 빠른 재개 가이드
- `.refactor_state.json` - 진행 상황 추적

#### 2. 디렉토리 구조 생성
```
youtube-ai/
├── core/                 # 핵심 엔진
├── providers/           # 외부 API 연동
│   ├── ai/             # Gemini, Claude, OpenAI
│   ├── stock/          # Pexels, Pixabay
│   └── tts/            # ElevenLabs, Google TTS
├── utils/              # 유틸리티
├── templates/          # 프롬프트 템플릿
├── config/             # 설정 파일
└── workflows/          # GitHub Actions
```

#### 3. 데이터 모델 (15개)
- Enums: VideoFormat, ContentStatus, AIProvider, TTSProvider
- Planner: ScriptSegment, ContentPlan
- Asset Manager: StockVideoAsset, AudioAsset, AssetBundle
- Editor: EditConfig, SubtitleSegment
- Uploader: YouTubeMetadata, UploadResult
- Orchestrator: ContentJob, SystemConfig

---

## Phase 2: AI Provider 구현

**완료 일시**: 2025-12-22

### 완료된 작업

#### 1. GeminiProvider (`providers/ai/gemini.py`)
- JSON 응답 생성 (`generate_json()`)
- 일반 텍스트 생성 (`generate_text()`)
- 사용량 추적 (`get_usage_stats()`)
- API 키 환경변수 관리

#### 2. 프롬프트 템플릿
- `templates/script_prompts/shorts_script.txt`
- `templates/metadata_prompts/title_description.txt`

---

## Phase 3: Planner 모듈 구현

**완료 일시**: 2025-12-22

### 완료된 작업

#### ContentPlanner (`core/planner.py`)
- 주제 아이디어 생성 (`generate_topic_ideas()`)
- AI 스크립트 생성 (`create_script()`)
- 메타데이터 최적화 (`optimize_metadata()`)
- 키워드 추출 (`extract_keywords()`)

---

## Phase 4: Stock Provider 구현

**완료 일시**: 2025-12-22

### 완료된 작업

#### 1. PexelsProvider (`providers/stock/pexels.py`)
- 영상 검색 (`search_videos()`)
- 영상 다운로드 (`download_video()`)
- 재시도 로직

#### 2. PixabayProvider (`providers/stock/pixabay.py`)
- 영상 검색 (`search_videos()`)
- 영상 다운로드 (`download_video()`)

---

## Phase 5: AssetManager 구현

**완료 일시**: 2025-12-22

### 완료된 작업

#### AssetManager (`core/asset_manager.py`)
- 전체 에셋 수집 (`collect_assets()`)
- 스톡 영상 수집 (멀티 provider)
- TTS 음성 생성 (gTTS, ElevenLabs)
- 캐시 시스템 (MD5 해시)

---

## Phase 6: Editor 구현

**완료 일시**: 2025-12-23

### 완료된 작업

#### VideoEditor (`core/editor.py`)
- MoviePy 통합
- 영상 생성 (`create_video()`)
- 클립 조정 및 연결
- 해상도 조정 (crop & resize)
- 자막 추가 (한글 지원)

---

## Phase 7: Uploader 구현

**완료 일시**: 2025-12-23

### 완료된 작업

#### YouTubeUploader (`core/uploader.py`)
- OAuth 2.0 인증
- 영상 업로드 (`upload_video()`)
- AI 메타데이터 생성 (`generate_metadata()`)
- 재시도 로직

---

## Phase 8: Orchestrator 구현

**완료 일시**: 2025-12-23

### 완료된 작업

#### ContentOrchestrator (`core/orchestrator.py`)
- 전체 파이프라인 관리
- 콘텐츠 생성 (`create_content()`)
- 작업 큐 관리
- 진행 상황 추적
- 에러 처리

#### 통합 테스트
- 전체 파이프라인 성공
- 에러 케이스 검증
- 성능 벤치마크

---

# 🚀 v4.0 업그레이드 프로젝트

## Phase 1: 데이터베이스 인프라

**완료 일시**: 2025-12-26

### 완료된 작업

#### 1. SQLAlchemy 통합
- SQLAlchemy 2.0.23 + Alembic 1.13.1
- `backend/database.py`: DB 세션 관리
- SQLite: `data/youtube_ai.db`

#### 2. ORM 모델 (`backend/models.py`)
- `Account`: 채널 계정 관리
- `AccountSettings`: 계정별 설정
- `JobHistory`: 작업 히스토리

#### 3. Pydantic 스키마 (`backend/schemas.py`)
- AccountCreate, AccountUpdate, AccountResponse
- AccountSettingsUpdate, AccountSettingsResponse
- JobHistoryResponse

#### 4. Account API (`backend/routers/accounts.py`)
- `POST /api/accounts/` - 계정 생성
- `GET /api/accounts/` - 계정 목록
- `GET /api/accounts/{id}` - 계정 상세
- `PUT /api/accounts/{id}/settings` - 설정 업데이트

#### 5. Alembic Migration
- 초기 마이그레이션 생성
- 3개 테이블 생성 완료

---

## Phase 2: 미디어 엔진 고도화

**완료 일시**: 2025-12-26

### 완료된 작업

#### 1. BGM 모델 (`core/models.py`)
- `MoodType` enum (6가지: HAPPY, SAD, ENERGETIC, CALM, TENSE, MYSTERIOUS)
- `BGMAsset` 모델
- `TemplateConfig` 모델
- `AssetBundle.bgm` 필드 추가

#### 2. BGM 매니저 (`core/bgm_manager.py`, 272줄)
- 카탈로그 관리 (JSON 기반)
- Mood별 BGM 선택
- 주제/톤 기반 분위기 자동 추론
- BGM 처리 (Pydub: 페이드, 볼륨, 루프)

**주요 메서드**:
- `add_bgm()`: BGM 파일 추가
- `get_bgm_by_mood()`: 분위기별 선택
- `auto_select_mood()`: 자동 분위기 추론
- `process_bgm()`: BGM 처리

#### 3. 템플릿 시스템 (3종)
- `templates/basic.json`: 기본 템플릿
- `templates/documentary.json`: 다큐멘터리
- `templates/entertainment.json`: 엔터테인먼트

**템플릿 비교**:
| 항목 | Basic | Documentary | Entertainment |
|------|-------|-------------|---------------|
| 폰트 크기 | 40 | 42 | 48 |
| 자막 색상 | white | #FFFFFF | #FFEB3B |
| 자막 위치 | bottom | bottom | center |
| BGM 분위기 | calm | calm | energetic |
| BGM 볼륨 | 0.25 | 0.2 | 0.35 |

#### 4. Planner 시간 제약 강화 (`core/planner.py`)
- `_validate_and_adjust_duration()` 메서드 추가
- 세그먼트 길이 자동 계산 (3글자/초)
- 비율 조정 (±5초 이상 차이 시)
- 미세 조정 (마지막 세그먼트)
- **효과**: 영상 길이 정확도 ±10초 → ±1초

#### 5. AssetManager BGM 통합 (`core/asset_manager.py`)
- `BGMManager` 통합
- `bgm_enabled` 파라미터 추가
- `_select_bgm()`: 주제/톤 기반 자동 선택
- `collect_assets()`에 BGM 수집 로직 추가

#### 6. Editor 템플릿 & BGM 믹싱 (`core/editor.py`)
- `_load_template()`: JSON 템플릿 로드
- `_load_audio_with_bgm()`: TTS + BGM 믹싱 (CompositeAudioClip)
- `_add_subtitles()`: 템플릿 기반 자막 스타일 (폰트, 색상, 위치)

#### 7. 수동 영상 업로드 (`scripts/manual_upload.py`, 280줄)
- CLI 모드: 인자로 메타데이터 전달
- 대화형 모드: 프롬프트 입력
- 예약 업로드 지원
- YouTubeUploader 통합

**사용 예시**:
```bash
# CLI 모드
python scripts/manual_upload.py --video output/video.mp4 --title "제목"

# 대화형 모드
python scripts/manual_upload.py --video output/video.mp4 --interactive
```

#### 8. BGM 설정 스크립트 (`scripts/setup_bgm.py`, 367줄)
- BGM 파일 추가 (`--add`)
- 디렉토리 스캔 (`--scan`)
- 카탈로그 통계 (`--stats`)
- 샘플 카탈로그 생성 (`--sample`)

**사용 예시**:
```bash
# BGM 추가
python scripts/setup_bgm.py --add music.mp3 --mood energetic

# 통계
python scripts/setup_bgm.py --stats
```

### 성과

**코드 변경**:
- 신규 파일: 5개 (bgm_manager.py, 3개 템플릿, 2개 스크립트)
- 수정 파일: 4개 (models, planner, asset_manager, editor)
- 총 추가: ~1,700줄

**기능 개선**:
| 항목 | v3.0 | v4.0 Phase 2 |
|------|------|--------------|
| BGM 지원 | ❌ | ✅ (6가지 분위기) |
| 템플릿 | ❌ | ✅ (3종) |
| 영상 길이 정확도 | ±10초 | ±1초 |
| 수동 업로드 | ❌ | ✅ |
| BGM 관리 도구 | ❌ | ✅ |

---

## 📊 전체 통계

### 리팩토링 프로젝트 (Phase 1~8)
- **기간**: 2일 (2025-12-22~23)
- **완료**: 8개 Phase
- **핵심 모듈**: 5개 (Planner, AssetManager, Editor, Uploader, Orchestrator)
- **Provider**: 5개 (Gemini, Pexels, Pixabay, gTTS, ElevenLabs)

### 업그레이드 프로젝트 (Phase 1~2)
- **기간**: 1일 (2025-12-26)
- **완료**: 2개 Phase
- **신규 기능**: 데이터베이스, BGM, 템플릿, 수동 업로드
- **API**: 4개 엔드포인트 추가

---

## 🔜 다음 단계

### v4.0 업그레이드 Phase 3~6 (예정)

- **Phase 3**: 멀티 계정 관리 고도화
- **Phase 4**: 스케줄링 시스템
- **Phase 5**: 모니터링 & 통계
- **Phase 6**: Frontend 통합

---

**마지막 업데이트**: 2025-12-26
**문서 버전**: 1.0
