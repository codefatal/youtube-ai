"""
Video Producer - 영상 제작 서비스
"""
import os
import re
from typing import Dict, List, Tuple
from .tts_service import TTSService
from .audio_processor import AudioProcessor
from .music_library import MusicLibrary


class VideoProducer:
    """완전한 영상 제작 파이프라인"""

    def __init__(self):
        self.tts_service = TTSService(provider=os.getenv('TTS_PROVIDER', 'google'))
        self.audio_processor = AudioProcessor()
        self.music_library = MusicLibrary()

    def produce_video(
        self,
        script: Dict,
        style_preset: str,
        output_path: str
    ) -> Tuple[str, str]:
        """완전한 영상 제작 파이프라인"""

        print("\n🎬 영상 제작 시작...")

        temp_dir = './temp'
        os.makedirs(temp_dir, exist_ok=True)

        # 1. TTS 음성 생성
        print("\n1️⃣ 음성 생성 중...")
        voice_segments = self.tts_service.generate_with_timestamps(
            script['content'],
            output_dir=os.path.join(temp_dir, 'audio')
        )

        voice_path, voice_duration = self.audio_processor.merge_audio_segments(
            voice_segments,
            os.path.join(temp_dir, 'voice_final.mp3')
        )

        # 2. 배경음악 추가
        print("\n2️⃣ 배경음악 추가 중...")
        background_music_path = self.music_library.get_music_for_style(
            style_preset,
            int(voice_duration)
        )

        if background_music_path:
            adjusted_music_path = os.path.join(temp_dir, 'music_adjusted.mp3')
            self.audio_processor.adjust_audio_length(
                background_music_path,
                voice_duration,
                adjusted_music_path
            )

            final_audio_path = self.audio_processor.mix_voice_and_music(
                voice_path,
                adjusted_music_path,
                os.path.join(temp_dir, 'audio_with_music.mp3'),
                voice_volume=1.0,
                music_volume=0.25
            )
        else:
            final_audio_path = voice_path

        # 3. 이미지/영상 클립 생성
        print("\n3️⃣ 비주얼 생성 중...")
        visual_clips = self._generate_visual_clips(
            script,
            voice_segments,
            style_preset
        )

        # 4. 자막 생성
        print("\n4️⃣ 자막 생성 중...")
        subtitles = self._create_subtitles(voice_segments)

        # 5. 최종 합성
        print("\n5️⃣ 영상 합성 중...")
        final_video = self._compose_video(
            visual_clips,
            final_audio_path,
            subtitles,
            script['video_format'],
            voice_duration
        )

        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            preset='medium'
        )

        # 6. 썸네일 생성
        print("\n6️⃣ 썸네일 생성 중...")
        thumbnail_path = output_path.replace('.mp4', '_thumb.jpg')
        final_video.save_frame(thumbnail_path, t=2)

        print(f"\n✅ 영상 생성 완료: {output_path}")

        return output_path, thumbnail_path

    def _generate_visual_clips(
        self,
        script: Dict,
        voice_segments: List[Dict],
        style_preset: str
    ) -> List:
        """간단한 이미지 슬라이드 (실제로는 AI 이미지 생성)"""

        try:
            import moviepy.editor as mp
        except ImportError:
            raise ImportError("moviepy가 설치되지 않았습니다. pip install moviepy")

        clips = []

        # 임시: 단색 배경 (실제로는 AI 이미지 생성)
        colors = [
            (50, 50, 100),
            (100, 50, 50),
            (50, 100, 50),
            (100, 100, 50),
            (100, 50, 100),
        ]

        for i, segment in enumerate(voice_segments):
            # 5초 클립
            color = colors[i % len(colors)]
            clip = mp.ColorClip(size=(1920, 1080), color=color, duration=5)

            # 줌 효과
            clip = clip.resize(lambda t: 1 + 0.05 * t)

            clips.append(clip)

        return clips

    def _create_subtitles(self, voice_segments: List[Dict]) -> List[Dict]:
        """자막 데이터 생성"""
        subtitle_data = []

        for i, segment in enumerate(voice_segments):
            start_time = self._timestamp_to_seconds(segment['timestamp'])
            # 각 세그먼트는 약 5초로 가정
            end_time = start_time + 5

            subtitle_data.append({
                'start': start_time,
                'end': end_time,
                'text': segment['text']
            })

        return subtitle_data

    def _compose_video(
        self,
        visual_clips: List,
        audio_path: str,
        subtitles: List[Dict],
        video_format: str,
        duration: float
    ):
        """최종 영상 합성"""

        try:
            import moviepy.editor as mp
        except ImportError:
            raise ImportError("moviepy가 설치되지 않았습니다. pip install moviepy")

        # 비주얼 연결
        video = mp.concatenate_videoclips(visual_clips, method="compose")

        # 영상을 오디오 길이에 맞춤
        if video.duration > duration:
            video = video.subclip(0, duration)
        elif video.duration < duration:
            # 마지막 프레임을 freeze
            last_frame = visual_clips[-1]
            video = mp.concatenate_videoclips([video, last_frame.set_duration(duration - video.duration)])

        # 오디오 추가
        audio = mp.AudioFileClip(audio_path)
        video = video.set_audio(audio)

        # 자막 추가
        def make_textclip(txt):
            return mp.TextClip(
                txt,
                font='Arial-Bold',
                fontsize=50 if video_format == 'short' else 40,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(video.w * 0.9, None),
                align='center'
            )

        subtitle_clips = []
        for sub in subtitles:
            txt_clip = make_textclip(sub['text'])
            txt_clip = txt_clip.set_start(sub['start']).set_duration(sub['end'] - sub['start'])
            txt_clip = txt_clip.set_position(('center', 'bottom'))
            subtitle_clips.append(txt_clip)

        video = mp.CompositeVideoClip([video] + subtitle_clips)

        # 숏폼은 9:16 크롭
        if video_format == 'short':
            video = video.crop(
                x_center=video.w/2,
                y_center=video.h/2,
                width=int(video.h * 9/16),
                height=video.h
            )

        return video

    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """[00:05] -> 5.0"""
        match = re.match(r'(\d{2}):(\d{2})', timestamp)
        if match:
            minutes, seconds = map(int, match.groups())
            return minutes * 60 + seconds
        return 0.0
