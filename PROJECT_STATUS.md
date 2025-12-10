# 프로젝트 현황 요약 📊

마지막 업데이트: 2025-12-10

## 🎯 프로젝트 개요

**AI YouTube Automation** - 트렌드 분석부터 유튜브 업로드까지 완전 자동화된 영상 제작 시스템

### 핵심 가치
- ✅ Gemini 무료 API 활용으로 월 $0 운영 가능
- ✅ 웹 UI와 CLI 이중 인터페이스 제공
- ✅ 트렌드 분석 → 대본 생성 → 영상 제작 → 업로드 전체 자동화

---

## 📁 프로젝트 구조

```
youtubeAI/
├── backend/                    # FastAPI 백엔드 서버
│   ├── main.py                # API 엔드포인트
│   └── README.md
├── frontend/                   # Next.js 14 프론트엔드
│   ├── app/
│   │   ├── page.tsx           # 대시보드
│   │   ├── trends/            # 트렌드 분석
│   │   ├── scripts/           # 대본 생성
│   │   ├── videos/            # 영상 제작
│   │   ├── upload/            # 업로드
│   │   ├── automation/        # 전체 자동화
│   │   ├── costs/             # 비용 관리
│   │   └── settings/          # 설정
│   ├── components/
│   │   ├── Sidebar.tsx        # 사이드바
│   │   └── StatsCard.tsx      # 통계 카드
│   └── README.md
├── local_cli/                  # CLI 인터페이스
│   ├── main.py                # CLI 진입점
│   └── services/
│       ├── ai_service.py      # AI 통합 (Gemini/Claude)
│       ├── trend_analyzer.py  # 트렌드 분석
│       ├── script_generator.py # 대본 생성
│       ├── tts_service.py     # TTS 서비스
│       ├── audio_processor.py # 오디오 처리
│       ├── music_library.py   # 배경음악
│       ├── video_producer.py  # 영상 제작
│       └── youtube_uploader.py # 업로드
├── music/                      # 배경음악 폴더
├── output/                     # 출력 영상
├── temp/                       # 임시 파일
├── .env                        # 환경 변수 (사용자 생성)
├── .env.example               # 환경 변수 템플릿
├── requirements.txt           # Python 의존성
├── README.md                  # 메인 문서
├── QUICK_START.md            # 빠른 시작
├── PROJECT_SUMMARY.md        # 프로젝트 완성 요약
├── PROJECT_STATUS.md         # 이 파일
├── WEB_UI_GUIDE.md          # 웹 UI 가이드
├── TROUBLESHOOTING.md       # 문제 해결
├── VSCODE_GUIDE.md          # VSCode 통합
├── POWERSHELL_FIX.md        # PowerShell 설정
└── CLAUDE.md                # Claude Code 가이드
```

---

## ✅ 구현 완료된 기능

### 1. 웹 UI (Frontend)

#### 완전 구현
- ✅ **대시보드** (`/`)
  - 통계 카드 (총 영상, 월별 영상, 조회수, AI 비용)
  - API 연동 완료
  - 에러 시 기본값 0 표시
  - 빠른 액션 버튼

- ✅ **트렌드 분석** (`/trends`)
  - 지역 선택 (KR, US, JP, GB)
  - 영상 형식 선택 (숏폼/롱폼)
  - AI 분석 결과 표시 (키워드, 주제, 아이디어, 예상 조회수)
  - 설정 페이지와 연동 (기본 지역/형식 자동 적용)

- ✅ **대본 생성** (`/scripts`)
  - 키워드 입력
  - 영상 형식, 길이, 톤 설정
  - 여러 버전 생성 (A/B 테스트)
  - 복사 기능
  - 설정 페이지와 연동

- ✅ **전체 자동화** (`/automation`)
  - 원클릭 전체 프로세스 실행
  - 단계별 진행 상황 표시

- ✅ **비용 관리** (`/costs`)
  - Gemini/Claude 사용량 표시
  - 비용 절감 팁 제공
  - API 가격 정보

- ✅ **설정** (`/settings`)
  - AI 프로바이더 선택 (Auto/Gemini/Claude)
  - Gemini 모델 선택
  - 기본 지역/형식/톤 설정
  - localStorage 저장
  - 설정 변경 시 다른 페이지 자동 반영

- ✅ **사이드바 네비게이션**
  - 아이콘과 라벨
  - 현재 페이지 하이라이트

- ✅ **영상 제작** (`/videos`)
  - UI 완성
  - 무료 gTTS (Google Text-to-Speech) 통합
  - FFmpeg 기반 오디오/영상 처리
  - 진행 상황 실시간 표시
  - 완료 후 파일 경로 안내
  - 완전히 작동하는 기능

#### 개발 중 (안내 표시)
- ⚠️ **업로드** (`/upload`)
  - UI 완성
  - OAuth 인증 필요 안내 추가
  - YouTube OAuth 설정 필요

### 2. 백엔드 API (Backend)

#### 완전 구현
- ✅ **트렌드 분석 API** (`POST /api/trends/analyze`)
  - YouTube Data API 통합
  - Gemini AI 분석
  - 키워드, 주제, 아이디어, 예상 조회수 반환

- ✅ **대본 생성 API** (`POST /api/scripts/generate`)
  - Gemini/Claude AI 통합
  - 여러 버전 생성 지원
  - 타임스탬프 포함 대본

- ✅ **통계 API** (`GET /api/stats`)
  - 대시보드 통계 제공
  - 현재는 기본값 반환 (DB 미연동)

- ✅ **헬스 체크** (`GET /api/health`)
  - 서버 상태 확인

- ✅ **CORS 설정**
  - localhost:3000, 3001 허용

- ✅ **영상 제작 API** (`POST /api/videos/produce`)
  - VideoProducer 완전 구현
  - gTTS 무료 음성 합성
  - FFmpeg 기반 영상 처리
  - 실제 영상 파일 생성

#### 개발 중
- ⚠️ **업로드 API** (`POST /api/upload`)
  - 구현 완료 (OAuth 설정 필요)

- ⚠️ **전체 자동화 API** (`POST /api/automation/full`)
  - 구현 완료 (업로드 부분만 OAuth 필요)

### 3. AI 서비스 통합

- ✅ **Gemini API 통합**
  - 최신 SDK (`google-genai` v0.2.0+) 사용
  - 모델: `gemini-1.5-flash` (안정), `gemini-2.5-flash` (최신)
  - MAX_TOKENS 이슈 해결 (8000 토큰)
  - Thinking mode 토큰 고려
  - JSON 파싱 개선

- ✅ **Claude API 통합**
  - Sonnet 4.5 지원
  - 폴백 시스템

- ✅ **자동 폴백**
  - Gemini 실패 시 Claude로 자동 전환
  - AI_PROVIDER=auto 모드

### 4. CLI 인터페이스

- ✅ Click 기반 CLI
- ✅ 8개 명령어 (test-ai, analyze-trends, generate-script, produce-video, upload, full-automation, setup-music, list-music)
- ✅ 상세한 도움말

### 5. 문서화

- ✅ README.md - 전체 가이드
- ✅ QUICK_START.md - 5분 시작 가이드
- ✅ PROJECT_SUMMARY.md - 완성 요약
- ✅ WEB_UI_GUIDE.md - 웹 UI 사용법
- ✅ TROUBLESHOOTING.md - 문제 해결
- ✅ VSCODE_GUIDE.md - VSCode 통합
- ✅ POWERSHELL_FIX.md - PowerShell 설정
- ✅ CLAUDE.md - Claude Code 가이드 (신규)
- ✅ PROJECT_STATUS.md - 이 파일 (신규)

---

## 🔧 필요한 기능 (우선순위 순)

### 우선순위 1: 핵심 기능 완성

1. **데이터베이스 연동** ⭐ 최우선
   - [ ] 통계 데이터 저장/조회
   - [ ] 영상 메타데이터 저장
   - [ ] 비용 추적
   - 추천: SQLite (간단) 또는 PostgreSQL (확장성)

2. ~~**영상 제작 기능 활성화**~~ ✅ **완료!**
   - [x] gTTS 무료 TTS 통합
   - [x] FFmpeg 기반 오디오/영상 처리
   - [x] pydub 의존성 제거 (Python 3.14 호환)
   - [x] 영상 제작 파이프라인 테스트
   - [x] 프론트엔드 UX 개선

3. **YouTube OAuth 설정**
   - [ ] OAuth 2.0 클라이언트 ID 설정 가이드
   - [ ] credentials.json 관리
   - [ ] 업로드 기능 테스트

### 우선순위 2: 사용성 개선

4. **설정 백엔드 연동**
   - [ ] 설정을 서버에 저장
   - [ ] 사용자별 설정 관리

5. **영상 목록 및 관리**
   - [ ] 생성된 영상 목록 페이지
   - [ ] 영상 미리보기
   - [ ] 영상 삭제/수정

6. **에러 처리 개선**
   - [ ] 더 상세한 에러 메시지
   - [ ] Toast 알림 시스템
   - [ ] 에러 로깅

### 우선순위 3: 고급 기능

7. **스케줄링**
   - [ ] 정기적 자동 실행
   - [ ] Cron job 통합
   - [ ] 예약 업로드

8. **분석 대시보드**
   - [ ] 조회수 추적
   - [ ] A/B 테스트 결과
   - [ ] 키워드 성능 분석

9. **AI 이미지 생성**
   - [ ] Stable Diffusion 통합
   - [ ] DALL-E API
   - [ ] 자동 썸네일 생성

10. **다국어 지원**
    - [ ] 한국어/영어 UI
    - [ ] 다국어 대본 생성
    - [ ] 다국어 자막

---

## 🚀 실행 방법

### 웹 UI (추천)

**백엔드 실행:**
```bash
cd backend
python main.py
# http://localhost:8000 에서 실행
```

**프론트엔드 실행 (새 터미널):**
```bash
cd frontend
npm install  # 처음 한 번만
npm run dev
# http://localhost:3000 에서 실행
```

### CLI

```bash
# 가상환경 활성화
venv\Scripts\activate  # Windows

# 트렌드 분석
python local_cli/main.py analyze-trends --region KR --format short --ai gemini

# 대본 생성
python local_cli/main.py generate-script --keywords "AI,기술" --format short --duration 60 --ai gemini
```

---

## 📊 기술 스택

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Lucide Icons

### Backend
- FastAPI
- Python 3.10+
- Uvicorn

### AI/ML
- Google Gemini API
- Anthropic Claude API
- YouTube Data API v3

### 기타
- MoviePy (영상 편집)
- pydub (오디오 처리)
- FFmpeg (미디어 처리)

---

## 💰 비용 예상

### 현재 무료 사용 가능
- Gemini API: 무료 (트렌드 분석, 대본 생성, 메타데이터)
- YouTube Data API: 무료 (할당량 제한)
- **월 예상 비용: $0**

### 영상 제작 활성화 시
- Google Cloud TTS: ~$2-5/월
- **월 예상 비용: $2-5**

### 프리미엄 옵션
- Claude API: $15-30/월
- ElevenLabs TTS: $5/월
- **월 예상 비용: $20-35**

---

## 🔐 환경 변수

필수 `.env` 파일:

```env
# 필수
GEMINI_API_KEY=AIza...          # https://aistudio.google.com/apikey
YOUTUBE_API_KEY=...             # 트렌드 분석용

# 선택
ANTHROPIC_API_KEY=sk-ant-...    # Claude 사용 시
GEMINI_MODEL=gemini-1.5-flash   # 모델 선택
AI_PROVIDER=auto                # auto/gemini/claude
```

---

## 🐛 알려진 이슈

1. **통계 데이터**
   - 현재 하드코딩된 0 값 반환
   - 데이터베이스 연동 필요

2. ~~**영상 제작**~~ ✅ **해결됨!**
   - ~~Google Cloud TTS 서비스 계정 설정 필요~~ → gTTS 무료 사용
   - ~~MoviePy 및 FFmpeg 설치 필요~~ → FFmpeg 직접 사용
   - ~~pydub 의존성 오류~~ → FFmpeg 기반으로 재작성

3. **YouTube 업로드**
   - OAuth 2.0 인증 설정 필요
   - credentials.json 파일 필요

4. **설정 저장**
   - 현재 localStorage만 사용
   - 서버 연동 필요 (다중 기기 동기화)

---

## 📝 최근 변경사항

### 2025-12-10 (오후)
1. **영상 제작 기능 완전 구현** 🎉
   - gTTS (Google Text-to-Speech) 무료 서비스 통합
   - FFmpeg 기반 오디오 처리 (pydub 의존성 제거)
   - Python 3.14 호환성 완벽 해결
   - 실제 영상 파일 생성 테스트 완료

2. **프론트엔드 UX 대폭 개선**
   - 진행 상황 실시간 표시
   - 완료 후 파일 경로 안내
   - 파일 다운로드 방법 가이드
   - 새 영상 제작 및 YouTube 업로드 연결

3. **문서 업데이트**
   - CLAUDE.md 추가 (Claude Code 가이드)
   - PROJECT_STATUS.md 업데이트

### 2025-12-10 (오전)
1. **설정 페이지 연동**
   - 트렌드/대본/영상 페이지에서 설정 기본값 자동 적용
   - localStorage 기반 설정 저장

2. **Gemini API 업데이트**
   - 최신 SDK로 마이그레이션 (google-genai)
   - MAX_TOKENS 이슈 해결 (8000 토큰)
   - JSON 파싱 개선

3. **대시보드 API 연동**
   - 통계 API 구현
   - 에러 시 기본값 표시

---

## 📞 문의 및 기여

- GitHub: https://github.com/codefatal/youtube-ai
- Issues: 버그 리포트 및 기능 제안 환영

---

## 📄 라이선스

MIT License
