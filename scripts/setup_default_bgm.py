"""
기본 BGM 자동 다운로드 스크립트
YouTube Audio Library 무료 음악 다운로드
"""
import sys
import os
from pathlib import Path
import requests

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import MoodType

# 무료 BGM 다운로드 URL (저작권 없는 음악)
# Incompetech, Bensound 등의 무료 음악 사이트에서 직접 링크
FREE_BGM_URLS = {
    MoodType.HAPPY: {
        "name": "Happy Upbeat",
        "url": "https://www.bensound.com/bensound-music/bensound-ukulele.mp3",
        "license": "Bensound License"
    },
    MoodType.ENERGETIC: {
        "name": "Energetic Beat",
        "url": "https://www.bensound.com/bensound-music/bensound-creativeminds.mp3",
        "license": "Bensound License"
    },
    MoodType.CALM: {
        "name": "Calm Piano",
        "url": "https://www.bensound.com/bensound-music/bensound-relaxing.mp3",
        "license": "Bensound License"
    },
    MoodType.SAD: {
        "name": "Sad Piano",
        "url": "https://www.bensound.com/bensound-music/bensound-sadday.mp3",
        "license": "Bensound License"
    },
    MoodType.TENSE: {
        "name": "Tense Suspense",
        "url": "https://www.bensound.com/bensound-music/bensound-theelevatorbossanova.mp3",
        "license": "Bensound License"
    },
    MoodType.MYSTERIOUS: {
        "name": "Mysterious Ambient",
        "url": "https://www.bensound.com/bensound-music/bensound-deepblue.mp3",
        "license": "Bensound License"
    }
}


def download_bgm(mood: MoodType, output_dir: Path):
    """
    특정 분위기의 BGM 다운로드

    Args:
        mood: 분위기
        output_dir: 저장 디렉토리
    """
    bgm_info = FREE_BGM_URLS.get(mood)
    if not bgm_info:
        print(f"[WARNING] {mood.value} BGM 정보 없음")
        return False

    # mood별 폴더 생성
    mood_dir = output_dir / mood.value.upper()
    mood_dir.mkdir(parents=True, exist_ok=True)

    # 파일명 생성
    filename = f"{bgm_info['name'].replace(' ', '_').lower()}.mp3"
    filepath = mood_dir / filename

    # 이미 존재하면 스킵
    if filepath.exists():
        print(f"[SKIP] {mood.value} - {filename} (이미 존재)")
        return True

    try:
        print(f"[DOWNLOAD] {mood.value} - {bgm_info['name']}...")
        response = requests.get(bgm_info['url'], stream=True, timeout=60)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"[SUCCESS] {filepath}")
        return True

    except Exception as e:
        print(f"[ERROR] {mood.value} 다운로드 실패: {e}")
        if filepath.exists():
            filepath.unlink()
        return False


def setup_default_bgm():
    """기본 BGM 자동 다운로드"""
    print("=" * 60)
    print("기본 BGM 자동 다운로드")
    print("=" * 60)
    print()
    print("무료 BGM을 다운로드합니다 (Bensound - Creative Commons)")
    print("출처: https://www.bensound.com")
    print()

    # 프로젝트 루트 경로
    project_root = Path(__file__).parent.parent
    music_dir = project_root / "music"

    print(f"저장 위치: {music_dir}")
    print()

    # 각 분위기별 BGM 다운로드
    success_count = 0
    total_count = len(MoodType)

    for mood in MoodType:
        if download_bgm(mood, music_dir):
            success_count += 1

    print()
    print("=" * 60)
    print(f"다운로드 완료: {success_count}/{total_count}")
    print("=" * 60)

    if success_count > 0:
        print()
        print("[INFO] BGM이 성공적으로 다운로드되었습니다!")
        print("[INFO] 이제 영상 생성 시 자동으로 BGM이 적용됩니다.")
        print()
        print("[LICENSE] Bensound 음악은 다음 조건으로 사용 가능합니다:")
        print("  - 비상업적 사용: 무료")
        print("  - 상업적 사용: 라이선스 구매 필요")
        print("  - 자세한 내용: https://www.bensound.com/licensing")
    else:
        print()
        print("[ERROR] BGM 다운로드에 실패했습니다.")
        print("[INFO] 수동으로 BGM을 추가하려면:")
        print(f"  1. music/MOOD_NAME/ 폴더에 mp3 파일 추가")
        print(f"  2. 예: music/ENERGETIC/my_music.mp3")


if __name__ == "__main__":
    setup_default_bgm()
