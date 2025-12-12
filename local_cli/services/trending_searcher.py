"""
Trending Searcher - YouTube 트렌딩 영상 검색
YouTube Data API v3 기반, Creative Commons 필터링
"""
import os
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class TrendingSearcher:
    """YouTube 트렌딩 영상 검색 및 필터링"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: YouTube Data API 키 (없으면 환경변수에서 읽음)
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY가 필요합니다 (.env 파일 또는 인자)")

        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

        # 카테고리 ID 매핑
        self.categories = {
            'Science & Technology': '28',
            'Education': '27',
            'Entertainment': '24',
            'Music': '10',
            'Gaming': '20',
            'News & Politics': '25',
            'Howto & Style': '26',
            'Film & Animation': '1',
            'Comedy': '23',
        }

    def search_trending_videos(
        self,
        region: str = 'US',
        category: Optional[str] = None,
        max_results: int = 10,
        video_license: str = 'any',  # 'any', 'creativeCommon'
        video_duration: str = 'any',  # 'any', 'short', 'medium', 'long'
        min_views: int = 0,
        require_subtitles: bool = True
    ) -> List[Dict]:
        """트렌딩 영상 검색

        Args:
            region: 지역 코드 (US, KR, JP, GB 등)
            category: 카테고리 ('Science & Technology', 'Education' 등)
            max_results: 최대 결과 수
            video_license: 'any' 또는 'creativeCommon'
            video_duration: 'any', 'short' (<4분), 'medium' (4-20분), 'long' (>20분)
            min_views: 최소 조회수
            require_subtitles: 자막 필수 여부

        Returns:
            List[Dict]: 영상 정보 리스트
        """
        print(f"\n[INFO] 트렌딩 영상 검색 시작")
        print(f"  - 지역: {region}")
        print(f"  - 카테고리: {category or 'All'}")
        print(f"  - 라이선스: {video_license}")
        print(f"  - 길이: {video_duration}")
        print(f"  - 최소 조회수: {min_views:,}")

        try:
            # 검색 요청
            request_params = {
                'part': 'snippet,contentDetails,statistics',
                'chart': 'mostPopular',
                'regionCode': region,
                'maxResults': max_results * 2,  # 필터링 고려하여 2배 요청
            }

            # 카테고리 필터
            if category and category in self.categories:
                request_params['videoCategoryId'] = self.categories[category]

            # 라이선스 필터는 search()에서만 가능, videos().list()는 불가
            # 따라서 검색 후 라이선스 필터링

            request = self.youtube.videos().list(**request_params)
            response = request.execute()

            videos = []
            for item in response.get('items', []):
                video_info = self._parse_video_item(item)

                # 필터링
                if not self._apply_filters(
                    video_info,
                    video_license=video_license,
                    video_duration=video_duration,
                    min_views=min_views,
                    require_subtitles=require_subtitles
                ):
                    continue

                videos.append(video_info)

                if len(videos) >= max_results:
                    break

            print(f"[OK] {len(videos)}개 영상 발견")
            return videos

        except HttpError as e:
            print(f"[ERROR] YouTube API 오류: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] 검색 실패: {e}")
            return []

    def search_by_keywords(
        self,
        keywords: str,
        region: str = 'US',
        max_results: int = 10,
        video_license: str = 'any',
        video_duration: str = 'any',
        order: str = 'viewCount',  # 'viewCount', 'relevance', 'date', 'rating'
        require_subtitles: bool = True
    ) -> List[Dict]:
        """키워드로 영상 검색

        Args:
            keywords: 검색 키워드
            region: 지역 코드
            max_results: 최대 결과 수
            video_license: 'any' 또는 'creativeCommon'
            video_duration: 'any', 'short', 'medium', 'long'
            order: 정렬 기준
            require_subtitles: 자막 필수 여부

        Returns:
            List[Dict]: 영상 정보 리스트
        """
        print(f"\n[INFO] 키워드 검색: '{keywords}'")
        print(f"  - 지역: {region}")
        print(f"  - 정렬: {order}")

        try:
            # 검색 요청
            search_request = self.youtube.search().list(
                part='id',
                q=keywords,
                type='video',
                regionCode=region,
                maxResults=max_results * 2,
                order=order,
                videoLicense=video_license,
                videoDuration=video_duration,
                videoCaption='closedCaption' if require_subtitles else 'any'
            )

            search_response = search_request.execute()

            # 비디오 ID 추출
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

            if not video_ids:
                print("[WARNING] 검색 결과 없음")
                return []

            # 비디오 상세 정보 조회
            videos_request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            )

            videos_response = videos_request.execute()

            videos = []
            for item in videos_response.get('items', []):
                video_info = self._parse_video_item(item)
                videos.append(video_info)

                if len(videos) >= max_results:
                    break

            print(f"[OK] {len(videos)}개 영상 발견")
            return videos

        except HttpError as e:
            print(f"[ERROR] YouTube API 오류: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] 검색 실패: {e}")
            return []

    def _parse_video_item(self, item: Dict) -> Dict:
        """YouTube API 응답을 파싱

        Args:
            item: API 응답 아이템

        Returns:
            Dict: 정리된 영상 정보
        """
        snippet = item.get('snippet', {})
        content_details = item.get('contentDetails', {})
        statistics = item.get('statistics', {})

        # ISO 8601 duration 파싱 (PT1H2M3S → 초)
        duration_str = content_details.get('duration', 'PT0S')
        duration_seconds = self._parse_duration(duration_str)

        return {
            'video_id': item['id'],
            'title': snippet.get('title'),
            'description': snippet.get('description', '')[:500],
            'channel_name': snippet.get('channelTitle'),
            'channel_id': snippet.get('channelId'),
            'channel_url': f"https://www.youtube.com/channel/{snippet.get('channelId')}",
            'url': f"https://www.youtube.com/watch?v={item['id']}",
            'published_at': snippet.get('publishedAt'),
            'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url'),
            'category_id': snippet.get('categoryId'),
            'tags': snippet.get('tags', []),
            'duration': duration_seconds,
            'duration_str': duration_str,
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'license': content_details.get('licensedContent'),
            'caption': content_details.get('caption'),  # 'true' or 'false'
            'definition': content_details.get('definition'),  # 'hd' or 'sd'
        }

    def _parse_duration(self, duration_str: str) -> int:
        """ISO 8601 duration을 초로 변환

        Args:
            duration_str: PT1H2M3S 형식

        Returns:
            int: 초 단위 길이
        """
        import re

        # PT1H2M3S → 1시간 2분 3초
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    def _apply_filters(
        self,
        video: Dict,
        video_license: str,
        video_duration: str,
        min_views: int,
        require_subtitles: bool
    ) -> bool:
        """필터 조건 검사

        Args:
            video: 영상 정보
            video_license: 라이선스 조건
            video_duration: 길이 조건
            min_views: 최소 조회수
            require_subtitles: 자막 필수 여부

        Returns:
            bool: 통과 여부
        """
        # 조회수 필터
        if video['view_count'] < min_views:
            return False

        # 자막 필터
        if require_subtitles and video.get('caption') != 'true':
            return False

        # 길이 필터 (YouTube API의 기준과 동일)
        duration = video['duration']
        if video_duration == 'short' and duration >= 240:  # < 4분
            return False
        elif video_duration == 'medium' and (duration < 240 or duration >= 1200):  # 4-20분
            return False
        elif video_duration == 'long' and duration < 1200:  # > 20분
            return False

        # Creative Commons 필터는 API로 직접 불가능하므로 스킵
        # (실제로는 download 시점에 확인 가능)

        return True

    def filter_shorts(self, videos: List[Dict], max_duration: int = 60) -> List[Dict]:
        """숏폼 영상만 필터링

        Args:
            videos: 영상 리스트
            max_duration: 최대 길이 (초, 기본 60초)

        Returns:
            List[Dict]: 숏폼 영상 리스트
        """
        shorts = [v for v in videos if v['duration'] <= max_duration]
        print(f"[INFO] 숏폼 필터링: {len(shorts)}/{len(videos)}개")
        return shorts

    def filter_long_form(self, videos: List[Dict], min_duration: int = 180) -> List[Dict]:
        """롱폼 영상만 필터링

        Args:
            videos: 영상 리스트
            min_duration: 최소 길이 (초, 기본 3분)

        Returns:
            List[Dict]: 롱폼 영상 리스트
        """
        long_videos = [v for v in videos if v['duration'] >= min_duration]
        print(f"[INFO] 롱폼 필터링: {len(long_videos)}/{len(videos)}개")
        return long_videos

    def sort_by_views(self, videos: List[Dict], reverse: bool = True) -> List[Dict]:
        """조회수로 정렬

        Args:
            videos: 영상 리스트
            reverse: 내림차순 여부 (기본 True)

        Returns:
            List[Dict]: 정렬된 영상 리스트
        """
        return sorted(videos, key=lambda v: v['view_count'], reverse=reverse)

    def sort_by_engagement(self, videos: List[Dict], reverse: bool = True) -> List[Dict]:
        """참여도로 정렬 (좋아요 + 댓글)

        Args:
            videos: 영상 리스트
            reverse: 내림차순 여부 (기본 True)

        Returns:
            List[Dict]: 정렬된 영상 리스트
        """
        def engagement_score(v):
            return v['like_count'] + v['comment_count']

        return sorted(videos, key=engagement_score, reverse=reverse)


# 테스트 코드
if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

    from dotenv import load_dotenv
    load_dotenv()

    searcher = TrendingSearcher()

    # 1. 미국 트렌딩 영상 (과학/기술)
    print("=" * 70)
    print("테스트 1: 미국 트렌딩 영상 (Science & Technology)")
    print("=" * 70)

    videos = searcher.search_trending_videos(
        region='US',
        category='Science & Technology',
        max_results=5,
        video_duration='short',  # 숏폼만
        min_views=10000,
        require_subtitles=True
    )

    for i, video in enumerate(videos, 1):
        print(f"\n[{i}] {video['title']}")
        print(f"    채널: {video['channel_name']}")
        print(f"    조회수: {video['view_count']:,}")
        print(f"    길이: {video['duration']}초")
        print(f"    자막: {video.get('caption')}")
        print(f"    URL: {video['url']}")

    # 2. 키워드 검색
    print("\n" + "=" * 70)
    print("테스트 2: 키워드 검색 'AI technology explained'")
    print("=" * 70)

    videos = searcher.search_by_keywords(
        keywords='AI technology explained',
        region='US',
        max_results=3,
        order='viewCount',
        require_subtitles=True
    )

    for i, video in enumerate(videos, 1):
        print(f"\n[{i}] {video['title']}")
        print(f"    조회수: {video['view_count']:,}")
        print(f"    길이: {video['duration']}초")

    print("\n" + "=" * 70)
    print("테스트 완료!")
    print("=" * 70)
