"""
BGM Management API Router
Phase 5: BGM 자동/수동 추가 기능
Phase 7: Catalog 자동 업데이트 및 AI 분위기 분류
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path
import shutil
import json

from backend.schemas import MoodInfo, MoodsResponse, BGMInfo, BGMListResponse, BGMUploadResponse
import os

router = APIRouter(prefix="/api/bgm", tags=["BGM"])

# BGM 저장 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent.parent
BGM_DIR = Path(os.getenv("BGM_DIR", str(PROJECT_ROOT / "music")))
BGM_DIR.mkdir(parents=True, exist_ok=True)

CATALOG_PATH = BGM_DIR / "catalog.json"
FRONTEND_CATALOG_PATH = PROJECT_ROOT / "frontend" / "public" / "assets" / "bgm" / "bgm_catalog.json"


def classify_mood_with_ai(filename: str, name: str = "") -> str:
    """
    AI 기반 BGM 분위기 자동 분류 (간단한 키워드 기반)

    Args:
        filename: 파일명
        name: BGM 이름 (선택)

    Returns:
        분위기 (HAPPY, SAD, ENERGETIC, CALM, TENSE, MYSTERIOUS)
    """
    text = f"{filename} {name}".lower()

    # 키워드 기반 분류
    if any(word in text for word in ['happy', 'upbeat', 'joy', 'cheerful', 'bright']):
        return 'HAPPY'
    elif any(word in text for word in ['sad', 'melancholy', 'emotional', 'tear']):
        return 'SAD'
    elif any(word in text for word in ['energetic', 'beat', 'rock', 'fast', 'action']):
        return 'ENERGETIC'
    elif any(word in text for word in ['calm', 'relax', 'peace', 'meditation', 'piano']):
        return 'CALM'
    elif any(word in text for word in ['tense', 'suspense', 'thriller', 'dark']):
        return 'TENSE'
    elif any(word in text for word in ['mysterious', 'ambient', 'deep', 'mystery']):
        return 'MYSTERIOUS'
    else:
        return 'CALM'  # 기본값


def update_bgm_catalog(bgm_file_path: Path, mood: str, name: str = "", artist: str = "User Upload"):
    """
    BGM catalog.json 업데이트

    Args:
        bgm_file_path: BGM 파일 경로
        mood: 분위기
        name: BGM 이름
        artist: 아티스트 이름
    """
    try:
        # 파일 크기로 대략적인 길이 추정 (1MB ≈ 60초)
        file_size_mb = bgm_file_path.stat().st_size / (1024 * 1024)
        estimated_duration = file_size_mb * 60

        # catalog.json 로드
        if CATALOG_PATH.exists():
            with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)
        else:
            catalog_data = []

        # 새로운 엔트리 생성
        new_entry = {
            "name": name or bgm_file_path.stem.replace('_', ' ').title(),
            "mood": mood.lower(),
            "file_path": f"{mood.upper()}/{bgm_file_path.name}",
            "duration": round(estimated_duration, 2),
            "volume": 0.25,
            "artist": artist,
            "license": "User Upload - Check license",
            "url": ""
        }

        # 중복 확인 (file_path 기준)
        existing_idx = next(
            (i for i, item in enumerate(catalog_data) if item.get('file_path') == new_entry['file_path']),
            None
        )

        if existing_idx is not None:
            # 기존 엔트리 업데이트
            catalog_data[existing_idx] = new_entry
        else:
            # 새로운 엔트리 추가
            catalog_data.append(new_entry)

        # catalog.json 저장
        with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, ensure_ascii=False, indent=2)

        print(f"[BGM] catalog.json updated: {bgm_file_path.name}")

        # 프론트엔드 catalog도 업데이트
        update_frontend_catalog(catalog_data)

    except Exception as e:
        print(f"[ERROR] Failed to update catalog: {e}")


def update_frontend_catalog(catalog_data: List[dict]):
    """
    프론트엔드 bgm_catalog.json 업데이트

    Args:
        catalog_data: Catalog 데이터
    """
    try:
        # 프론트엔드 폴더 생성
        FRONTEND_CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        # bgm_catalog.json 생성
        frontend_catalog = {
            "version": "1.0",
            "source": "Bensound + User Uploads",
            "license": "Mixed - Check individual licenses",
            "total_count": len(catalog_data),
            "moods": list(set(item['mood'] for item in catalog_data)),
            "bgm_list": catalog_data
        }

        with open(FRONTEND_CATALOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(frontend_catalog, f, ensure_ascii=False, indent=2)

        print(f"[BGM] Frontend catalog updated: {len(catalog_data)} items")

    except Exception as e:
        print(f"[ERROR] Failed to update frontend catalog: {e}")


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
    mood: str = Form("auto"),
    name: str = Form("")
):
    """
    Phase 7: BGM 파일 업로드 (Catalog 자동 업데이트)

    Args:
        file: 오디오 파일 (mp3, wav, ogg 등)
        mood: 분위기 (auto, HAPPY, SAD, ENERGETIC, CALM, TENSE, MYSTERIOUS)
        name: BGM 이름 (선택)

    Returns:
        업로드된 BGM 정보
    """
    # 파일 확장자 검증
    allowed_extensions = [".mp3", ".wav", ".ogg", ".m4a"]
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(allowed_extensions)}"
        )

    # AI 분위기 자동 분류
    if mood == "auto":
        mood = classify_mood_with_ai(file.filename, name)
        print(f"[BGM] AI 분위기 분류: {file.filename} -> {mood}")
    else:
        mood = mood.upper()

    # 분위기 폴더 생성
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
            # 길이 측정 실패 시 파일 크기로 추정
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            duration = file_size_mb * 60

        # ✨ Catalog 자동 업데이트
        update_bgm_catalog(file_path, mood, name or file.filename)

        # 프론트엔드 폴더에도 복사
        frontend_bgm_dir = PROJECT_ROOT / "frontend" / "public" / "assets" / "bgm" / mood
        frontend_bgm_dir.mkdir(parents=True, exist_ok=True)
        frontend_file_path = frontend_bgm_dir / file.filename
        shutil.copy2(file_path, frontend_file_path)

        return {
            "message": "BGM 업로드 성공 (Catalog 자동 업데이트됨)",
            "file_name": file.filename,
            "mood": mood,
            "duration": duration,
            "file_path": str(file_path.relative_to(Path.cwd()))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")
