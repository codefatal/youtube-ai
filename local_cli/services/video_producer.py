"""
Video Producer - 영상 제작 서비스
"""
import os
import re
from typing import Dict, List, Tuple, Any, Optional
from .tts_service import TTSService
from .audio_processor import AudioProcessor
from .music_library import MusicLibrary
from .image_generator import ImageGenerator


class VideoProducer:
    """완전한 영상 제작 파이프라인

    TTS, 오디오 처리, 비주얼 생성, 자막, 영상 합성을 포함한
    전체 영상 제작 워크플로우를 관리합니다.
    """

    # 임시 비주얼 배경 색상 (AI 이미지 생성 비활성화 시 사용)
    VISUAL_COLORS = [
        (50, 50, 100),   # 진한 파란색
        (100, 50, 50),   # 진한 빨간색
        (50, 100, 50),   # 진한 초록색
        (100, 100, 50),  # 노란색
        (100, 50, 100),  # 보라색
    ]

    def __init__(self):
        """VideoProducer 초기화"""
        # 무료 TTS 사용 (gTTS 또는 local)
        tts_provider = os.getenv('TTS_PROVIDER', 'gtts')
        self.tts_service = TTSService(provider=tts_provider)
        self.audio_processor = AudioProcessor()
        self.music_library = MusicLibrary()

        # 이미지 생성 (Pexels API 기본 활성화)
        # 환경 변수: pexels (추천), text (그라데이션+텍스트), unsplash, none
        image_provider = os.getenv('IMAGE_PROVIDER', 'pexels')
        self.image_generator = ImageGenerator(provider=image_provider)

    def produce_video(
        self,
        script: Dict,
        style_preset: str,
        output_path: str
    ) -> Tuple[str, str]:
        """완전한 영상 제작 파이프라인

        Args:
            script: 대본 정보 (content, video_format 포함)
            style_preset: 스타일 프리셋 (calm, energetic 등)
            output_path: 출력 영상 경로 (.mp4)

        Returns:
            Tuple[str, str]: (영상 경로, 썸네일 경로)

        Raises:
            Exception: 영상 제작 중 오류 발생 시
        """
        print("\n🎬 영상 제작 시작...")

        temp_dir = './temp'
        os.makedirs(temp_dir, exist_ok=True)

        # 출력 디렉토리 미리 생성
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

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

        # RGBA를 RGB로 변환하여 JPEG 저장
        from PIL import Image
        import numpy as np

        frame = final_video.get_frame(2)  # 2초 시점 프레임
        img = Image.fromarray(frame)

        # RGBA인 경우 RGB로 변환
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        img.save(thumbnail_path, 'JPEG', quality=95)

        print(f"\n✅ 영상 생성 완료: {output_path}")

        return output_path, thumbnail_path

    def _generate_visual_clips(
        self,
        script: Dict,
        voice_segments: List[Dict],
        style_preset: str
    ) -> List[Any]:
        """비주얼 클립 생성

        AI 이미지 생성을 시도하며, 실패 시 단색 배경 사용

        Args:
            script: 대본 정보
            voice_segments: TTS 세그먼트 (duration 포함)
            style_preset: 스타일 프리셋

        Returns:
            List[MoviePy VideoClip]: 비주얼 클립 리스트

        Raises:
            ImportError: MoviePy가 설치되지 않은 경우
        """
        try:
            # MoviePy 2.x import
            from moviepy import (
                VideoFileClip, ImageClip, ColorClip,
                concatenate_videoclips, CompositeVideoClip,
                AudioFileClip, TextClip
            )
        except ImportError:
            raise ImportError(
                "moviepy가 설치되지 않았습니다. 설치: pip install moviepy imageio-ffmpeg"
            )

        clips = []

        # 전체 영상 길이 계산
        total_duration = sum(seg.get('duration', 5.0) for seg in voice_segments)

        # 최소 5개 이미지 보장
        min_images = 5
        num_segments = len(voice_segments)

        # 이미지 변경 간격 계산 (최소 3초, 최대 10초)
        if num_segments >= min_images:
            # 세그먼트가 충분하면 각 세그먼트당 1개 이미지
            image_change_points = []
            current_time = 0.0
            for segment in voice_segments:
                image_change_points.append((current_time, segment['text']))
                current_time += segment.get('duration', 5.0)
        else:
            # 세그먼트가 부족하면 균등하게 분할 (최소 5개)
            image_interval = max(3.0, min(10.0, total_duration / min_images))
            image_change_points = []
            current_time = 0.0
            seg_idx = 0

            while current_time < total_duration and len(image_change_points) < min_images * 2:  # 넉넉하게
                # 현재 시간에 해당하는 세그먼트 찾기
                time_sum = 0.0
                for idx, segment in enumerate(voice_segments):
                    time_sum += segment.get('duration', 5.0)
                    if time_sum > current_time:
                        seg_idx = idx
                        break

                if seg_idx < len(voice_segments):
                    image_change_points.append((current_time, voice_segments[seg_idx]['text']))

                current_time += image_interval

        # 최소 5개 보장
        if len(image_change_points) < min_images:
            # 부족하면 세그먼트 텍스트 반복 사용
            while len(image_change_points) < min_images:
                idx = len(image_change_points) % num_segments
                time_point = (len(image_change_points) * total_duration / min_images,
                             voice_segments[idx]['text'])
                image_change_points.append(time_point)

        print(f"\n[INFO] 총 {len(image_change_points)}개 이미지 생성 예정 (최소 {min_images}개 보장)")

        # AI 이미지 생성
        if self.image_generator.enabled:
            print("\n🎨 AI 이미지 생성 중...")
            image_paths = []
            for i, (time_point, text) in enumerate(image_change_points):
                output_path = f'./temp/images/image_{i}.png'
                image_path = self.image_generator.generate_image_for_segment(
                    text,
                    style_preset,
                    output_path
                )
                image_paths.append(image_path)
        else:
            image_paths = [None] * len(image_change_points)

        # 이미지 클립 생성
        for i, ((start_time, text), image_path) in enumerate(zip(image_change_points, image_paths)):
            # 다음 이미지 변경 시점까지의 duration 계산
            if i < len(image_change_points) - 1:
                duration = image_change_points[i + 1][0] - start_time
            else:
                duration = total_duration - start_time

            # duration이 너무 짧거나 음수면 보정
            if duration <= 0:
                continue

            # AI 생성 이미지가 있으면 사용, 없으면 단색 배경
            if image_path and os.path.exists(image_path):
                clip = ImageClip(image_path, duration=duration)
                print(f"[OK] AI 이미지 사용: {os.path.basename(image_path)} ({duration:.1f}초)")
            else:
                # PIL로 단색 배경 이미지 생성
                from PIL import Image
                import numpy as np

                color = self.VISUAL_COLORS[i % len(self.VISUAL_COLORS)]
                img = Image.new('RGB', (1920, 1080), color)
                img_array = np.array(img)

                clip = ImageClip(img_array, duration=duration)

            # 줌 효과
            clip = clip.resized(lambda t: 1 + 0.01 * t)

            clips.append(clip)

        return clips

    def _create_subtitles(self, voice_segments: List[Dict]) -> List[Dict]:
        """자막 데이터 생성 (TTS 세그먼트 실제 길이 사용)"""
        subtitle_data = []

        cumulative_time = 0.0
        for segment in voice_segments:
            # 세그먼트 실제 길이 사용 (기본값 5초)
            duration = segment.get('duration', 5.0)

            subtitle_data.append({
                'start': cumulative_time,
                'end': cumulative_time + duration,
                'text': segment['text']
            })

            cumulative_time += duration

        return subtitle_data

    def _find_font(self) -> Optional[str]:
        """시스템에서 사용 가능한 폰트 찾기

        Returns:
            Optional[str]: 폰트 경로 또는 None (기본 폰트 사용)
        """
        import platform

        # Windows 폰트 경로
        if platform.system() == 'Windows':
            fonts_dir = r'C:\Windows\Fonts'

            # 한글 지원 폰트 우선 (맑은 고딕)
            preferred_fonts = [
                os.path.join(fonts_dir, 'malgun.ttf'),     # 맑은 고딕
                os.path.join(fonts_dir, 'malgunbd.ttf'),   # 맑은 고딕 Bold
                os.path.join(fonts_dir, 'gulim.ttc'),      # 굴림
                os.path.join(fonts_dir, 'arial.ttf'),      # Arial
                os.path.join(fonts_dir, 'arialbd.ttf'),    # Arial Bold
            ]
        # Linux 폰트 경로
        elif platform.system() == 'Linux':
            preferred_fonts = [
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            ]
        # macOS 폰트 경로
        elif platform.system() == 'Darwin':
            preferred_fonts = [
                '/System/Library/Fonts/AppleSDGothicNeo.ttc',
                '/Library/Fonts/Arial Bold.ttf',
                '/System/Library/Fonts/Helvetica.ttc',
            ]
        else:
            preferred_fonts = []

        # 사용 가능한 첫 번째 폰트 반환
        for font_path in preferred_fonts:
            if os.path.exists(font_path):
                print(f"✅ 폰트 발견: {font_path}")
                return font_path

        # 폰트를 찾지 못한 경우
        print("⚠️ 시스템 폰트를 찾을 수 없습니다. 기본 폰트 사용")
        return None

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
            # MoviePy 2.x import
            from moviepy import (
                concatenate_videoclips, CompositeVideoClip,
                AudioFileClip, TextClip
            )
        except ImportError:
            raise ImportError("moviepy가 설치되지 않았습니다. pip install moviepy imageio-ffmpeg")

        # 비주얼 연결
        video = concatenate_videoclips(visual_clips, method="compose")

        # 영상을 오디오 길이에 맞춤
        if video.duration > duration:
            video = video.subclipped(0, duration)
        elif video.duration < duration:
            # 마지막 프레임을 freeze
            last_frame = visual_clips[-1]
            video = concatenate_videoclips([video, last_frame.with_duration(duration - video.duration)])

        # 오디오 추가
        audio = AudioFileClip(audio_path)
        video = video.with_audio(audio)

        # 숏폼은 9:16 크롭 (자막 추가 전에 먼저 크롭)
        if video_format == 'short':
            video = video.cropped(
                x_center=int(video.w/2),
                y_center=int(video.h/2),
                width=int(video.h * 9/16),
                height=int(video.h)
            )

        # 자막 추가 (폰트 경로 자동 탐지)
        font_path = self._find_font()

        def make_textclip(txt):
            # 텍스트 길이에 따라 폰트 크기 동적 조절
            text_length = len(txt)

            if video_format == 'short':
                # 숏폼: 더 공격적인 폰트 크기 조절로 잘림 방지
                if text_length < 20:
                    font_size = 42
                elif text_length < 35:
                    font_size = 35
                elif text_length < 50:
                    font_size = 30
                elif text_length < 70:
                    font_size = 26
                else:
                    font_size = 22  # 매우 긴 텍스트
            else:
                # 긴 영상: 더 공격적인 폰트 크기 조절
                if text_length < 25:
                    font_size = 45
                elif text_length < 45:
                    font_size = 38
                elif text_length < 65:
                    font_size = 32
                elif text_length < 90:
                    font_size = 28
                else:
                    font_size = 24  # 매우 긴 텍스트

            # 자막 영역을 95%로 확대 (더 넓게)
            max_width = int(video.w * 0.95)

            return TextClip(
                text=txt,
                font=font_path,
                font_size=font_size,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(max_width, None)  # 90%로 확대
            )

        subtitle_clips = []
        for sub in subtitles:
            txt_clip = make_textclip(sub['text'])
            txt_clip = txt_clip.with_start(sub['start']).with_duration(sub['end'] - sub['start'])

            # 숏폼은 화면 중앙 하단, 긴 영상은 하단
            if video_format == 'short':
                txt_clip = txt_clip.with_position(('center', int(video.h * 0.75)))  # 75% 위치
            else:
                txt_clip = txt_clip.with_position(('center', int(video.h * 0.85)))  # 85% 위치

            subtitle_clips.append(txt_clip)

        video = CompositeVideoClip([video] + subtitle_clips)

        return video
