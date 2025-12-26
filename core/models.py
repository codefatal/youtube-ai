"""
Core Data Models for YouTube AI v3.0
AI-Powered Original Content Creator

Pydantic models for type safety and validation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ============================================================
# Enums
# ============================================================

class VideoFormat(str, Enum):
    """영상 포맷"""
    SHORTS = "shorts"  # 세로형 (1080x1920)
    LANDSCAPE = "landscape"  # 가로형 (1920x1080)
    SQUARE = "square"  # 정사각형 (1080x1080)


class ContentStatus(str, Enum):
    """콘텐츠 생성 상태"""
    PLANNING = "planning"  # 기획 중
    SCRIPTING = "scripting"  # 스크립트 작성 중
    ASSET_GATHERING = "asset_gathering"  # 소재 수집 중
    EDITING = "editing"  # 편집 중
    UPLOADING = "uploading"  # 업로드 중
    COMPLETED = "completed"  # 완료
    FAILED = "failed"  # 실패


class AIProvider(str, Enum):
    """AI 제공자"""
    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI = "openai"


class TTSProvider(str, Enum):
    """TTS 제공자"""
    ELEVENLABS = "elevenlabs"
    GOOGLE_CLOUD = "google_cloud"
    GTTS = "gtts"


class MoodType(str, Enum):
    """BGM 분위기 타입"""
    HAPPY = "happy"           # 밝고 즐거운
    SAD = "sad"               # 슬프고 감성적인
    ENERGETIC = "energetic"   # 활기차고 신나는
    CALM = "calm"             # 차분하고 평온한
    TENSE = "tense"           # 긴장감 있는
    MYSTERIOUS = "mysterious" # 신비로운


# ============================================================
# Planner Models
# ============================================================

class ScriptSegment(BaseModel):
    """스크립트 세그먼트"""
    text: str = Field(..., description="대사 텍스트")
    keyword: str = Field(..., description="영상 검색 키워드")
    duration: Optional[float] = Field(None, description="예상 길이(초)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "강아지는 사람의 가장 좋은 친구입니다.",
                "keyword": "happy dog playing park",
                "duration": 3.0
            }
        }
    }


class ContentPlan(BaseModel):
    """콘텐츠 기획"""
    title: str = Field(..., description="영상 제목")
    description: str = Field(..., description="영상 설명")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    category: str = Field("22", description="YouTube 카테고리 ID (22=People & Blogs)")
    format: VideoFormat = Field(VideoFormat.SHORTS, description="영상 포맷")
    target_duration: int = Field(60, description="목표 길이(초)")
    segments: List[ScriptSegment] = Field(..., description="스크립트 세그먼트")

    # AI 생성 정보
    ai_provider: AIProvider = Field(AIProvider.GEMINI, description="사용된 AI")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시각")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "강아지와 함께하는 행복한 하루",
                "description": "강아지와 함께 공원에서 즐거운 시간을 보내는 모습",
                "tags": ["강아지", "반려동물", "힐링"],
                "segments": [
                    {
                        "text": "강아지는 사람의 가장 좋은 친구입니다.",
                        "keyword": "happy dog playing"
                    }
                ]
            }
        }
    }


# ============================================================
# Asset Manager Models
# ============================================================

class StockVideoAsset(BaseModel):
    """스톡 영상 에셋"""
    id: str = Field(..., description="영상 ID")
    url: str = Field(..., description="다운로드 URL")
    provider: str = Field(..., description="제공자 (pexels/pixabay)")
    keyword: str = Field(..., description="검색 키워드")
    duration: float = Field(..., description="영상 길이(초)")
    resolution: str = Field("1080x1920", description="해상도")
    local_path: Optional[str] = Field(None, description="로컬 저장 경로")
    downloaded: bool = Field(False, description="다운로드 여부")


class AudioAsset(BaseModel):
    """오디오 에셋"""
    text: str = Field(..., description="텍스트")
    provider: TTSProvider = Field(..., description="TTS 제공자")
    voice_id: Optional[str] = Field(None, description="음성 ID")
    local_path: Optional[str] = Field(None, description="로컬 저장 경로")
    duration: Optional[float] = Field(None, description="오디오 길이(초)")


class BGMAsset(BaseModel):
    """배경음악 에셋"""
    name: str = Field(..., description="음악 파일명")
    local_path: str = Field(..., description="로컬 파일 경로")
    mood: MoodType = Field(..., description="분위기")
    duration: float = Field(..., description="길이 (초)")
    volume: float = Field(default=0.3, description="볼륨 (0.0 ~ 1.0)")
    artist: Optional[str] = Field(None, description="아티스트")
    license: Optional[str] = Field(None, description="라이선스")


class TemplateConfig(BaseModel):
    """쇼츠 템플릿 설정"""
    name: str = Field(..., description="템플릿 이름")
    description: str = Field(..., description="설명")

    # 자막 설정
    subtitle_font: str = Field(default="malgun.ttf", description="폰트 파일명")
    subtitle_fontsize: int = Field(default=40, description="폰트 크기")
    subtitle_color: str = Field(default="white", description="자막 색상")
    subtitle_stroke_color: str = Field(default="black", description="외곽선 색상")
    subtitle_stroke_width: int = Field(default=2, description="외곽선 두께")
    subtitle_position: str = Field(default="bottom", description="위치 (top, center, bottom)")
    subtitle_y_offset: int = Field(default=100, description="하단 여백")

    # 자막 애니메이션
    subtitle_animation: Optional[str] = Field(None, description="애니메이션 (pop, slide, fade, karaoke)")

    # 영상 효과
    transition_effect: Optional[str] = Field(None, description="트랜지션 (fade, crossfade, none)")
    color_grading: Optional[str] = Field(None, description="색 보정 (warm, cool, bw, none)")

    # BGM 설정
    bgm_enabled: bool = Field(default=True, description="BGM 활성화")
    bgm_mood: Optional[MoodType] = Field(default=MoodType.ENERGETIC, description="BGM 분위기")


class AssetBundle(BaseModel):
    """에셋 번들"""
    videos: List[StockVideoAsset] = Field(default_factory=list, description="영상 에셋")
    audio: Optional[AudioAsset] = Field(None, description="오디오 에셋")
    bgm: Optional[BGMAsset] = Field(None, description="배경음악 에셋")  # Phase 2 추가
    background_music: Optional[str] = Field(None, description="배경 음악 경로 (하위 호환)")


# ============================================================
# Editor Models
# ============================================================

class SubtitleSegment(BaseModel):
    """자막 세그먼트"""
    text: str = Field(..., description="자막 텍스트")
    start_time: float = Field(..., description="시작 시간(초)")
    end_time: float = Field(..., description="종료 시간(초)")
    style: Dict[str, Any] = Field(
        default_factory=lambda: {
            "fontsize": 40,
            "color": "white",
            "bg_color": "black",
            "position": ("center", "bottom")
        },
        description="자막 스타일"
    )


class EditConfig(BaseModel):
    """편집 설정"""
    resolution: tuple[int, int] = Field((1080, 1920), description="해상도 (width, height)")
    fps: int = Field(30, description="프레임 레이트")
    enable_transitions: bool = Field(True, description="트랜지션 효과 사용")
    enable_subtitle_animation: bool = Field(True, description="자막 애니메이션 사용")
    background_music_volume: float = Field(0.3, description="배경 음악 볼륨 (0.0-1.0)")
    output_dir: str = Field("./output", description="출력 디렉토리")


# ============================================================
# Uploader Models
# ============================================================

class YouTubeMetadata(BaseModel):
    """YouTube 메타데이터"""
    title: str = Field(..., max_length=100, description="제목 (최대 100자)")
    description: str = Field(..., max_length=5000, description="설명 (최대 5000자)")
    tags: List[str] = Field(default_factory=list, description="태그 (최대 500자)")
    category_id: str = Field("22", description="카테고리 ID")
    privacy_status: str = Field("private", description="공개 상태 (public/private/unlisted)")
    publish_at: Optional[datetime] = Field(None, description="예약 업로드 시각")


class UploadResult(BaseModel):
    """업로드 결과"""
    success: bool = Field(..., description="성공 여부")
    video_id: Optional[str] = Field(None, description="YouTube 영상 ID")
    url: Optional[str] = Field(None, description="YouTube URL")
    error: Optional[str] = Field(None, description="에러 메시지")
    uploaded_at: datetime = Field(default_factory=datetime.now, description="업로드 시각")


# ============================================================
# Orchestrator Models
# ============================================================

class ContentJob(BaseModel):
    """콘텐츠 생성 작업"""
    job_id: str = Field(..., description="작업 ID")
    status: ContentStatus = Field(ContentStatus.PLANNING, description="상태")
    plan: Optional[ContentPlan] = Field(None, description="콘텐츠 기획")
    assets: Optional[AssetBundle] = Field(None, description="에셋 번들")
    output_video_path: Optional[str] = Field(None, description="최종 영상 경로")
    upload_result: Optional[UploadResult] = Field(None, description="업로드 결과")

    # 메타 정보
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시각")
    updated_at: datetime = Field(default_factory=datetime.now, description="업데이트 시각")
    error_log: List[str] = Field(default_factory=list, description="에러 로그")

    model_config = {
        "json_schema_extra": {
            "example": {
                "job_id": "job_20251222_001",
                "status": "planning",
                "created_at": "2025-12-22T16:00:00Z"
            }
        }
    }


class JobHistory(BaseModel):
    """작업 히스토리"""
    total_jobs: int = Field(0, description="총 작업 수")
    completed_jobs: int = Field(0, description="완료 작업 수")
    failed_jobs: int = Field(0, description="실패 작업 수")
    jobs: List[ContentJob] = Field(default_factory=list, description="작업 목록")


# ============================================================
# Configuration Models
# ============================================================

class SystemConfig(BaseModel):
    """시스템 설정"""
    # AI 설정
    ai_provider: AIProvider = Field(AIProvider.GEMINI, description="AI 제공자")
    gemini_model: str = Field("gemini-2.0-flash-exp", description="Gemini 모델")

    # TTS 설정
    tts_provider: TTSProvider = Field(TTSProvider.ELEVENLABS, description="TTS 제공자")
    elevenlabs_voice_id: Optional[str] = Field(None, description="ElevenLabs 음성 ID")

    # 영상 설정
    default_format: VideoFormat = Field(VideoFormat.SHORTS, description="기본 포맷")
    default_duration: int = Field(60, description="기본 길이(초)")

    # 자동화 설정
    auto_upload: bool = Field(False, description="자동 업로드 여부")
    auto_schedule_interval: int = Field(24, description="자동 생성 간격(시간)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ai_provider": "gemini",
                "tts_provider": "elevenlabs",
                "default_format": "shorts",
                "auto_upload": False
            }
        }
    }
