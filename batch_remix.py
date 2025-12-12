"""
YouTube 리믹스 배치 처리 스크립트
트렌딩 영상 자동 다운로드 → 번역 → 리믹스
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

import time
from typing import List, Dict
from local_cli.services.trending_searcher import TrendingSearcher
from local_cli.services.youtube_downloader import YouTubeDownloader
from local_cli.services.subtitle_translator import SubtitleTranslator
from local_cli.services.metadata_manager import MetadataManager
from local_cli.services.video_remixer import VideoRemixer


class RemixBatchProcessor:
    """리믹스 배치 처리기"""

    def __init__(
        self,
        download_dir: str = './downloads',
        remix_dir: str = './remixed',
        metadata_dir: str = './metadata'
    ):
        """
        Args:
            download_dir: 다운로드 디렉토리
            remix_dir: 리믹스 영상 출력 디렉토리
            metadata_dir: 메타데이터 디렉토리
        """
        self.searcher = TrendingSearcher()
        self.downloader = YouTubeDownloader(download_dir=download_dir)
        self.translator = SubtitleTranslator()
        self.metadata_manager = MetadataManager(metadata_dir=metadata_dir)
        self.remixer = VideoRemixer()

        self.download_dir = download_dir
        self.remix_dir = remix_dir
        os.makedirs(remix_dir, exist_ok=True)

        self.stats = {
            'searched': 0,
            'downloaded': 0,
            'translated': 0,
            'remixed': 0,
            'failed': 0,
            'skipped': 0
        }

    def process_trending(
        self,
        region: str = 'US',
        category: str = 'Science & Technology',
        max_videos: int = 5,
        video_duration: str = 'short',
        min_views: int = 10000,
        target_lang: str = 'ko',
        skip_existing: bool = True
    ) -> Dict:
        """트렌딩 영상 자동 처리

        Args:
            region: 지역 코드
            category: 카테고리
            max_videos: 처리할 최대 영상 수
            video_duration: 'short', 'medium', 'long'
            min_views: 최소 조회수
            target_lang: 번역 목표 언어
            skip_existing: 이미 처리된 영상 스킵

        Returns:
            Dict: 처리 결과 통계
        """
        print("=" * 70)
        print("YouTube 리믹스 배치 처리 시작")
        print("=" * 70)

        # Step 1: 트렌딩 영상 검색
        print(f"\n[1/5] 트렌딩 영상 검색 중...")
        videos = self.searcher.search_trending_videos(
            region=region,
            category=category,
            max_results=max_videos,
            video_duration=video_duration,
            min_views=min_views,
            require_subtitles=True
        )

        self.stats['searched'] = len(videos)

        if not videos:
            print("[WARNING] 검색 결과가 없습니다")
            return self.stats

        print(f"[OK] {len(videos)}개 영상 발견")

        # Step 2-5: 각 영상 처리
        for i, video in enumerate(videos, 1):
            print(f"\n{'=' * 70}")
            print(f"영상 {i}/{len(videos)}: {video['title'][:50]}...")
            print(f"{'=' * 70}")

            video_id = video['video_id']

            # 이미 처리된 영상 스킵
            if skip_existing:
                existing = self.metadata_manager.get_video_metadata(video_id)
                if existing and existing.get('processing', {}).get('status') == 'completed':
                    print(f"[SKIP] 이미 처리된 영상: {video_id}")
                    self.stats['skipped'] += 1
                    continue

            try:
                # Step 2: 다운로드
                success = self._download_video(video)
                if not success:
                    self.stats['failed'] += 1
                    continue

                # Step 3: 번역
                success = self._translate_subtitles(video, target_lang)
                if not success:
                    self.stats['failed'] += 1
                    continue

                # Step 4: 메타데이터 저장
                self._save_metadata(video, target_lang)

                # Step 5: 리믹스
                success = self._remix_video(video)
                if not success:
                    self.stats['failed'] += 1
                    continue

                print(f"\n[OK] 영상 처리 완료: {video['title'][:50]}")
                self.metadata_manager.update_status(video_id, 'completed')

                # API 한도 보호 (1초 대기)
                time.sleep(1)

            except Exception as e:
                print(f"[ERROR] 처리 실패: {e}")
                self.stats['failed'] += 1
                self.metadata_manager.update_status(
                    video_id,
                    'failed',
                    error_message=str(e)
                )

        # 최종 결과
        print("\n" + "=" * 70)
        print("배치 처리 완료")
        print("=" * 70)
        print(f"\n[통계]")
        print(f"  - 검색: {self.stats['searched']}개")
        print(f"  - 다운로드: {self.stats['downloaded']}개")
        print(f"  - 번역: {self.stats['translated']}개")
        print(f"  - 리믹스: {self.stats['remixed']}개")
        print(f"  - 실패: {self.stats['failed']}개")
        print(f"  - 스킵: {self.stats['skipped']}개")

        return self.stats

    def _download_video(self, video: Dict) -> bool:
        """영상 다운로드

        Args:
            video: 영상 정보

        Returns:
            bool: 성공 여부
        """
        print(f"\n[2/5] 다운로드 중...")
        video_url = video['url']

        result = self.downloader.download_video(
            video_url,
            download_subtitles=True,
            subtitle_lang='en'
        )

        if result['success']:
            video['video_path'] = result['video_path']
            video['subtitle_path'] = result['subtitle_path']
            self.stats['downloaded'] += 1
            return True
        else:
            print(f"[ERROR] 다운로드 실패: {result.get('error')}")
            return False

    def _translate_subtitles(self, video: Dict, target_lang: str) -> bool:
        """자막 번역

        Args:
            video: 영상 정보
            target_lang: 목표 언어

        Returns:
            bool: 성공 여부
        """
        print(f"\n[3/5] 자막 번역 중...")

        if not video.get('subtitle_path'):
            print("[WARNING] 자막 파일 없음, 번역 스킵")
            return False

        subtitle_path = video['subtitle_path']
        translated_path = subtitle_path.replace('.en.srt', f'.{target_lang}.srt')

        result = self.translator.translate_srt_file(
            input_path=subtitle_path,
            output_path=translated_path,
            target_lang=target_lang,
            batch_size=10
        )

        if result['success']:
            video['translated_subtitle_path'] = translated_path
            self.stats['translated'] += 1
            return True
        else:
            print(f"[ERROR] 번역 실패: {result.get('error')}")
            return False

    def _save_metadata(self, video: Dict, target_lang: str):
        """메타데이터 저장

        Args:
            video: 영상 정보
            target_lang: 목표 언어
        """
        print(f"\n[4/5] 메타데이터 저장 중...")

        # 제목/설명 번역
        translated_metadata = self.translator.translate_metadata(
            title=video['title'],
            description=video.get('description', ''),
            target_lang=target_lang
        )

        metadata = {
            'video_id': video['video_id'],
            'original': {
                'url': video['url'],
                'title': video['title'],
                'description': video.get('description', '')[:500],
                'channel_name': video['channel_name'],
                'channel_url': video['channel_url'],
                'views': video['view_count'],
                'likes': video['like_count'],
                'duration': video['duration'],
                'upload_date': video.get('published_at'),
                'license': video.get('license'),
                'category': video.get('category_id'),
                'tags': video.get('tags', [])[:10],
            },
            'translated': {
                'title': translated_metadata['title'],
                'description': translated_metadata['description'],
                'subtitle_path': video.get('translated_subtitle_path'),
            },
            'processing': {
                'status': 'processing',
            },
            'files': {
                'original_video': video.get('video_path'),
                'original_subtitle': video.get('subtitle_path'),
                'translated_subtitle': video.get('translated_subtitle_path'),
                'remixed_video': os.path.join(
                    self.remix_dir,
                    f"{video['video_id']}_{target_lang}.mp4"
                ),
            },
            'copyright': {
                'attribution': f'Original: "{video["title"]}" by {video["channel_name"]}',
                'license': video.get('license'),
                'commercial_use': False,
                'modifications': True,
            }
        }

        self.metadata_manager.save_video_metadata(metadata)

    def _remix_video(self, video: Dict) -> bool:
        """영상 리믹스

        Args:
            video: 영상 정보

        Returns:
            bool: 성공 여부
        """
        print(f"\n[5/5] 영상 리믹스 중...")

        video_path = video.get('video_path')
        translated_subtitle_path = video.get('translated_subtitle_path')

        if not video_path or not translated_subtitle_path:
            print("[ERROR] 필요한 파일 없음")
            return False

        output_path = os.path.join(
            self.remix_dir,
            f"{video['video_id']}_ko.mp4"
        )

        result = self.remixer.add_translated_subtitles(
            video_path=video_path,
            subtitle_path=translated_subtitle_path,
            output_path=output_path
        )

        if result:
            self.stats['remixed'] += 1
            return True
        else:
            return False


# 실행 스크립트
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='YouTube 리믹스 배치 처리')
    parser.add_argument('--region', default='US', help='지역 코드 (기본: US)')
    parser.add_argument('--category', default='Science & Technology', help='카테고리')
    parser.add_argument('--max-videos', type=int, default=3, help='최대 영상 수 (기본: 3)')
    parser.add_argument('--duration', default='short', choices=['short', 'medium', 'long'], help='영상 길이')
    parser.add_argument('--min-views', type=int, default=10000, help='최소 조회수 (기본: 10,000)')
    parser.add_argument('--target-lang', default='ko', help='번역 언어 (기본: ko)')
    parser.add_argument('--no-skip', action='store_true', help='이미 처리된 영상도 재처리')

    args = parser.parse_args()

    processor = RemixBatchProcessor()

    stats = processor.process_trending(
        region=args.region,
        category=args.category,
        max_videos=args.max_videos,
        video_duration=args.duration,
        min_views=args.min_views,
        target_lang=args.target_lang,
        skip_existing=not args.no_skip
    )

    print("\n처리 완료!")
    print(f"성공: {stats['remixed']}개 / 실패: {stats['failed']}개")
