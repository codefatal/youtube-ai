"""
Manual Video Upload Script
Phase 2: 수동 영상 업로드 기능

Usage:
  python scripts/manual_upload.py --video path/to/video.mp4
  python scripts/manual_upload.py --video path/to/video.mp4 --title "제목" --description "설명"
"""
import sys
import os
from pathlib import Path
import argparse
from datetime import datetime
from typing import Optional

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.uploader import YouTubeUploader
from core.models import YouTubeMetadata


def interactive_metadata() -> YouTubeMetadata:
    """
    대화형 메타데이터 입력

    Returns:
        YouTubeMetadata 객체
    """
    print("\n=== YouTube 메타데이터 입력 ===\n")

    title = input("제목 (최대 100자): ").strip()
    if not title:
        title = f"Uploaded Video {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    description = input("설명 (최대 5000자, 선택사항): ").strip()
    if not description:
        description = "Uploaded via YouTube AI v4.0"

    tags_input = input("태그 (쉼표로 구분, 선택사항): ").strip()
    tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else []

    category_id = input("카테고리 ID (기본값: 22 - People & Blogs): ").strip()
    if not category_id:
        category_id = "22"

    privacy_status = input("공개 상태 (public/private/unlisted, 기본값: private): ").strip().lower()
    if privacy_status not in ["public", "private", "unlisted"]:
        privacy_status = "private"

    publish_at_input = input("예약 업로드 시각 (형식: YYYY-MM-DD HH:MM, 선택사항): ").strip()
    publish_at = None
    if publish_at_input:
        try:
            publish_at = datetime.strptime(publish_at_input, "%Y-%m-%d %H:%M")
            print(f"예약 시각: {publish_at}")
        except ValueError:
            print("[WARNING] 잘못된 날짜 형식. 예약 업로드를 건너뜁니다.")

    return YouTubeMetadata(
        title=title,
        description=description,
        tags=tags,
        category_id=category_id,
        privacy_status=privacy_status,
        publish_at=publish_at
    )


def upload_video(
    video_path: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    category_id: str = "22",
    privacy_status: str = "private",
    publish_at: Optional[str] = None,
    interactive: bool = False
) -> bool:
    """
    영상 업로드

    Args:
        video_path: 영상 파일 경로
        title: 제목
        description: 설명
        tags: 태그 (쉼표로 구분)
        category_id: 카테고리 ID
        privacy_status: 공개 상태
        publish_at: 예약 업로드 시각 (YYYY-MM-DD HH:MM)
        interactive: 대화형 모드 여부

    Returns:
        업로드 성공 여부
    """
    # 1. 파일 존재 확인
    if not os.path.exists(video_path):
        print(f"[ERROR] 영상 파일을 찾을 수 없습니다: {video_path}")
        return False

    print(f"\n[Upload] 영상 파일: {video_path}")
    print(f"[Upload] 파일 크기: {os.path.getsize(video_path) / (1024**2):.2f} MB")

    # 2. 메타데이터 생성
    if interactive:
        metadata = interactive_metadata()
    else:
        # CLI 인자로 메타데이터 생성
        if not title:
            title = f"Uploaded Video {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        if not description:
            description = "Uploaded via YouTube AI v4.0"

        tag_list = [tag.strip() for tag in tags.split(',')] if tags else []

        publish_datetime = None
        if publish_at:
            try:
                publish_datetime = datetime.strptime(publish_at, "%Y-%m-%d %H:%M")
            except ValueError:
                print("[WARNING] 잘못된 날짜 형식. 예약 업로드를 건너뜁니다.")

        metadata = YouTubeMetadata(
            title=title,
            description=description,
            tags=tag_list,
            category_id=category_id,
            privacy_status=privacy_status,
            publish_at=publish_datetime
        )

    # 3. 메타데이터 출력
    print("\n=== 업로드 메타데이터 ===")
    print(f"제목: {metadata.title}")
    print(f"설명: {metadata.description}")
    print(f"태그: {', '.join(metadata.tags)}")
    print(f"카테고리: {metadata.category_id}")
    print(f"공개 상태: {metadata.privacy_status}")
    if metadata.publish_at:
        print(f"예약 시각: {metadata.publish_at}")
    print("=" * 50)

    # 4. 업로드 확인
    if interactive:
        confirm = input("\n업로드를 진행하시겠습니까? (y/N): ").strip().lower()
        if confirm != 'y':
            print("[CANCELLED] 업로드가 취소되었습니다.")
            return False

    # 5. 업로드 실행
    try:
        uploader = YouTubeUploader()

        print(f"\n[Upload] YouTube 업로드 시작...")
        result = uploader.upload_video(
            video_path=video_path,
            metadata=metadata
        )

        if result.success:
            print(f"\n{'='*70}")
            print(f"[SUCCESS] 업로드 완료!")
            print(f"{'='*70}")
            print(f"Video ID: {result.video_id}")
            print(f"URL: {result.url}")
            print(f"업로드 시각: {result.uploaded_at}")
            print(f"{'='*70}\n")
            return True
        else:
            print(f"\n[ERROR] 업로드 실패: {result.error}")
            return False

    except Exception as e:
        print(f"\n[ERROR] 업로드 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="YouTube AI v4.0 - Manual Video Upload",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 대화형 모드
  python scripts/manual_upload.py --video output/video.mp4 --interactive

  # CLI 모드
  python scripts/manual_upload.py --video output/video.mp4 --title "제목" --description "설명"

  # 예약 업로드
  python scripts/manual_upload.py --video output/video.mp4 --title "제목" --publish-at "2025-12-31 18:00"
        """
    )

    parser.add_argument(
        '--video',
        required=True,
        help='업로드할 영상 파일 경로'
    )

    parser.add_argument(
        '--title',
        help='영상 제목 (최대 100자)'
    )

    parser.add_argument(
        '--description',
        help='영상 설명 (최대 5000자)'
    )

    parser.add_argument(
        '--tags',
        help='태그 (쉼표로 구분, 예: "tag1,tag2,tag3")'
    )

    parser.add_argument(
        '--category',
        default='22',
        help='YouTube 카테고리 ID (기본값: 22 - People & Blogs)'
    )

    parser.add_argument(
        '--privacy',
        choices=['public', 'private', 'unlisted'],
        default='private',
        help='공개 상태 (기본값: private)'
    )

    parser.add_argument(
        '--publish-at',
        help='예약 업로드 시각 (형식: "YYYY-MM-DD HH:MM")'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='대화형 모드 (메타데이터를 프롬프트로 입력)'
    )

    args = parser.parse_args()

    # 업로드 실행
    success = upload_video(
        video_path=args.video,
        title=args.title,
        description=args.description,
        tags=args.tags,
        category_id=args.category,
        privacy_status=args.privacy,
        publish_at=args.publish_at,
        interactive=args.interactive
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
