"""
Title Service (Phase 1: 퀄리티 개선)
Pillow를 사용하여 정확한 제목 이미지 렌더링

MoviePy TextClip의 폰트 메트릭 부정확 문제 해결
"""
from typing import Tuple, Optional
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import re
import sys

# config 불러오기
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.config import (
    CANVAS_WIDTH, CANVAS_HEIGHT,
    FONT_TITLE, FONT_SIZE_TITLE,
    STROKE_WIDTH
)


class TitleService:
    """
    Pillow 기반 제목 이미지 생성 서비스

    장점:
    - 정확한 텍스트 바운딩 박스 계산
    - Descender(g, j, y 등) 잘림 방지
    - 반투명 배경 박스 정확한 크기
    - Safe Zone 정밀 적용
    """

    # 설정 상수
    SAFE_ZONE_TOP_RATIO = 0.07      # 상단 7% (유튜브 UI 회피)
    TITLE_SECTION_RATIO = 0.25      # 상단 25% (제목 영역)
    BG_OPACITY = int(255 * 0.7)     # 70% 불투명
    STROKE_WIDTH = 3                 # 외곽선 두께
    PADDING_X = 50                   # 좌우 패딩
    PADDING_Y = 40                   # 상하 패딩
    MAX_CHARS_PER_LINE = 18          # 한 줄 최대 글자 수

    def __init__(self):
        """TitleService 초기화"""
        self.font = None
        self._load_font()

    def _load_font(self):
        """폰트 로드"""
        try:
            self.font = ImageFont.truetype(FONT_TITLE, FONT_SIZE_TITLE)
            print(f"[TitleService] 폰트 로드 완료: {FONT_TITLE} ({FONT_SIZE_TITLE}px)")
        except Exception as e:
            print(f"[WARNING] 폰트 로드 실패: {e}")
            # 대체 폰트 시도
            fallback_fonts = [
                "malgun.ttf",
                "NanumGothic.ttf",
                "C:/Windows/Fonts/malgun.ttf",
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
            ]
            for fallback in fallback_fonts:
                try:
                    self.font = ImageFont.truetype(fallback, FONT_SIZE_TITLE)
                    print(f"[TitleService] 대체 폰트 사용: {fallback}")
                    break
                except:
                    continue

            if self.font is None:
                self.font = ImageFont.load_default()
                print("[WARNING] 기본 폰트 사용 (품질 저하)")

    def _clean_title(self, title: str) -> str:
        """
        제목에서 이모지 및 특수문자 제거

        Args:
            title: 원본 제목

        Returns:
            정제된 제목
        """
        # 모든 이모지 범위 제거 (U+1F000 ~ U+1FFFF)
        title = re.sub(r'[\U0001F000-\U0001FFFF]', '', title)
        # 추가 이모지 및 특수 기호 제거
        title = re.sub(r'[✨💡🎉🔥💪🙌👍❤️🎯📢🎵🎶👇👆⭐️🌟💫⚡️🚀✅❌⚠️💯🎁🏆🎬📱💻🌈☀️🌙⭐🔴🟢🔵⚫⚪]', '', title)
        # 다른 특수문자 범위 제거
        title = re.sub(r'[\u2600-\u26FF\u2700-\u27BF]', '', title)
        title = title.strip()

        return title if title else "영상 제목"

    def _wrap_text(self, text: str) -> str:
        """
        텍스트 줄바꿈 (단어 단위)

        Args:
            text: 원본 텍스트

        Returns:
            줄바꿈이 적용된 텍스트
        """
        if len(text) <= self.MAX_CHARS_PER_LINE:
            return text

        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word

            if len(test_line) <= self.MAX_CHARS_PER_LINE:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return '\n'.join(lines)

    def _get_text_bbox(self, text: str) -> Tuple[int, int, int, int]:
        """
        텍스트의 정확한 바운딩 박스 계산

        Args:
            text: 텍스트

        Returns:
            (left, top, right, bottom) 튜플
        """
        # 임시 이미지로 정확한 크기 측정
        temp_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        bbox = draw.textbbox((0, 0), text, font=self.font)
        return bbox

    def _get_text_size(self, text: str) -> Tuple[int, int]:
        """
        텍스트의 실제 크기 계산 (Descender 포함)

        Args:
            text: 텍스트

        Returns:
            (width, height) 튜플
        """
        bbox = self._get_text_bbox(text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        # Descender 추가 여유 (텍스트 높이의 20%)
        descender_buffer = int(height * 0.2)

        return (width, height + descender_buffer)

    def create_title_image(
        self,
        title: str,
        canvas_width: int = CANVAS_WIDTH,
        canvas_height: int = CANVAS_HEIGHT
    ) -> Tuple[Image.Image, dict]:
        """
        제목 이미지 생성 (Pillow 기반)

        Args:
            title: 제목 텍스트
            canvas_width: 캔버스 너비 (기본 1080)
            canvas_height: 캔버스 높이 (기본 1920)

        Returns:
            (PIL.Image, 메타데이터 dict) 튜플
            메타데이터: {
                'y_position': int,      # 제목 Y 위치
                'bg_height': int,       # 배경 박스 높이
                'text_height': int,     # 텍스트 높이
                'line_count': int       # 줄 수
            }
        """
        # 1. 제목 정제 및 줄바꿈
        clean_title = self._clean_title(title)
        wrapped_title = self._wrap_text(clean_title)
        line_count = wrapped_title.count('\n') + 1

        print(f"[TitleService] 제목 처리: '{clean_title[:30]}...' ({line_count}줄)")

        # 2. 텍스트 크기 계산
        text_width, text_height = self._get_text_size(wrapped_title)

        # 3. 배경 박스 크기 계산 (충분한 패딩)
        bg_width = min(text_width + self.PADDING_X * 2 + self.STROKE_WIDTH * 2, canvas_width - 40)
        bg_height = text_height + self.PADDING_Y * 2 + self.STROKE_WIDTH * 2

        # 4. Safe Zone 계산
        safe_zone_top = int(canvas_height * self.SAFE_ZONE_TOP_RATIO)  # 상단 7%
        title_section_height = int(canvas_height * self.TITLE_SECTION_RATIO)  # 상단 25%

        # 배경 박스가 제목 영역을 넘지 않도록 제한
        max_bg_height = title_section_height - safe_zone_top - 20
        if bg_height > max_bg_height:
            bg_height = max_bg_height
            print(f"[TitleService] 배경 높이 제한: {bg_height}px")

        # 5. 위치 계산 (Safe Zone 적용)
        bg_x = (canvas_width - bg_width) // 2
        bg_y = safe_zone_top

        # 6. 투명 캔버스 생성 (전체 화면 크기)
        img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 7. 반투명 배경 박스 그리기
        draw.rectangle(
            [bg_x, bg_y, bg_x + bg_width, bg_y + bg_height],
            fill=(0, 0, 0, self.BG_OPACITY)
        )

        # 8. 텍스트 위치 계산 (배경 박스 내 중앙)
        text_x = (canvas_width - text_width) // 2
        text_y = bg_y + (bg_height - text_height) // 2

        # 9. 외곽선 그리기 (검은색, 4방향)
        outline_offsets = [
            (-self.STROKE_WIDTH, 0),
            (self.STROKE_WIDTH, 0),
            (0, -self.STROKE_WIDTH),
            (0, self.STROKE_WIDTH),
            (-self.STROKE_WIDTH, -self.STROKE_WIDTH),
            (self.STROKE_WIDTH, -self.STROKE_WIDTH),
            (-self.STROKE_WIDTH, self.STROKE_WIDTH),
            (self.STROKE_WIDTH, self.STROKE_WIDTH),
        ]

        for dx, dy in outline_offsets:
            draw.text(
                (text_x + dx, text_y + dy),
                wrapped_title,
                font=self.font,
                fill=(0, 0, 0, 255),
                align='center'
            )

        # 10. 메인 텍스트 그리기 (흰색)
        draw.text(
            (text_x, text_y),
            wrapped_title,
            font=self.font,
            fill=(255, 255, 255, 255),
            align='center'
        )

        # 메타데이터
        metadata = {
            'y_position': bg_y,
            'bg_height': bg_height,
            'text_height': text_height,
            'line_count': line_count,
            'bg_width': bg_width,
            'safe_zone_top': safe_zone_top
        }

        print(f"[TitleService] 제목 이미지 생성 완료: {bg_width}x{bg_height}px @ Y={bg_y}")

        return (img, metadata)

    def create_title_array(
        self,
        title: str,
        canvas_width: int = CANVAS_WIDTH,
        canvas_height: int = CANVAS_HEIGHT
    ) -> Tuple[np.ndarray, dict]:
        """
        제목 이미지를 numpy array로 반환 (MoviePy ImageClip용)

        Args:
            title: 제목 텍스트
            canvas_width: 캔버스 너비
            canvas_height: 캔버스 높이

        Returns:
            (numpy.ndarray, 메타데이터 dict) 튜플
        """
        img, metadata = self.create_title_image(title, canvas_width, canvas_height)
        return (np.array(img), metadata)


# 싱글톤 인스턴스
_title_service = None


def get_title_service() -> TitleService:
    """TitleService 싱글톤 인스턴스 반환"""
    global _title_service
    if _title_service is None:
        _title_service = TitleService()
    return _title_service
