# 문제 해결 가이드

## 일반적인 문제

### 1. ModuleNotFoundError

**증상:**
```
ModuleNotFoundError: No module named 'moviepy'
```

**해결:**
```bash
# 가상환경 활성화 확인
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 의존성 재설치
pip install -r requirements.txt
```

### 2. FFmpeg 오류

**증상:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**해결:**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
1. https://ffmpeg.org/download.html 접속
2. Windows builds 다운로드
3. 압축 해제 후 `bin` 폴더를 환경 변수 PATH에 추가
4. 터미널 재시작 후 `ffmpeg -version` 확인

### 3. API 키 오류

**증상:**
```
ValueError: GEMINI_API_KEY가 설정되지 않았습니다
```

**해결:**
```bash
# .env 파일 확인
cat .env  # Linux/macOS
type .env # Windows

# 다음이 포함되어 있는지 확인:
GEMINI_API_KEY=AIza...
```

### 4. YouTube OAuth 오류

**증상:**
```
FileNotFoundError: client_secrets.json 파일이 없습니다
```

**해결:**
1. Google Cloud Console (https://console.cloud.google.com) 접속
2. 프로젝트 생성 또는 선택
3. "API 및 서비스" > "라이브러리" > "YouTube Data API v3" 활성화
4. "사용자 인증 정보" > "사용자 인증 정보 만들기" > "OAuth 클라이언트 ID"
5. 애플리케이션 유형: "데스크톱 앱"
6. JSON 다운로드 → `client_secrets.json`으로 저장 → 프로젝트 루트에 배치

### 5. Google Cloud TTS 인증 오류

**증상:**
```
DefaultCredentialsError: Could not automatically determine credentials
```

**해결:**
```bash
# 서비스 계정 키 파일 확인
ls google-credentials.json  # Linux/macOS
dir google-credentials.json # Windows

# .env에 경로 설정
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json

# 또는 환경 변수로 설정
export GOOGLE_APPLICATION_CREDENTIALS="./google-credentials.json"  # Linux/macOS
set GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json       # Windows
```

## API 관련 문제

### 6. Gemini API 할당량 초과

**증상:**
```
ResourceExhausted: 429 Quota exceeded
```

**해결:**
```bash
# 옵션 1: Claude로 전환
# .env 파일:
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...

# 옵션 2: 잠시 대기 (15 RPM 제한)
# 옵션 3: auto 모드 사용 (자동 폴백)
AI_PROVIDER=auto
```

### 7. Claude API 오류

**증상:**
```
AuthenticationError: Invalid API key
```

**해결:**
```bash
# API 키 확인
# https://console.anthropic.com/account/keys

# .env에 올바른 키 설정
ANTHROPIC_API_KEY=sk-ant-api...
```

## 영상 제작 문제

### 8. 메모리 부족 오류

**증상:**
```
MemoryError: Unable to allocate array
```

**해결:**
```python
# 영상 해상도 낮추기
# local_cli/services/video_producer.py 수정:
clip = mp.ColorClip(size=(1280, 720), ...)  # 1920x1080 대신

# 또는 짧은 영상 제작
python local_cli/main.py produce-video --duration 30
```

### 9. 자막 오류

**증상:**
```
OSError: cannot open resource
```

**해결:**
```bash
# ImageMagick 설치 (자막 렌더링용)

# Ubuntu
sudo apt-get install imagemagick

# macOS
brew install imagemagick

# Windows
# https://imagemagick.org/script/download.php

# moviepy 설정 파일 수정
# venv/lib/python3.x/site-packages/moviepy/config_defaults.py
IMAGEMAGICK_BINARY = "magick"  # Windows
IMAGEMAGICK_BINARY = "/usr/local/bin/convert"  # Linux/macOS
```

### 10. TTS 음성 생성 오류

**증상:**
```
Exception: Text-to-speech failed
```

**해결:**
```bash
# 로컬 TTS로 테스트
TTS_PROVIDER=local

# pyttsx3 설치 확인
pip install pyttsx3

# Google TTS 사용 시 인증 확인
# google-credentials.json 파일 확인
```

## 업로드 문제

### 11. YouTube 업로드 실패

**증상:**
```
HttpError 403: Forbidden
```

**해결:**
1. YouTube Data API v3 활성화 확인
2. OAuth 동의 화면 설정 완료 확인
3. 앱 게시 상태 확인 (테스트 중/프로덕션)
4. `token.pickle` 삭제 후 재인증

```bash
rm token.pickle
python local_cli/main.py upload --video ./output/video.mp4 ...
```

### 12. 썸네일 업로드 실패

**증상:**
```
Warning: 썸네일 업로드 실패
```

**해결:**
- 썸네일 파일 존재 확인
- 파일 크기 < 2MB 확인
- 이미지 형식: JPG, PNG
- 해상도: 1280x720 이상

## 성능 문제

### 13. 영상 제작이 너무 느림

**최적화:**
```bash
# 1. 낮은 해상도 사용
# 2. 짧은 영상 제작
# 3. threads 증가

# video_producer.py:
final_video.write_videofile(
    fps=24,  # 30 대신
    preset='ultrafast',  # 'medium' 대신
    threads=8
)
```

### 14. AI 응답이 너무 느림

**최적화:**
```bash
# Gemini 사용 (더 빠름)
AI_PROVIDER=gemini

# 또는 max_tokens 줄이기
# script_generator.py:
max_tokens=1000  # 2000 대신
```

## 기타 문제

### 15. 파일 경로 오류 (Windows)

**증상:**
```
FileNotFoundError: [WinError 3] The system cannot find the path specified
```

**해결:**
```python
# 경로에 역슬래시 대신 슬래시 사용
output_path = './output/video.mp4'  # 올바름
# output_path = '.\\output\\video.mp4'  # 피하기
```

### 16. 한글 인코딩 오류

**증상:**
```
UnicodeDecodeError: 'cp949' codec can't decode
```

**해결:**
```python
# 파일 읽기/쓰기 시 encoding 명시
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
```

## 도움 받기

### 로그 확인

```bash
# 상세 로그로 실행
python local_cli/main.py --help

# 오류 메시지 전체 복사
```

### 이슈 제보

https://github.com/yourusername/ai-youtube-automation/issues

**포함 사항:**
1. 오류 메시지 전체
2. OS 및 Python 버전
3. 실행한 명령어
4. `.env` 설정 (API 키 제외)

### 커뮤니티

- Discord: (링크)
- Reddit: r/AIYouTubeAutomation

## 자주 묻는 질문 (FAQ)

**Q: 완전 무료로 사용 가능한가요?**
A: 네! Gemini API (무료) + 로컬 TTS + 무료 음악 = $0/월

**Q: 한국어 음성은 지원하나요?**
A: 네, Google TTS와 Azure TTS가 한국어를 지원합니다.

**Q: 하루 몇 개의 영상을 만들 수 있나요?**
A: Gemini 무료는 하루 1,500 요청 제한이 있어 약 50개 정도 가능합니다.

**Q: 영상 품질을 높이려면?**
A: Claude + ElevenLabs TTS + AI 이미지 생성 사용

**Q: 상업적 사용 가능한가요?**
A: MIT 라이선스이므로 자유롭게 사용 가능합니다. 단, YouTube 정책 준수 필요.
