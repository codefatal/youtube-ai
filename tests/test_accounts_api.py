"""
Account Management API 테스트
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
from backend.database import SessionLocal, Base, engine
from backend.models import Account, AccountSettings, ChannelType

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """테스트용 DB 초기화"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_account(setup_database):
    """계정 생성 테스트"""
    response = client.post(
        "/api/accounts/",
        json={
            "channel_name": "테스트 채널",
            "channel_type": "info",
            "default_prompt_style": "정보성",
            "is_active": True,
            "credentials_path": None
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["channel_name"] == "테스트 채널"
    assert data["channel_type"] == "info"
    assert "id" in data


def test_list_accounts(setup_database):
    """계정 목록 조회 테스트"""
    response = client.get("/api/accounts/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_account_detail(setup_database):
    """계정 상세 조회 테스트"""
    # 먼저 계정 생성
    create_response = client.post(
        "/api/accounts/",
        json={
            "channel_name": "상세 테스트 채널",
            "channel_type": "humor"
        }
    )
    account_id = create_response.json()["id"]

    # 상세 조회
    response = client.get(f"/api/accounts/{account_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == account_id
    assert "settings" in data  # AccountSettings 포함


def test_update_account_settings(setup_database):
    """계정 설정 수정 테스트"""
    # 계정 생성
    create_response = client.post(
        "/api/accounts/",
        json={"channel_name": "설정 테스트 채널", "channel_type": "info"}
    )
    account_id = create_response.json()["id"]

    # 설정 수정
    response = client.put(
        f"/api/accounts/{account_id}/settings",
        json={
            "tts_provider": "elevenlabs",
            "tts_voice_id": "pNInz6obpgDQGcFmaJgB",
            "tts_stability": 0.7,
            "tts_similarity_boost": 0.8,
            "default_duration": 90
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tts_provider"] == "elevenlabs"
    assert data["tts_stability"] == 0.7
    assert data["default_duration"] == 90


def test_delete_account(setup_database):
    """계정 삭제 테스트"""
    # 계정 생성
    create_response = client.post(
        "/api/accounts/",
        json={"channel_name": "삭제 테스트 채널", "channel_type": "trend"}
    )
    account_id = create_response.json()["id"]

    # 삭제
    response = client.delete(f"/api/accounts/{account_id}")
    assert response.status_code == 204

    # 삭제 확인
    get_response = client.get(f"/api/accounts/{account_id}")
    assert get_response.status_code == 404
