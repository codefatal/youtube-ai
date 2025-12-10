# AI YouTube Automation - 완전 자동 영상 제작 시스템

트렌드 분석부터 유튜브 업로드까지 **완전 자동화**된 AI 영상 제작 파이프라인

## 🎯 핵심 기능

- ✅ **YouTube 트렌드 분석** (AI 기반)
- ✅ **자동 대본 생성** (Gemini/Claude)
- ✅ **TTS 음성 생성** (다중 제공자 지원)
- ✅ **배경음악 자동 추가**
- ✅ **영상 자동 합성** (자막 포함)
- ✅ **YouTube 자동 업로드** (메타데이터 AI 생성)

## 💰 비용

### Gemini 무료 사용 (추천)
- **월 비용**: $0-5 (TTS만 유료)
- **대본 생성**: 무료 (Gemini Flash)
- **트렌드 분석**: 무료 (Gemini Flash)
- **메타데이터**: 무료 (Gemini Flash)

### Claude 프리미엄 (고품질)
- **월 비용**: $20-30
- **대본 생성**: Claude Sonnet 4.5
- **트렌드 분석**: Claude Sonnet 4.5

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/ai-youtube-automation.git
cd ai-youtube-automation

# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# FFmpeg 설치 (필수)
# Ubuntu: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
# Windows: https://ffmpeg.org/download.html
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
# 필수: GEMINI_API_KEY, YOUTUBE_API_KEY
# 선택: ANTHROPIC_API_KEY (Claude 사용 시)
```

**Gemini API 키 발급 (무료)**
1. https://makersuite.google.com/app/apikey 방문
2. "Create API Key" 클릭
3. API 키를 `.env`의 `GEMINI_API_KEY`에 붙여넣기

**YouTube API 키 발급**
1. https://console.cloud.google.com 방문
2. YouTube Data API v3 활성화
3. OAuth 2.0 클라이언트 ID 생성
4. `client_secrets.json` 다운로드

### 3. 첫 테스트

```bash
# AI 서비스 테스트
python local_cli/main.py test-ai --provider gemini

# 트렌드 분석
python local_cli/main.py analyze-trends --format short --ai gemini

# 대본 생성
python local_cli/main.py generate-script \
  --keywords "AI,technology,future" \
  --format short \
  --duration 60 \
  --ai gemini

# 전체 자동화 (테스트 - 업로드 제외)
python local_cli/main.py full-automation --ai gemini --no-upload
```

### 4. 음악 설정 (선택)

```bash
# 음악 폴더 구조 생성
python local_cli/main.py setup-music

# 무료 음악 다운로드 (YouTube Audio Library, Free Music Archive)
# 해당 폴더에 음악 파일 추가:
# - ./music/youtube_audio_library/upbeat/
# - ./music/youtube_audio_library/ambient/
# 등등
```

## 📖 사용 가이드

### 트렌드 분석

```bash
python local_cli/main.py analyze-trends \
  --region KR \
  --format short \
  --ai gemini
```

**옵션:**
- `--region`: 지역 코드 (US, KR, JP 등)
- `--format`: 영상 형식 (short, long)
- `--ai`: AI 제공자 (gemini, claude, auto)

### 대본 생성

```bash
python local_cli/main.py generate-script \
  --keywords "AI,기술,미래" \
  --format short \
  --duration 60 \
  --tone informative \
  --versions 3 \
  --ai gemini \
  --output ./scripts/my_script.txt
```

**옵션:**
- `--keywords`: 키워드 (쉼표로 구분)
- `--format`: 영상 형식 (short, long)
- `--duration`: 초 단위 길이
- `--tone`: 톤 (informative, entertaining, educational)
- `--versions`: 생성할 버전 수 (A/B 테스트용)
- `--output`: 출력 파일 경로

### 영상 제작

```bash
python local_cli/main.py produce-video \
  --script ./scripts/my_script.txt \
  --format short \
  --style short_trendy \
  --output ./output/my_video.mp4
```

**옵션:**
- `--script`: 대본 파일 경로 또는 직접 텍스트
- `--format`: 영상 형식 (short=9:16, long=16:9)
- `--style`: 스타일 프리셋 (short_trendy, long_educational)
- `--output`: 출력 영상 경로

### YouTube 업로드

```bash
python local_cli/main.py upload \
  --video ./output/my_video.mp4 \
  --keywords "AI,기술,미래" \
  --script ./scripts/my_script.txt \
  --ai gemini \
  --privacy public
```

**옵션:**
- `--video`: 영상 파일 경로
- `--keywords`: 메타데이터 생성용 키워드
- `--script`: 대본 파일 (메타데이터 생성에 사용)
- `--privacy`: 공개 설정 (public, private, unlisted)

### 전체 자동화

```bash
# 완전 자동 실행 (트렌드 분석 → 대본 생성 → 영상 제작 → 업로드)
python local_cli/main.py full-automation \
  --region US \
  --format short \
  --ai gemini \
  --duration 60
```

**옵션:**
- `--no-upload`: 업로드 단계 건너뛰기 (테스트용)

## 🎨 고급 설정

### AI Provider 선택

**.env 파일:**
```bash
# auto: Gemini 우선, 실패 시 Claude로 폴백
AI_PROVIDER=auto

# gemini: Gemini만 사용 (무료)
# AI_PROVIDER=gemini

# claude: Claude만 사용 (고품질)
# AI_PROVIDER=claude
```

### TTS Provider 선택

**.env 파일:**
```bash
# google: Google Cloud TTS (권장, 가성비)
TTS_PROVIDER=google

# local: pyttsx3 (무료, 품질 낮음)
# TTS_PROVIDER=local

# elevenlabs: ElevenLabs (최고 품질, $5/월)
# TTS_PROVIDER=elevenlabs
```

### 비디오 스타일 프리셋

- `short_trendy`: 숏폼, 활기찬 배경음악
- `long_educational`: 롱폼, 차분한 배경음악
- `long_storytelling`: 롱폼, 영화 같은 음악

## 📁 프로젝트 구조

```
ai-youtube-automation/
├── local_cli/
│   ├── main.py                 # CLI 진입점
│   └── services/
│       ├── ai_service.py       # Gemini/Claude 통합
│       ├── trend_analyzer.py   # 트렌드 분석
│       ├── script_generator.py # 대본 생성
│       ├── tts_service.py      # TTS
│       ├── audio_processor.py  # 오디오 처리
│       ├── music_library.py    # 배경음악
│       ├── video_producer.py   # 영상 제작
│       └── youtube_uploader.py # YouTube 업로드
├── music/                      # 배경음악 폴더
├── output/                     # 출력 파일
├── temp/                       # 임시 파일
├── .env                        # 환경 변수
├── requirements.txt            # Python 의존성
└── README.md                   # 이 파일
```

## 🔧 문제 해결

### FFmpeg 오류

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html에서 다운로드
# 환경 변수 PATH에 추가
```

### Google Cloud TTS 인증 오류

```bash
# 서비스 계정 키 다운로드 후
export GOOGLE_APPLICATION_CREDENTIALS="./google-credentials.json"

# 또는 .env에 추가
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
```

### YouTube OAuth 오류

1. `client_secrets.json`이 프로젝트 루트에 있는지 확인
2. YouTube Data API v3가 활성화되어 있는지 확인
3. OAuth 동의 화면 설정 완료 확인

### Gemini API 할당량 초과

```bash
# .env에서 Claude로 전환
AI_PROVIDER=claude

# 또는 하이브리드 모드 (기본값)
AI_PROVIDER=auto
```

## 💡 팁

### 비용 최소화

1. **Gemini 무료 사용**: AI_PROVIDER=gemini
2. **로컬 TTS**: TTS_PROVIDER=local (품질 낮음)
3. **무료 음악**: YouTube Audio Library 활용

### 품질 최대화

1. **Claude 사용**: AI_PROVIDER=claude
2. **ElevenLabs TTS**: TTS_PROVIDER=elevenlabs
3. **대본 여러 버전 생성**: --versions 5

### 효율적인 워크플로우

```bash
# 1. 트렌드 분석
python local_cli/main.py analyze-trends --format short --ai gemini

# 2. 여러 대본 생성 (A/B 테스트)
python local_cli/main.py generate-script \
  --keywords "트렌드키워드" \
  --format short \
  --duration 60 \
  --versions 3 \
  --output ./scripts/script.txt

# 3. 각 버전별 영상 제작
for i in 1 2 3; do
  python local_cli/main.py produce-video \
    --script ./scripts/script_v${i}.txt \
    --format short \
    --output ./output/video_v${i}.mp4
done

# 4. 최고 성능 영상 업로드
python local_cli/main.py upload \
  --video ./output/video_v1.mp4 \
  --keywords "키워드" \
  --script ./scripts/script_v1.txt
```

## 📊 비용 예시

### 시나리오 1: 완전 무료 (Gemini + 로컬 TTS)
- AI: $0 (Gemini 무료)
- TTS: $0 (pyttsx3 로컬)
- 음악: $0 (YouTube Audio Library)
- **총 월 비용: $0**

### 시나리오 2: 추천 (Gemini + Google TTS)
- AI: $0 (Gemini 무료)
- TTS: $2-5 (Google Cloud TTS)
- 음악: $0 (YouTube Audio Library)
- **총 월 비용: $2-5**

### 시나리오 3: 프리미엄 (Claude + ElevenLabs)
- AI: $15-30 (Claude API)
- TTS: $5 (ElevenLabs)
- 음악: $0 (YouTube Audio Library)
- **총 월 비용: $20-35**

## 🤝 기여

버그 리포트, 기능 제안, Pull Request 환영합니다!

## 📄 라이선스

MIT License

## 📞 문의

이슈 트래커: https://github.com/yourusername/ai-youtube-automation/issues
