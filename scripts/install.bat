@echo off
REM 설치 스크립트 (Windows)

echo 🚀 AI YouTube Automation 설치 시작...

REM Python 버전 확인
python --version
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo https://www.python.org/downloads/ 에서 Python 3.11+ 설치
    pause
    exit /b 1
)

REM 가상환경 생성
echo.
echo 📦 가상환경 생성 중...
python -m venv venv

REM 가상환경 활성화
echo.
echo ✅ 가상환경 활성화...
call venv\Scripts\activate.bat

REM 의존성 설치
echo.
echo 📥 의존성 설치 중...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM FFmpeg 확인
echo.
echo 🔍 FFmpeg 확인 중...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ FFmpeg가 설치되지 않았습니다.
    echo https://ffmpeg.org/download.html 에서 다운로드
) else (
    echo ✅ FFmpeg가 설치되어 있습니다.
)

REM .env 파일 생성
echo.
echo 📝 환경 변수 파일 생성...
if not exist .env (
    copy .env.example .env
    echo ✅ .env 파일이 생성되었습니다. API 키를 설정해주세요.
) else (
    echo ⚠️ .env 파일이 이미 존재합니다.
)

REM 폴더 생성
echo.
echo 📁 필요한 폴더 생성...
mkdir output 2>nul
mkdir temp 2>nul
mkdir music\youtube_audio_library\upbeat 2>nul
mkdir music\youtube_audio_library\ambient 2>nul
mkdir music\youtube_audio_library\cinematic 2>nul
mkdir music\free_music_archive 2>nul

echo.
echo ✅ 설치 완료!
echo.
echo 다음 단계:
echo 1. .env 파일에 API 키 설정
echo 2. python local_cli\main.py test-ai --provider gemini
echo 3. QUICK_START.md 참고

pause
