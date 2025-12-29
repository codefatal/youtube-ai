"""
BGM Management API Router
Phase 5: BGM 자동/수동 추가 기능
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path
import shutil

from backend.schemas import MoodInfo, MoodsResponse, BGMInfo, BGMListResponse, BGMUploadResponse
import os

router = APIRouter(prefix="/api/bgm", tags=["BGM"])

# BGM 저장 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent.parent
BGM_DIR = Path(os.getenv("BGM_DIR", str(PROJECT_ROOT / "music")))
BGM_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/moods", response_model=MoodsResponse)
async def list_moods():
    """
    Phase 5: 사용 가능한 분위기 목록

    6가지 분위기 타입 제공
    """
    moods = [
        MoodInfo(
            value="auto",
            label="자동 선택",
            description="주제와 톤에 맞춰 AI가 자동으로 분위기 선택"
        ),
        MoodInfo(
            value="HAPPY",
            label="행복한",
            description="밝고 즐거운 분위기 (유머, 일상 브이로그)"
        ),
        MoodInfo(
            value="SAD",
            label="슬픈",
            description="차분하고 감성적인 분위기 (회상, 감동)"
        ),
        MoodInfo(
            value="ENERGETIC",
            label="활기찬",
            description="빠르고 역동적인 분위기 (스포츠, 액션)"
        ),
        MoodInfo(
            value="CALM",
            label="차분한",
            description="편안하고 여유로운 분위기 (명상, 힐링)"
        ),
        MoodInfo(
            value="TENSE",
            label="긴장감 있는",
            description="긴박하고 스릴 있는 분위기 (스릴러, 서스펜스)"
        ),
        MoodInfo(
            value="MYSTERIOUS",
            label="신비로운",
            description="몽환적이고 신비한 분위기 (미스터리, 판타지)"
        )
    ]

    return {"moods": moods}


@router.get("/list", response_model=BGMListResponse)
async def list_bgm_files():
    """
    Phase 5: 사용 가능한 BGM 파일 목록

    music 디렉토리에서 BGM 파일 스캔
    """
    from core.bgm_manager import BGMManager

    try:
        bgm_manager = BGMManager()
        all_bgm = []

        # 모든 분위기의 BGM 수집
        for mood_folder in BGM_DIR.iterdir():
            if mood_folder.is_dir():
                mood_name = mood_folder.name.upper()

                for audio_file in mood_folder.glob("*.mp3"):
                    # 파일 정보 수집 (pydub로 길이 측정 시도)
                    try:
                        from pydub import AudioSegment
                        audio = AudioSegment.from_file(str(audio_file))
                        duration = len(audio) / 1000.0
                    except Exception as e:
                        # 길이 측정 실패 시 0.0 (pydub/ffmpeg 없을 수 있음)
                        duration = 0.0

                    bgm_info = BGMInfo(
                        name=audio_file.stem,
                        mood=mood_name,
                        duration=duration,
                        file_path=str(audio_file.relative_to(Path.cwd()))
                    )
                    all_bgm.append(bgm_info)

        return {
            "bgm_files": all_bgm,
            "total": len(all_bgm)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BGM 목록 조회 실패: {str(e)}")


@router.post("/upload", response_model=BGMUploadResponse)
async def upload_bgm(
    file: UploadFile = File(...),
    mood: str = "CALM"
):
    """
    Phase 5: BGM 파일 업로드

    Args:
        file: 오디오 파일 (mp3, wav, ogg 등)
        mood: 분위기 (HAPPY, SAD, ENERGETIC, CALM, TENSE, MYSTERIOUS)
    """
    # 파일 확장자 검증
    allowed_extensions = [".mp3", ".wav", ".ogg", ".m4a"]
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(allowed_extensions)}"
        )

    # 분위기 폴더 생성
    mood = mood.upper()
    mood_dir = BGM_DIR / mood
    mood_dir.mkdir(parents=True, exist_ok=True)

    # 파일 저장
    try:
        file_path = mood_dir / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 파일 길이 측정
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(file_path))
            duration = len(audio) / 1000.0
        except Exception as e:
            # 길이 측정 실패 시 0.0 (pydub/ffmpeg 없을 수 있음)
            duration = 0.0

        return {
            "message": "BGM 업로드 성공",
            "file_name": file.filename,
            "mood": mood,
            "duration": duration,
            "file_path": str(file_path.relative_to(Path.cwd()))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")
