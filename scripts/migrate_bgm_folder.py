"""
BGM 폴더 마이그레이션 스크립트
Phase 1: music/ → assets/bgm/ 이동

기존 music/ 폴더의 BGM 파일들을 assets/bgm/ 구조로 복사합니다.
"""
import shutil
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def migrate_bgm_files():
    """music/ → assets/bgm/ 마이그레이션"""

    old_music_dir = project_root / "music"
    new_bgm_dir = project_root / "assets" / "bgm"

    # assets/bgm 폴더 생성
    new_bgm_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("BGM 폴더 마이그레이션 시작")
    print("=" * 70)
    print(f"소스: {old_music_dir}")
    print(f"대상: {new_bgm_dir}")
    print()

    if not old_music_dir.exists():
        print(f"[WARNING] {old_music_dir} 폴더가 없습니다.")
        print("[INFO] music/ 폴더가 없으면 마이그레이션이 필요하지 않습니다.")
        print("[INFO] assets/bgm/ 폴더에 직접 BGM 파일을 추가하세요.")
        return

    # 각 mood 폴더 복사
    copied_count = 0
    for mood_folder in old_music_dir.iterdir():
        if not mood_folder.is_dir():
            continue

        # free_music_archive, youtube_audio_library 등 특수 폴더 제외
        if mood_folder.name.lower() in ["free_music_archive", "youtube_audio_library"]:
            print(f"[SKIP] {mood_folder.name} (특수 폴더)")
            continue

        # catalog.json 제외
        if mood_folder.name == "catalog.json":
            continue

        # 대상 폴더 생성
        target_folder = new_bgm_dir / mood_folder.name
        target_folder.mkdir(parents=True, exist_ok=True)

        # mp3 파일 복사
        mp3_files = list(mood_folder.glob("*.mp3"))
        for mp3_file in mp3_files:
            target_file = target_folder / mp3_file.name

            if target_file.exists():
                print(f"[EXISTS] {mood_folder.name}/{mp3_file.name}")
            else:
                shutil.copy2(mp3_file, target_file)
                print(f"[COPY] {mood_folder.name}/{mp3_file.name} → assets/bgm/{mood_folder.name}/")
                copied_count += 1

    # default 폴더 생성 (fallback용)
    default_folder = new_bgm_dir / "default"
    default_folder.mkdir(parents=True, exist_ok=True)

    # CALM 폴더의 파일 하나를 default로 복사 (fallback용)
    calm_folder = new_bgm_dir / "CALM"
    if calm_folder.exists():
        calm_files = list(calm_folder.glob("*.mp3"))
        if calm_files and not list(default_folder.glob("*.mp3")):
            default_file = default_folder / "default_calm.mp3"
            shutil.copy2(calm_files[0], default_file)
            print(f"\n[DEFAULT] {calm_files[0].name} → assets/bgm/default/ (fallback용)")
            copied_count += 1

    print()
    print("=" * 70)
    print(f"마이그레이션 완료: {copied_count}개 파일 복사됨")
    print("=" * 70)
    print()
    print("[NEXT] 다음 단계:")
    print("1. assets/bgm/ 폴더 구조 확인:")
    print("   - assets/bgm/HAPPY/")
    print("   - assets/bgm/SAD/")
    print("   - assets/bgm/ENERGETIC/")
    print("   - assets/bgm/CALM/")
    print("   - assets/bgm/TENSE/")
    print("   - assets/bgm/MYSTERIOUS/")
    print("   - assets/bgm/default/ (fallback)")
    print()
    print("2. 추가 BGM 파일을 원하는 mood 폴더에 넣으세요.")
    print("3. 프로그램 실행 시 자동으로 카탈로그가 생성됩니다.")
    print()


if __name__ == "__main__":
    migrate_bgm_files()
