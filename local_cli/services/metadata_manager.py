"""
Metadata Manager - 리믹스 영상 메타데이터 관리
출처 정보, 저작권, 처리 상태 추적
"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class MetadataManager:
    """리믹스 영상 메타데이터 및 출처 관리"""

    def __init__(self, metadata_dir: str = './metadata'):
        """
        Args:
            metadata_dir: 메타데이터 저장 디렉토리
        """
        self.metadata_dir = metadata_dir
        self.videos_file = os.path.join(metadata_dir, 'videos.json')
        os.makedirs(metadata_dir, exist_ok=True)

        # 메타데이터 파일이 없으면 생성
        if not os.path.exists(self.videos_file):
            self._save_db({})

    def _load_db(self) -> Dict:
        """메타데이터 DB 로드"""
        try:
            with open(self.videos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] DB 로드 실패: {e}, 빈 DB 생성")
            return {}

    def _save_db(self, db: Dict):
        """메타데이터 DB 저장"""
        try:
            with open(self.videos_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] DB 저장 실패: {e}")

    def save_video_metadata(self, video_data: Dict) -> bool:
        """영상 메타데이터 저장

        Args:
            video_data: 영상 메타데이터 (REMIX_ARCHITECTURE.md 스키마 참조)
                - video_id (필수)
                - original: 원본 영상 정보
                - translated: 번역 정보
                - processing: 처리 상태
                - files: 파일 경로들
                - copyright: 저작권 정보

        Returns:
            bool: 성공 여부
        """
        if 'video_id' not in video_data:
            print("[ERROR] video_id가 없습니다")
            return False

        video_id = video_data['video_id']

        try:
            db = self._load_db()

            # 메타데이터 업데이트
            if video_id in db:
                print(f"[INFO] 기존 메타데이터 업데이트: {video_id}")
                # 기존 데이터 병합
                db[video_id].update(video_data)
            else:
                print(f"[INFO] 새 메타데이터 저장: {video_id}")
                db[video_id] = video_data

            # 타임스탬프 자동 추가
            if 'processing' not in db[video_id]:
                db[video_id]['processing'] = {}

            db[video_id]['processing']['last_updated'] = datetime.now().isoformat()

            self._save_db(db)
            return True

        except Exception as e:
            print(f"[ERROR] 메타데이터 저장 실패: {e}")
            return False

    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """영상 메타데이터 조회

        Args:
            video_id: YouTube 비디오 ID

        Returns:
            Dict: 메타데이터 또는 None
        """
        db = self._load_db()
        return db.get(video_id)

    def list_videos(self, status: Optional[str] = None) -> List[Dict]:
        """영상 목록 조회

        Args:
            status: 필터링할 상태 (pending, processing, completed, failed)

        Returns:
            List[Dict]: 영상 메타데이터 리스트
        """
        db = self._load_db()
        videos = list(db.values())

        # 상태 필터링
        if status:
            videos = [
                v for v in videos
                if v.get('processing', {}).get('status') == status
            ]

        # 최신순 정렬
        videos.sort(
            key=lambda v: v.get('processing', {}).get('last_updated', ''),
            reverse=True
        )

        return videos

    def update_status(self, video_id: str, status: str, **extra_fields) -> bool:
        """영상 처리 상태 업데이트

        Args:
            video_id: YouTube 비디오 ID
            status: 새 상태 (pending, processing, completed, failed)
            **extra_fields: 추가 필드 (error_message 등)

        Returns:
            bool: 성공 여부
        """
        metadata = self.get_video_metadata(video_id)
        if not metadata:
            print(f"[WARNING] 메타데이터를 찾을 수 없습니다: {video_id}")
            return False

        # 상태 업데이트
        if 'processing' not in metadata:
            metadata['processing'] = {}

        metadata['processing']['status'] = status
        metadata['processing']['last_updated'] = datetime.now().isoformat()

        # 추가 필드
        for key, value in extra_fields.items():
            metadata['processing'][key] = value

        return self.save_video_metadata(metadata)

    def generate_attribution_text(self, video_id: str, format: str = 'full') -> str:
        """출처 표시 텍스트 생성

        Args:
            video_id: YouTube 비디오 ID
            format: 'full' (전체), 'short' (간단), 'markdown' (마크다운)

        Returns:
            str: 출처 표시 텍스트
        """
        metadata = self.get_video_metadata(video_id)
        if not metadata:
            return f"[ERROR] 메타데이터 없음: {video_id}"

        original = metadata.get('original', {})
        copyright_info = metadata.get('copyright', {})

        title = original.get('title', 'Unknown Title')
        channel = original.get('channel_name', 'Unknown Channel')
        url = original.get('url', f'https://youtube.com/watch?v={video_id}')
        license_type = copyright_info.get('license', original.get('license', 'Unknown License'))

        if format == 'short':
            return f"Original: \"{title}\" by {channel}"

        elif format == 'markdown':
            return f"""## 원본 영상 정보

**제목:** {title}
**채널:** {channel}
**출처:** {url}
**라이선스:** {license_type}

이 영상은 원작자의 허가 하에 번역 및 재업로드되었습니다.
Original video translated and reuploaded with permission.
"""

        else:  # full
            attribution = copyright_info.get('attribution', f'Original: "{title}" by {channel}')
            return f"""원본 영상: "{title}" by {channel}
출처: {url}
라이선스: {license_type}

{attribution}

이 영상은 원작자의 허가 하에 번역 및 재업로드되었습니다.
Original video translated and reuploaded with permission."""

    def get_stats(self) -> Dict:
        """전체 통계 조회

        Returns:
            Dict: 통계 정보
                - total: 전체 영상 수
                - by_status: 상태별 개수
                - total_views: 원본 영상 총 조회수
                - total_duration: 총 영상 길이
        """
        db = self._load_db()
        videos = list(db.values())

        stats = {
            'total': len(videos),
            'by_status': {},
            'total_views': 0,
            'total_duration': 0
        }

        for video in videos:
            # 상태별 카운트
            status = video.get('processing', {}).get('status', 'unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            # 조회수 합계
            views = video.get('original', {}).get('views', 0)
            stats['total_views'] += views

            # 영상 길이 합계
            duration = video.get('original', {}).get('duration', 0)
            stats['total_duration'] += duration

        return stats

    def delete_video(self, video_id: str, delete_files: bool = False) -> bool:
        """영상 메타데이터 삭제

        Args:
            video_id: YouTube 비디오 ID
            delete_files: 관련 파일도 삭제 여부

        Returns:
            bool: 성공 여부
        """
        metadata = self.get_video_metadata(video_id)
        if not metadata:
            print(f"[WARNING] 메타데이터를 찾을 수 없습니다: {video_id}")
            return False

        # 파일 삭제
        if delete_files:
            files = metadata.get('files', {})
            for file_path in files.values():
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"[OK] 파일 삭제: {os.path.basename(file_path)}")
                    except Exception as e:
                        print(f"[WARNING] 파일 삭제 실패: {e}")

        # 메타데이터 삭제
        db = self._load_db()
        if video_id in db:
            del db[video_id]
            self._save_db(db)
            print(f"[OK] 메타데이터 삭제: {video_id}")
            return True

        return False


# 테스트 코드
if __name__ == '__main__':
    manager = MetadataManager()

    # 테스트 메타데이터
    test_data = {
        'video_id': 'test123',
        'original': {
            'url': 'https://youtube.com/watch?v=test123',
            'title': 'Amazing AI Technology Explained',
            'description': 'In this video, we explore AI...',
            'channel_name': 'Tech Insider',
            'channel_url': 'https://youtube.com/@techinsider',
            'views': 1500000,
            'likes': 50000,
            'duration': 62,
            'upload_date': '2024-11-15',
            'license': 'Creative Commons Attribution',
        },
        'translated': {
            'title': '놀라운 AI 기술 설명',
            'description': '이 영상에서는 AI를 탐구합니다...',
        },
        'processing': {
            'status': 'completed',
            'download_date': '2025-12-12T10:30:00',
            'translation_date': '2025-12-12T10:35:00',
        },
        'files': {
            'original_video': './downloads/test123.mp4',
            'translated_subtitle': './downloads/test123.ko.srt',
        },
        'copyright': {
            'attribution': 'Original: "Amazing AI Technology Explained" by Tech Insider',
            'license': 'CC-BY 3.0',
            'commercial_use': True,
        }
    }

    print("=== 메타데이터 저장 테스트 ===")
    success = manager.save_video_metadata(test_data)
    print(f"저장 결과: {success}")

    print("\n=== 메타데이터 조회 테스트 ===")
    loaded = manager.get_video_metadata('test123')
    if loaded:
        print(f"제목: {loaded['original']['title']}")
        print(f"상태: {loaded['processing']['status']}")

    print("\n=== 출처 표시 텍스트 생성 ===")
    print(manager.generate_attribution_text('test123', format='full'))

    print("\n=== 전체 통계 ===")
    stats = manager.get_stats()
    print(f"전체 영상: {stats['total']}개")
    print(f"상태별: {stats['by_status']}")
