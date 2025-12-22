# YouTube Remix System - 해외 영상 자동 번역 및 리믹스

해외 인기 영상을 자동으로 다운로드하고, 자막을 번역하여 한국어 숏폼으로 재가공하는 완전 자동화 시스템

## 🎯 핵심 기능

### ✅ 완전 구현된 기능
- **트렌딩 영상 검색** - YouTube Data API v3 기반, 14가지 카테고리 지원, 날짜 범위 검색, 정렬 (조회수/날짜/평점/관련성)
- **키워드 검색** - 맞춤형 영상 검색 (영상 길이, 최소 조회수 필터, 날짜 범위, 정렬 옵션)
- **영상 다운로드** - yt-dlp 기반 고품질 다운로드 (영상 + SRT 자막)
- **자막 번역** - Gemini API로 무료 번역 (타임스탬프 유지)
- **영상 리믹스** - MoviePy 2.x로 번역 자막 합성
- **하드코딩 자막 처리** - OCR로 영상 내 자막 추출 → 번역 → 재인코딩 (NEW!)
- **메타데이터 관리** - JSON 기반 영상 정보 및 출처 자동 기록
- **배치 자동화** - 검색 → 다운로드 → 번역 → 리믹스 전체 자동화
- **웹 UI** - Next.js 14 기반 직관적 인터페이스
- **REST API** - FastAPI 기반 백엔드

## 💰 비용

### 💯 완전 무료 사용 가능! 🎉
- **번역**: 무료 (Gemini Flash API)
- **영상 처리**: 무료 (FFmpeg, MoviePy)
- **OCR**: 무료 (EasyOCR)
- **YouTube 검색**: 무료 (YouTube Data API - 할당량 제한 있음)

## 🚀 빠른 시작

### 1. 저장소 클론 및 의존성 설치

```bash
git clone https://github.com/codefatal/youtube-ai.git
cd youtube-ai

# Python 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```bash
# 필수
GEMINI_API_KEY=your_gemini_api_key_here
YOUTUBE_API_KEY=your_youtube_data_api_key_here

# 선택 (Claude 사용 시)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
AI_PROVIDER=gemini  # 또는 claude, auto
```

**API 키 발급:**
- Gemini API: https://aistudio.google.com/apikey (무료)
- YouTube Data API: https://console.cloud.google.com/apis/credentials

### 3. 웹 UI 실행 (추천)

**백엔드 서버 실행:**
```bash
cd backend
python main.py
# http://localhost:8000 에서 실행
```

**프론트엔드 서버 실행 (새 터미널):**
```bash
cd frontend
npm install  # 최초 1회만
npm run dev
# http://localhost:3000 에서 실행
```

브라우저에서 `http://localhost:3000` 접속!

### 4. CLI 사용

```bash
# 가상환경 활성화 (선택)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 트렌딩 영상 검색
python local_cli/main.py search-trending --region US --category "Science & Technology"

# 영상 다운로드
python local_cli/main.py download-video --url "https://youtube.com/watch?v=..."

# 자막 번역
python local_cli/main.py translate-subtitle --subtitle-path "path/to/subtitle.srt"

# 영상 리믹스
python local_cli/main.py remix-video --video-path "video.mp4" --subtitle-path "translated.srt"

# 전체 자동화 (검색 → 다운로드 → 번역 → 리믹스)
python local_cli/main.py batch-remix --region US --max-videos 5
```

## 📖 주요 사용법

### 웹 UI 워크플로우

1. **영상 검색** (`/search`)
   - 트렌딩 검색: 지역, 카테고리, 영상 길이, 최소 조회수, **정렬 (조회수/날짜/평점/관련성)**, **날짜 범위** 선택
   - 키워드 검색: 검색어 입력 + 필터 설정 + **정렬 옵션** + **날짜 범위**
   - 다운로드 버튼 클릭 → 자동 다운로드 + 메타데이터 저장
   - ⚠️ **주의**: 트렌딩 검색에서 정렬/날짜 범위를 설정하면 일반 검색으로 전환됩니다 (YouTube API 제한)

2. **영상 목록** (`/videos`)
   - 다운로드한 모든 영상 확인
   - 상태별 필터링 (대기, 다운로드 완료, 번역 완료, 완료)
   - **하드코딩 자막 처리**: 스캔 아이콘 클릭 (영상 내 자막 OCR)
   - 파일 정보 확인

3. **배치 처리** (`/batch`)
   - 설정: 지역, 카테고리, 최대 영상 수 등
   - 시작 버튼 클릭 → 전체 자동화 실행
   - 실시간 진행 상황 모니터링 (3초마다 갱신)

### CLI 워크플로우

```bash
# 1단계: 트렌딩 영상 검색 (날짜 범위, 정렬 포함)
python local_cli/main.py search-trending \
  --region US \
  --category "Science & Technology" \
  --duration short \
  --min-views 10000 \
  --order date \
  --published-after "2024-01-01T00:00:00Z" \
  --published-before "2024-12-31T23:59:59Z"

# 2단계: 영상 다운로드
python local_cli/main.py download-video \
  --url "https://youtube.com/watch?v=VIDEO_ID"

# 3단계: 자막 번역
python local_cli/main.py translate-subtitle \
  --subtitle-path downloads/VIDEO_ID.en.srt \
  --target-lang ko

# 4단계: 영상 리믹스
python local_cli/main.py remix-video \
  --video-path downloads/VIDEO_ID.mp4 \
  --subtitle-path downloads/VIDEO_ID.ko.srt \
  --output final.mp4

# 또는 전체 자동화 (1~4단계 통합)
python local_cli/main.py batch-remix \
  --region US \
  --category "Science & Technology" \
  --max-videos 3 \
  --target-lang ko
```

## 🏗️ 시스템 아키텍처

### Backend (FastAPI)
```
local_cli/services/
├── trending_searcher.py      # YouTube 트렌딩/키워드 검색
├── youtube_downloader.py     # yt-dlp 영상 다운로드
├── subtitle_translator.py    # Gemini API 자막 번역
├── video_remixer.py          # MoviePy 영상 합성
├── metadata_manager.py       # JSON 메타데이터 관리
└── hardcoded_subtitle_processor.py  # OCR 자막 처리 (NEW!)
```

### Frontend (Next.js 14)
```
frontend/app/
├── page.tsx           # 대시보드
├── search/            # 영상 검색
├── videos/            # 영상 목록
├── batch/             # 배치 처리
└── settings/          # 설정
```

### API 엔드포인트
```
POST /api/search/trending         # 트렌딩 검색
POST /api/search/keywords          # 키워드 검색
POST /api/download                 # 영상 다운로드
POST /api/translate                # 자막 번역
POST /api/remix                    # 영상 리믹스
POST /api/batch/start              # 배치 시작
GET  /api/batch/status/{job_id}   # 배치 상태
GET  /api/videos                   # 영상 목록
POST /api/hardcoded-subtitle/process  # 하드코딩 자막 처리 (NEW!)
```

## 🆕 새로운 기능

### 하드코딩 자막 처리 (2025-12-12)

영상에 이미 인코딩된 자막을 OCR로 추출하고 번역하는 기능:

**처리 과정:**
1. EasyOCR로 영상 내 자막 추출
2. 자막 위치, 색상, 크기 분석
3. Gemini API로 번역
4. 원본 자막 영역을 검은 박스로 제거
5. 같은 위치에 번역 자막 재인코딩 (흰색 테두리 + 원본 스타일 유지)

**사용 방법:**
- 웹 UI: 영상 목록에서 보라색 스캔 아이콘 클릭
- CLI: `python test_hardcoded_subtitle.py`

**필요 패키지:**
```bash
pip install easyocr opencv-python-headless torch torchvision
```

## ⚠️ 저작권 주의사항

### 🔴 위험: 일반 영상 재업로드
일반 영상을 단순 번역해서 재업로드하면 **저작권 침해**로 채널 정지될 수 있습니다.

### ✅ 안전한 사용 방법

1. **Creative Commons 영상만 사용**
   ```python
   # 검색 시 CC 라이선스 필터 적용
   searcher.search_trending_videos(
       video_license='creativeCommon',
       ...
   )
   ```

2. **원 제작자 허락 받기**
   - 이메일로 번역 및 재업로드 허가 요청
   - 수익 공유 조건 협의

3. **Fair Use 조건 충족**
   - 교육, 비평, 리뷰 등 변형적 사용
   - 짧은 클립만 사용
   - 원본 링크 명시

4. **출처 명시**
   - 영상 설명란에 원본 링크 및 출처 명시
   - 메타데이터 관리자가 자동으로 생성해줌

## 📊 시스템 비교

### 현재 시스템 vs 일반 양산형 쇼츠 프로그램

| 항목 | 현재 시스템 | 일반 양산형 프로그램 |
|------|------------|-------------------|
| **영상 소스** | YouTube 검색 API | 수동 선택/크롤링 |
| **자막 처리** | SRT 번역 + 하드코딩 OCR | SRT만 또는 수동 |
| **번역** | Gemini API (무료) | 유료 API 필요 |
| **자동화** | 완전 자동 (배치) | 반자동/수동 |
| **웹 UI** | Next.js 대시보드 | 간단한 UI 또는 CLI만 |
| **메타데이터** | 자동 기록/관리 | 수동 관리 |
| **비용** | 무료 | 월 $20-50 |

### 장점
- ✅ 완전 무료 (Gemini API 사용)
- ✅ 검색부터 리믹스까지 완전 자동화
- ✅ 하드코딩 자막도 처리 가능 (OCR)
- ✅ 출처 자동 기록 (저작권 안전)
- ✅ 웹 UI + CLI 듀얼 인터페이스

### 개선 가능 영역
- ⚠️ OCR 정확도 (폰트/배경에 따라 다름)
- ⚠️ YouTube API 할당량 제한 (일 10,000 유닛)
- ⚠️ 하드코딩 자막 처리 시간 (1분 영상 ≈ 5-10분)

## 🔧 트러블슈팅

### 1. Gemini API 오류
```bash
# API 키 확인
echo $GEMINI_API_KEY  # Linux/Mac
echo %GEMINI_API_KEY%  # Windows

# 새 API 키 발급: https://aistudio.google.com/apikey
```

### 2. 영상 다운로드 실패
```bash
# yt-dlp 업데이트
pip install --upgrade yt-dlp
```

### 3. OCR 패키지 설치 오류
```bash
# 빌드 툴 문제 시
pip install easyocr opencv-python-headless --no-deps
pip install torch torchvision pyyaml python-bidi
```

### 4. 프론트엔드 포트 충돌
```bash
# 다른 포트 사용
npm run dev -- -p 3001
```

더 자세한 문제 해결은 `TROUBLESHOOTING.md` 참고

## 📚 문서

- **빠른 시작**: `QUICK_START.md`
- **웹 UI 가이드**: `WEB_UI_REMIX_GUIDE.md`
- **리믹스 아키텍처**: `REMIX_ARCHITECTURE.md`
- **프로젝트 상태**: `PROJECT_STATUS.md`
- **트러블슈팅**: `TROUBLESHOOTING.md`
- **개발자 가이드**: `CLAUDE.md`

## 🤝 기여

이슈 및 PR 환영합니다!
- GitHub Issues: https://github.com/codefatal/youtube-ai/issues
- 버그 리포트, 기능 제안, 문서 개선 모두 환영

## 📄 라이선스

MIT License

## ⚡ 효율적 사용 팁

### 1. Creative Commons 필터 활성화
```python
# trending_searcher.py 기본값 수정
video_license='creativeCommon'  # 기본값으로 설정
```

### 2. 배치 자동화 활용
- 웹 UI `/batch` 페이지에서 한 번에 여러 영상 처리
- 시간대별 자동 실행 (cron/Task Scheduler)

### 3. 하드코딩 자막은 필요시에만
- OCR은 시간이 오래 걸리므로 SRT 자막이 없는 경우만 사용
- 샘플링 간격 조정으로 속도↑ 정확도↓ 트레이드오프

### 4. YouTube API 할당량 관리
- 하루 10,000 유닛 제한 (검색 1회 = 100 유닛)
- `max_results` 를 적절히 조절 (기본 10개)

### 5. 메타데이터 활용
- 모든 영상의 출처가 자동 기록됨
- `metadata/videos.json` 에서 확인 가능
- 업로드 시 설명란에 자동 추가

---

**Made with ❤️ for YouTube Creators**

**⚠️ 주의**: 이 도구는 교육 및 개인 프로젝트 목적입니다. 상업적 사용 시 반드시 원 제작자의 허락을 받으세요.
