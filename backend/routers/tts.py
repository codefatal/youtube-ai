"""
TTS Preview API Router
음성 미리듣기 및 Voice ID 조회
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import hashlib
from pathlib import Path

router = APIRouter(prefix="/api/tts", tags=["TTS"])

# 미리듣기용 임시 디렉토리
PREVIEW_DIR = Path("./downloads/audio/preview")
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)


class TTSPreviewRequest(BaseModel):
    """TTS 미리듣기 요청"""
    text: str = Field(..., min_length=1, max_length=500, description="변환할 텍스트 (최대 500자)")
    voice_id: str = Field(default="pNInz6obpgDQGcFmaJgB", description="ElevenLabs Voice ID")
    stability: float = Field(default=0.5, ge=0.0, le=1.0, description="음성 안정성")
    similarity_boost: float = Field(default=0.75, ge=0.0, le=1.0, description="유사도")
    style: float = Field(default=0.0, ge=0.0, le=1.0, description="스타일 과장도")


class VoiceInfo(BaseModel):
    """Voice 정보"""
    voice_id: str
    name: str
    language: str
    description: str


@router.post("/preview")
async def preview_tts(request: TTSPreviewRequest):
    """
    TTS 미리듣기 (짧은 텍스트만)

    전체 영상을 생성하지 않고 설정값을 테스트할 수 있습니다.
    같은 텍스트 + 설정이면 캐시된 파일을 반환합니다.
    """
    try:
        from elevenlabs.client import ElevenLabs
        import os

        # API 키 확인
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY가 설정되지 않았습니다.")

        # 캐시 파일명 생성
        settings_str = f"{request.voice_id}_{request.stability}_{request.similarity_boost}_{request.style}"
        cache_hash = hashlib.md5(
            f"{request.text}_{settings_str}".encode()
        ).hexdigest()[:10]
        filename = f"preview_{cache_hash}.mp3"
        filepath = PREVIEW_DIR / filename

        # 캐시 확인
        if filepath.exists():
            return FileResponse(
                path=str(filepath),
                media_type="audio/mpeg",
                filename=filename,
                headers={"X-Cache": "HIT"}
            )

        # TTS 생성
        client = ElevenLabs(api_key=api_key)

        audio_generator = client.text_to_speech.convert(
            text=request.text,
            voice_id=request.voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": request.stability,
                "similarity_boost": request.similarity_boost,
                "style": request.style,
                "use_speaker_boost": True
            }
        )

        # 저장
        with open(filepath, 'wb') as f:
            for chunk in audio_generator:
                if isinstance(chunk, bytes):
                    f.write(chunk)

        # 파일 반환
        return FileResponse(
            path=str(filepath),
            media_type="audio/mpeg",
            filename=filename,
            headers={"X-Cache": "MISS"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS 생성 실패: {str(e)}")


@router.get("/voices")
async def list_voices():
    """
    사용 가능한 ElevenLabs Voice 목록

    실제 API 호출 대신 미리 정의된 목록 반환 (비용 절감)
    """
    # 추천 한국어 지원 Voice ID
    voices = [
        VoiceInfo(
            voice_id="pNInz6obpgDQGcFmaJgB",
            name="Adam (Male)",
            language="Multilingual",
            description="밝고 친근한 남성 목소리 (한국어 지원)"
        ),
        VoiceInfo(
            voice_id="EXAVITQu4vr4xnSDxMaL",
            name="Bella (Female)",
            language="Multilingual",
            description="부드럽고 차분한 여성 목소리 (한국어 지원)"
        ),
        VoiceInfo(
            voice_id="FGY2WhTYpPnrIDTdsKH5",
            name="Laura (Female)",
            language="Multilingual",
            description="활기차고 명랑한 여성 목소리 (한국어 지원)"
        ),
        VoiceInfo(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            name="George (Male)",
            language="English",
            description="권위 있는 남성 목소리 (영어 전용)"
        )
    ]

    return {"voices": voices}


@router.delete("/cache")
async def clear_preview_cache():
    """
    미리듣기 캐시 삭제
    """
    import shutil

    if PREVIEW_DIR.exists():
        shutil.rmtree(PREVIEW_DIR)
        PREVIEW_DIR.mkdir()

    return {"message": "미리듣기 캐시가 삭제되었습니다."}