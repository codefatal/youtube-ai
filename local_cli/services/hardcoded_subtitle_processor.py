"""
Hardcoded Subtitle Processor - 영상에 인코딩된 자막 추출 및 교체
OCR로 자막 추출 → 번역 → 원본 자막 제거 → 번역 자막 재인코딩
"""
import os
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import pysrt
from datetime import timedelta

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("[WARNING] EasyOCR not installed. Install with: pip install easyocr")


class HardcodedSubtitleProcessor:
    """영상에 인코딩된 자막 처리"""

    def __init__(self, font_path: Optional[str] = None):
        """
        Args:
            font_path: 사용할 폰트 경로 (None이면 기본 폰트)
        """
        if not EASYOCR_AVAILABLE:
            raise ImportError("EasyOCR이 필요합니다: pip install easyocr")

        # OCR 리더 초기화 (영어 우선, 필요시 다른 언어 추가)
        print("[INFO] OCR 엔진 초기화 중...")
        self.reader = easyocr.Reader(['en'], gpu=False)

        # 폰트 설정 (무료 폰트: Noto Sans)
        self.font_path = font_path
        if not self.font_path:
            # 기본 폰트 경로 (시스템에 따라 다를 수 있음)
            self.font_path = self._find_default_font()

        print(f"[INFO] 폰트: {self.font_path}")

    def _find_default_font(self) -> str:
        """시스템에서 사용 가능한 기본 폰트 찾기"""
        # Windows
        possible_fonts = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "/System/Library/Fonts/Helvetica.ttc",  # Mac
        ]

        for font in possible_fonts:
            if os.path.exists(font):
                return font

        # 폰트를 찾지 못하면 None 반환 (MoviePy 기본 폰트 사용)
        print("[WARNING] 기본 폰트를 찾지 못했습니다. MoviePy 기본 폰트 사용")
        return None

    def extract_hardcoded_subtitles(
        self,
        video_path: str,
        subtitle_region: Optional[Tuple[int, int, int, int]] = None,
        sample_interval: float = 0.5
    ) -> List[Dict]:
        """영상에서 하드코딩된 자막 추출

        Args:
            video_path: 영상 파일 경로
            subtitle_region: 자막 영역 (x, y, width, height). None이면 하단 30% 자동 감지
            sample_interval: 프레임 샘플링 간격 (초)

        Returns:
            List[Dict]: 추출된 자막 정보
                - text: 자막 텍스트
                - start_time: 시작 시간 (초)
                - end_time: 종료 시간 (초)
                - bbox: 자막 위치 (x, y, width, height)
                - color: 자막 색상 (R, G, B)
                - font_size: 예상 폰트 크기
        """
        print(f"\n[INFO] 하드코딩 자막 추출 시작: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"영상을 열 수 없습니다: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps

        # 자막 영역 설정 (하단 30%)
        if not subtitle_region:
            subtitle_region = (
                0,
                int(frame_height * 0.7),
                frame_width,
                int(frame_height * 0.3)
            )

        print(f"[INFO] 영상 정보: {frame_width}x{frame_height}, {fps:.2f}fps, {duration:.1f}초")
        print(f"[INFO] 자막 영역: {subtitle_region}")
        print(f"[INFO] 프레임 샘플링 간격: {sample_interval}초 ({int(fps * sample_interval)}프레임마다)")

        subtitles = []
        current_text = None
        current_start = None
        frame_interval = int(fps * sample_interval)

        frame_count = 0
        processed_frames = 0
        ocr_detected_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 샘플링 간격에 따라 처리
            if frame_count % frame_interval != 0:
                frame_count += 1
                continue

            current_time = frame_count / fps
            processed_frames += 1

            # 자막 영역 추출
            x, y, w, h = subtitle_region
            subtitle_frame = frame[y:y+h, x:x+w]

            # 첫 번째 프레임 저장 (디버깅용)
            if processed_frames == 1:
                debug_frame_path = os.path.join(output_dir, f"{Path(video_path).stem}_debug_frame.jpg") if 'output_dir' in locals() else None
                if debug_frame_path:
                    cv2.imwrite(debug_frame_path, subtitle_frame)
                    print(f"[DEBUG] 첫 번째 샘플 프레임 저장: {debug_frame_path}")

            # OCR 수행
            results = self.reader.readtext(subtitle_frame)

            if processed_frames % 20 == 0:  # 20프레임마다 진행 상황 출력
                print(f"[INFO] 처리 중... {current_time:.1f}초 / {duration:.1f}초 (OCR 감지: {ocr_detected_count}건)")

            if results:
                # 가장 큰 텍스트 박스 선택 (보통 자막이 가장 큼)
                results.sort(key=lambda x: (x[0][2][0] - x[0][0][0]) * (x[0][2][1] - x[0][0][1]), reverse=True)
                bbox, text, confidence = results[0]

                text = text.strip()

                if confidence > 0.3 and len(text) > 2:  # 신뢰도 필터
                    ocr_detected_count += 1

                    # 자막 위치 계산 (전체 프레임 기준)
                    abs_bbox = (
                        int(bbox[0][0] + x),
                        int(bbox[0][1] + y),
                        int(bbox[2][0] - bbox[0][0]),
                        int(bbox[2][1] - bbox[0][1])
                    )

                    # 자막 색상 추출
                    text_region = subtitle_frame[
                        int(bbox[0][1]):int(bbox[2][1]),
                        int(bbox[0][0]):int(bbox[2][0])
                    ]
                    avg_color = cv2.mean(text_region)[:3]
                    color = (int(avg_color[2]), int(avg_color[1]), int(avg_color[0]))  # BGR to RGB

                    # 폰트 크기 추정
                    font_size = abs_bbox[3]

                    # 같은 텍스트가 연속되면 end_time만 업데이트
                    if text == current_text:
                        if subtitles:
                            subtitles[-1]['end_time'] = current_time + sample_interval
                    else:
                        # 새로운 자막
                        if current_text:
                            # 이전 자막 저장 완료
                            pass

                        subtitles.append({
                            'text': text,
                            'start_time': current_time,
                            'end_time': current_time + sample_interval,
                            'bbox': abs_bbox,
                            'color': color,
                            'font_size': font_size
                        })
                        current_text = text
                        current_start = current_time

                        if len(subtitles) % 10 == 0:
                            print(f"[PROGRESS] {current_time:.1f}s / {duration:.1f}s - 자막 {len(subtitles)}개 발견")
            else:
                current_text = None

            frame_count += 1

        cap.release()

        print(f"\n[SUMMARY] OCR 처리 완료:")
        print(f"  - 처리한 프레임: {processed_frames}개")
        print(f"  - OCR 감지: {ocr_detected_count}건")
        print(f"  - 추출된 자막: {len(subtitles)}개")

        print(f"[OK] 자막 추출 완료: {len(subtitles)}개")
        return subtitles

    def create_srt_from_hardcoded(self, subtitles: List[Dict], output_path: str) -> str:
        """추출된 자막을 SRT 파일로 저장

        Args:
            subtitles: extract_hardcoded_subtitles에서 반환된 자막 리스트
            output_path: 출력 SRT 파일 경로

        Returns:
            str: 생성된 SRT 파일 경로
        """
        subs = pysrt.SubRipFile()

        for i, sub in enumerate(subtitles, 1):
            start = timedelta(seconds=sub['start_time'])
            end = timedelta(seconds=sub['end_time'])

            item = pysrt.SubRipItem(
                index=i,
                start=start,
                end=end,
                text=sub['text']
            )
            subs.append(item)

        subs.save(output_path, encoding='utf-8')
        print(f"[OK] SRT 파일 저장: {output_path}")
        return output_path

    def remove_hardcoded_subtitles(
        self,
        video_path: str,
        subtitles: List[Dict],
        output_path: str
    ) -> str:
        """영상에서 하드코딩된 자막 제거 (검은 박스로 가리기)

        Args:
            video_path: 원본 영상 경로
            subtitles: 제거할 자막 정보
            output_path: 출력 영상 경로

        Returns:
            str: 자막 제거된 영상 경로
        """
        print(f"\n[INFO] 하드코딩 자막 제거 시작")

        clip = VideoFileClip(video_path)

        def mask_frame(get_frame, t):
            frame = get_frame(t)

            # 현재 시간에 해당하는 자막 찾기
            for sub in subtitles:
                if sub['start_time'] <= t <= sub['end_time']:
                    x, y, w, h = sub['bbox']
                    # 검은 박스로 가리기 (약간 여유 추가)
                    padding = 5
                    cv2.rectangle(
                        frame,
                        (x - padding, y - padding),
                        (x + w + padding, y + h + padding),
                        (0, 0, 0),
                        -1
                    )

            return frame

        # 프레임 처리 함수 적용
        masked_clip = clip.fl(lambda gf, t: mask_frame(gf, t))

        print(f"[INFO] 영상 인코딩 중...")
        masked_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None
        )

        clip.close()
        masked_clip.close()

        print(f"[OK] 자막 제거 완료: {output_path}")
        return output_path

    def add_translated_subtitles_with_style(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
        original_subtitles: List[Dict]
    ) -> str:
        """번역된 자막을 원본 스타일로 영상에 추가

        Args:
            video_path: 자막이 제거된 영상 경로
            subtitle_path: 번역된 SRT 자막 경로
            output_path: 최종 출력 영상 경로
            original_subtitles: 원본 자막 정보 (스타일 참조용)

        Returns:
            str: 최종 영상 경로
        """
        print(f"\n[INFO] 번역 자막 추가 시작")

        video = VideoFileClip(video_path)
        subs = pysrt.open(subtitle_path, encoding='utf-8')

        # 평균 자막 스타일 계산
        if original_subtitles:
            avg_color = np.mean([s['color'] for s in original_subtitles], axis=0)
            avg_font_size = int(np.mean([s['font_size'] for s in original_subtitles]))
            avg_y_position = int(np.mean([s['bbox'][1] for s in original_subtitles]))
        else:
            avg_color = (255, 255, 255)  # 흰색
            avg_font_size = 40
            avg_y_position = int(video.h * 0.85)

        print(f"[INFO] 자막 스타일: 색상={avg_color}, 크기={avg_font_size}px, 위치=y{avg_y_position}")

        subtitle_clips = []

        for sub in subs:
            start_time = sub.start.ordinal / 1000.0
            duration = (sub.end.ordinal - sub.start.ordinal) / 1000.0

            # PIL로 텍스트 이미지 생성 (외곽선 추가)
            img = self._create_text_with_outline(
                text=sub.text,
                font_size=avg_font_size,
                text_color=tuple(int(c) for c in avg_color),
                outline_color=(0, 0, 0),
                outline_width=3
            )

            # PIL Image를 numpy array로 변환
            img_array = np.array(img)

            # ImageClip 생성
            from moviepy.editor import ImageClip
            txt_clip = ImageClip(img_array, duration=duration)
            txt_clip = txt_clip.set_start(start_time)
            txt_clip = txt_clip.set_position(('center', avg_y_position))

            subtitle_clips.append(txt_clip)

        # 최종 합성
        final_video = CompositeVideoClip([video] + subtitle_clips)

        print(f"[INFO] 최종 영상 인코딩 중...")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None
        )

        video.close()
        final_video.close()
        for clip in subtitle_clips:
            clip.close()

        print(f"[OK] 번역 자막 추가 완료: {output_path}")
        return output_path

    def _create_text_with_outline(
        self,
        text: str,
        font_size: int,
        text_color: Tuple[int, int, int],
        outline_color: Tuple[int, int, int],
        outline_width: int
    ) -> Image.Image:
        """외곽선이 있는 텍스트 이미지 생성

        Args:
            text: 텍스트
            font_size: 폰트 크기
            text_color: 텍스트 색상 (R, G, B)
            outline_color: 외곽선 색상 (R, G, B)
            outline_width: 외곽선 두께

        Returns:
            PIL.Image: 생성된 이미지
        """
        # 폰트 로드
        try:
            if self.font_path and os.path.exists(self.font_path):
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # 텍스트 크기 계산
        dummy_img = Image.new('RGBA', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 여유 공간 추가
        padding = outline_width * 2 + 10
        img_width = text_width + padding * 2
        img_height = text_height + padding * 2

        # 투명 배경 이미지 생성
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 텍스트 위치
        x = padding
        y = padding

        # 외곽선 그리기 (검은색)
        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x != 0 or offset_y != 0:
                    draw.text(
                        (x + offset_x, y + offset_y),
                        text,
                        font=font,
                        fill=outline_color + (255,)
                    )

        # 텍스트 그리기
        draw.text((x, y), text, font=font, fill=text_color + (255,))

        return img

    def process_video_with_hardcoded_subs(
        self,
        video_path: str,
        output_dir: str,
        translator,
        target_lang: str = 'ko'
    ) -> Dict:
        """하드코딩 자막이 있는 영상 전체 처리

        Args:
            video_path: 원본 영상 경로
            output_dir: 출력 디렉토리
            translator: SubtitleTranslator 인스턴스
            target_lang: 번역 대상 언어

        Returns:
            Dict: 처리 결과
                - extracted_srt: 추출된 자막 SRT 경로
                - translated_srt: 번역된 자막 SRT 경로
                - cleaned_video: 자막 제거된 영상 경로
                - final_video: 최종 영상 경로
        """
        video_name = Path(video_path).stem
        os.makedirs(output_dir, exist_ok=True)

        # 1. 자막 추출
        print("\n" + "="*70)
        print("STEP 1: 하드코딩 자막 추출")
        print("="*70)
        subtitles = self.extract_hardcoded_subtitles(video_path)

        if not subtitles:
            print("[WARNING] 자막을 찾을 수 없습니다")
            return {'success': False, 'error': 'No subtitles found'}

        # 2. SRT 파일 생성
        extracted_srt = os.path.join(output_dir, f"{video_name}_extracted.srt")
        self.create_srt_from_hardcoded(subtitles, extracted_srt)

        # 3. 자막 번역
        print("\n" + "="*70)
        print("STEP 2: 자막 번역")
        print("="*70)
        translated_srt = os.path.join(output_dir, f"{video_name}_translated.{target_lang}.srt")
        translator.translate_srt_file(extracted_srt, translated_srt, target_lang)

        # 4. 원본 자막 제거
        print("\n" + "="*70)
        print("STEP 3: 원본 자막 제거")
        print("="*70)
        cleaned_video = os.path.join(output_dir, f"{video_name}_cleaned.mp4")
        self.remove_hardcoded_subtitles(video_path, subtitles, cleaned_video)

        # 5. 번역 자막 추가
        print("\n" + "="*70)
        print("STEP 4: 번역 자막 추가")
        print("="*70)
        final_video = os.path.join(output_dir, f"{video_name}_final.mp4")
        self.add_translated_subtitles_with_style(
            cleaned_video,
            translated_srt,
            final_video,
            subtitles
        )

        print("\n" + "="*70)
        print("처리 완료!")
        print("="*70)

        return {
            'success': True,
            'extracted_srt': extracted_srt,
            'translated_srt': translated_srt,
            'cleaned_video': cleaned_video,
            'final_video': final_video,
            'subtitle_count': len(subtitles)
        }
