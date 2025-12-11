"""
Audio Processor - 오디오 편집 및 처리 서비스 (FFmpeg 직접 사용)
"""
import re
import os
import subprocess
from typing import List, Dict, Tuple


class AudioProcessor:
    """오디오 처리 (병합, 믹싱 등) - FFmpeg 직접 사용"""

    def merge_audio_segments(
        self,
        segments: List[Dict],
        output_path: str
    ) -> Tuple[str, float]:
        """분할된 오디오를 타임스탬프에 맞춰 병합"""

        print(f"🎵 오디오 세그먼트 병합 중...")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # FFmpeg concat 파일 생성
        concat_file = output_path.replace('.mp3', '_concat.txt')

        with open(concat_file, 'w', encoding='utf-8') as f:
            for segment in segments:
                # Windows 절대 경로로 변환
                audio_path = os.path.abspath(segment['audio_path'])
                # FFmpeg는 / 사용 (Windows에서도)
                audio_path = audio_path.replace('\\', '/')
                f.write(f"file '{audio_path}'\n")

        # FFmpeg로 오디오 병합
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            ffmpeg_path = get_ffmpeg_exe()
        except:
            ffmpeg_path = 'ffmpeg'

        cmd = [
            ffmpeg_path,
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg 오류: {e.stderr.decode()}")
            raise

        # concat 파일 삭제
        if os.path.exists(concat_file):
            os.remove(concat_file)

        # 오디오 길이 가져오기
        duration_seconds = self._get_audio_duration(output_path, ffmpeg_path)

        print(f"✅ 오디오 병합 완료: {output_path} ({duration_seconds:.1f}초)")
        return output_path, duration_seconds

    def _get_audio_duration(self, audio_path: str, ffmpeg_path: str = 'ffmpeg') -> float:
        """FFmpeg로 오디오 길이 가져오기 (ffprobe 없이)"""
        try:
            # FFmpeg으로 직접 오디오 정보 가져오기
            cmd = [
                ffmpeg_path,
                '-i', audio_path,
                '-f', 'null',
                '-'
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            # stderr에서 Duration 파싱
            match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})', result.stderr)
            if match:
                hours, minutes, seconds = match.groups()
                duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                return duration
        except Exception as e:
            print(f"⚠️ 오디오 길이 측정 실패: {e}")

        # MoviePy fallback
        try:
            from moviepy import AudioFileClip
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            return duration
        except:
            pass

        # 최종 기본값
        return 30.0

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
        """음성과 배경음악 믹싱 (FFmpeg 사용)"""

        print(f"🎵 음성과 배경음악 믹싱 중...")

        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            ffmpeg_path = get_ffmpeg_exe()
        except:
            ffmpeg_path = 'ffmpeg'

        # 볼륨 조절 (0.0-1.0 -> dB)
        voice_db = 0  # 원본 볼륨
        music_db = -20  # 배경음악은 -20dB (약 10%)

        cmd = [
            ffmpeg_path,
            '-i', voice_path,
            '-i', music_path,
            '-filter_complex',
            f'[0:a]volume={voice_db}dB[a1];[1:a]volume={music_db}dB,aloop=loop=-1:size=2e+09[a2];[a1][a2]amerge=inputs=2[a]',
            '-map', '[a]',
            '-ac', '2',
            '-c:a', 'libmp3lame',
            '-q:a', '2',
            '-y',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # 믹싱 실패 시 음성만 사용
            print("⚠️ 배경음악 믹싱 실패, 음성만 사용합니다")
            import shutil
            shutil.copy(voice_path, output_path)

        print(f"✅ 믹싱 완료: {output_path}")
        return output_path

    def adjust_audio_length(
        self,
        audio_path: str,
        target_duration: float,
        output_path: str
    ) -> str:
        """오디오 길이 조정 (FFmpeg 사용)"""

        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            ffmpeg_path = get_ffmpeg_exe()
        except:
            ffmpeg_path = 'ffmpeg'

        cmd = [
            ffmpeg_path,
            '-i', audio_path,
            '-t', str(target_duration),
            '-af', 'afade=t=out:st=' + str(max(0, target_duration - 5)) + ':d=5',
            '-y',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # 실패 시 원본 복사
            import shutil
            shutil.copy(audio_path, output_path)

        return output_path
