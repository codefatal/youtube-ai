"""
Editor Module
MoviePy 기반 영상 편집 및 합성 (SHORTS_SPEC.md 기준)
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

# SHORTS_SPEC.md: config.py 상수 사용
from core.config import (
    CANVAS_WIDTH, CANVAS_HEIGHT,
    FONT_TITLE, FONT_SUBTITLE,
    FONT_SIZE_TITLE, FONT_SIZE_SUBTITLE,
    SUBTITLE_SAFE_Y_MIN, SUBTITLE_SAFE_Y_MAX,
    clamp_y_to_safe_zone
)

# SHORTS_SPEC.md: SubtitleService 사용 (Pillow 기반)
from core.services.subtitle_service import get_subtitle_service


class VideoEditor:
    """MoviePy 기반 영상 편집기"""

    # ✨ 시각 효과 설정 (Task 3)
    ENABLE_KEN_BURNS = True      # Ken Burns Effect (Zoom)
    ENABLE_CROSSFADE = True      # 클립 간 크로스페이드
    KEN_BURNS_ZOOM_RATIO = 1.15  # 줌 배율 (1.1 ~ 1.2 권장)
    CROSSFADE_DURATION = 0.3     # 크로스페이드 길이 (초)

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

        # 영상 길이 제어 - TTS 길이에 맞춤 (무음 추가 없이)
        if audio_clip:
            actual_duration = audio_clip.duration
            target_duration = actual_duration  # TTS 길이를 최종 길이로 사용
            print(f"[Editor] TTS 길이: {actual_duration:.2f}초")
            print(f"[Editor] 최종 영상 길이를 TTS에 맞춤: {target_duration:.2f}초")
        else:
            target_duration = content_plan.target_duration
            print(f"[Editor] 오디오 없음, 목표 길이 사용: {target_duration:.2f}초")

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

        # 6. 자막 추가 (FIX: target_duration 강제)
        if content_plan.segments:
            final_video = self._add_subtitles(
                final_video,
                content_plan,
                target_duration  # audio_clip.duration 대신 target_duration 사용
            )

        # 7. 출력 파일명 생성
        if not output_filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"video_{timestamp}.mp4"

        output_path = os.path.join(self.config.output_dir, output_filename)

        # FIX: 최종 영상 길이 강제 조정
        actual_video_duration = final_video.duration
        print(f"[Editor] 렌더링 전 영상 길이: {actual_video_duration:.2f}초 (목표: {target_duration:.2f}초)")

        if abs(actual_video_duration - target_duration) > 0.5:
            print(f"[WARNING] 영상 길이가 목표와 {abs(actual_video_duration - target_duration):.2f}초 차이남. 강제 조정 중...")
            if actual_video_duration > target_duration:
                # 길면 자르기
                final_video = final_video.subclipped(0, target_duration)
            else:
                # 짧으면 마지막 프레임 freeze
                final_video = final_video.with_duration(target_duration)
            print(f"[Editor] 영상 길이 조정 완료: {final_video.duration:.2f}초")

        # 8. 영상 렌더링
        try:
            print(f"\n[Editor] 렌더링 시작: {output_filename} ({target_duration:.2f}초)")
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
        Phase 2: TTS 오디오와 BGM 믹싱 (고도화 버전)

        Args:
            asset_bundle: AssetBundle 객체
            target_duration: 목표 길이 (초)

        Returns:
            믹싱된 AudioFileClip 또는 TTS만, 또는 None
        """
        # MoviePy audio effects import
        from moviepy.audio import fx as afx

        # 1. TTS 오디오 로드
        tts_audio = self._load_audio(asset_bundle)

        # 2. BGM이 없으면 TTS만 반환
        if not asset_bundle.bgm or (self.template and not self.template.bgm_enabled):
            return tts_audio

        # 3. BGM 처리
        try:
            bgm_asset = asset_bundle.bgm

            # ✨ BGM 파일 존재 및 유효성 검증
            if not bgm_asset.local_path or not os.path.exists(bgm_asset.local_path):
                print(f"[ERROR] BGM 파일이 존재하지 않습니다: {bgm_asset.local_path}")
                return tts_audio

            bgm_file_size = os.path.getsize(bgm_asset.local_path)
            if bgm_file_size < 1024:  # 1KB 미만이면 유효하지 않음
                print(f"[ERROR] BGM 파일 크기가 너무 작습니다: {bgm_file_size} bytes")
                return tts_audio

            print(f"[Editor] BGM 파일 검증 완료: {bgm_asset.name} ({bgm_file_size / 1024:.1f}KB)")

            # BGM 볼륨 설정 (템플릿 우선, 없으면 AssetBundle 기본값)
            # ✨ 볼륨 범위 조정: 0.15 ~ 0.3 (기존 0.1~0.2는 너무 낮음)
            # ✨ getattr로 안전하게 접근 (템플릿에 bgm_volume이 없을 수 있음)
            bgm_volume = getattr(self.template, 'bgm_volume', bgm_asset.volume) if self.template else bgm_asset.volume
            bgm_volume = max(0.15, min(0.3, bgm_volume))  # 안전한 범위로 클램프

            # ✨ MoviePy로 직접 BGM 로드 및 처리 (ffmpeg 의존성 제거)
            bgm_audio = self.AudioFileClip(bgm_asset.local_path)
            print(f"[Editor] BGM 원본 로드: {bgm_audio.duration:.2f}초")

            # ✨ audio_loop: 영상 길이에 맞게 BGM 반복
            if bgm_audio.duration < target_duration:
                loops_needed = int(target_duration / bgm_audio.duration) + 1
                print(f"[Editor] BGM 반복 필요: {loops_needed}회")
                bgm_audio = afx.AudioLoop(bgm_audio, nloops=loops_needed)

            # ✨ 정확한 길이로 자르기
            bgm_audio = bgm_audio.subclipped(0, target_duration)

            # ✨ 페이드 인/아웃 적용
            bgm_audio = afx.AudioFadeIn(bgm_audio, 1.0)  # 1초 페이드 인
            bgm_audio = afx.AudioFadeOut(bgm_audio, 2.0)  # 2초 페이드 아웃

            # ✨ volumex로 볼륨 조절 (핵심!)
            bgm_audio = bgm_audio.with_effects([afx.MultiplyVolume(bgm_volume)])
            print(f"[Editor] BGM 처리 완료: {bgm_audio.duration:.2f}초, 볼륨: {bgm_volume}")

            # 4. TTS가 있으면 믹싱, 없으면 BGM만
            if tts_audio:
                # ✨ CompositeAudioClip: BGM을 먼저 배치하고 TTS를 위에 올림
                # TTS가 BGM에 묻히지 않도록 TTS 볼륨 유지
                mixed_audio = self.CompositeAudioClip([bgm_audio, tts_audio])
                print(f"[Editor] TTS + BGM 믹싱 완료 (BGM 볼륨: {bgm_volume})")
                return mixed_audio
            else:
                return bgm_audio

        except Exception as e:
            print(f"[ERROR] BGM 처리 실패: {e}")
            import traceback
            traceback.print_exc()
            # 폴백: TTS만 반환
            return tts_audio

    def _compose_video_clips(
        self,
        clips: List,
        target_duration: float,
        video_format: VideoFormat
    ):
        """
        여러 클립을 조정하고 연결 (Task 3: VFX 효과 포함)

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

        # ✨ Task 3-2: 크로스페이드를 위해 각 클립 길이 조정
        crossfade_duration = self.CROSSFADE_DURATION if self.ENABLE_CROSSFADE else 0
        num_clips = len(clips)

        # 크로스페이드로 인한 오버랩 시간 계산
        total_overlap = crossfade_duration * (num_clips - 1) if num_clips > 1 else 0
        effective_duration = target_duration + total_overlap

        # Phase 3: 각 클립의 길이 계산 (균등 분배 + 미세 조정)
        base_clip_duration = effective_duration / len(clips)

        processed_clips = []

        for i, clip in enumerate(clips):
            # Phase 3: 마지막 클립은 남은 시간 정확히 맞춤
            if i == len(clips) - 1:
                # 이미 처리된 클립들의 총 시간 계산
                elapsed_time = sum(c.duration for c in processed_clips)
                clip_duration = effective_duration - elapsed_time
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

            # ✨ Task 3-1: Ken Burns Effect 적용
            if self.ENABLE_KEN_BURNS:
                clip = self._apply_ken_burns_effect(clip, self.KEN_BURNS_ZOOM_RATIO)

            # ✨ Task 3-2: 크로스페이드 효과 적용 (MoviePy 2.x 호환)
            if self.ENABLE_CROSSFADE and crossfade_duration > 0:
                from moviepy.video import fx as vfx
                # 첫 클립은 페이드 인만, 마지막 클립은 페이드 아웃만
                if i > 0:
                    # CrossFadeIn 효과 적용
                    clip = clip.with_effects([vfx.CrossFadeIn(crossfade_duration)])
                if i < num_clips - 1:
                    # CrossFadeOut 효과 적용
                    clip = clip.with_effects([vfx.CrossFadeOut(crossfade_duration)])

            processed_clips.append(clip)

        # 클립 연결
        try:
            # ✨ Task 3-2: 크로스페이드가 활성화되면 오버랩 연결
            if self.ENABLE_CROSSFADE and crossfade_duration > 0 and num_clips > 1:
                # CompositeVideoClip으로 오버랩 배치
                clips_with_timing = []
                current_start = 0

                for i, clip in enumerate(processed_clips):
                    clips_with_timing.append(clip.with_start(current_start))
                    # 다음 클립은 크로스페이드만큼 겹침
                    current_start += clip.duration - crossfade_duration

                final_clip = self.CompositeVideoClip(clips_with_timing, size=(width, height))
                print(f"[Editor] 클립 {len(processed_clips)}개 크로스페이드 연결 완료 (오버랩: {crossfade_duration}초)")
            else:
                final_clip = self.concatenate_videoclips(processed_clips, method="compose")
                print(f"[Editor] 클립 {len(processed_clips)}개 연결 완료")

            final_duration = final_clip.duration
            print(f"[Editor] 최종 영상 길이: {final_duration:.2f}초 (목표: {target_duration:.2f}초, 차이: {abs(final_duration - target_duration):.2f}초)")
            return final_clip
        except Exception as e:
            print(f"[ERROR] 클립 연결 실패: {e}")
            import traceback
            traceback.print_exc()
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

    def _apply_ken_burns_effect(self, clip, zoom_ratio: float = 1.15):
        """
        ✨ Task 3-1: Ken Burns Effect (천천히 줌인하는 효과)

        정적인 영상에 동적인 느낌을 주기 위해 서서히 줌인합니다.

        Args:
            clip: VideoFileClip
            zoom_ratio: 최종 줌 배율 (1.1 ~ 1.2 권장)

        Returns:
            Ken Burns 효과가 적용된 클립
        """
        if not self.ENABLE_KEN_BURNS:
            return clip

        try:
            duration = clip.duration
            width, height = clip.size

            def zoom_effect(get_frame, t):
                """시간에 따라 점진적으로 줌인"""
                # t=0일 때 zoom=1.0, t=duration일 때 zoom=zoom_ratio
                progress = t / duration if duration > 0 else 0
                current_zoom = 1.0 + (zoom_ratio - 1.0) * progress

                # 현재 프레임 가져오기
                frame = get_frame(t)

                # 줌 적용 (중앙 기준으로 크롭)
                import numpy as np
                from PIL import Image

                # numpy array를 PIL Image로 변환
                img = Image.fromarray(frame)

                # 새로운 크기 계산
                new_width = int(width * current_zoom)
                new_height = int(height * current_zoom)

                # 리사이즈
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 중앙 크롭
                left = (new_width - width) // 2
                top = (new_height - height) // 2
                img_cropped = img_resized.crop((left, top, left + width, top + height))

                return np.array(img_cropped)

            # transform 적용
            zoomed_clip = clip.transform(zoom_effect)
            print(f"[Editor] Ken Burns Effect 적용: 줌 배율 {zoom_ratio}")

            return zoomed_clip

        except Exception as e:
            print(f"[WARNING] Ken Burns Effect 적용 실패: {e}")
            return clip

    def _create_shorts_layout(self, video_clip, title: str, duration: float):
        """
        Phase 2: 쇼츠 레이아웃 생성 (상단 1/4 + 중앙 1/2 + 하단 1/4)
        SHORTS_SPEC.md: config.py 상수 사용

        Args:
            video_clip: 원본 비디오 클립 (1080x1920)
            title: 영상 제목
            duration: 영상 길이

        Returns:
            레이아웃이 적용된 CompositeVideoClip
        """
        width = CANVAS_WIDTH   # 1080
        height = CANVAS_HEIGHT  # 1920

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

            # 2. 상단 제목 텍스트 (SHORTS_SPEC.md: config.py 폰트 사용)
            # 이모지 및 특수문자 제거 (MoviePy 렌더링 오류 방지)
            import re
            # 모든 이모지 범위 제거 (U+1F000 ~ U+1FFFF)
            title = re.sub(r'[\U0001F000-\U0001FFFF]', '', title)
            # 추가 이모지 및 특수 기호 제거
            title = re.sub(r'[✨💡🎉🔥💪🙌👍❤️🎯📢🎵🎶👇👆⭐️🌟💫⚡️🚀✅❌⚠️💯🎁🏆🎬📱💻🌈☀️🌙⭐🔴🟢🔵⚫⚪]', '', title)
            # 다른 특수문자 범위 제거
            title = re.sub(r'[\u2600-\u26FF\u2700-\u27BF]', '', title)
            title = title.strip()

            if not title:
                title = "영상 제목"  # 빈 제목 방지

            # FIX: 줄바꿈 기준 증가 (15자 → 20자)
            wrapped_title = self._wrap_text(title, max_chars=20)

            # ✨ UPGRADE_AI.md 수정사항 적용
            # 1. stroke_width 설정 (마진 계산에 사용)
            stroke_width = 3

            # SHORTS_SPEC.md: config.py에서 폰트 및 크기 가져옴
            title_text_clip = self.TextClip(
                text=wrapped_title,
                font=FONT_TITLE,  # config.py에서 관리
                font_size=FONT_SIZE_TITLE,  # 80px
                color='white',
                stroke_color='black',
                stroke_width=stroke_width,
                method='label',  # 자동 크기 조정 (size 지정 안 함)
                interline=70  # ✨ 줄 간격 더 증가 (60→70, 하단 잘림 방지)
            ).with_duration(duration)

            # FIX: 반투명 배경 박스 추가 (차별화) + Safe Zone 적용
            text_width, text_height = title_text_clip.size

            # 줄바꿈 개수 확인 (줄간격 고려)
            line_count = wrapped_title.count('\n') + 1

            # ✨ 수정 1: 수직 패딩 대폭 증가 (Descender 잘림 방지)
            # stroke_width 만큼 추가 마진 확보
            stroke_margin = stroke_width * 2

            # 패딩 추가 (좌우 40px + stroke 마진)
            bg_width = min(text_width + 80 + stroke_margin, width - 40)

            # ✨ 수직 패딩 비율 대폭 증가 (기존 3.0/2.2 → 4.0/3.0)
            # Descender(g, j, y 등) 및 폰트 높이 계산 오차 고려
            vertical_padding_ratio = 4.0 if line_count == 1 else 3.0
            bg_height = int(text_height * (1 + vertical_padding_ratio)) + stroke_margin

            print(f"[Title] 줄 수: {line_count}, 텍스트 높이: {text_height}px, 배경 박스 높이: {bg_height}px")

            # ✨ 수정 2: 유튜브 쇼츠 Safe Zone 적용 (상단 5~8% 여백)
            # 유튜브 쇼츠 UI(검색 버튼 등)에 가려지지 않도록 상단에서 약 7% 내려온 위치
            safe_zone_top = int(height * 0.07)  # 1920px * 0.07 = 약 134px

            # Safe Zone: 배경 박스가 top_height를 넘지 않도록 제한
            max_bg_height = top_height - safe_zone_top - 20  # 하단 20px 여백
            if bg_height > max_bg_height:
                bg_height = max_bg_height
                print(f"[WARNING] 제목 박스 높이 제한: {bg_height}px (max: {max_bg_height}px)")

            title_bg = self.ColorClip(
                size=(bg_width, bg_height),
                color=(0, 0, 0),  # 검은색
            ).with_duration(duration).with_opacity(0.7)  # 70% 불투명

            # ✨ 배경 박스 위치: Safe Zone 적용 (상단 7% 지점부터 시작)
            # 기존: bg_y = max(20, (top_height - bg_height) // 2)
            # 수정: bg_y = safe_zone_top (유튜브 UI 회피)
            bg_y = safe_zone_top

            # 하단 잘림 방지: bg_y + bg_height가 top_height를 넘지 않도록
            if bg_y + bg_height > top_height - 20:
                bg_y = top_height - bg_height - 20

            title_bg = title_bg.with_position(('center', bg_y))

            # ✨ 수정 3: 텍스트 위치 - 배경 박스 내 중앙 + 하단 여유 추가
            # Descender 잘림 방지를 위해 텍스트를 배경 박스 상단에 약간 붙임
            # (하단에 더 많은 여유 공간 확보)
            descender_buffer = int(text_height * 0.15)  # 텍스트 높이의 15% 추가 버퍼
            text_y = bg_y + (bg_height - text_height) // 2 - descender_buffer

            # text_y가 bg_y보다 작아지지 않도록 보정
            text_y = max(bg_y + 10, text_y)

            title_text_clip = title_text_clip.with_position(('center', text_y))

            print(f"[Title] Safe Zone: {safe_zone_top}px, 배경 Y: {bg_y}px, 텍스트 Y: {text_y}px, 하단 여유: {bg_y + bg_height - text_y - text_height}px")

            # FIX: 배경 + 텍스트를 하나로 합성
            title_composite = self.CompositeVideoClip(
                [title_bg, title_text_clip],
                size=(width, top_height)
            ).with_duration(duration).with_position((0, 0))

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
                    title_composite,  # title_clip → title_composite
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
        자막 추가 (SHORTS_SPEC.md: SubtitleService + Safe Zone 적용)

        Args:
            video_clip: 베이스 비디오 클립
            content_plan: ContentPlan 객체
            total_duration: 총 영상 길이

        Returns:
            자막이 추가된 CompositeVideoClip
        """
        if not content_plan.segments:
            return video_clip

        # SHORTS_SPEC.md: SubtitleService 사용 (Pillow 기반 + Safe Zone)
        subtitle_service = get_subtitle_service()

        # 세그먼트를 dict 리스트로 변환 (SubtitleService 인터페이스 맞춤)
        segments_data = []
        current_time = 0.0

        for seg in content_plan.segments:
            duration = seg.duration if seg.duration else 3.0

            # Whisper로 정렬된 경우 start/end 사용, 아니면 누적 계산
            if hasattr(seg, 'start') and seg.start is not None:
                start_time = seg.start
                end_time = seg.end if hasattr(seg, 'end') else start_time + duration
            else:
                start_time = current_time
                end_time = current_time + duration

            segments_data.append({
                "text": seg.text,
                "start": start_time,
                "end": end_time,
                "duration": duration
            })

            current_time = end_time

        # SubtitleService로 자막 클립 정보 생성 (PIL Image + Safe Zone 적용됨)
        subtitle_clip_data = subtitle_service.create_subtitle_clips(segments_data, fps=self.config.fps)

        # PIL Image를 MoviePy ImageClip으로 변환
        subtitle_clips = []

        for i, data in enumerate(subtitle_clip_data):
            try:
                pil_image = data["image"]       # PIL.Image
                start_time = data["start"]      # float
                duration = data["duration"]     # float
                y_position = data["y_position"] # int (Safe Zone 적용됨)

                # PIL Image를 numpy array로 변환하여 ImageClip 생성
                import numpy as np
                img_array = np.array(pil_image)

                # MoviePy ImageClip 생성
                img_clip = self.ImageClip(img_array).with_duration(duration).with_start(start_time)

                # 위치는 이미 PIL 이미지에 포함되어 있으므로 (0, 0)으로 배치
                img_clip = img_clip.with_position((0, 0))

                subtitle_clips.append(img_clip)

                print(f"[Subtitle {i+1}] '{data['text'][:30]}...' at {start_time:.1f}s-{start_time+duration:.1f}s (Safe Zone Y={y_position}px)")

            except Exception as e:
                print(f"[WARNING] 자막 이미지 변환 실패 ({i+1}): {e}")
                import traceback
                traceback.print_exc()

        if subtitle_clips:
            # 비디오 + 자막 합성
            video_clip = self.CompositeVideoClip([video_clip] + subtitle_clips)
            print(f"[Editor] 자막 {len(subtitle_clips)}개 추가 완료 (SHORTS_SPEC.md Safe Zone 적용)")

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
