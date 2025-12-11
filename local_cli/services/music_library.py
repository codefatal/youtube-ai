"""
Music Library - 무료 배경음악 라이브러리 관리
"""
import os
import random
from typing import Optional


class MusicLibrary:
    """무료 음악 라이브러리 관리"""

    MUSIC_SOURCES = {
        'youtube_audio_library': {
            'path': './music/youtube_audio_library/',
            'license': 'Free to use',
            'genres': ['ambient', 'electronic', 'cinematic', 'upbeat']
        },
        'free_music_archive': {
            'path': './music/free_music_archive/',
            'license': 'Creative Commons',
            'genres': ['jazz', 'classical', 'indie']
        }
    }

    def get_music_for_style(self, style: str, duration_seconds: int) -> Optional[str]:
        """스타일에 맞는 배경음악 선택"""

        genre_mapping = {
            'short_trendy': 'upbeat',
            'long_educational': 'ambient',
            'long_storytelling': 'cinematic',
            'calm': 'ambient',
            'energetic': 'upbeat',
            'professional': 'ambient',
            'creative': 'electronic'
        }

        genre = genre_mapping.get(style, 'ambient')

        # 음악 폴더 구조 자동 생성
        self._ensure_music_structure()

        # 해당 장르의 음악 파일 찾기
        music_files = self._find_music_files(genre)

        if not music_files:
            print("⚠️ 음악 파일을 찾을 수 없습니다.")
            print("💡 MUSIC_GUIDE.md를 참고하여 무료 배경음악을 다운로드하세요.")
            return None

        # 랜덤 선택
        selected_music = random.choice(music_files)

        print(f"🎵 배경음악 선택: {os.path.basename(selected_music)}")

        return selected_music

    def _ensure_music_structure(self):
        """음악 폴더 구조가 없으면 자동 생성"""
        for source, info in self.MUSIC_SOURCES.items():
            for genre in info['genres']:
                genre_path = os.path.join(info['path'], genre)
                if not os.path.exists(genre_path):
                    os.makedirs(genre_path, exist_ok=True)

    def _find_music_files(self, genre: str):
        """장르에 맞는 음악 파일 찾기"""
        music_files = []

        for source, info in self.MUSIC_SOURCES.items():
            genre_path = os.path.join(info['path'], genre)
            if os.path.exists(genre_path):
                for file in os.listdir(genre_path):
                    if file.endswith(('.mp3', '.wav', '.ogg')):
                        music_files.append(os.path.join(genre_path, file))

        return music_files

    def list_available_music(self) -> dict:
        """사용 가능한 음악 목록 반환"""
        available = {}

        for source, info in self.MUSIC_SOURCES.items():
            available[source] = {}
            for genre in info['genres']:
                genre_path = os.path.join(info['path'], genre)
                if os.path.exists(genre_path):
                    files = [f for f in os.listdir(genre_path)
                            if f.endswith(('.mp3', '.wav', '.ogg'))]
                    available[source][genre] = files

        return available

    def create_default_music_structure(self):
        """기본 음악 폴더 구조 생성"""
        print("🎵 기본 음악 폴더 구조 생성 중...")

        for source, info in self.MUSIC_SOURCES.items():
            for genre in info['genres']:
                genre_path = os.path.join(info['path'], genre)
                os.makedirs(genre_path, exist_ok=True)

        print("""
✅ 음악 폴더 구조가 생성되었습니다.

다음 위치에 무료 음악 파일을 추가하세요:
- ./music/youtube_audio_library/ (YouTube Audio Library에서 다운로드)
- ./music/free_music_archive/ (Free Music Archive에서 다운로드)

각 장르별 폴더:
- ambient/ : 차분한 배경음악
- electronic/ : 전자음악
- cinematic/ : 영화 같은 웅장한 음악
- upbeat/ : 활기찬 음악
- jazz/ : 재즈
- classical/ : 클래식
- indie/ : 인디 음악
        """)
