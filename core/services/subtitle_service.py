"""
Subtitle Service (SHORTS_SPEC.md 기준)
Pillow를 사용하여 안전하고 스타일리시한 자막 이미지 생성
"""
from typing import List, Tuple, Optional
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

# config 불러오기
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.config import (
    CANVAS_WIDTH, CANVAS_HEIGHT,
    MAX_TEXT_WIDTH_PX,
    SUBTITLE_SAFE_Y_MIN, SUBTITLE_SAFE_Y_MAX,
    COLOR_TEXT_PRIMARY, COLOR_BG_TRANSPARENT_BLACK,
    FONT_SUBTITLE, FONT_SIZE_SUBTITLE, FONT_SIZE_SUBTITLE_SMALL,
    STROKE_WIDTH,
    SUBTITLE_BG_PADDING_X, SUBTITLE_BG_PADDING_Y, SUBTITLE_BG_OPACITY,
    clamp_y_to_safe_zone
)


class SubtitleService:
    """
    Pillow 기반 자막 이미지 생성 서비스

    SHORTS_SPEC.md 요구사항:
    - MoviePy TextClip 대신 PIL.Image 사용
    - 반투명 검은 배경 박스 (가독성 극대화)
    - Safe Zone 강제 적용
    - 단어별 줄바꿈 (MAX_TEXT_WIDTH 초과 방지)
    """

    def __init__(self):
        """SubtitleService 초기화"""
        try:
            self.font_large = ImageFont.truetype(FONT_SUBTITLE, FONT_SIZE_SUBTITLE)
            self.font_small = ImageFont.truetype(FONT_SUBTITLE, FONT_SIZE_SUBTITLE_SMALL)
        except Exception as e:
            print(f"[WARNING] 폰트 로드 실패: {e}. 기본 폰트 사용")
            self.font_large = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def _wrap_text(self, text: str, font: ImageFont, max_width: int) -> str:
        """
        텍스트를 단어 단위로 줄바꿈 (SHORTS_SPEC.md 요구사항)

        Args:
            text: 원본 텍스트
            font: 폰트 객체
            max_width: 최대 너비 (px)

        Returns:
            줄바꿈이 적용된 텍스트
        """
        words = text.split()
        lines = []
        current_line = ""

        # 임시 이미지로 텍스트 크기 측정
        temp_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(temp_img)

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return '\n'.join(lines)

    def _get_text_size(self, text: str, font: ImageFont) -> Tuple[int, int]:
        """
        텍스트의 실제 크기 계산

        Args:
            text: 텍스트
            font: 폰트 객체

        Returns:
            (width, height) 튜플
        """
        temp_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        bbox = draw.textbbox((0, 0), text, font=font)

        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        return (width, height)

    def create_subtitle_image(
        self,
        text: str,
        y_position: Optional[int] = None
    ) -> Tuple[Image.Image, int]:
        """
        자막 이미지 생성 (SHORTS_SPEC.md 스타일)

        Args:
            text: 자막 텍스트
            y_position: Y 좌표 (None이면 하단 기본값)

        Returns:
            (PIL.Image, y_position) 튜플
        """
        # 폰트 선택 (텍스트 길이에 따라)
        text_len = len(text.replace('\n', ''))
        font = self.font_small if text_len > 30 else self.font_large

        # 줄바꿈 적용
        wrapped_text = self._wrap_text(text, font, MAX_TEXT_WIDTH_PX)

        # 텍스트 크기 계산
        text_width, text_height = self._get_text_size(wrapped_text, font)

        # 배경 박스 크기 (패딩 포함)
        bg_width = min(text_width + SUBTITLE_BG_PADDING_X * 2, CANVAS_WIDTH)
        bg_height = text_height + SUBTITLE_BG_PADDING_Y * 2

        # Y 좌표 결정 및 Safe Zone 적용
        if y_position is None:
            # 기본값: 하단에서 150px 위
            y_position = SUBTITLE_SAFE_Y_MAX - bg_height - 150

        # Safe Zone 강제 적용
        y_position = clamp_y_to_safe_zone(y_position, bg_height)

        # 투명 캔버스 생성
        img = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # X 좌표 (중앙 정렬)
        bg_x = (CANVAS_WIDTH - bg_width) // 2

        # 1. 반투명 검은 배경 박스 그리기 (SHORTS_SPEC.md Type B)
        bg_color = COLOR_BG_TRANSPARENT_BLACK  # (0, 0, 0, 150)
        draw.rectangle(
            [bg_x, y_position, bg_x + bg_width, y_position + bg_height],
            fill=bg_color
        )

        # 2. 텍스트 그리기 (중앙 정렬)
        text_x = (CANVAS_WIDTH - text_width) // 2
        text_y = y_position + SUBTITLE_BG_PADDING_Y

        # 외곽선 (검은색)
        for dx, dy in [(-STROKE_WIDTH, 0), (STROKE_WIDTH, 0), (0, -STROKE_WIDTH), (0, STROKE_WIDTH)]:
            draw.text(
                (text_x + dx, text_y + dy),
                wrapped_text,
                font=font,
                fill=(0, 0, 0, 255),  # 검은색 외곽선
                align='center'
            )

        # 텍스트 본체 (흰색)
        draw.text(
            (text_x, text_y),
            wrapped_text,
            font=font,
            fill=COLOR_TEXT_PRIMARY + (255,),  # (255, 255, 255, 255)
            align='center'
        )

        return (img, y_position)

    def create_subtitle_clips(
        self,
        segments: List[dict],
        fps: int = 30
    ) -> List[dict]:
        """
        세그먼트 리스트로부터 자막 클립 정보 생성

        Args:
            segments: 정렬된 세그먼트 리스트
                [{"text": "...", "start": 0.0, "end": 1.0, "duration": 1.0}, ...]
            fps: 프레임 레이트

        Returns:
            자막 클립 정보 리스트
            [
                {
                    "image": PIL.Image,
                    "start": 0.0,
                    "duration": 1.0,
                    "y_position": 1200
                },
                ...
            ]
        """
        subtitle_clips = []

        for i, segment in enumerate(segments):
            text = segment.get('text', '')
            start = segment.get('start', 0.0)
            duration = segment.get('duration', 1.0)

            # 효과음 제거
            import re
            text = re.sub(r'\([^)]*\)', '', text).strip()

            if not text:
                continue

            # 자막 이미지 생성
            subtitle_img, y_pos = self.create_subtitle_image(text)

            subtitle_clips.append({
                "image": subtitle_img,
                "start": start,
                "duration": duration,
                "y_position": y_pos,
                "text": text
            })

            print(f"[Subtitle {i+1}] '{text[:30]}...' at {start:.1f}s-{start+duration:.1f}s (Safe Zone: Y={y_pos}px)")

        return subtitle_clips


# 싱글톤 인스턴스
_subtitle_service = None


def get_subtitle_service() -> SubtitleService:
    """SubtitleService 싱글톤 인스턴스 반환"""
    global _subtitle_service
    if _subtitle_service is None:
        _subtitle_service = SubtitleService()
    return _subtitle_service
