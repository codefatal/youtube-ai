"""
Pixabay API를 활용한 BGM 자동 다운로드 스크립트
테마별로 Royalty-Free 음원을 다운로드하고 manifest.json을 생성합니다.
"""
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any
import time

# .env 파일 로드
load_dotenv()

# API 설정
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
PIXABAY_AUDIO_URL = "https://pixabay.com/api/"

# 다운로드 설정
THEMES = {
    "cinematic": "cinematic orchestral epic",
    "upbeat": "upbeat energetic happy",
    "chill": "chill relax ambient"
}
ITEMS_PER_THEME = 10
OUTPUT_BASE_DIR = Path("frontend/public/assets/bgm")
MANIFEST_PATH = OUTPUT_BASE_DIR / "bgm_manifest.json"


def search_audio(theme_query: str, per_page: int = 20) -> List[Dict[str, Any]]:
    """
    Pixabay API로 오디오 검색

    Args:
        theme_query: 검색 쿼리 (예: "cinematic orchestral")
        per_page: 결과 개수 (최대 200)

    Returns:
        오디오 메타데이터 리스트
    """
    params = {
        "key": PIXABAY_API_KEY,
        "q": theme_query,
        "audio_type": "music",
        "per_page": per_page,
        "safesearch": "true"
    }

    print(f"  [SEARCH] Searching: '{theme_query}'...")
    response = requests.get(PIXABAY_AUDIO_URL, params=params)

    if response.status_code != 200:
        print(f"  [ERROR] API request failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return []

    data = response.json()
    total_hits = data.get("totalHits", 0)
    hits = data.get("hits", [])

    print(f"  [OK] {len(hits)} items fetched (total: {total_hits})")
    return hits


def download_audio(audio_data: Dict[str, Any], theme_name: str, index: int) -> Dict[str, Any] | None:
    """
    오디오 파일 다운로드

    Args:
        audio_data: Pixabay API 응답 데이터
        theme_name: 테마 이름 (cinematic, upbeat, chill)
        index: 파일 인덱스 (1부터 시작)

    Returns:
        다운로드 성공 시 메타데이터, 실패 시 None
    """
    # 다운로드 URL (preview_url은 미리듣기용, audio_url이 실제 파일)
    # Pixabay API는 무료 계정의 경우 preview만 제공할 수 있음
    download_url = audio_data.get("audio_url") or audio_data.get("preview_url")

    if not download_url:
        print(f"    [WARN] No download URL (ID: {audio_data.get('id')})")
        return None

    # 파일명 생성 (안전한 문자만 사용)
    title = audio_data.get("tags", f"bgm_{index}")
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')[:50]

    filename = f"{theme_name}_{index:02d}_{safe_title}.mp3"
    theme_dir = OUTPUT_BASE_DIR / theme_name
    theme_dir.mkdir(parents=True, exist_ok=True)

    file_path = theme_dir / filename

    # 이미 다운로드된 파일은 건너뛰기
    if file_path.exists():
        print(f"    [SKIP] File exists: {filename}")
        return {
            "title": audio_data.get("tags", "Unknown"),
            "file_path": f"/assets/bgm/{theme_name}/{filename}",
            "artist": audio_data.get("user", "Unknown Artist"),
            "pixabay_url": audio_data.get("pageURL", ""),
            "thumbnail": audio_data.get("userImageURL", ""),
            "duration": audio_data.get("duration", 0),
            "theme": theme_name
        }

    # 파일 다운로드
    try:
        print(f"    [DOWNLOAD] Downloading: {filename}...")
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"    [OK] Downloaded: {filename} ({file_size_mb:.2f} MB)")

        return {
            "title": audio_data.get("tags", "Unknown"),
            "file_path": f"/assets/bgm/{theme_name}/{filename}",
            "artist": audio_data.get("user", "Unknown Artist"),
            "pixabay_url": audio_data.get("pageURL", ""),
            "thumbnail": audio_data.get("userImageURL", ""),
            "duration": audio_data.get("duration", 0),
            "theme": theme_name
        }

    except Exception as e:
        print(f"    [ERROR] Download failed: {e}")
        return None


def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("[BGM] Pixabay BGM Auto Download Script")
    print("=" * 70)

    # API 키 확인
    if not PIXABAY_API_KEY:
        print("[ERROR] .env file does not contain PIXABAY_API_KEY")
        return

    print(f"[OK] API Key: {PIXABAY_API_KEY[:10]}...")
    print(f"[INFO] Save Path: {OUTPUT_BASE_DIR.absolute()}\n")

    # 출력 디렉토리 생성
    OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

    all_bgm_data = []

    # 테마별 다운로드
    for theme_name, theme_query in THEMES.items():
        print(f"\n{'='*70}")
        print(f"[THEME] {theme_name.upper()}")
        print(f"{'='*70}")

        # 오디오 검색
        audio_results = search_audio(theme_query, per_page=ITEMS_PER_THEME * 2)

        if not audio_results:
            print(f"  [WARN] No results for '{theme_name}'. Skipping.")
            continue

        # 상위 N개 다운로드
        downloaded_count = 0
        for i, audio_data in enumerate(audio_results, start=1):
            if downloaded_count >= ITEMS_PER_THEME:
                break

            metadata = download_audio(audio_data, theme_name, i)
            if metadata:
                all_bgm_data.append(metadata)
                downloaded_count += 1

            # API 레이트 리미트 방지 (초당 100 요청 제한 있을 수 있음)
            time.sleep(0.2)

        print(f"\n  [STATS] {theme_name} theme: {downloaded_count} downloaded")

    # Manifest JSON 생성
    print(f"\n{'='*70}")
    print("[MANIFEST] Creating bgm_manifest.json...")
    print(f"{'='*70}")

    manifest = {
        "version": "1.0",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": len(all_bgm_data),
        "themes": list(THEMES.keys()),
        "bgm_list": all_bgm_data
    }

    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Manifest saved: {MANIFEST_PATH.absolute()}")
    print(f"     Total {len(all_bgm_data)} BGM registered\n")

    # 요약 출력
    print(f"{'='*70}")
    print("[SUMMARY] Download Complete")
    print(f"{'='*70}")
    for theme_name in THEMES.keys():
        theme_count = sum(1 for bgm in all_bgm_data if bgm['theme'] == theme_name)
        print(f"  - {theme_name.capitalize()}: {theme_count} files")
    print(f"\n  Total {len(all_bgm_data)} BGM downloaded!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
