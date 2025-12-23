"""
Editor Module
MoviePy 기반 영상 편집 및 합성
"""
import os
from typing import List, Optional, Tuple
from pathlib import Path

from core.models import (
    ContentPlan,
    AssetBundle,
    EditConfig,
    SubtitleSegment,
    VideoFormat
)


class VideoEditor:
    """MoviePy 기반 영상 편집기"""

    def __init__(self, config: Optional[EditConfig] = None):
        """
        VideoEditor 초기화

        Args:
            config: 편집 설정 (None이면 기본값 사용)
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

    def create_video(
        self,
        content_plan: ContentPlan,
        asset_bundle: AssetBundle,
        output_filename: Optional[str] = None
    ) -> Optional[str]:
        """
        ContentPlan과 AssetBundle로 최종 영상 생성

        Args:
            content_plan: ContentPlan 객체
            asset_bundle: AssetBundle 객체 (영상 + 음성)
            output_filename: 출력 파일명 (None이면 자동 생성)

        Returns:
            저장된 영상 경로 또는 None
        """
        print(f"\n[Editor] 영상 편집 시작: {content_plan.title}")

        # 1. 비디오 클립 로드
        video_clips = self._load_video_clips(asset_bundle)
        if not video_clips:
            print("[ERROR] 사용 가능한 비디오 클립이 없습니다")
            return None

        # 2. 오디오 로드
        audio_clip = self._load_audio(asset_bundle)

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
                remove_temp=True,
                verbose=False,
                logger=None
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
                clip = clip.with_subclip(0, clip_duration)
            else:
                # 클립이 더 짧으면 루프 (최대 clip_duration까지)
                loops_needed = int(clip_duration / clip.duration) + 1
                clip = clip.loop(n=loops_needed).with_subclip(0, clip_duration)

            # 2. 해상도 조정 (crop & resize)
            clip = self._resize_and_crop(clip, width, height)

            # 3. 트랜지션 효과 (첫 클립 제외)
            if i > 0 and self.config.enable_transitions:
                clip = clip.crossfadein(0.5)

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
            end_time = (i + 1) * segment_duration

            # 자막 텍스트 (효과음 제거)
            import re
            text = re.sub(r'\([^)]*\)', '', segment.text).strip()

            if not text:
                continue

            # 텍스트 길이에 따라 폰트 크기 조정
            text_len = len(text)
            if text_len > 50:
                fontsize = 32
            elif text_len > 30:
                fontsize = 36
            else:
                fontsize = 40

            try:
                # TextClip 생성
                txt_clip = self.TextClip(
                    text=text,
                    font='Arial',
                    font_size=fontsize,
                    color='white',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(self.config.resolution[0] * 0.9, None)
                )

                # 위치 설정 (하단 중앙)
                txt_clip = txt_clip.with_position(('center', 'bottom')).margin(bottom=50)

                # 시간 설정
                txt_clip = txt_clip.with_start(start_time).with_duration(segment_duration)

                # 페이드 효과
                if self.config.enable_subtitle_animation:
                    txt_clip = txt_clip.crossfadein(0.3).crossfadeout(0.3)

                subtitle_clips.append(txt_clip)

            except Exception as e:
                print(f"[WARNING] 자막 생성 실패 ({i+1}): {e}")

        if subtitle_clips:
            # 비디오 + 자막 합성
            video_clip = self.CompositeVideoClip([video_clip] + subtitle_clips)
            print(f"[Editor] 자막 {len(subtitle_clips)}개 추가 완료")

        return video_clip

    def __repr__(self):
        return f"VideoEditor(resolution={self.config.resolution}, fps={self.config.fps})"
