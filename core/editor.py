"""
Editor Module
MoviePy 기반 영상 편집 및 합성
"""
import os
import json
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path

from core.models import (
    ContentPlan,
    AssetBundle,
    EditConfig,
    SubtitleSegment,
    VideoFormat,
    TemplateConfig
)
from core.bgm_manager import BGMManager


class VideoEditor:
    """MoviePy 기반 영상 편집기"""

    def __init__(self, config: Optional[EditConfig] = None, template_name: Optional[str] = None):
        """
        VideoEditor 초기화

        Args:
            config: 편집 설정 (None이면 기본값 사용)
            template_name: 템플릿 이름 (Phase 2: basic, documentary, entertainment)
        """
        self.config = config or EditConfig()

        # MoviePy import
        try:
            from moviepy import (
                VideoFileClip,
                AudioFileClip,
                ImageClip,
                TextClip,
                CompositeVideoClip,
                CompositeAudioClip,
                concatenate_videoclips
            )
            self.VideoFileClip = VideoFileClip
            self.AudioFileClip = AudioFileClip
            self.ImageClip = ImageClip
            self.TextClip = TextClip
            self.CompositeVideoClip = CompositeVideoClip
            self.CompositeAudioClip = CompositeAudioClip
            self.concatenate_videoclips = concatenate_videoclips
            print("[Editor] MoviePy 로드 완료")
        except ImportError as e:
            raise ImportError(
                f"MoviePy 패키지를 찾을 수 없습니다: {e}\n"
                "pip install moviepy를 실행하세요."
            )

        # 출력 디렉토리 생성
        os.makedirs(self.config.output_dir, exist_ok=True)

        # Phase 2: 템플릿 로드 (create_video에서 동적으로 처리)
        self.template: Optional[TemplateConfig] = None

        # Phase 2: BGM 매니저
        self.bgm_manager = BGMManager()

    def create_video(
        self,
        content_plan: ContentPlan,
        asset_bundle: AssetBundle,
        output_filename: Optional[str] = None,
        template_name: Optional[str] = None  # ✨ NEW
    ) -> Optional[str]:
        """
        ContentPlan과 AssetBundle로 최종 영상 생성

        Args:
            content_plan: ContentPlan 객체
            asset_bundle: AssetBundle 객체 (영상 + 음성)
            output_filename: 출력 파일명 (None이면 자동 생성)
            template_name: 사용할 템플릿 이름 (✨ NEW)

        Returns:
            저장된 영상 경로 또는 None
        """
        print(f"\n[Editor] 영상 편집 시작: {content_plan.title}")

        # ✨ NEW: 템플릿 동적 로드
        if template_name:
            self.template = self._load_template(template_name)
            if self.template:
                print(f"[Editor] 템플릿 로드 완료: {self.template.name}")
        else:
            self.template = None


        # 1. 비디오 클립 로드
        video_clips = self._load_video_clips(asset_bundle)
        if not video_clips:
            print("[ERROR] 사용 가능한 비디오 클립이 없습니다")
            return None

        # 2. 오디오 로드 (Phase 2: BGM 믹싱 포함)
        audio_clip = self._load_audio_with_bgm(asset_bundle, content_plan.target_duration)

        # 3. 영상 길이 계산 (오디오 길이 기준)
        if audio_clip:
            target_duration = audio_clip.duration
        else:
            target_duration = content_plan.target_duration

        print(f"[Editor] 목표 길이: {target_duration:.2f}초")

        # 4. 영상 클립 조정 및 연결
        final_video = self._compose_video_clips(
            video_clips,
            target_duration,
            content_plan.format
        )

        if not final_video:
            print("[ERROR] 영상 합성 실패")
            return None

        # 5. 오디오 추가
        if audio_clip:
            final_video = final_video.with_audio(audio_clip)

        # 6. 자막 추가
        if content_plan.segments:
            final_video = self._add_subtitles(
                final_video,
                content_plan,
                audio_clip.duration if audio_clip else target_duration
            )

        # 7. 출력 파일명 생성
        if not output_filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"video_{timestamp}.mp4"

        output_path = os.path.join(self.config.output_dir, output_filename)

        # 8. 영상 렌더링
        try:
            print(f"\n[Editor] 렌더링 시작: {output_filename}")
            final_video.write_videofile(
                output_path,
                fps=self.config.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )

            print(f"[SUCCESS] 영상 생성 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"[ERROR] 렌더링 실패: {e}")
            import traceback
            traceback.print_exc()
            return None

        finally:
            # 리소스 정리
            final_video.close()
            if audio_clip:
                audio_clip.close()
            for clip in video_clips:
                clip.close()

    def _load_video_clips(self, asset_bundle: AssetBundle) -> List:
        """
        AssetBundle에서 비디오 클립 로드

        Args:
            asset_bundle: AssetBundle 객체

        Returns:
            VideoFileClip 리스트
        """
        clips = []

        for asset in asset_bundle.videos:
            if not asset.local_path or not os.path.exists(asset.local_path):
                print(f"[WARNING] 영상 파일을 찾을 수 없음: {asset.id}")
                continue

            try:
                clip = self.VideoFileClip(asset.local_path)
                clips.append(clip)
                print(f"[Editor] 클립 로드: {asset.id} ({clip.duration:.2f}초)")
            except Exception as e:
                print(f"[ERROR] 클립 로드 실패 ({asset.id}): {e}")

        return clips

    def _load_audio(self, asset_bundle: AssetBundle):
        """
        AssetBundle에서 오디오 로드

        Args:
            asset_bundle: AssetBundle 객체

        Returns:
            AudioFileClip 또는 None
        """
        if not asset_bundle.audio:
            return None

        audio_path = asset_bundle.audio.local_path
        if not audio_path or not os.path.exists(audio_path):
            print("[WARNING] 오디오 파일을 찾을 수 없음")
            return None

        try:
            audio_clip = self.AudioFileClip(audio_path)
            print(f"[Editor] 오디오 로드: {audio_clip.duration:.2f}초")
            return audio_clip
        except Exception as e:
            print(f"[ERROR] 오디오 로드 실패: {e}")
            return None

    def _load_audio_with_bgm(self, asset_bundle: AssetBundle, target_duration: float):
        """
        Phase 2: TTS 오디오와 BGM 믹싱

        Args:
            asset_bundle: AssetBundle 객체
            target_duration: 목표 길이 (초)

        Returns:
            믹싱된 AudioFileClip 또는 TTS만, 또는 None
        """
        # 1. TTS 오디오 로드
        tts_audio = self._load_audio(asset_bundle)

        # 2. BGM이 없으면 TTS만 반환
        if not asset_bundle.bgm or (self.template and not self.template.bgm_enabled):
            return tts_audio

        # 3. BGM 처리
        try:
            bgm_asset = asset_bundle.bgm

            # BGM 볼륨 설정 (템플릿 우선, 없으면 AssetBundle 기본값)
            bgm_volume = self.template.bgm_volume if self.template else bgm_asset.volume

            # BGM 처리 (길이 조정, 페이드)
            processed_bgm_path = self.bgm_manager.process_bgm(
                bgm=bgm_asset,
                target_duration=target_duration,
                fade_in=1.0,
                fade_out=2.0,
                volume=bgm_volume
            )

            # BGM 오디오 로드
            bgm_audio = self.AudioFileClip(processed_bgm_path)
            print(f"[Editor] BGM 로드: {bgm_audio.duration:.2f}초, 볼륨: {bgm_volume}")

            # 4. TTS가 있으면 믹싱, 없으면 BGM만
            if tts_audio:
                # CompositeAudioClip으로 믹싱
                mixed_audio = self.CompositeAudioClip([tts_audio, bgm_audio])
                print(f"[Editor] TTS + BGM 믹싱 완료")
                return mixed_audio
            else:
                return bgm_audio

        except Exception as e:
            print(f"[ERROR] BGM 처리 실패: {e}")
            # 폴백: TTS만 반환
            return tts_audio

    def _compose_video_clips(
        self,
        clips: List,
        target_duration: float,
        video_format: VideoFormat
    ):
        """
        여러 클립을 조정하고 연결

        Args:
            clips: VideoFileClip 리스트
            target_duration: 목표 길이 (초)
            video_format: 영상 포맷

        Returns:
            CompositeVideoClip 또는 None
        """
        if not clips:
            return None

        # 해상도 설정
        width, height = self.config.resolution

        # 각 클립의 길이 계산 (균등 분배)
        clip_duration = target_duration / len(clips)

        processed_clips = []

        for i, clip in enumerate(clips):
            # 1. 길이 조정
            if clip.duration > clip_duration:
                # 클립이 더 길면 잘라내기
                clip = clip.subclipped(0, clip_duration)
            else:
                # 클립이 더 짧으면 반복 재생 (간단한 방법)
                # MoviePy 2.x에서 loop()가 제대로 작동하지 않을 수 있으므로
                # 클립을 여러 번 이어붙이는 방식 사용
                loops_needed = int(clip_duration / clip.duration) + 1
                repeated_clips = [clip] * loops_needed
                clip = self.concatenate_videoclips(repeated_clips, method="compose")
                clip = clip.subclipped(0, clip_duration)

            # 2. 해상도 조정 (crop & resize)
            clip = self._resize_and_crop(clip, width, height)

            processed_clips.append(clip)

        # 클립 연결
        try:
            final_clip = self.concatenate_videoclips(processed_clips, method="compose")
            print(f"[Editor] 클립 {len(processed_clips)}개 연결 완료")
            return final_clip
        except Exception as e:
            print(f"[ERROR] 클립 연결 실패: {e}")
            return None

    def _resize_and_crop(self, clip, target_width: int, target_height: int):
        """
        클립을 목표 해상도에 맞게 조정 (crop & resize)

        Args:
            clip: VideoFileClip
            target_width: 목표 너비
            target_height: 목표 높이

        Returns:
            조정된 클립
        """
        clip_width, clip_height = clip.size
        target_ratio = target_width / target_height
        clip_ratio = clip_width / clip_height

        if clip_ratio > target_ratio:
            # 클립이 더 넓음 → 좌우 크롭
            new_width = int(clip_height * target_ratio)
            x_center = clip_width / 2
            x1 = int(x_center - new_width / 2)
            clip = clip.cropped(x1=x1, width=new_width)
        else:
            # 클립이 더 높음 → 상하 크롭
            new_height = int(clip_width / target_ratio)
            y_center = clip_height / 2
            y1 = int(y_center - new_height / 2)
            clip = clip.cropped(y1=y1, height=new_height)

        # 리사이즈
        clip = clip.resized((target_width, target_height))

        return clip

    def _add_subtitles(
        self,
        video_clip,
        content_plan: ContentPlan,
        total_duration: float
    ):
        """
        자막 추가

        Args:
            video_clip: 베이스 비디오 클립
            content_plan: ContentPlan 객체
            total_duration: 총 영상 길이

        Returns:
            자막이 추가된 CompositeVideoClip
        """
        if not content_plan.segments:
            return video_clip

        # 세그먼트별 시간 계산
        segment_duration = total_duration / len(content_plan.segments)

        subtitle_clips = []

        for i, segment in enumerate(content_plan.segments):
            start_time = i * segment_duration

            # 자막 텍스트 (효과음 제거)
            import re
            text = re.sub(r'\([^)]*\)', '', segment.text).strip()

            if not text:
                continue

            # Phase 2: 템플릿 설정 적용
            if self.template:
                fontsize = self.template.subtitle_fontsize
                color = self.template.subtitle_color
                stroke_color = self.template.subtitle_stroke_color
                stroke_width = self.template.subtitle_stroke_width
                font_file = self.template.subtitle_font
                y_offset = self.template.subtitle_y_offset
                position = self.template.subtitle_position
            else:
                # 텍스트 길이에 따라 폰트 크기 조정 (기본 동작)
                text_len = len(text)
                if text_len > 50:
                    fontsize = 32
                elif text_len > 30:
                    fontsize = 36
                else:
                    fontsize = 40
                color = 'white'
                stroke_color = 'black'
                stroke_width = 2
                font_file = 'malgun.ttf'
                y_offset = 100
                position = 'bottom'

            try:
                # 폰트 경로 설정 (Windows 호환)
                import platform
                if platform.system() == 'Windows':
                    # Windows: 폰트 파일명 → 전체 경로
                    font_path = f'C:\\Windows\\Fonts\\{font_file}'
                else:
                    # Linux/Mac: DejaVu Sans (fallback)
                    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

                # TextClip 생성
                txt_clip = self.TextClip(
                    text=text,
                    font=font_path,
                    font_size=fontsize,
                    color=color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    method='caption',
                    size=(int(self.config.resolution[0] * 0.9), None)
                )

                # 위치 설정 (템플릿 기반)
                if position == 'bottom':
                    y_position = int(self.config.resolution[1] - y_offset)
                    txt_clip = txt_clip.with_position(('center', y_position))
                elif position == 'center':
                    txt_clip = txt_clip.with_position('center')
                elif position == 'top':
                    txt_clip = txt_clip.with_position(('center', y_offset))
                else:
                    # 기본값: 하단
                    y_position = int(self.config.resolution[1] - 100)
                    txt_clip = txt_clip.with_position(('center', y_position))

                # 시간 설정
                txt_clip = txt_clip.with_start(start_time).with_duration(segment_duration)

                subtitle_clips.append(txt_clip)

            except Exception as e:
                print(f"[WARNING] 자막 생성 실패 ({i+1}): {e}")

        if subtitle_clips:
            # 비디오 + 자막 합성
            video_clip = self.CompositeVideoClip([video_clip] + subtitle_clips)
            print(f"[Editor] 자막 {len(subtitle_clips)}개 추가 완료")

        return video_clip

    def _load_template(self, template_name: str) -> Optional[TemplateConfig]:
        """
        Phase 2: 템플릿 JSON 파일 로드

        Args:
            template_name: 템플릿 이름 (basic, documentary, entertainment)

        Returns:
            TemplateConfig 객체 또는 None
        """
        template_path = Path(__file__).parent.parent / "templates" / f"{template_name}.json"

        if not template_path.exists():
            print(f"[WARNING] 템플릿 파일 없음: {template_path}")
            return None

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return TemplateConfig(**data)
        except Exception as e:
            print(f"[ERROR] 템플릿 로드 실패: {e}")
            return None

    def __repr__(self):
        return f"VideoEditor(resolution={self.config.resolution}, fps={self.config.fps})"
