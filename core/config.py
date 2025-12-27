"""
YouTube Shorts Configuration
모든 하드코딩된 값을 중앙 관리 (SHORTS_SPEC.md 기준)
"""

# ==================== 해상도 ====================
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920

# ==================== Safe Zone (SHORTS_SPEC.md) ====================
# YouTube Shorts UI(좋아요, 설명란 등)가 자막을 가리지 않도록 안전 영역 설정

# 상단 여백: 15% (약 288px) - 배터리, 상태바, 검색 버튼 회피
SAFE_TOP_RATIO = 0.15
SAFE_TOP_PX = int(CANVAS_HEIGHT * SAFE_TOP_RATIO)  # 288px

# 하단 여백: 30% (약 576px) - 영상 제목, 설명란, 채널명, 사운드바 회피
SAFE_BOTTOM_RATIO = 0.30
SAFE_BOTTOM_PX = int(CANVAS_HEIGHT * (1.0 - SAFE_BOTTOM_RATIO))  # 1344px

# 좌우 여백: 10% (약 108px) - 좋아요/댓글 버튼 및 엣지 잘림 방지
SAFE_SIDE_RATIO = 0.10
SAFE_SIDE_PX = int(CANVAS_WIDTH * SAFE_SIDE_RATIO)  # 108px

# 최대 텍스트 너비: 80% (좌우 10%씩 제외)
MAX_TEXT_WIDTH_RATIO = 0.80
MAX_TEXT_WIDTH_PX = int(CANVAS_WIDTH * MAX_TEXT_WIDTH_RATIO)  # 864px

# Safe Zone 계산된 좌표
# 자막이 배치 가능한 Y 범위: 288px ~ 1344px (총 1056px)
SUBTITLE_SAFE_Y_MIN = SAFE_TOP_PX
SUBTITLE_SAFE_Y_MAX = SAFE_BOTTOM_PX


# ==================== 색상 테마 ====================
# 텍스트 색상
COLOR_TEXT_PRIMARY = (255, 255, 255)  # 흰색 (#FFFFFF)
COLOR_TEXT_HIGHLIGHT = (255, 215, 0)  # 노란색 (#FFD700) - 강조 단어

# 배경 색상
COLOR_BG_BLACK = (0, 0, 0)  # 검은색
COLOR_BG_TRANSPARENT_BLACK = (0, 0, 0, 150)  # 반투명 검은색 (alpha=150)

# 외곽선 색상
COLOR_STROKE_BLACK = (0, 0, 0)  # 검은색 외곽선


# ==================== 폰트 설정 ====================
import platform
import os

# Windows 기본 폰트
if platform.system() == 'Windows':
    FONT_TITLE = 'C:\\Windows\\Fonts\\malgunbd.ttf'  # 맑은 고딕 Bold
    FONT_SUBTITLE = 'C:\\Windows\\Fonts\\malgun.ttf'  # 맑은 고딕
else:
    # Linux/Mac 폴백
    FONT_TITLE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    FONT_SUBTITLE = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

# 폰트 크기
FONT_SIZE_TITLE = 80  # 제목 (큼)
FONT_SIZE_SUBTITLE = 70  # 자막 (중간)
FONT_SIZE_SUBTITLE_SMALL = 60  # 자막 (작음, 긴 텍스트용)

# 외곽선 두께
STROKE_WIDTH = 3  # px


# ==================== 자막 스타일 ====================
# 배경 박스 패딩
SUBTITLE_BG_PADDING_X = 30  # 좌우 패딩 (px)
SUBTITLE_BG_PADDING_Y = 20  # 상하 패딩 (px)

# 배경 박스 불투명도
SUBTITLE_BG_OPACITY = 0.6  # 60% (0.0 ~ 1.0)

# 제목 배경 박스 패딩
TITLE_BG_PADDING_X = 40
TITLE_BG_PADDING_Y = 30
TITLE_BG_OPACITY = 0.7  # 70%


# ==================== 쇼츠 레이아웃 ====================
# 3단 레이아웃: 상단(제목) + 중앙(영상) + 하단(자막)
LAYOUT_TOP_HEIGHT = CANVAS_HEIGHT // 4  # 480px
LAYOUT_MIDDLE_HEIGHT = CANVAS_HEIGHT // 2  # 960px
LAYOUT_BOTTOM_HEIGHT = CANVAS_HEIGHT // 4  # 480px


# ==================== Whisper 설정 ====================
# Whisper 모델 크기 (tiny, base, small, medium, large)
WHISPER_MODEL = "base"  # 속도와 정확도 균형

# Word-level timestamps 활성화
WHISPER_WORD_TIMESTAMPS = True

# 언어 설정
WHISPER_LANGUAGE = "ko"  # 한국어


# ==================== 경로 설정 ====================
# 프로젝트 루트 경로
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent

# 출력 디렉토리
OUTPUT_DIR = PROJECT_ROOT / "output"
DOWNLOADS_DIR = PROJECT_ROOT / "downloads"
AUDIO_DIR = DOWNLOADS_DIR / "audio"
VIDEO_DIR = DOWNLOADS_DIR / "stock_videos"
MUSIC_DIR = PROJECT_ROOT / "music"


# ==================== 유틸리티 함수 ====================
def clamp_y_to_safe_zone(y: int, text_height: int) -> int:
    """
    Y 좌표를 Safe Zone 내로 제한

    Args:
        y: 원본 Y 좌표
        text_height: 텍스트 높이

    Returns:
        Safe Zone 내로 조정된 Y 좌표
    """
    # 상단 제한
    if y < SUBTITLE_SAFE_Y_MIN:
        y = SUBTITLE_SAFE_Y_MIN

    # 하단 제한
    if y + text_height > SUBTITLE_SAFE_Y_MAX:
        y = SUBTITLE_SAFE_Y_MAX - text_height

    # 그래도 넘치면 상단으로 강제 이동
    if y < SUBTITLE_SAFE_Y_MIN:
        y = SUBTITLE_SAFE_Y_MIN

    return y


def is_in_safe_zone(y: int, text_height: int) -> bool:
    """
    텍스트가 Safe Zone 내에 있는지 확인

    Args:
        y: Y 좌표
        text_height: 텍스트 높이

    Returns:
        Safe Zone 내에 있으면 True
    """
    return (y >= SUBTITLE_SAFE_Y_MIN) and (y + text_height <= SUBTITLE_SAFE_Y_MAX)
