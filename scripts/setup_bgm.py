"""
BGM Setup Script
Phase 2: BGM 다운로드 및 카탈로그 생성

이 스크립트는 assets/music/ 디렉토리에 BGM 파일을 조직하고
catalog.json 메타데이터를 생성합니다.

Usage:
  # 로컬 BGM 파일 추가
  python scripts/setup_bgm.py --add path/to/music.mp3 --mood energetic --name "Upbeat Track"

  # 디렉토리의 모든 BGM 스캔 및 카탈로그 생성
  python scripts/setup_bgm.py --scan assets/music

  # 카탈로그 통계 출력
  python scripts/setup_bgm.py --stats
"""
import sys
import os
import shutil
import argparse
from pathlib import Path
from typing import Optional

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.bgm_manager import BGMManager
from core.models import MoodType


def add_bgm(
    file_path: str,
    mood: str,
    name: Optional[str] = None,
    artist: Optional[str] = None,
    license: Optional[str] = None,
    copy: bool = True
) -> bool:
    """
    BGM 파일을 추가하고 카탈로그에 등록

    Args:
        file_path: 음악 파일 경로
        mood: 분위기 (happy, sad, energetic, calm, tense, mysterious)
        name: 음악 이름
        artist: 아티스트
        license: 라이선스
        copy: assets/music/로 복사할지 여부

    Returns:
        성공 여부
    """
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {file_path}")
        return False

    # Mood 검증
    try:
        mood_enum = MoodType[mood.upper()]
    except KeyError:
        print(f"[ERROR] 잘못된 mood 값: {mood}")
        print(f"사용 가능한 mood: {', '.join([m.value for m in MoodType])}")
        return False

    # BGMManager 초기화
    bgm_manager = BGMManager()

    # 파일 복사
    if copy:
        # assets/music/{mood}/ 디렉토리 생성
        mood_dir = bgm_manager.music_dir / mood.lower()
        mood_dir.mkdir(parents=True, exist_ok=True)

        # 파일 복사
        dest_path = mood_dir / file_path.name
        shutil.copy2(file_path, dest_path)
        print(f"[BGM] 파일 복사: {file_path} → {dest_path}")
        target_path = dest_path
    else:
        target_path = file_path

    # 카탈로그에 추가
    try:
        bgm_asset = bgm_manager.add_bgm(
            file_path=str(target_path),
            mood=mood_enum,
            name=name,
            artist=artist,
            license=license
        )

        # 카탈로그 저장
        bgm_manager.save_catalog()

        print(f"\n[SUCCESS] BGM 추가 완료!")
        print(f"  이름: {bgm_asset.name}")
        print(f"  분위기: {bgm_asset.mood.value}")
        print(f"  길이: {bgm_asset.duration:.1f}초")
        print(f"  경로: {bgm_asset.local_path}")

        return True

    except Exception as e:
        print(f"[ERROR] BGM 추가 실패: {e}")
        return False


def scan_directory(directory: str) -> bool:
    """
    디렉토리를 스캔하여 BGM 파일 찾기

    Args:
        directory: 스캔할 디렉토리 경로

    Returns:
        성공 여부
    """
    directory = Path(directory)

    if not directory.exists():
        print(f"[ERROR] 디렉토리를 찾을 수 없습니다: {directory}")
        return False

    # 지원하는 오디오 확장자
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'}

    # BGMManager 초기화
    bgm_manager = BGMManager()

    # 파일 스캔
    found_files = []
    for ext in audio_extensions:
        found_files.extend(directory.glob(f"**/*{ext}"))

    if not found_files:
        print(f"[WARNING] {directory}에서 오디오 파일을 찾을 수 없습니다.")
        return False

    print(f"[BGM] {len(found_files)}개의 오디오 파일을 발견했습니다.\n")

    # 각 파일에 대해 mood 입력 받기
    for i, file_path in enumerate(found_files, 1):
        print(f"\n[{i}/{len(found_files)}] {file_path.name}")
        print(f"  경로: {file_path}")

        # Mood 입력
        print(f"  분위기 선택:")
        for j, mood in enumerate(MoodType, 1):
            print(f"    {j}. {mood.value}")

        mood_input = input(f"  분위기 번호 (1-{len(MoodType)}, s=skip): ").strip()

        if mood_input.lower() == 's':
            print(f"  [SKIP] {file_path.name} 건너뛰기")
            continue

        try:
            mood_index = int(mood_input) - 1
            mood = list(MoodType)[mood_index]
        except (ValueError, IndexError):
            print(f"  [WARNING] 잘못된 입력. 건너뜁니다.")
            continue

        # 이름 입력 (선택사항)
        name_input = input(f"  이름 (엔터=파일명 사용): ").strip()
        name = name_input if name_input else file_path.stem

        # 아티스트 입력 (선택사항)
        artist = input(f"  아티스트 (선택사항): ").strip() or None

        # BGM 추가
        try:
            bgm_asset = bgm_manager.add_bgm(
                file_path=str(file_path),
                mood=mood,
                name=name,
                artist=artist
            )
            print(f"  [SUCCESS] 추가 완료!")

        except Exception as e:
            print(f"  [ERROR] 추가 실패: {e}")

    # 카탈로그 저장
    bgm_manager.save_catalog()

    print(f"\n{'='*70}")
    print(f"[SUCCESS] BGM 스캔 및 카탈로그 생성 완료!")
    print(f"{'='*70}")

    return True


def show_statistics():
    """카탈로그 통계 출력"""
    bgm_manager = BGMManager()
    stats = bgm_manager.get_statistics()

    print("\n" + "="*70)
    print("BGM 카탈로그 통계")
    print("="*70)

    for mood, count in stats.items():
        if mood != "total":
            print(f"  {mood.ljust(15)}: {count}개")

    print("-"*70)
    print(f"  {'총계'.ljust(15)}: {stats['total']}개")
    print("="*70 + "\n")

    # 각 분위기별 BGM 목록
    for mood in MoodType:
        bgms = bgm_manager.list_bgms_by_mood(mood)
        if bgms:
            print(f"\n[{mood.value.upper()}]")
            for bgm in bgms:
                artist_info = f" - {bgm.artist}" if bgm.artist else ""
                print(f"  - {bgm.name}{artist_info} ({bgm.duration:.1f}초)")


def create_sample_catalog():
    """샘플 카탈로그 생성 (테스트용)"""
    print("[BGM] 샘플 카탈로그 생성 중...")

    bgm_manager = BGMManager()

    # 샘플 BGM 데이터 (실제 파일은 없지만 구조 예시)
    samples = [
        {
            "name": "Happy Day",
            "mood": MoodType.HAPPY,
            "duration": 120.0,
            "artist": "Sample Artist",
            "license": "CC BY 4.0"
        },
        {
            "name": "Calm Ocean",
            "mood": MoodType.CALM,
            "duration": 180.0,
            "artist": "Relaxing Music",
            "license": "CC0"
        },
        {
            "name": "Epic Energy",
            "mood": MoodType.ENERGETIC,
            "duration": 90.0,
            "artist": "Upbeat Tracks",
            "license": "CC BY 4.0"
        }
    ]

    for sample in samples:
        # 샘플 파일 경로 (실제로는 존재하지 않음)
        sample_path = bgm_manager.music_dir / sample["mood"].value / f"{sample['name']}.mp3"

        # 카탈로그에만 추가 (파일 생성 없이)
        from core.models import BGMAsset
        asset = BGMAsset(
            name=sample["name"],
            local_path=str(sample_path),
            mood=sample["mood"],
            duration=sample["duration"],
            artist=sample["artist"],
            license=sample["license"]
        )
        bgm_manager.catalog[sample["mood"]].append(asset)

    # 카탈로그 저장
    bgm_manager.save_catalog()

    print("[SUCCESS] 샘플 카탈로그 생성 완료!")
    print("실제 BGM을 추가하려면 --add 옵션을 사용하세요.")


def main():
    parser = argparse.ArgumentParser(
        description="YouTube AI v4.0 - BGM Setup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # BGM 파일 추가
  python scripts/setup_bgm.py --add music.mp3 --mood energetic --name "Upbeat Track"

  # 디렉토리 스캔
  python scripts/setup_bgm.py --scan path/to/music/folder

  # 통계 출력
  python scripts/setup_bgm.py --stats

  # 샘플 카탈로그 생성
  python scripts/setup_bgm.py --sample
        """
    )

    parser.add_argument(
        '--add',
        help='추가할 BGM 파일 경로'
    )

    parser.add_argument(
        '--mood',
        choices=[m.value for m in MoodType],
        help='BGM 분위기 (happy, sad, energetic, calm, tense, mysterious)'
    )

    parser.add_argument(
        '--name',
        help='BGM 이름 (기본값: 파일명)'
    )

    parser.add_argument(
        '--artist',
        help='아티스트 (선택사항)'
    )

    parser.add_argument(
        '--license',
        help='라이선스 (예: CC BY 4.0, CC0, etc.)'
    )

    parser.add_argument(
        '--no-copy',
        action='store_true',
        help='파일을 assets/music/으로 복사하지 않음'
    )

    parser.add_argument(
        '--scan',
        help='BGM 파일을 스캔할 디렉토리'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='BGM 카탈로그 통계 출력'
    )

    parser.add_argument(
        '--sample',
        action='store_true',
        help='샘플 카탈로그 생성 (테스트용)'
    )

    args = parser.parse_args()

    # 명령 실행
    if args.add:
        if not args.mood:
            print("[ERROR] --mood 옵션이 필요합니다.")
            parser.print_help()
            sys.exit(1)

        success = add_bgm(
            file_path=args.add,
            mood=args.mood,
            name=args.name,
            artist=args.artist,
            license=args.license,
            copy=not args.no_copy
        )
        sys.exit(0 if success else 1)

    elif args.scan:
        success = scan_directory(args.scan)
        sys.exit(0 if success else 1)

    elif args.stats:
        show_statistics()
        sys.exit(0)

    elif args.sample:
        create_sample_catalog()
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
