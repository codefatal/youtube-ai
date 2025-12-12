"""
YouTube Video Downloader - yt-dlp 기반
해외 인기 영상 다운로드 및 자막 추출
"""
import os
import json
import yt_dlp
from typing import Dict, List, Optional
from pathlib import Path


class YouTubeDownloader:
    """YouTube 영상 및 자막 다운로드"""

    def __init__(self, download_dir: str = './downloads'):
        """
        Args:
            download_dir: 다운로드 디렉토리
        """
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)

    def download_video(
        self,
        url: str,
        download_subtitles: bool = True,
        subtitle_lang: str = 'en',
        video_format: str = 'best[height<=1080]'
    ) -> Dict:
        """YouTube 영상 다운로드

        Args:
            url: YouTube 영상 URL
            download_subtitles: 자막 다운로드 여부
            subtitle_lang: 자막 언어 (en, en-US 등)
            video_format: 영상 품질 (best, best[height<=720] 등)

        Returns:
            Dict: 다운로드 정보
                - video_id: YouTube 비디오 ID
                - video_path: 다운로드된 영상 경로
                - subtitle_path: 자막 파일 경로 (있으면)
                - info: 메타데이터
        """
        print(f"\n[INFO] 영상 다운로드 시작: {url}")

        # yt-dlp 옵션 설정
        ydl_opts = {
            'format': video_format,
            'outtmpl': os.path.join(self.download_dir, '%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
        }

        # 자막 다운로드 옵션
        if download_subtitles:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True  # 자동 생성 자막도 포함
            ydl_opts['subtitleslangs'] = [subtitle_lang, 'en', 'en-US']  # 우선순위
            ydl_opts['subtitlesformat'] = 'srt'  # SRT 형식

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 영상 정보 추출
                print("[INFO] 영상 정보 추출 중...")
                info = ydl.extract_info(url, download=True)

                video_id = info['id']
                video_ext = info['ext']
                video_path = os.path.join(self.download_dir, f"{video_id}.{video_ext}")

                # 자막 파일 찾기
                subtitle_path = None
                if download_subtitles:
                    # 가능한 자막 파일 경로들
                    possible_subtitles = [
                        os.path.join(self.download_dir, f"{video_id}.{subtitle_lang}.srt"),
                        os.path.join(self.download_dir, f"{video_id}.en.srt"),
                        os.path.join(self.download_dir, f"{video_id}.en-US.srt"),
                    ]

                    for sub_path in possible_subtitles:
                        if os.path.exists(sub_path):
                            subtitle_path = sub_path
                            print(f"[OK] 자막 파일 발견: {os.path.basename(sub_path)}")
                            break

                    if not subtitle_path:
                        print("[WARNING] 자막 파일을 찾을 수 없습니다")

                # 메타데이터 저장
                metadata_path = os.path.join(self.download_dir, f"{video_id}.info.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(info, f, ensure_ascii=False, indent=2)

                print(f"[OK] 다운로드 완료: {os.path.basename(video_path)}")

                return {
                    'success': True,
                    'video_id': video_id,
                    'video_path': video_path,
                    'subtitle_path': subtitle_path,
                    'metadata_path': metadata_path,
                    'info': self._extract_metadata(info)
                }

        except Exception as e:
            print(f"[ERROR] 다운로드 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_metadata(self, info: dict) -> Dict:
        """유용한 메타데이터만 추출

        Args:
            info: yt-dlp가 반환한 전체 정보

        Returns:
            Dict: 핵심 메타데이터
        """
        return {
            'video_id': info.get('id'),
            'title': info.get('title'),
            'description': info.get('description', '')[:500],  # 첫 500자만
            'channel': info.get('channel'),
            'channel_id': info.get('channel_id'),
            'channel_url': info.get('channel_url'),
            'duration': info.get('duration'),  # 초 단위
            'view_count': info.get('view_count', 0),
            'like_count': info.get('like_count', 0),
            'upload_date': info.get('upload_date'),  # YYYYMMDD 형식
            'categories': info.get('categories', []),
            'tags': info.get('tags', [])[:10],  # 상위 10개 태그
            'thumbnail': info.get('thumbnail'),
            'license': info.get('license'),
            'width': info.get('width'),
            'height': info.get('height'),
            'fps': info.get('fps'),
            'has_subtitles': bool(info.get('subtitles')),
            'automatic_captions': bool(info.get('automatic_captions')),
        }

    def get_video_info(self, url: str) -> Optional[Dict]:
        """영상 다운로드 없이 메타데이터만 추출

        Args:
            url: YouTube 영상 URL

        Returns:
            Dict: 메타데이터 또는 None
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._extract_metadata(info)
        except Exception as e:
            print(f"[ERROR] 정보 추출 실패: {e}")
            return None

    def check_subtitles_available(self, url: str, lang: str = 'en') -> bool:
        """자막 사용 가능 여부 확인

        Args:
            url: YouTube 영상 URL
            lang: 확인할 언어 코드

        Returns:
            bool: 자막 사용 가능 여부
        """
        info = self.get_video_info(url)
        if not info:
            return False

        return info.get('has_subtitles', False) or info.get('automatic_captions', False)

    def download_playlist(
        self,
        playlist_url: str,
        max_videos: int = 10,
        **kwargs
    ) -> List[Dict]:
        """플레이리스트 영상 다운로드

        Args:
            playlist_url: YouTube 플레이리스트 URL
            max_videos: 최대 다운로드 개수
            **kwargs: download_video()에 전달할 추가 인자

        Returns:
            List[Dict]: 다운로드 결과 리스트
        """
        print(f"\n[INFO] 플레이리스트 다운로드 시작: {playlist_url}")
        print(f"[INFO] 최대 {max_videos}개 영상")

        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # 플레이리스트 목록만 먼저 추출
        }

        results = []

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)

                entries = playlist_info.get('entries', [])
                total = min(len(entries), max_videos)

                print(f"[INFO] 총 {len(entries)}개 영상 발견, {total}개 다운로드 예정")

                for i, entry in enumerate(entries[:max_videos]):
                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    print(f"\n[{i+1}/{total}] {entry.get('title', 'Unknown')}")

                    result = self.download_video(video_url, **kwargs)
                    results.append(result)

        except Exception as e:
            print(f"[ERROR] 플레이리스트 처리 실패: {e}")

        print(f"\n[INFO] 플레이리스트 다운로드 완료: {len(results)}/{max_videos}개 성공")
        return results


# 테스트 코드
if __name__ == '__main__':
    downloader = YouTubeDownloader()

    # 테스트 URL (Creative Commons 영상)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 예시 (실제로는 CC 영상 사용)

    # 정보만 먼저 확인
    print("=== 영상 정보 확인 ===")
    info = downloader.get_video_info(test_url)
    if info:
        print(f"제목: {info['title']}")
        print(f"채널: {info['channel']}")
        print(f"길이: {info['duration']}초")
        print(f"조회수: {info['view_count']:,}")
        print(f"자막 있음: {info['has_subtitles']}")

    # 자막 확인
    has_subs = downloader.check_subtitles_available(test_url)
    print(f"\n자막 사용 가능: {has_subs}")

    # 실제 다운로드는 주석 처리 (필요시 활성화)
    # result = downloader.download_video(test_url)
    # print(f"\n다운로드 결과: {result}")
