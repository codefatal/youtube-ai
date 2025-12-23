"""
Pixabay Stock Video Provider
무료 스톡 영상 API wrapper
"""
import os
import requests
from typing import List, Optional, Dict, Any
from core.models import StockVideoAsset


class PixabayProvider:
    """Pixabay API 제공자"""

    BASE_URL = "https://pixabay.com/api/videos/"

    def __init__(self, api_key: Optional[str] = None):
        """
        Pixabay Provider 초기화

        Args:
            api_key: Pixabay API 키 (None이면 환경변수에서 가져옴)
        """
        self.api_key = api_key or os.getenv('PIXABAY_API_KEY')
        if not self.api_key:
            raise ValueError("PIXABAY_API_KEY가 설정되지 않았습니다")

    def search_videos(
        self,
        query: str,
        per_page: int = 5,
        video_type: str = "all"
    ) -> List[StockVideoAsset]:
        """
        키워드로 영상 검색

        Args:
            query: 검색 키워드 (영어)
            per_page: 결과 개수 (기본 5개, 최대 200)
            video_type: 영상 타입 (all/film/animation)

        Returns:
            StockVideoAsset 리스트
        """
        params = {
            'key': self.api_key,
            'q': query,
            'per_page': min(per_page, 200),
            'video_type': video_type
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            hits = data.get('hits', [])

            assets = []
            for video in hits:
                asset = self._parse_video(video, query)
                if asset:
                    assets.append(asset)

            print(f"[Pixabay] '{query}' 검색 완료: {len(assets)}개 발견")
            return assets

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Pixabay API 오류: {e}")
            return []

    def _parse_video(self, video_data: Dict[str, Any], keyword: str) -> Optional[StockVideoAsset]:
        """
        Pixabay API 응답을 StockVideoAsset으로 변환

        Args:
            video_data: Pixabay API 응답 데이터
            keyword: 검색 키워드

        Returns:
            StockVideoAsset 또는 None
        """
        try:
            video_id = str(video_data.get('id'))
            duration = video_data.get('duration', 0)

            # 비디오 파일 선택 (가장 높은 품질)
            videos = video_data.get('videos', {})

            # 우선순위: large > medium > small > tiny
            download_url = None
            resolution = "1080x1920"

            for quality in ['large', 'medium', 'small', 'tiny']:
                if quality in videos:
                    video_info = videos[quality]
                    download_url = video_info.get('url')
                    width = video_info.get('width', 1080)
                    height = video_info.get('height', 1920)
                    resolution = f"{width}x{height}"
                    break

            if not download_url:
                return None

            return StockVideoAsset(
                id=f"pixabay_{video_id}",
                url=download_url,
                provider="pixabay",
                keyword=keyword,
                duration=duration,
                resolution=resolution,
                downloaded=False
            )

        except Exception as e:
            print(f"[ERROR] Pixabay 비디오 파싱 실패: {e}")
            return None

    def download_video(
        self,
        asset: StockVideoAsset,
        output_dir: str = "./downloads/stock_videos"
    ) -> Optional[str]:
        """
        영상 다운로드

        Args:
            asset: StockVideoAsset 객체
            output_dir: 저장 디렉토리

        Returns:
            저장된 파일 경로 또는 None
        """
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{asset.id}.mp4"
        filepath = os.path.join(output_dir, filename)

        # 이미 다운로드된 경우
        if os.path.exists(filepath):
            print(f"[Pixabay] 이미 다운로드됨: {filename}")
            return filepath

        try:
            print(f"[Pixabay] 다운로드 시작: {filename}")
            response = requests.get(asset.url, stream=True, timeout=60)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"[SUCCESS] 다운로드 완료: {filepath}")
            return filepath

        except Exception as e:
            print(f"[ERROR] 다운로드 실패: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return None

    def __repr__(self):
        return "PixabayProvider()"
