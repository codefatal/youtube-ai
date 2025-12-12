"""
Video Remixer - 원본 영상 + 번역 자막 합성
MoviePy 기반 자막 오버레이
"""
import os
import pysrt
from typing import Dict, List, Optional
from moviepy import VideoFileClip, TextClip, CompositeVideoClip


class VideoRemixer:
    """원본 영상 + 번역 자막 합성"""

    def __init__(self):
        """초기화"""
        # 기본 자막 스타일
        self.default_style = {
            'fontsize': 48,
            'font': 'Arial-Bold',
            'color': 'white',
            'stroke_color': 'black',
            'stroke_width': 2,
            'method': 'caption',
            'align': 'center',
            'size': None,  # Auto width
        }

    def add_translated_subtitles(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
        style: Optional[Dict] = None
    ) -> str:
        """원본 영상에 번역 자막 추가

        Args:
            video_path: 원본 영상 경로
            subtitle_path: 번역된 SRT 파일 경로
            output_path: 출력 영상 경로
            style: 자막 스타일 (기본값 사용 가능)

        Returns:
            str: 출력 파일 경로 (성공) 또는 None (실패)
        """
        print(f"\n[INFO] 영상 리믹스 시작")
        print(f"[INFO] 원본: {os.path.basename(video_path)}")
        print(f"[INFO] 자막: {os.path.basename(subtitle_path)}")

        try:
            # 영상 로드
            print("[INFO] 영상 로딩 중...")
            video = VideoFileClip(video_path)
            video_w, video_h = video.size

            # 자막 로드
            print("[INFO] 자막 파싱 중...")
            subs = pysrt.open(subtitle_path, encoding='utf-8')
            print(f"[OK] {len(subs)}개 자막 로드됨")

            # 스타일 설정
            final_style = self.default_style.copy()
            if style:
                final_style.update(style)

            # 자막 크기를 영상 크기 기반으로 자동 설정
            if final_style['size'] is None:
                # 영상 너비의 95%를 자막 너비로 사용
                final_style['size'] = (int(video_w * 0.95), None)

            # 자막 클립 생성
            print("[INFO] 자막 클립 생성 중...")
            subtitle_clips = []

            for i, sub in enumerate(subs):
                # 시간 변환 (pysrt → 초)
                start_time = self._srt_time_to_seconds(sub.start)
                end_time = self._srt_time_to_seconds(sub.end)
                duration = end_time - start_time

                # 자막 텍스트
                text = sub.text.strip()
                if not text:
                    continue

                # 텍스트 길이에 따라 폰트 크기 조정
                text_length = len(text)
                if text_length < 20:
                    fontsize = 48
                elif text_length < 40:
                    fontsize = 42
                elif text_length < 60:
                    fontsize = 38
                elif text_length < 80:
                    fontsize = 34
                else:
                    fontsize = 30

                try:
                    # TextClip 생성
                    txt_clip = TextClip(
                        text=text,
                        font_size=fontsize,
                        color=final_style['color'],
                        stroke_color=final_style['stroke_color'],
                        stroke_width=final_style['stroke_width'],
                        font=final_style['font'],
                        method=final_style['method'],
                        size=final_style['size'],
                    )

                    # 위치 설정 (하단 중앙)
                    txt_clip = txt_clip.with_position(('center', video_h * 0.85))

                    # 시간 설정
                    txt_clip = txt_clip.with_start(start_time).with_duration(duration)

                    subtitle_clips.append(txt_clip)

                    if (i + 1) % 10 == 0:
                        print(f"[INFO] 진행: {i+1}/{len(subs)} 자막 생성")

                except Exception as e:
                    print(f"[WARNING] 자막 {i+1} 생성 실패: {e}")
                    continue

            print(f"[OK] {len(subtitle_clips)}개 자막 클립 생성 완료")

            # 영상 + 자막 합성
            print("[INFO] 영상 합성 중...")
            final_video = CompositeVideoClip([video] + subtitle_clips)

            # 출력 디렉토리 생성
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 렌더링
            print("[INFO] 렌더링 시작...")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=video.fps,
                preset='medium',
                threads=4,
                logger=None  # 진행률 표시 비활성화
            )

            # 리소스 정리
            video.close()
            final_video.close()

            print(f"[OK] 리믹스 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"[ERROR] 리믹스 실패: {e}")
            import traceback
            traceback.print_exc()
            return None

    def add_attribution_overlay(
        self,
        video_path: str,
        attribution_text: str,
        output_path: str,
        duration: float = 3.0,
        position: str = 'start'
    ) -> str:
        """영상에 출처 표시 오버레이 추가

        Args:
            video_path: 입력 영상 경로
            attribution_text: 출처 표시 텍스트
            output_path: 출력 영상 경로
            duration: 출처 표시 지속 시간 (초)
            position: 'start' (시작) 또는 'end' (끝)

        Returns:
            str: 출력 파일 경로 (성공) 또는 None (실패)
        """
        print(f"\n[INFO] 출처 표시 추가")

        try:
            # 영상 로드
            video = VideoFileClip(video_path)
            video_w, video_h = video.size

            # 출처 텍스트 클립 생성
            txt_clip = TextClip(
                text=attribution_text,
                font_size=24,
                color='white',
                stroke_color='black',
                stroke_width=1,
                font='Arial',
                method='caption',
                size=(int(video_w * 0.9), None)
            )

            # 위치 및 시간 설정
            txt_clip = txt_clip.with_position(('center', 'top'))

            if position == 'start':
                txt_clip = txt_clip.with_start(0).with_duration(duration)
            else:  # end
                start_time = max(0, video.duration - duration)
                txt_clip = txt_clip.with_start(start_time).with_duration(duration)

            # 합성
            final_video = CompositeVideoClip([video, txt_clip])

            # 렌더링
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=video.fps,
                preset='medium',
                threads=4
            )

            # 리소스 정리
            video.close()
            final_video.close()

            print(f"[OK] 출처 표시 추가 완료: {output_path}")
            return output_path

        except Exception as e:
            print(f"[ERROR] 출처 표시 추가 실패: {e}")
            return None

    def _srt_time_to_seconds(self, srt_time) -> float:
        """SRT 시간 형식을 초 단위로 변환

        Args:
            srt_time: pysrt.SubRipTime 객체

        Returns:
            float: 초 단위 시간
        """
        return (
            srt_time.hours * 3600 +
            srt_time.minutes * 60 +
            srt_time.seconds +
            srt_time.milliseconds / 1000.0
        )

    def create_short_clip(
        self,
        video_path: str,
        output_path: str,
        start_time: float,
        duration: float,
        subtitle_path: Optional[str] = None
    ) -> str:
        """롱폼에서 숏폼 클립 추출 + 자막 추가

        Args:
            video_path: 원본 영상 경로
            output_path: 출력 영상 경로
            start_time: 시작 시간 (초)
            duration: 클립 길이 (초)
            subtitle_path: 자막 파일 경로 (선택)

        Returns:
            str: 출력 파일 경로 (성공) 또는 None (실패)
        """
        print(f"\n[INFO] 숏폼 클립 추출")
        print(f"[INFO] 시작: {start_time}초, 길이: {duration}초")

        try:
            # 영상 로드
            video = VideoFileClip(video_path)

            # 클립 추출
            clip = video.subclipped(start_time, start_time + duration)

            # 자막이 있으면 추가
            if subtitle_path:
                # 임시 클립 저장
                temp_path = output_path.replace('.mp4', '_temp.mp4')
                clip.write_videofile(
                    temp_path,
                    codec='libx264',
                    audio_codec='aac',
                    fps=video.fps
                )

                # 자막 추가
                result = self.add_translated_subtitles(
                    temp_path,
                    subtitle_path,
                    output_path
                )

                # 임시 파일 삭제
                if os.path.exists(temp_path):
                    os.remove(temp_path)

                video.close()
                return result

            else:
                # 자막 없이 저장
                clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    fps=video.fps
                )

                video.close()
                print(f"[OK] 클립 추출 완료: {output_path}")
                return output_path

        except Exception as e:
            print(f"[ERROR] 클립 추출 실패: {e}")
            return None


# 테스트 코드
if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

    remixer = VideoRemixer()

    # 테스트 파일 경로 (실제 파일이 있어야 동작)
    # test_video = './downloads/test123.mp4'
    # test_subtitle = './downloads/test123.ko.srt'
    # output_video = './remixed/test123_ko.mp4'

    # if os.path.exists(test_video) and os.path.exists(test_subtitle):
    #     result = remixer.add_translated_subtitles(
    #         test_video,
    #         test_subtitle,
    #         output_video
    #     )
    #     print(f"\n결과: {result}")
    # else:
    #     print("테스트 파일이 없습니다")

    print("Video Remixer 모듈 로드 완료")
    print("실제 테스트는 다운로드된 영상이 있어야 가능합니다")
