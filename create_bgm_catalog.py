"""
BGM catalog.json 생성 스크립트 (mutagen 불필요)
"""
import json
import os
from pathlib import Path
import sys

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from core.models import MoodType

def create_catalog():
    """music/ 폴더를 스캔하여 catalog.json 생성"""
    music_dir = Path("music")
    if not music_dir.exists():
        print("[ERROR] music/ folder not found")
        return False

    catalog_data = []

    print("=" * 70)
    print("[CATALOG] Creating BGM catalog.json...")
    print("=" * 70)

    for mood in MoodType:
        mood_dir = music_dir / mood.value.upper()
        if not mood_dir.exists():
            print(f"  [SKIP] {mood.value.upper()}/ folder not found")
            continue

        # 해당 mood 폴더의 모든 mp3 파일 탐색
        mp3_files = list(mood_dir.glob("*.mp3"))
        if not mp3_files:
            print(f"  [WARN] No MP3 files in {mood.value.upper()}/")
            continue

        for mp3_file in mp3_files:
            # 기본 duration (실제 길이는 재생 시 확인)
            file_size_mb = mp3_file.stat().st_size / (1024 * 1024)
            estimated_duration = file_size_mb * 60  # 대략적인 길이 (1MB ≈ 60초)

            catalog_entry = {
                "name": mp3_file.stem.replace('_', ' ').title(),
                "mood": mood.value,
                "file_path": f"{mood.value.upper()}/{mp3_file.name}",
                "duration": round(estimated_duration, 2),
                "volume": 0.25,  # 기본 볼륨
                "artist": "Bensound",
                "license": "Bensound - Creative Commons",
                "url": "https://www.bensound.com"
            }
            catalog_data.append(catalog_entry)
            print(f"  [OK] {mood.value.upper()}/{mp3_file.name} ({file_size_mb:.2f} MB)")

    # catalog.json 저장 (music 폴더)
    catalog_path_music = music_dir / "catalog.json"
    try:
        with open(catalog_path_music, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] catalog.json created: {catalog_path_music.absolute()}")
        print(f"     Total {len(catalog_data)} BGM entries")
    except Exception as e:
        print(f"\n[ERROR] Failed to create catalog.json: {e}")
        return False

    # catalog.json 복사 (프론트엔드용)
    frontend_bgm_dir = Path("frontend/public/assets/bgm")
    frontend_bgm_dir.mkdir(parents=True, exist_ok=True)

    catalog_path_frontend = frontend_bgm_dir / "bgm_catalog.json"
    try:
        with open(catalog_path_frontend, 'w', encoding='utf-8') as f:
            json.dump({
                "version": "1.0",
                "source": "Bensound (https://www.bensound.com)",
                "license": "Creative Commons - Non-commercial use",
                "total_count": len(catalog_data),
                "moods": [mood.value for mood in MoodType],
                "bgm_list": catalog_data
            }, f, ensure_ascii=False, indent=2)
        print(f"[OK] bgm_catalog.json created: {catalog_path_frontend.absolute()}")
    except Exception as e:
        print(f"[ERROR] Failed to copy to frontend: {e}")

    print("\n" + "=" * 70)
    print("[SUMMARY] BGM Catalog Created Successfully")
    print("=" * 70)
    for mood in MoodType:
        count = sum(1 for item in catalog_data if item['mood'] == mood.value)
        if count > 0:
            print(f"  - {mood.value.capitalize()}: {count} files")
    print(f"\n  Total: {len(catalog_data)} BGM files")
    print("=" * 70 + "\n")

    return True


if __name__ == "__main__":
    create_catalog()
