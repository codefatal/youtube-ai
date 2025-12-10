#!/bin/bash
# 설치 스크립트 (Linux/macOS)

echo "🚀 AI YouTube Automation 설치 시작..."

# Python 버전 확인
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 버전: $python_version"

# 가상환경 생성
echo "\n📦 가상환경 생성 중..."
python3 -m venv venv

# 가상환경 활성화
echo "\n✅ 가상환경 활성화..."
source venv/bin/activate

# 의존성 설치
echo "\n📥 의존성 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# FFmpeg 확인
echo "\n🔍 FFmpeg 확인 중..."
if command -v ffmpeg &> /dev/null
then
    echo "✅ FFmpeg가 설치되어 있습니다."
    ffmpeg -version | head -n 1
else
    echo "⚠️ FFmpeg가 설치되지 않았습니다."
    echo "설치 방법:"
    echo "  - Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  - macOS: brew install ffmpeg"
fi

# .env 파일 생성
echo "\n📝 환경 변수 파일 생성..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env 파일이 생성되었습니다. API 키를 설정해주세요."
else
    echo "⚠️ .env 파일이 이미 존재합니다."
fi

# 폴더 생성
echo "\n📁 필요한 폴더 생성..."
mkdir -p output
mkdir -p temp
mkdir -p music/youtube_audio_library/upbeat
mkdir -p music/youtube_audio_library/ambient
mkdir -p music/youtube_audio_library/cinematic
mkdir -p music/free_music_archive

echo "\n✅ 설치 완료!"
echo "\n다음 단계:"
echo "1. .env 파일에 API 키 설정"
echo "2. python local_cli/main.py test-ai --provider gemini"
echo "3. QUICK_START.md 참고"
