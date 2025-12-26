"""
BGM Manager for YouTube AI v4.0
Background Music Selection and Processing

Handles:
- Music catalog management
- Mood-based BGM selection
- Audio processing (volume, fade, looping)
"""
from typing import List, Optional, Dict
from pathlib import Path
import json
import random
from pydub import AudioSegment
from pydub.effects import normalize

from core.models import BGMAsset, MoodType


class BGMManager:
    """배경음악 관리자"""

    def __init__(self, music_dir: str = "assets/music"):
        """
        Args:
            music_dir: 음악 파일 디렉토리 경로
        """
        self.music_dir = Path(music_dir)
        self.music_dir.mkdir(parents=True, exist_ok=True)

        # BGM 카탈로그 (mood별 분류)
        self.catalog: Dict[MoodType, List[BGMAsset]] = {
            mood: [] for mood in MoodType
        }

        # 메타데이터 파일 경로
        self.metadata_file = self.music_dir / "catalog.json"

        # 카탈로그 로드
        self._load_catalog()

    def _load_catalog(self):
        """카탈로그 메타데이터 로드"""
        if not self.metadata_file.exists():
            print(f"[BGMManager] 카탈로그 파일 없음: {self.metadata_file}")
            return

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # JSON → BGMAsset 변환
            for mood_str, assets_data in data.items():
                try:
                    mood = MoodType[mood_str.upper()]
                    self.catalog[mood] = [
                        BGMAsset(**asset_data) for asset_data in assets_data
                    ]
                except (KeyError, ValueError) as e:
                    print(f"[BGMManager] 잘못된 mood: {mood_str} - {e}")

            total_count = sum(len(assets) for assets in self.catalog.values())
            print(f"[BGMManager] 카탈로그 로드 완료: {total_count}개 BGM")

        except Exception as e:
            print(f"[BGMManager] 카탈로그 로드 실패: {e}")

    def save_catalog(self):
        """카탈로그 메타데이터 저장"""
        # BGMAsset → JSON 변환
        data = {
            mood.value: [asset.model_dump() for asset in assets]
            for mood, assets in self.catalog.items()
            if assets  # 빈 리스트는 저장하지 않음
        }

        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"[BGMManager] 카탈로그 저장 완료: {self.metadata_file}")

        except Exception as e:
            print(f"[BGMManager] 카탈로그 저장 실패: {e}")

    def add_bgm(
        self,
        file_path: str,
        mood: MoodType,
        name: Optional[str] = None,
        artist: Optional[str] = None,
        license: Optional[str] = None,
        volume: float = 0.3
    ) -> BGMAsset:
        """
        BGM 추가

        Args:
            file_path: 음악 파일 경로
            mood: 분위기 타입
            name: 음악 이름 (파일명 기본값)
            artist: 아티스트
            license: 라이선스
            volume: 기본 볼륨

        Returns:
            BGMAsset 객체
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"BGM 파일 없음: {file_path}")

        # 오디오 길이 측정
        try:
            audio = AudioSegment.from_file(str(file_path))
            duration = len(audio) / 1000.0  # ms → sec
        except Exception as e:
            print(f"[BGMManager] 오디오 로드 실패: {e}")
            duration = 0.0

        # BGMAsset 생성
        asset = BGMAsset(
            name=name or file_path.stem,
            local_path=str(file_path),
            mood=mood,
            duration=duration,
            volume=volume,
            artist=artist,
            license=license
        )

        # 카탈로그에 추가
        self.catalog[mood].append(asset)

        print(f"[BGMManager] BGM 추가: {asset.name} ({mood.value}, {duration:.1f}초)")

        return asset

    def get_bgm_by_mood(
        self,
        mood: MoodType,
        min_duration: Optional[float] = None
    ) -> Optional[BGMAsset]:
        """
        분위기에 맞는 BGM 선택

        Args:
            mood: 원하는 분위기
            min_duration: 최소 길이 (초)

        Returns:
            선택된 BGMAsset (없으면 None)
        """
        candidates = self.catalog.get(mood, [])

        # 최소 길이 필터링
        if min_duration:
            candidates = [
                bgm for bgm in candidates
                if bgm.duration >= min_duration
            ]

        if not candidates:
            print(f"[BGMManager] {mood.value} BGM 없음 (min_duration={min_duration})")
            return None

        # 랜덤 선택
        selected = random.choice(candidates)
        print(f"[BGMManager] BGM 선택: {selected.name} ({mood.value})")

        return selected

    def auto_select_mood(self, topic: str, tone: str) -> MoodType:
        """
        주제와 톤에서 자동으로 분위기 추론

        Args:
            topic: 영상 주제
            tone: 영상 톤 (정보성, 힐링, 유머 등)

        Returns:
            추론된 MoodType
        """
        topic_lower = topic.lower()
        tone_lower = tone.lower()

        # 키워드 기반 분위기 매칭
        if any(keyword in topic_lower for keyword in ["슬픈", "눈물", "이별", "sad"]):
            return MoodType.SAD

        if any(keyword in topic_lower for keyword in ["행복", "즐거운", "happy", "joy"]):
            return MoodType.HAPPY

        if any(keyword in topic_lower for keyword in ["긴장", "스릴", "공포", "thriller"]):
            return MoodType.TENSE

        if any(keyword in topic_lower for keyword in ["신비", "미스터리", "mystery"]):
            return MoodType.MYSTERIOUS

        # 톤 기반 매칭
        if "힐링" in tone_lower or "차분" in tone_lower:
            return MoodType.CALM

        if "유머" in tone_lower or "재미" in tone_lower:
            return MoodType.HAPPY

        # 기본값: 활기찬 분위기
        return MoodType.ENERGETIC

    def process_bgm(
        self,
        bgm: BGMAsset,
        target_duration: float,
        fade_in: float = 1.0,
        fade_out: float = 2.0,
        volume: Optional[float] = None
    ) -> str:
        """
        BGM 처리 (길이 조정, 페이드, 볼륨)

        Args:
            bgm: BGMAsset 객체
            target_duration: 목표 길이 (초)
            fade_in: 페이드 인 길이 (초)
            fade_out: 페이드 아웃 길이 (초)
            volume: 볼륨 배율 (None이면 bgm.volume 사용)

        Returns:
            처리된 오디오 파일 경로
        """
        try:
            # 오디오 로드
            audio = AudioSegment.from_file(bgm.local_path)

            # 볼륨 조정
            volume_db = (volume or bgm.volume) * 100 - 100  # 0.0~1.0 → -100~0 dB
            audio = audio + volume_db

            # 길이 조정 (loop 또는 trim)
            target_ms = int(target_duration * 1000)
            audio_ms = len(audio)

            if audio_ms < target_ms:
                # 루프 (반복)
                loop_count = (target_ms // audio_ms) + 1
                audio = audio * loop_count

            # 정확한 길이로 자르기
            audio = audio[:target_ms]

            # 페이드 효과
            fade_in_ms = int(fade_in * 1000)
            fade_out_ms = int(fade_out * 1000)

            audio = audio.fade_in(fade_in_ms).fade_out(fade_out_ms)

            # 정규화 (볼륨 균일화)
            audio = normalize(audio)

            # 임시 파일로 저장
            output_path = self.music_dir / f"processed_{bgm.name}.mp3"
            audio.export(str(output_path), format="mp3", bitrate="192k")

            print(f"[BGMManager] BGM 처리 완료: {output_path} ({target_duration:.1f}초)")

            return str(output_path)

        except Exception as e:
            print(f"[BGMManager] BGM 처리 실패: {e}")
            raise

    def get_random_bgm(self, min_duration: Optional[float] = None) -> Optional[BGMAsset]:
        """
        전체 카탈로그에서 랜덤 BGM 선택

        Args:
            min_duration: 최소 길이 (초)

        Returns:
            선택된 BGMAsset (없으면 None)
        """
        all_bgms = []
        for bgms in self.catalog.values():
            all_bgms.extend(bgms)

        # 최소 길이 필터링
        if min_duration:
            all_bgms = [bgm for bgm in all_bgms if bgm.duration >= min_duration]

        if not all_bgms:
            return None

        return random.choice(all_bgms)

    def list_bgms_by_mood(self, mood: MoodType) -> List[BGMAsset]:
        """특정 분위기의 BGM 목록 조회"""
        return self.catalog.get(mood, [])

    def get_statistics(self) -> Dict[str, int]:
        """카탈로그 통계"""
        stats = {
            mood.value: len(bgms)
            for mood, bgms in self.catalog.items()
        }
        stats["total"] = sum(stats.values())
        return stats
