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
                ColorClip,
                TextClip,
                CompositeVideoClip,
                CompositeAudioClip,
                concatenate_videoclips
            )
            self.VideoFileClip = VideoFileClip
            self.AudioFileClip = AudioFileClip
            self.ImageClip = ImageClip
            self.ColorClip = ColorClip
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

        # 3. Phase 3: 영상 길이 계산 (오디오 길이 기준 - 정확도 개선)
        if audio_clip:
            target_duration = audio_clip.duration
            print(f"[Editor] 실제 TTS 오디오 길이 사용: {target_duration:.2f}초")
        elif asset_bundle.audio and asset_bundle.audio.duration:
            # TTS duration이 명시적으로 설정된 경우
            target_duration = asset_bundle.audio.duration
            print(f"[Editor] TTS AssetBundle 길이 사용: {target_duration:.2f}초")
        else:
            target_duration = content_plan.target_duration
            print(f"[Editor] ContentPlan 목표 길이 사용: {target_duration:.2f}초")

        print(f"[Editor] 최종 목표 길이: {target_duration:.2f}초")

        # 4. 영상 클립 조정 및 연결
        final_video = self._compose_video_clips(
            video_clips,
            target_duration,
            content_plan.format
        )

        if not final_video:
            print("[ERROR] 영상 합성 실패")
            return None

        # 4-1. Phase 2: 쇼츠 레이아웃 적용 (SHORTS 포맷인 경우)
        if content_plan.format == VideoFormat.SHORTS:
            final_video = self._create_shorts_layout(
                final_video,
                content_plan.title,
                target_duration
            )

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

        # Phase 3: 각 클립의 길이 계산 (균등 분배 + 미세 조정)
        base_clip_duration = target_duration / len(clips)

        processed_clips = []

        for i, clip in enumerate(clips):
            # Phase 3: 마지막 클립은 남은 시간 정확히 맞춤
            if i == len(clips) - 1:
                # 이미 처리된 클립들의 총 시간 계산
                elapsed_time = sum(c.duration for c in processed_clips)
                clip_duration = target_duration - elapsed_time
                print(f"[Editor] 마지막 클립 길이 조정: {clip_duration:.2f}초 (남은 시간)")
            else:
                clip_duration = base_clip_duration

            # 1. 길이 조정
            if clip.duration > clip_duration:
                # 클립이 더 길면 잘라내기
                clip = clip.subclipped(0, clip_duration)
            else:
                # 클립이 더 짧으면 반복 재생
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
            final_duration = final_clip.duration
            print(f"[Editor] 클립 {len(processed_clips)}개 연결 완료")
            print(f"[Editor] 최종 영상 길이: {final_duration:.2f}초 (목표: {target_duration:.2f}초, 차이: {abs(final_duration - target_duration):.2f}초)")
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

    def _create_shorts_layout(self, video_clip, title: str, duration: float):
        """
        Phase 2: 쇼츠 레이아웃 생성 (상단 1/4 + 중앙 1/2 + 하단 1/4)

        Args:
            video_clip: 원본 비디오 클립 (1080x1920)
            title: 영상 제목
            duration: 영상 길이

        Returns:
            레이아웃이 적용된 CompositeVideoClip
        """
        width = 1080
        height = 1920

        # 섹션 높이 계산
        top_height = height // 4      # 480px
        middle_height = height // 2   # 960px
        bottom_height = height // 4   # 480px

        try:
            # 1. 상단 검은 배경 (480px)
            top_bg = self.ColorClip(
                size=(width, top_height),
                color=(0, 0, 0)
            ).with_duration(duration).with_position((0, 0))

            # 2. 상단 제목 텍스트
            import platform
            font_path = 'C:\\Windows\\Fonts\\malgunbd.ttf' if platform.system() == 'Windows' else '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

            # 제목 줄바꿈 (10자 기준 - 짧게 제한)
            wrapped_title = self._wrap_text(title, max_chars=10)

            title_clip = self.TextClip(
                text=wrapped_title,
                font=font_path,
                font_size=55,  # 크기 줄임
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(int(width * 0.8), None)  # 폭 줄임
            ).with_duration(duration)

            # 제목을 상단 섹션 중앙에 정확히 배치
            title_y = (top_height - title_clip.size[1]) // 2
            title_clip = title_clip.with_position(('center', title_y))

            # 3. 중앙 비디오 (960px) - 원본 비디오를 중앙 섹션에 맞게 조정
            # 비디오 크기 확인
            video_width, video_height = video_clip.size

            # 중앙 섹션 비율에 맞게 crop & resize
            middle_video = self._resize_and_crop(video_clip, width, middle_height)
            middle_video = middle_video.with_position((0, top_height))

            # 4. 하단 검은 배경 (480px)
            bottom_bg = self.ColorClip(
                size=(width, bottom_height),
                color=(0, 0, 0)
            ).with_duration(duration).with_position((0, top_height + middle_height))

            # 5. 모든 레이어 합성
            composite = self.CompositeVideoClip(
                [
                    top_bg,
                    title_clip,
                    middle_video,
                    bottom_bg
                ],
                size=(width, height)
            )

            print(f"[Editor] 쇼츠 레이아웃 적용 완료 (상단: {top_height}px, 중앙: {middle_height}px, 하단: {bottom_height}px)")
            return composite

        except Exception as e:
            print(f"[ERROR] 쇼츠 레이아웃 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            # 폴백: 원본 비디오 반환
            return video_clip

    def _wrap_text(self, text: str, max_chars: int = 25) -> str:
        """
        자막 텍스트를 단어 단위로 줄바꿈 (Phase 1)

        Args:
            text: 원본 텍스트
            max_chars: 한 줄 최대 글자 수 (기본 25자, 너무 긴 텍스트만 줄바꿈)

        Returns:
            줄바꿈이 적용된 텍스트
        """
        if len(text) <= max_chars:
            return text

        # 단어 단위로 분리 (공백 기준)
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            # 현재 줄에 단어를 추가했을 때 길이 체크
            test_line = current_line + (" " if current_line else "") + word

            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                # 현재 줄이 비어있지 않으면 저장
                if current_line:
                    lines.append(current_line)
                # 새로운 줄 시작
                current_line = word

        # 마지막 줄 추가
        if current_line:
            lines.append(current_line)

        return '\n'.join(lines)

    def _add_subtitles(
        self,
        video_clip,
        content_plan: ContentPlan,
        total_duration: float
    ):
        """
        자막 추가 (Phase 1 재설계: TTS 세그먼트별 정확한 싱크)

        Args:
            video_clip: 베이스 비디오 클립
            content_plan: ContentPlan 객체
            total_duration: 총 영상 길이

        Returns:
            자막이 추가된 CompositeVideoClip
        """
        if not content_plan.segments:
            return video_clip

        subtitle_clips = []
        current_time = 0.0  # 누적 시간 추적

        for i, segment in enumerate(content_plan.segments):
            # 자막 텍스트 (효과음 제거)
            import re
            text = re.sub(r'\([^)]*\)', '', segment.text).strip()

            if not text:
                # 텍스트가 없어도 시간은 진행
                if segment.duration:
                    current_time += segment.duration
                continue

            # Phase 1 수정: 세그먼트 텍스트 그대로 사용 (강제 줄바꿈 제거)
            # 단, 너무 길면 자동 줄바꿈 (25자 기준)
            if len(text) > 25:
                text = self._wrap_text(text, max_chars=25)
            # 그 외에는 세그먼트 텍스트 그대로 (1줄 표시)

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
                # Phase 1: 기본 폰트 크기 (60-70)
                text_len = len(text.replace('\n', ''))  # 줄바꿈 제외한 글자 수
                if text_len > 50:
                    fontsize = 60
                elif text_len > 30:
                    fontsize = 65
                else:
                    fontsize = 70
                color = 'white'
                stroke_color = 'black'
                stroke_width = 3  # 외곽선 두께
                font_file = 'malgun.ttf'
                y_offset = 150  # 하단 여백
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

                # Phase 1 수정: TextClip 생성 (자동 크기 조정)
                txt_clip = self.TextClip(
                    text=text,
                    font=font_path,
                    font_size=fontsize,
                    color=color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    method='label',  # caption → label (자동 크기)
                    # size 제거 - 자동으로 텍스트 크기에 맞춤
                )

                # Phase 2: 쇼츠 레이아웃 적용 시 자막 위치 조정
                if content_plan.format == VideoFormat.SHORTS:
                    # 쇼츠 레이아웃: 중간 영상 영역 하단에 자막 배치
                    # 중간 영상 영역: y=480~1440 (960px)
                    # 하단에서 150px 위 (y=1290)
                    y_position = 1440 - 150
                    txt_clip = txt_clip.with_position(('center', y_position))
                elif position == 'bottom':
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

                # Phase 1 수정: 세그먼트별 정확한 시간 설정
                segment_duration = segment.duration if segment.duration else 3.0
                txt_clip = txt_clip.with_start(current_time).with_duration(segment_duration)

                subtitle_clips.append(txt_clip)

                # 누적 시간 업데이트
                current_time += segment_duration

                print(f"[Subtitle {i+1}] '{text[:30]}...' at {current_time-segment_duration:.1f}s-{current_time:.1f}s ({segment_duration:.1f}s)")

            except Exception as e:
                print(f"[WARNING] 자막 생성 실패 ({i+1}): {e}")
                # 에러가 나도 시간은 진행
                if segment.duration:
                    current_time += segment.duration

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
