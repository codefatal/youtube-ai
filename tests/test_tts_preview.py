"""
TTS Preview API 테스트
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app

client = TestClient(app)


def test_tts_preview():
    """TTS 미리듣기 테스트"""
    response = client.post(
        "/api/tts/preview",
        json={
            "text": "안녕하세요, 테스트입니다.",
            "voice_id": "pNInz6obpgDQGcFmaJgB",
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0
        }
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"

    # 캐시 헤더 확인
    cache_header = response.headers.get("X-Cache")
    assert cache_header in ["HIT", "MISS"]


def test_tts_preview_caching():
    """TTS 미리듣기 캐싱 테스트"""
    payload = {
        "text": "캐싱 테스트 텍스트",
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "stability": 0.6,
        "similarity_boost": 0.8,
        "style": 0.2
    }

    # 첫 번째 요청 (MISS)
    response1 = client.post("/api/tts/preview", json=payload)
    assert response1.status_code == 200
    cache1 = response1.headers.get("X-Cache")

    # 두 번째 요청 (HIT)
    response2 = client.post("/api/tts/preview", json=payload)
    assert response2.status_code == 200
    cache2 = response2.headers.get("X-Cache")

    # 두 번째 요청은 캐시에서 가져와야 함
    assert cache2 == "HIT"


def test_list_voices():
    """Voice 목록 조회 테스트"""
    response = client.get("/api/tts/voices")

    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert len(data["voices"]) > 0

    # Voice 정보 구조 확인
    voice = data["voices"][0]
    assert "voice_id" in voice
    assert "name" in voice
    assert "language" in voice
