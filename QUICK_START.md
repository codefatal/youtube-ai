# 🚀 빠른 시작 가이드 (5분 안에!)

## 1단계: 설치 (2분)

```bash
# 저장소 클론
git clone https://github.com/yourusername/ai-youtube-automation.git
cd ai-youtube-automation

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 2단계: API 키 설정 (2분)

### Gemini API 키 발급 (무료!)

1. https://makersuite.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. API 키 복사

### 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 다음 추가:
GEMINI_API_KEY=여기에_API_키_붙여넣기
AI_PROVIDER=gemini
TTS_PROVIDER=local
```

## 3단계: 첫 실행! (1분)

### 옵션 A: CLI로 실행

```bash
# 트렌드 분석
python local_cli/main.py analyze-trends --format short --ai gemini

# 대본 생성
python local_cli/main.py generate-script \
  --keywords "AI,기술,미래" \
  --format short \
  --duration 60 \
  --ai gemini

# 전체 자동화 (업로드 제외)
python local_cli/main.py full-automation --ai gemini --no-upload
```

### 옵션 B: Python 스크립트로 실행

```bash
python examples/simple_script_generation.py
```

## 완료! 🎉

이제 `./output/` 폴더를 확인하세요!

## 다음 단계

### YouTube 업로드 설정

1. https://console.cloud.google.com 접속
2. YouTube Data API v3 활성화
3. OAuth 2.0 클라이언트 ID 생성
4. `client_secrets.json` 다운로드 후 프로젝트 루트에 저장

### 고품질 TTS 설정 (선택)

```bash
# Google Cloud TTS (권장)
# 1. Google Cloud 프로젝트 생성
# 2. Text-to-Speech API 활성화
# 3. 서비스 계정 키 다운로드
# 4. .env에 추가:
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
TTS_PROVIDER=google
```

### 배경음악 추가 (선택)

```bash
# 폴더 구조 생성
python local_cli/main.py setup-music

# YouTube Audio Library에서 무료 음악 다운로드
# ./music/youtube_audio_library/upbeat/ 폴더에 추가
```

## 문제 해결

### "ModuleNotFoundError: No module named 'moviepy'"

```bash
pip install -r requirements.txt
```

### "FFmpeg not found"

```bash
# Ubuntu
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# https://ffmpeg.org/download.html 에서 다운로드
```

### "GEMINI_API_KEY not set"

`.env` 파일이 프로젝트 루트에 있고, `GEMINI_API_KEY=...`가 설정되어 있는지 확인

## 도움말

```bash
# 전체 명령어 보기
python local_cli/main.py --help

# 특정 명령어 도움말
python local_cli/main.py analyze-trends --help
```

## 다음 읽어보기

- [전체 README](README.md) - 상세 가이드
- [예제 스크립트](examples/) - 더 많은 예제
