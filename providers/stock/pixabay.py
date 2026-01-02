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
    MUSIC_BASE_URL = "https://pixabay.com/api/"  # Music API 엔드포인트

    def __init__(self, api_key: Optional[str] = None):
        """
        Pixabay Provider 초기화 (Phase 6: API 키 검증 강화)

        Args:
            api_key: Pixabay API 키 (None이면 환경변수에서 가져옴)
        """
        self.api_key = api_key or os.getenv('PIXABAY_API_KEY')

        # Phase 6: API 키 검증 (기본값 체크)
        if not self.api_key or self.api_key == 'your_pixabay_api_key_here':
            print("[WARNING] Pixabay API 키가 설정되지 않았습니다. Pixabay 검색이 비활성화됩니다.")
            print("[INFO] .env 파일에 PIXABAY_API_KEY를 설정하세요.")
            self.api_key = None  # 명시적으로 None 설정
        else:
            print("[INFO] Pixabay API 키 확인 완료")

    def search_videos(
        self,
        query: str,
        per_page: int = 5,
        video_type: str = "film",  # Phase 4: 기본값 film (실사 영상)
        orientation: str = "vertical",  # Phase 4: 쇼츠용 세로 영상
        editors_choice: bool = True,  # Phase 4: 에디터 추천 영상 우선
        safesearch: bool = True,
        min_width: int = 720,  # Phase 4: 최소 해상도
        min_height: int = 1280
    ) -> List[StockVideoAsset]:
        """
        키워드로 영상 검색 (Phase 4: 고품질 파라미터 튜닝)

        Args:
            query: 검색 키워드 (영어)
            per_page: 결과 개수 (기본 5개, 최대 200)
            video_type: 영상 타입 (all/film/animation) - 기본값 film
            orientation: 영상 방향 (all/horizontal/vertical) - 기본값 vertical
            editors_choice: 에디터 추천 영상만 (기본값 True)
            safesearch: 안전 검색 (기본값 True)
            min_width: 최소 너비 (기본값 720)
            min_height: 최소 높이 (기본값 1280)

        Returns:
            StockVideoAsset 리스트
        """
        # Phase 6: API 키가 없으면 빈 리스트 반환
        if not self.api_key:
            return []

        # Phase 4: 고품질 파라미터 설정
        params = {
            'key': self.api_key,
            'q': query,
            'per_page': min(per_page, 200),
            'video_type': video_type,
            'orientation': orientation,
            'safesearch': safesearch,
            'min_width': min_width,
            'min_height': min_height
        }

        # Phase 4: editors_choice는 True/False 문자열로 전달
        if editors_choice:
            params['editors_choice'] = 'true'

        try:
            print(f"[Pixabay] Phase 4: 고품질 검색 시작 - '{query}'")
            print(f"[Pixabay]   - video_type: {video_type}, orientation: {orientation}")
            print(f"[Pixabay]   - editors_choice: {editors_choice}, min_res: {min_width}x{min_height}")

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

            # Phase 4: Fallback - 결과가 없으면 제약 완화
            if len(assets) == 0 and (orientation != "all" or editors_choice):
                print(f"[Pixabay] Phase 4: 결과 없음 - Fallback 시도 (orientation=all, editors_choice=False)")
                return self._search_with_fallback(query, per_page, video_type, safesearch, min_width, min_height)

            return assets

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Pixabay API 오류: {e}")
            return []

    def _search_with_fallback(
        self,
        query: str,
        per_page: int,
        video_type: str,
        safesearch: bool,
        min_width: int,
        min_height: int
    ) -> List[StockVideoAsset]:
        """
        Phase 4: Fallback 검색 (제약 완화)

        orientation을 all로, editors_choice를 False로 재시도
        """
        params = {
            'key': self.api_key,
            'q': query,
            'per_page': min(per_page, 200),
            'video_type': video_type,
            'orientation': 'all',  # 모든 방향
            'safesearch': safesearch,
            'min_width': min_width,
            'min_height': min_height
            # editors_choice 제거
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

            print(f"[Pixabay] Fallback 검색 완료: {len(assets)}개 발견")
            return assets

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Pixabay Fallback API 오류: {e}")
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

    def search_music(
        self,
        query: str,
        per_page: int = 5,
        audio_type: str = "music"
    ) -> List[Dict[str, Any]]:
        """
        키워드로 음악 검색

        Args:
            query: 검색 키워드 (영어)
            per_page: 결과 개수 (기본 5개, 최대 200)
            audio_type: 오디오 타입 (music/sound_effect)

        Returns:
            음악 정보 리스트
        """
        if not self.api_key:
            return []

        params = {
            'key': self.api_key,
            'q': query,
            'per_page': min(per_page, 200),
            'audio_type': audio_type
        }

        try:
            response = requests.get(
                self.MUSIC_BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            hits = data.get('hits', [])

            music_list = []
            for music in hits:
                parsed = self._parse_music(music, query)
                if parsed:
                    music_list.append(parsed)

            print(f"[Pixabay] '{query}' 음악 검색 완료: {len(music_list)}개 발견")
            return music_list

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Pixabay Music API 오류: {e}")
            return []

    def _parse_music(self, music_data: Dict[str, Any], keyword: str) -> Optional[Dict[str, Any]]:
        """
        Pixabay Music API 응답을 파싱

        Args:
            music_data: Pixabay API 응답 데이터
            keyword: 검색 키워드

        Returns:
            음악 정보 딕셔너리 또는 None
        """
        try:
            music_id = str(music_data.get('id'))
            name = music_data.get('tags', keyword)
            duration = music_data.get('duration', 0)
            download_url = music_data.get('download_link')

            if not download_url:
                return None

            return {
                'id': f"pixabay_music_{music_id}",
                'name': name,
                'url': download_url,
                'duration': duration,
                'keyword': keyword,
                'provider': 'pixabay'
            }

        except Exception as e:
            print(f"[ERROR] Pixabay 음악 파싱 실패: {e}")
            return None

    def download_music(
        self,
        music_info: Dict[str, Any],
        output_dir: str = "./music"
    ) -> Optional[str]:
        """
        음악 다운로드

        Args:
            music_info: 음악 정보 딕셔너리
            output_dir: 저장 디렉토리

        Returns:
            저장된 파일 경로 또는 None
        """
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{music_info['id']}.mp3"
        filepath = os.path.join(output_dir, filename)

        # 이미 다운로드된 경우
        if os.path.exists(filepath):
            print(f"[Pixabay] 이미 다운로드됨: {filename}")
            return filepath

        try:
            print(f"[Pixabay] 음악 다운로드 시작: {filename}")
            response = requests.get(music_info['url'], stream=True, timeout=60)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"[SUCCESS] 음악 다운로드 완료: {filepath}")
            return filepath

        except Exception as e:
            print(f"[ERROR] 음악 다운로드 실패: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
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
