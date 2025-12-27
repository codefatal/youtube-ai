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
import subprocess
import shutil

from core.models import BGMAsset, MoodType


def _get_audio_duration(file_path: str) -> float:
    """오디오 파일의 길이를 ffprobe를 이용해 초 단위로 반환"""
    ffprobe_cmd = shutil.which("ffprobe")
    if not ffprobe_cmd:
        raise FileNotFoundError("ffprobe를 찾을 수 없습니다. ffmpeg이 설치되어 있고 PATH에 추가되었는지 확인하세요.")

    command = [
        ffprobe_cmd,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"[BGMManager] 오디오 길이 측정 실패: {file_path} - {e}")
        return 0.0


class BGMManager:
    """배경음악 관리자"""

    def __init__(self, music_dir: str = "music"):
        """
        Args:
            music_dir: 음악 파일 디렉토리 경로 (Phase 3: "assets/music" → "music")
        """
        self.music_dir = Path(music_dir)
        self.music_dir.mkdir(parents=True, exist_ok=True)

        # ffmpeg 경로 찾기 (Windows Chocolatey 경로 포함)
        self.ffmpeg_cmd = shutil.which("ffmpeg")
        if not self.ffmpeg_cmd:
            # Chocolatey 설치 경로 확인
            choco_ffmpeg = Path("C:/ProgramData/chocolatey/bin/ffmpeg.exe")
            if choco_ffmpeg.exists():
                self.ffmpeg_cmd = str(choco_ffmpeg)
            else:
                raise FileNotFoundError("ffmpeg를 찾을 수 없습니다. ffmpeg이 설치되어 있고 PATH에 추가되었는지 확인하세요.")

        # BGM 카탈로그 (mood별 분류)
        self.catalog: Dict[MoodType, List[BGMAsset]] = {
            mood: [] for mood in MoodType
        }

        # 메타데이터 파일 경로
        self.metadata_file = self.music_dir / "catalog.json"

        # 카탈로그 로드
        self._load_catalog()

    def _load_catalog(self):
        """
        카탈로그 메타데이터 로드
        Phase 3: 카탈로그가 없으면 music 폴더 자동 스캔
        """
        if not self.metadata_file.exists():
            print(f"[BGMManager] 카탈로그 파일 없음: {self.metadata_file}")
            # Phase 3: music 폴더를 스캔해서 자동 생성 시도
            self._auto_scan_music_folder()
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

    def _auto_scan_music_folder(self):
        """
        Phase 3: music 폴더를 스캔해서 BGM 자동 감지 및 카탈로그 생성

        폴더 구조:
        music/
          HAPPY/
            song1.mp3
            song2.mp3
          ENERGETIC/
            track1.mp3
          ...
        """
        print(f"[BGMManager] music 폴더 자동 스캔 중: {self.music_dir}")

        found_count = 0
        for mood_folder in self.music_dir.iterdir():
            if not mood_folder.is_dir():
                continue

            # 폴더 이름으로 mood 판별
            mood_name = mood_folder.name.upper()
            try:
                mood = MoodType[mood_name]
            except KeyError:
                print(f"[BGMManager] 알 수 없는 mood 폴더: {mood_folder.name}")
                continue

            # 해당 mood 폴더에서 오디오 파일 찾기
            for audio_file in mood_folder.glob("*.mp3"):
                try:
                    asset = self.add_bgm(
                        file_path=str(audio_file),
                        mood=mood,
                        name=audio_file.stem,
                        volume=0.2  # Phase 3: 기본 볼륨 0.3 → 0.2
                    )
                    found_count += 1
                except Exception as e:
                    print(f"[BGMManager] BGM 추가 실패 ({audio_file.name}): {e}")

        if found_count > 0:
            print(f"[BGMManager] 자동 스캔 완료: {found_count}개 BGM 발견")
            # 카탈로그 저장
            self.save_catalog()
        else:
            print(f"[BGMManager] 자동 스캔 결과: BGM 파일 없음")
            print(f"[BGMManager] BGM을 사용하려면 music/MOOD_NAME/ 폴더에 mp3 파일을 넣으세요")
            print(f"[BGMManager] 예: music/ENERGETIC/track1.mp3")

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
        volume: float = 0.2  # Phase 3: 0.3 → 0.2
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

        # 오디오 길이 측정 (ffprobe 사용)
        duration = _get_audio_duration(str(file_path))

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
        BGM 처리 (길이 조정, 페이드, 볼륨) - ffmpeg 직접 호출 방식

        Args:
            bgm: BGMAsset 객체
            target_duration: 목표 길이 (초)
            fade_in: 페이드 인 길이 (초)
            fade_out: 페이드 아웃 길이 (초)
            volume: 볼륨 배율 (None이면 bgm.volume 사용)

        Returns:
            처리된 오디오 파일 경로
        """
        output_path = self.music_dir / f"processed_{bgm.name}.mp3"
        final_volume = volume or bgm.volume
        
        # ffmpeg 명령어 구성
        command = [
            self.ffmpeg_cmd,
            "-y",  # 덮어쓰기 허용
            "-i", str(bgm.local_path),
            "-filter_complex",
            # 루프 필터: 오디오를 target_duration보다 길게 반복
            # atrim 필터: 정확한 길이로 자르기
            # afade 필터: 페이드 인/아웃 효과
            # volume 필터: 볼륨 조절
            f"aloop=loop=-1:size=2e+09,atrim=0:{target_duration},afade=t=in:ss=0:d={fade_in},afade=t=out:st={target_duration - fade_out}:d={fade_out},volume={final_volume}",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(output_path)
        ]

        try:
            print(f"[BGMManager] ffmpeg으로 BGM 처리 중: {' '.join(command)}")
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"[BGMManager] BGM 처리 완료: {output_path} ({target_duration:.1f}초)")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"[BGMManager] BGM 처리 실패: {e}")
            print(f"  - FFMPEG STDERR: {e.stderr}")
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
