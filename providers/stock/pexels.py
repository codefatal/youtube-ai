"""
Pexels Stock Video Provider
무료 스톡 영상 API wrapper
"""
import os
import requests
from typing import List, Optional, Dict, Any
from core.models import StockVideoAsset


class PexelsProvider:
    """Pexels API 제공자"""

    BASE_URL = "https://api.pexels.com/videos"

    def __init__(self, api_key: Optional[str] = None):
        """
        Pexels Provider 초기화

        Args:
            api_key: Pexels API 키 (None이면 환경변수에서 가져옴)
        """
        self.api_key = api_key or os.getenv('PEXELS_API_KEY')
        if not self.api_key:
            raise ValueError("PEXELS_API_KEY가 설정되지 않았습니다")

        self.headers = {
            'Authorization': self.api_key
        }

    def search_videos(
        self,
        query: str,
        per_page: int = 5,
        orientation: str = "portrait",
        size: str = "medium"
    ) -> List[StockVideoAsset]:
        """
        키워드로 영상 검색

        Args:
            query: 검색 키워드 (영어)
            per_page: 결과 개수 (기본 5개)
            orientation: 영상 방향 (portrait/landscape/square)
            size: 영상 크기 (small/medium/large)

        Returns:
            StockVideoAsset 리스트
        """
        params = {
            'query': query,
            'per_page': per_page,
            'orientation': orientation,
            'size': size
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            videos = data.get('videos', [])

            assets = []
            for video in videos:
                asset = self._parse_video(video, query)
                if asset:
                    assets.append(asset)

            print(f"[Pexels] '{query}' 검색 완료: {len(assets)}개 발견")
            return assets

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Pexels API 오류: {e}")
            return []

    def _parse_video(self, video_data: Dict[str, Any], keyword: str) -> Optional[StockVideoAsset]:
        """
        Pexels API 응답을 StockVideoAsset으로 변환

        Args:
            video_data: Pexels API 응답 데이터
            keyword: 검색 키워드

        Returns:
            StockVideoAsset 또는 None
        """
        try:
            video_id = str(video_data.get('id'))
            duration = video_data.get('duration', 0)

            # 비디오 파일 선택 (HD 우선)
            video_files = video_data.get('video_files', [])
            if not video_files:
                return None

            # HD 또는 가장 높은 품질 선택
            selected_file = None
            for file in video_files:
                quality = file.get('quality', '')
                if 'hd' in quality.lower():
                    selected_file = file
                    break

            if not selected_file:
                selected_file = video_files[0]

            download_url = selected_file.get('link')
            width = selected_file.get('width', 1080)
            height = selected_file.get('height', 1920)
            resolution = f"{width}x{height}"

            return StockVideoAsset(
                id=f"pexels_{video_id}",
                url=download_url,
                provider="pexels",
                keyword=keyword,
                duration=duration,
                resolution=resolution,
                downloaded=False
            )

        except Exception as e:
            print(f"[ERROR] Pexels 비디오 파싱 실패: {e}")
            return None

    def get_popular_videos(
        self,
        per_page: int = 5,
        orientation: str = "portrait"
    ) -> List[StockVideoAsset]:
        """
        인기 영상 가져오기

        Args:
            per_page: 결과 개수
            orientation: 영상 방향

        Returns:
            StockVideoAsset 리스트
        """
        params = {
            'per_page': per_page,
            'orientation': orientation
        }

        try:
            response = requests.get(
                f"{self.BASE_URL}/popular",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            videos = data.get('videos', [])

            assets = []
            for video in videos:
                asset = self._parse_video(video, "popular")
                if asset:
                    assets.append(asset)

            print(f"[Pexels] 인기 영상 {len(assets)}개 가져옴")
            return assets

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Pexels API 오류: {e}")
            return []

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
            print(f"[Pexels] 이미 다운로드됨: {filename}")
            return filepath

        try:
            print(f"[Pexels] 다운로드 시작: {filename}")
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
        return "PexelsProvider()"
