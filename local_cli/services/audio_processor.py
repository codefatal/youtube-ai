"""
Audio Processor - 오디오 편집 및 처리 서비스
"""
import re
from typing import List, Dict, Tuple


class AudioProcessor:
    """오디오 처리 (병합, 믹싱 등)"""

    def merge_audio_segments(
        self,
        segments: List[Dict],
        output_path: str
    ) -> Tuple[str, float]:
        """분할된 오디오를 타임스탬프에 맞춰 병합"""

        print(f"🎵 오디오 세그먼트 병합 중...")

        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub가 설치되지 않았습니다. pip install pydub")

        final_audio = AudioSegment.silent(duration=0)

        for i, segment in enumerate(segments):
            audio = AudioSegment.from_file(segment['audio_path'])

            # 타임스탬프를 밀리초로 변환
            time_ms = self._timestamp_to_ms(segment['timestamp'])

            # 현재 오디오 길이와 목표 시간 차이만큼 무음 추가
            current_length = len(final_audio)
            if time_ms > current_length:
                silence = AudioSegment.silent(duration=time_ms - current_length)
                final_audio += silence

            final_audio += audio

        final_audio.export(output_path, format='mp3')
        duration_seconds = len(final_audio) / 1000

        print(f"✅ 오디오 병합 완료: {output_path} ({duration_seconds:.1f}초)")
        return output_path, duration_seconds

    def _timestamp_to_ms(self, timestamp: str) -> int:
        """[00:05] -> 5000ms"""
        match = re.match(r'(\d{2}):(\d{2})', timestamp)
        if match:
            minutes, seconds = map(int, match.groups())
            return (minutes * 60 + seconds) * 1000
        return 0

    def mix_voice_and_music(
        self,
        voice_path: str,
        music_path: str,
        output_path: str,
        voice_volume: float = 1.0,
        music_volume: float = 0.2
    ) -> str:
        """음성과 배경음악 믹싱"""

        print(f"🎵 음성과 배경음악 믹싱 중...")

        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub가 설치되지 않았습니다. pip install pydub")

        voice = AudioSegment.from_file(voice_path)
        music = AudioSegment.from_file(music_path)

        # 볼륨 조절 (dB 단위)
        voice = voice + (20 * voice_volume - 20)
        music = music + (20 * music_volume - 20)

        # 음악을 음성 길이에 맞춤
        if len(music) < len(voice):
            music = music * (len(voice) // len(music) + 1)
        music = music[:len(voice)]

        # 오버레이
        mixed = voice.overlay(music)

        mixed.export(output_path, format='mp3')

        print(f"✅ 믹싱 완료: {output_path}")
        return output_path

    def adjust_audio_length(
        self,
        audio_path: str,
        target_duration: float,
        output_path: str
    ) -> str:
        """오디오 길이 조정"""

        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub가 설치되지 않았습니다. pip install pydub")

        audio = AudioSegment.from_file(audio_path)
        audio_duration = len(audio) / 1000  # 초 단위

        target_ms = int(target_duration * 1000)

        if audio_duration < target_duration:
            # 오디오가 짧으면 반복
            repeats = int(target_duration / audio_duration) + 1
            audio = audio * repeats

        # 정확한 길이로 자르기
        audio = audio[:target_ms]

        # 마지막 5초 페이드 아웃
        fade_duration = min(5000, len(audio))
        audio = audio.fade_out(fade_duration)

        audio.export(output_path, format='mp3')

        return output_path
