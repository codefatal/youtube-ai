# Phase 3: ElevenLabs TTS 고도화

**작업 기간**: 0.5주 (2026-01-13 ~ 2026-01-16)
**담당 모듈**: `core/asset_manager.py`, `backend/routers/tts.py`
**우선순위**: ⭐⭐⭐ (중)
**난이도**: 🔥🔥 (중)
**의존성**: Phase 1 완료 필수

---

## 📋 개요

현재 구현된 기본 ElevenLabs TTS를 고도화하여 상세 파라미터 제어, 미리듣기 기능, 스마트 캐싱을 추가합니다. Phase 1에서 구축한 `AccountSettings` 테이블과 연동하여 계정별로 다른 음성 설정을 적용할 수 있습니다.

### 목표
- ✅ ElevenLabs 파라미터 상세 제어 (Stability, Similarity Boost, Style)
- ✅ TTS 미리듣기 API 구현
- ✅ 해시 기반 스마트 캐싱 강화
- ✅ AccountSettings 연동
- ✅ 비용 절감 (API 호출 50% 감소)

---

## 🗂️ 디렉토리 구조

```
youtube-ai/
├── backend/
│   └── routers/
│       └── tts.py           # ✨ NEW - TTS 미리듣기 API
├── core/
│   └── asset_manager.py     # 🔧 MODIFY - ElevenLabs 고도화
└── tests/
    └── test_tts_preview.py  # ✨ NEW - 미리듣기 테스트
```

---

## 🏗️ 구현 단계

### Step 1: ElevenLabs 파라미터 추가 (`core/asset_manager.py`)

기존 `_generate_elevenlabs()` 메소드를 확장합니다.

```python
# core/asset_manager.py

class AssetManager:
    def _generate_elevenlabs(
        self,
        text: str,
        voice_id: str = "pNInz6obpgDQGcFmaJgB",  # Adam
        stability: float = 0.5,      # ✨ NEW: 0.0 ~ 1.0
        similarity_boost: float = 0.75,  # ✨ NEW: 0.0 ~ 1.0
        style: float = 0.0,          # ✨ NEW: 0.0 ~ 1.0 (과장 정도)
        use_speaker_boost: bool = True  # ✨ NEW: 목소리 강화
    ) -> Optional[str]:
        """
        ElevenLabs TTS 고도화 버전

        Args:
            text: 변환할 텍스트
            voice_id: ElevenLabs Voice ID
            stability: 음성 안정성 (낮을수록 감정 표현 풍부, 높을수록 일관성 유지)
            similarity_boost: 원본 목소리와의 유사도 (높을수록 원본에 가까움)
            style: 스타일 과장 정도 (0.0 = 자연스러움, 1.0 = 과장됨)
            use_speaker_boost: 목소리 강화 (True 권장)

        Returns:
            저장된 파일 경로 또는 None
        """
        try:
            from elevenlabs.client import ElevenLabs
            import os

            # API 키 확인
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                print("[ERROR] ELEVENLABS_API_KEY 환경변수가 설정되지 않았습니다.")
                return self._generate_gtts(text)

            # ✨ 파일명 생성 (설정값 포함 해시)
            # 같은 텍스트라도 파라미터가 다르면 다른 파일로 저장
            settings_str = f"{voice_id}_{stability}_{similarity_boost}_{style}"
            combined_hash = hashlib.md5(
                f"{text}_{settings_str}".encode()
            ).hexdigest()[:10]

            filename = f"tts_elevenlabs_{combined_hash}.mp3"
            filepath = self.audio_dir / filename

            # 이미 생성된 경우 (스마트 캐싱)
            if filepath.exists():
                print(f"[TTS] 캐시에서 로드: {filename}")
                return str(filepath)

            # ElevenLabs 클라이언트 생성
            client = ElevenLabs(api_key=api_key)

            # ✨ 상세 설정으로 TTS 생성
            print(f"[ElevenLabs] 음성 생성 중...")
            print(f"  - Voice: {voice_id}")
            print(f"  - Stability: {stability}")
            print(f"  - Similarity Boost: {similarity_boost}")
            print(f"  - Style: {style}")

            audio_generator = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                # ✨ Voice Settings 추가
                voice_settings={
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            )

            # 오디오 저장
            with open(filepath, 'wb') as f:
                for chunk in audio_generator:
                    if isinstance(chunk, bytes):
                        f.write(chunk)

            print(f"[SUCCESS] ElevenLabs TTS 생성 완료: {filepath}")
            return str(filepath)

        except ImportError:
            print("[ERROR] elevenlabs 패키지가 설치되지 않았습니다.")
            return self._generate_gtts(text)
        except Exception as e:
            print(f"[ERROR] ElevenLabs TTS 생성 실패: {e}")
            return self._generate_gtts(text)

    def _generate_tts(self, content_plan: ContentPlan, account_id: Optional[int] = None) -> Optional[AudioAsset]:
        """
        TTS 음성 생성 (AccountSettings 연동)

        Args:
            content_plan: ContentPlan 객체
            account_id: 계정 ID (Phase 1 DB 연동)

        Returns:
            AudioAsset 객체 또는 None
        """
        full_text = " ".join([seg.text for seg in content_plan.segments])

        # ✨ AccountSettings에서 TTS 설정 가져오기
        if account_id:
            settings = self._get_account_tts_settings(account_id)
        else:
            # 기본값
            settings = {
                "tts_provider": self.tts_provider,
                "tts_voice_id": "pNInz6obpgDQGcFmaJgB",
                "tts_stability": 0.5,
                "tts_similarity_boost": 0.75,
                "tts_style": 0.0
            }

        # TTS 생성 (설정 반영)
        if settings["tts_provider"] == "elevenlabs":
            filepath = self._generate_elevenlabs(
                text=full_text,
                voice_id=settings["tts_voice_id"],
                stability=settings["tts_stability"],
                similarity_boost=settings["tts_similarity_boost"],
                style=settings["tts_style"]
            )
        else:
            filepath = self._generate_gtts(full_text)

        if filepath:
            return AudioAsset(
                text=full_text,
                provider=TTSProvider(settings["tts_provider"]),
                local_path=filepath
            )

        return None

    def _get_account_tts_settings(self, account_id: int) -> dict:
        """
        AccountSettings에서 TTS 설정 가져오기

        Args:
            account_id: 계정 ID

        Returns:
            설정 딕셔너리
        """
        from backend.database import SessionLocal
        from backend.models import AccountSettings

        db = SessionLocal()
        try:
            settings = db.query(AccountSettings).filter(
                AccountSettings.account_id == account_id
            ).first()

            if settings:
                return {
                    "tts_provider": settings.tts_provider,
                    "tts_voice_id": settings.tts_voice_id or "pNInz6obpgDQGcFmaJgB",
                    "tts_stability": settings.tts_stability,
                    "tts_similarity_boost": settings.tts_similarity_boost,
                    "tts_style": settings.tts_style
                }
        finally:
            db.close()

        # 기본값 반환
        return {
            "tts_provider": "gtts",
            "tts_voice_id": "pNInz6obpgDQGcFmaJgB",
            "tts_stability": 0.5,
            "tts_similarity_boost": 0.75,
            "tts_style": 0.0
        }
```

---

### Step 2: TTS 미리듣기 API (`backend/routers/tts.py`)

프론트엔드에서 설정을 변경하며 즉시 미리듣기 할 수 있는 API를 만듭니다.

```python
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
```

---

### Step 3: FastAPI 라우터 등록 (`backend/main.py`)

```python
# backend/main.py

from backend.routers import accounts, tts  # ✨ tts 추가

# ... 앱 생성 후 ...

app.include_router(accounts.router)
app.include_router(tts.router)  # ✨ NEW
```

---

## ✅ 테스트 체크리스트

### 1. 파라미터 제어 테스트

```python
# tests/test_tts_advanced.py
from core.asset_manager import AssetManager

asset_manager = AssetManager(tts_provider="elevenlabs")

# 안정성 낮음 (감정 풍부)
filepath1 = asset_manager._generate_elevenlabs(
    text="안녕하세요! 오늘은 정말 신나는 하루입니다!",
    stability=0.3,
    similarity_boost=0.75,
    style=0.5
)

# 안정성 높음 (일관성)
filepath2 = asset_manager._generate_elevenlabs(
    text="안녕하세요! 오늘은 정말 신나는 하루입니다!",
    stability=0.9,
    similarity_boost=0.75,
    style=0.0
)

# 두 파일이 다르게 생성되었는지 확인
assert filepath1 != filepath2
print("파라미터별 음성 생성 성공")
```

### 2. 미리듣기 API 테스트

**curl 테스트**:

```bash
# 미리듣기 생성
curl -X POST "http://localhost:8000/api/tts/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "안녕하세요, 테스트 음성입니다.",
    "voice_id": "pNInz6obpgDQGcFmaJgB",
    "stability": 0.7,
    "similarity_boost": 0.8,
    "style": 0.2
  }' \
  --output preview.mp3

# Voice 목록 조회
curl -X GET "http://localhost:8000/api/tts/voices"

# 캐시 삭제
curl -X DELETE "http://localhost:8000/api/tts/cache"
```

**프론트엔드 통합** (Phase 5에서):
```javascript
// TTS 설정 변경 시 미리듣기
async function previewVoice(text, settings) {
  const response = await fetch('/api/tts/preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: text,
      voice_id: settings.voiceId,
      stability: settings.stability,
      similarity_boost: settings.similarityBoost,
      style: settings.style
    })
  });

  const blob = await response.blob();
  const audioUrl = URL.createObjectURL(blob);

  // 오디오 재생
  const audio = new Audio(audioUrl);
  audio.play();
}
```

### 3. 캐싱 효율성 테스트

```python
# tests/test_tts_caching.py
import time
from core.asset_manager import AssetManager

asset_manager = AssetManager(tts_provider="elevenlabs")

text = "이것은 캐싱 테스트입니다."

# 첫 번째 호출 (API 호출)
start = time.time()
filepath1 = asset_manager._generate_elevenlabs(text)
time1 = time.time() - start

# 두 번째 호출 (캐시)
start = time.time()
filepath2 = asset_manager._generate_elevenlabs(text)
time2 = time.time() - start

# 캐싱으로 인한 속도 향상 확인
assert filepath1 == filepath2
assert time2 < time1 * 0.1  # 10배 이상 빠름
print(f"첫 호출: {time1:.2f}초, 캐시 호출: {time2:.4f}초")
print(f"속도 향상: {time1/time2:.1f}배")
```

---

## 📊 성공 기준

- [x] TTS 파라미터 조절 작동 (Stability, Similarity Boost, Style)
- [x] 미리듣기 API 응답 시간 1초 이내 (캐시 HIT 시)
- [x] 캐싱으로 API 호출 50% 감소 (동일 텍스트 재사용 시)
- [x] AccountSettings 연동 확인 (계정별 다른 목소리 적용)
- [x] Voice 목록 API 작동

---

## 💰 비용 최적화 전략

### ElevenLabs 무료 티어
- **무료**: 월 10,000자 (약 영상 15~20개)
- **유료**: $5/월 30,000자 (약 영상 50~100개)

### 캐싱 전략
1. **해시 기반 캐싱**: 같은 텍스트 + 설정 = 캐시 재사용
2. **미리듣기 캐싱**: 자주 사용하는 샘플 텍스트 캐시
3. **개발 환경**: gTTS 사용, 프로덕션에서만 ElevenLabs

### 예상 API 호출 감소
- **캐싱 전**: 100개 영상 = 100번 API 호출
- **캐싱 후**: 100개 영상 = 50~60번 API 호출 (40~50% 절감)

---

## 🚀 커밋 전략

```bash
# Step 1
git add core/asset_manager.py
git commit -m "Phase 3: Add ElevenLabs advanced parameters (stability, similarity_boost, style)"

# Step 2
git add backend/routers/tts.py
git commit -m "Phase 3: Add TTS preview API with caching"

# Step 3
git add backend/main.py
git commit -m "Phase 3: Integrate TTS router into FastAPI"

# 테스트
git add tests/test_tts_advanced.py tests/test_tts_caching.py
git commit -m "Phase 3: Add TTS advanced tests"
```

---

## ⚠️ 주의사항

1. **API 키 보안**
   - `.env` 파일에 ELEVENLABS_API_KEY 저장
   - Git에 커밋하지 않도록 `.gitignore` 확인

2. **API 호출 한도**
   - 무료 티어: 월 10,000자
   - 한도 초과 시 자동으로 gTTS 폴백

3. **Voice ID 확인**
   - ElevenLabs 콘솔에서 Voice ID 확인
   - 한국어 지원 모델(`eleven_multilingual_v2`) 필수

4. **미리듣기 텍스트 길이**
   - 500자 제한 (비용 절감)
   - 긴 텍스트는 전체 생성 사용

---

## 📚 참고 자료

- **ElevenLabs 공식 문서**: https://elevenlabs.io/docs
- **Voice Settings 가이드**: https://elevenlabs.io/docs/speech-synthesis/voice-settings
- **API 요금**: https://elevenlabs.io/pricing

---

## 📚 다음 단계

Phase 3 완료 후:
- **Phase 4**: 스케줄링 시스템 (계정별 자동 음성 생성)
- **Phase 5**: 프론트엔드 (TTS 설정 UI, 미리듣기 버튼)

**Phase 4로 이동**: [UPGRADE_PHASE4.md](./UPGRADE_PHASE4.md)

---

**작성일**: 2025-12-26
**버전**: 1.0
**상태**: Ready for Implementation
