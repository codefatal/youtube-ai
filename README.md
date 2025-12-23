# YouTube AI - 독창적 콘텐츠 자동 생성 시스템

AI 기반 완전 자동화 YouTube 콘텐츠 생성 파이프라인 - 기획부터 업로드까지 자동화

## 🎯 핵심 개념

**기존 "리믹스 시스템"에서 "독창적 콘텐츠 생성"으로 전환**

- ❌ **기존**: 해외 영상 다운로드 → 번역 → 재업로드 (저작권 위험)
- ✅ **현재**: AI가 주제 생성 → 스크립트 작성 → 무료 소재 수집 → 영상 제작 → 업로드 (100% 독창적)

### 왜 전환했나?

1. **저작권 안전**: 타인의 영상 재업로드는 채널 정지 위험
2. **독창성**: AI 생성 스크립트 + 저작권 프리 소재 = 완전히 새로운 콘텐츠
3. **지속 가능성**: YouTube의 중복 콘텐츠 정책 준수
4. **법적 안정성**: 모든 소재가 상업적 이용 가능 (Pexels, Pixabay)

## 💰 비용

### 💯 완전 무료 사용 가능!

- **AI (Gemini Flash)**: 무료 (월 1,500 requests)
- **스톡 영상 (Pexels/Pixabay)**: 무료 (상업적 이용 가능)
- **TTS (gTTS)**: 무료
- **영상 편집 (MoviePy/FFmpeg)**: 무료
- **YouTube API**: 무료 (일 10,000 쿼터)

**선택적 유료 옵션**:
- ElevenLabs TTS (고품질 음성): $5/월~
- Claude API (고급 AI): $20/월~

## 🚀 빠른 시작

### 1. 저장소 클론 및 환경 설정

```bash
git clone https://github.com/codefatal/youtube-ai.git
cd youtube-ai

# Python 가상환경 생성 (권장)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일 생성 (`.env.example` 참고):

```bash
# 필수
GEMINI_API_KEY=your_gemini_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here

# 선택 (더 많은 소재)
PIXABAY_API_KEY=your_pixabay_api_key_here

# 선택 (YouTube 업로드)
YOUTUBE_API_KEY=your_youtube_api_key_here
```

**API 키 발급 방법**:
- **Gemini**: https://aistudio.google.com/apikey (무료)
- **Pexels**: https://www.pexels.com/api/ (무료)
- **Pixabay**: https://pixabay.com/api/docs/ (무료)
- **YouTube**: https://console.cloud.google.com/apis/credentials

### 3. 빠른 테스트

```bash
# 1. AI 연결 테스트
python tests/test_planner.py

# 2. 스톡 영상 검색 테스트
python tests/test_asset_manager.py

# 3. 전체 파이프라인 테스트 (업로드 제외)
python scripts/auto_create.py \
  --topic "강아지 훈련 팁" \
  --format shorts \
  --duration 60 \
  --no-upload
```

## 📖 사용 방법

### CLI 사용 (스크립트)

#### 1. 자동 콘텐츠 생성

```bash
# 기본 사용 (AI가 주제 자동 생성)
python scripts/auto_create.py --upload

# 주제 지정
python scripts/auto_create.py \
  --topic "초보자를 위한 Python 팁" \
  --format shorts \
  --duration 60 \
  --upload

# 포맷 옵션
python scripts/auto_create.py \
  --format landscape \    # shorts, landscape, square
  --duration 300 \        # 초 단위
  --no-upload             # 로컬에만 저장
```

#### 2. 로컬 스케줄러 (매일 자동 실행)

```bash
# 스케줄러 시작 (매일 오전 9시 자동 실행)
python scripts/schedule_local.py

# 테스트 (즉시 실행)
python scripts/schedule_local.py --test
```

### Python 코드로 사용

```python
from core.orchestrator import ContentOrchestrator
from core.models import VideoFormat, SystemConfig, AIProvider, TTSProvider

# 설정
config = SystemConfig(
    ai_provider=AIProvider.GEMINI,
    tts_provider=TTSProvider.GTTS,
    default_format=VideoFormat.SHORTS,
    default_duration=60,
    auto_upload=False
)

# Orchestrator 생성
orchestrator = ContentOrchestrator(
    config=config,
    log_file="logs/my_job.log"
)

# 콘텐츠 생성
job = orchestrator.create_content(
    topic="건강한 아침 루틴",
    video_format=VideoFormat.SHORTS,
    target_duration=60,
    upload=False
)

# 결과 확인
print(f"영상 경로: {job.output_video_path}")
print(f"상태: {job.status.value}")

if job.upload_result and job.upload_result.success:
    print(f"YouTube URL: {job.upload_result.url}")
```

### GitHub Actions (자동 스케줄링)

#### 설정 방법

1. **GitHub Secrets 추가** (Repository → Settings → Secrets and variables → Actions)
   - `GEMINI_API_KEY`
   - `PEXELS_API_KEY`
   - `PIXABAY_API_KEY` (선택)
   - `YOUTUBE_API_KEY` (선택)

2. **자동 실행**
   - 매일 오전 9시 (KST) 자동 실행 (`.github/workflows/auto_create_content.yml`)

3. **수동 실행**
   - GitHub → Actions → "Auto Create YouTube Content" → Run workflow

## 🏗️ 시스템 아키텍처

### 전체 파이프라인

```
┌─────────────────────────────────────────────────────────────────┐
│                        ContentOrchestrator                       │
│                      (파이프라인 총괄 관리)                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
        ┌───────────────┐ ┌─────────────┐ ┌──────────┐
        │   Planner     │ │AssetManager │ │  Editor  │
        │ (AI 기획)     │ │ (소재 수집) │ │(영상편집)│
        └───────────────┘ └─────────────┘ └──────────┘
                │                 │              │
                ▼                 ▼              ▼
        ┌───────────────┐ ┌─────────────┐ ┌──────────┐
        │ContentPlan    │ │AssetBundle  │ │Video File│
        │(스크립트/키워드)│ │(영상/음성)   │ │(.mp4)    │
        └───────────────┘ └─────────────┘ └──────────┘
                                                  │
                                                  ▼
                                          ┌──────────┐
                                          │ Uploader │
                                          │(YouTube) │
                                          └──────────┘
```

### 핵심 모듈

#### 1. **Planner** (`core/planner.py`)
- **기능**: AI 기반 콘텐츠 기획
- **작업**:
  - 주제 아이디어 생성 (트렌드 분석)
  - 스크립트 작성 (타임스탬프 포함)
  - 키워드 추출 (영상/음악 검색용)
- **AI Provider**: Gemini Flash (무료)

#### 2. **Asset Manager** (`core/asset_manager.py`)
- **기능**: 스톡 소재 자동 수집
- **작업**:
  - 키워드 기반 영상 검색 (Pexels, Pixabay)
  - 자동 다운로드 및 캐싱
  - TTS 음성 생성 (gTTS, ElevenLabs)
- **소스**: 100% 저작권 프리 (상업적 이용 가능)

#### 3. **Editor** (`core/editor.py`)
- **기능**: 영상 합성 및 편집
- **작업**:
  - 영상 클립 자동 배치
  - 자막 생성 및 싱크
  - 트랜지션 효과
  - 배경 음악 믹싱 (선택)
- **엔진**: MoviePy 2.x

#### 4. **Uploader** (`core/uploader.py`)
- **기능**: YouTube 자동 업로드
- **작업**:
  - OAuth 2.0 인증
  - 메타데이터 자동 생성 (제목, 설명, 태그)
  - SEO 최적화
  - 예약 업로드 (선택)
  - 실패 시 자동 재시도
- **API**: YouTube Data API v3

#### 5. **Orchestrator** (`core/orchestrator.py`)
- **기능**: 전체 파이프라인 조율
- **작업**:
  - 작업 상태 관리 (State Machine)
  - 작업 큐 관리
  - 진행 상황 실시간 추적
  - 에러 핸들링 및 롤백
  - 로깅 및 통계

### 디렉토리 구조

```
youtube-ai/
├── core/                      # 핵심 모듈
│   ├── models.py              # Pydantic 데이터 모델 (15개)
│   ├── planner.py             # AI 기획 모듈
│   ├── asset_manager.py       # 소재 수집 모듈
│   ├── editor.py              # 영상 편집 모듈
│   ├── uploader.py            # YouTube 업로드 모듈
│   └── orchestrator.py        # 파이프라인 총괄
│
├── providers/                 # 외부 서비스 연동
│   ├── ai/                    # AI Provider (Gemini, Claude)
│   │   ├── gemini.py
│   │   └── __init__.py
│   ├── stock/                 # 스톡 영상 (Pexels, Pixabay)
│   │   ├── pexels.py
│   │   ├── pixabay.py
│   │   └── __init__.py
│   └── tts/                   # TTS (gTTS, ElevenLabs)
│       └── __init__.py
│
├── templates/                 # AI 프롬프트 템플릿
│   ├── script_prompts/
│   │   ├── shorts_script.txt
│   │   └── landscape_script.txt
│   └── metadata_prompts/
│       └── title_description.txt
│
├── scripts/                   # 자동화 스크립트
│   ├── auto_create.py         # CLI 콘텐츠 생성
│   └── schedule_local.py      # 로컬 스케줄러
│
├── tests/                     # 테스트 코드
│   ├── test_planner.py
│   ├── test_asset_manager.py
│   ├── test_editor.py
│   ├── test_uploader.py
│   └── test_orchestrator.py
│
├── .github/workflows/         # GitHub Actions
│   └── auto_create_content.yml
│
├── config/                    # 설정 파일
│   └── default.yaml
│
├── data/                      # 런타임 데이터
│   ├── cache/                 # 다운로드 캐시
│   └── job_history.json       # 작업 이력
│
├── output/                    # 생성된 영상
├── logs/                      # 로그 파일
│
└── legacy/                    # 기존 리믹스 시스템 (참고용)
```

## 📊 현재 상태

### ✅ 완료된 Phase (100%)

- **Phase 1**: 기반 구조 설계 (디렉토리, 데이터 모델)
- **Phase 2**: Planner 모듈 (AI 기획)
- **Phase 3**: Asset Manager (스톡 소재 수집)
- **Phase 4**: Editor 모듈 (영상 편집)
- **Phase 5**: Uploader 모듈 (YouTube 업로드)
- **Phase 6**: Orchestrator (파이프라인 통합)
- **Phase 7**: 자동화 및 스케줄링 (GitHub Actions, 로컬 스케줄러)

### 🔄 진행 중

- **Phase 8**: 테스트 및 최적화
  - 통합 테스트 작성
  - 성능 벤치마크
  - 에러 케이스 처리
  - 문서화 최종 업데이트

### 전체 진행률: **87.5%** (7/8 Phase 완료)

## 🎬 예제 출력물

### 1. Shorts (세로형 60초)

```
제목: "하루 10분으로 건강해지는 아침 루틴"
길이: 60초
해상도: 1080x1920 (9:16)
포맷: MP4
자막: 한국어 (gTTS 음성 + 자동 자막)
소재: Pexels 무료 영상 5-10개 + 트랜지션
```

### 2. Landscape (가로형 5분)

```
제목: "초보자를 위한 Python 기초 완전 정복"
길이: 300초
해상도: 1920x1080 (16:9)
포맷: MP4
자막: 한국어 (ElevenLabs 음성 + 자동 자막)
소재: Pixabay 무료 영상 15-20개 + 배경 음악
```

## 🔧 고급 설정

### 1. AI Provider 변경

```python
# Gemini (무료)
config = SystemConfig(ai_provider=AIProvider.GEMINI)

# Claude (유료, 고품질)
config = SystemConfig(ai_provider=AIProvider.CLAUDE)
```

### 2. TTS Provider 변경

```python
# gTTS (무료)
config = SystemConfig(tts_provider=TTSProvider.GTTS)

# ElevenLabs (유료, 고품질)
config = SystemConfig(tts_provider=TTSProvider.ELEVENLABS)
```

### 3. 영상 포맷 설정

```python
# Shorts (세로형)
VideoFormat.SHORTS       # 1080x1920 (9:16)

# Landscape (가로형)
VideoFormat.LANDSCAPE    # 1920x1080 (16:9)

# Square (정방형)
VideoFormat.SQUARE       # 1080x1080 (1:1)
```

### 4. 진행 상황 콜백

```python
def my_callback(message: str, progress: int):
    print(f"[{progress}%] {message}")

orchestrator = ContentOrchestrator(
    progress_callback=my_callback
)
```

## 🧪 테스트

### 개별 모듈 테스트

```bash
# Planner 테스트
python tests/test_planner.py

# Asset Manager 테스트
python tests/test_asset_manager.py

# Editor 테스트
python tests/test_editor.py

# Uploader 테스트
python tests/test_uploader.py

# Orchestrator 통합 테스트
python tests/test_orchestrator.py
```

### 전체 파이프라인 테스트

```bash
# 업로드 제외 (로컬 테스트)
python scripts/auto_create.py \
  --topic "테스트 주제" \
  --format shorts \
  --duration 60 \
  --no-upload

# 업로드 포함 (실제 배포)
python scripts/auto_create.py \
  --topic "테스트 주제" \
  --upload
```

## 📚 상세 문서

### 개발자 가이드

- **REFACTOR_PLAN.md**: 전체 리팩토링 계획 (8단계 Phase)
- **QUICK_REFACTOR_GUIDE.md**: 빠른 시작 가이드
- **CLAUDE.md**: Claude Code 사용 가이드
- **Phase 요약**: `PHASE1_SUMMARY.md` ~ `PHASE7_SUMMARY.md`

### Phase별 요약

- **Phase 1**: 디렉토리 구조 + 데이터 모델 (15개 Pydantic 모델)
- **Phase 2**: AI 프롬프트 + Gemini API wrapper + Planner
- **Phase 3**: Pexels/Pixabay API + Asset Manager + TTS
- **Phase 4**: MoviePy 영상 편집 + 자막 + 트랜지션
- **Phase 5**: YouTube API v3 + OAuth 2.0 + SEO 최적화 + 재시도
- **Phase 6**: 파이프라인 State Machine + 작업 큐 + 진행 추적 + 로깅
- **Phase 7**: GitHub Actions + 로컬 스케줄러 + CLI 스크립트

## 🔒 법적 고려사항

### ✅ 100% 합법적 사용

1. **AI 생성 스크립트**: 완전히 독창적
2. **스톡 영상**: Pexels/Pixabay (상업적 이용 허가)
3. **AI 음성**: gTTS/ElevenLabs (ToS 준수)
4. **YouTube 정책**: 중복 콘텐츠 없음

### ⚠️ 주의사항

- **출처 표시 불필요**: Pexels/Pixabay는 크레딧 불필요 (하지만 권장)
- **상업적 이용 가능**: 수익 창출 활성화 가능
- **재배포 금지**: 생성된 영상을 스톡 영상으로 재판매 불가

## 🤝 기여

이슈 및 PR 환영합니다!

- **GitHub**: https://github.com/codefatal/youtube-ai
- **Issues**: 버그 리포트, 기능 제안
- **Pull Requests**: 코드 개선, 문서 업데이트

### 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

MIT License

Copyright (c) 2025 YouTube AI Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

## 🎯 로드맵

### Phase 8 (진행 중)

- [ ] 통합 테스트 작성
- [ ] 성능 벤치마크
- [ ] 에러 케이스 처리 강화
- [ ] 최종 문서화

### 향후 계획

- [ ] 웹 UI 개선 (React 대시보드)
- [ ] 다국어 지원 (영어, 일본어)
- [ ] 고급 AI 기능 (음성 클로닝, 이미지 생성)
- [ ] 멀티 플랫폼 업로드 (TikTok, Instagram)
- [ ] CMS 통합 (Google Sheets, Notion)

## ⚡ 성능

### 벤치마크 (예상)

- **Shorts (60초)**: 5-10분 (AI 생성 + 영상 편집)
- **Landscape (300초)**: 15-20분
- **동시 작업**: 최대 3개 (메모리 제한)

### 최적화 팁

1. **캐싱 활용**: 다운로드한 영상은 `data/cache/`에 저장
2. **배치 처리**: 여러 영상을 한 번에 생성
3. **GitHub Actions**: 서버에서 자동 실행 (로컬 리소스 절약)

## 🙋 FAQ

### Q: 완전히 무료인가요?

A: 네! Gemini API (무료), Pexels/Pixabay (무료), gTTS (무료) 조합이면 0원입니다.

### Q: YouTube 업로드가 안 돼요.

A: `client_secrets.json` 파일이 필요합니다. [YouTube API 설정 가이드](https://developers.google.com/youtube/v3/quickstart/python) 참고.

### Q: 영상 품질이 낮아요.

A: ElevenLabs TTS (유료)를 사용하면 음성 품질이 크게 향상됩니다. `.env`에서 `ELEVENLABS_API_KEY` 설정.

### Q: 저작권 문제 없나요?

A: 100% 안전합니다. AI 생성 스크립트 + 상업적 이용 가능한 스톡 영상만 사용합니다.

### Q: 수익 창출 가능한가요?

A: 네! YouTube 파트너 프로그램 조건 충족 시 광고 수익 가능합니다.

---

**Made with ❤️ for YouTube Creators**

**GitHub**: https://github.com/codefatal/youtube-ai

**문의**: Issues 페이지로 문의주세요!
