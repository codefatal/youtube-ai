"""
Account Management API Router
계정 생성, 조회, 수정, 삭제 (CRUD)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Account, AccountSettings
from backend.schemas import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountDetailResponse,
    AccountSettingsUpdate,
    AccountSettingsResponse
)

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


# ============================================================================
# Account CRUD
# ============================================================================

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 YouTube 계정 생성
    자동으로 기본 설정(AccountSettings)도 생성됩니다.
    """
    # 중복 확인
    existing = db.query(Account).filter(Account.channel_name == account.channel_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"채널명 '{account.channel_name}'이 이미 존재합니다."
        )

    # Account 생성
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.flush()  # ID 생성을 위해 flush

    # 기본 AccountSettings 생성
    db_settings = AccountSettings(account_id=db_account.id)
    db.add(db_settings)

    db.commit()
    db.refresh(db_account)

    return db_account


@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    모든 계정 목록 조회
    """
    accounts = db.query(Account).offset(skip).limit(limit).all()
    return accounts


@router.get("/{account_id}", response_model=AccountDetailResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 계정 상세 조회 (설정 및 작업 이력 포함)
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}를 찾을 수 없습니다."
        )

    return account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db)
):
    """
    계정 정보 수정 (부분 업데이트)
    """
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}를 찾을 수 없습니다."
        )

    # 부분 업데이트
    update_data = account_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_account, key, value)

    db.commit()
    db.refresh(db_account)

    return db_account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    계정 삭제 (설정 및 작업 이력도 함께 삭제)
    """
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}를 찾을 수 없습니다."
        )

    db.delete(db_account)
    db.commit()

    return None


# ============================================================================
# AccountSettings CRUD
# ============================================================================

@router.get("/{account_id}/settings", response_model=AccountSettingsResponse)
def get_account_settings(
    account_id: int,
    db: Session = Depends(get_db)
):
    """
    계정 설정 조회
    """
    settings = db.query(AccountSettings).filter(
        AccountSettings.account_id == account_id
    ).first()

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}의 설정을 찾을 수 없습니다."
        )

    return settings


@router.put("/{account_id}/settings", response_model=AccountSettingsResponse)
def update_account_settings(
    account_id: int,
    settings_update: AccountSettingsUpdate,
    db: Session = Depends(get_db)
):
    """
    계정 설정 수정
    """
    db_settings = db.query(AccountSettings).filter(
        AccountSettings.account_id == account_id
    ).first()

    if not db_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"계정 ID {account_id}의 설정을 찾을 수 없습니다."
        )

    # 업데이트
    update_data = settings_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_settings, key, value)

    db.commit()
    db.refresh(db_settings)

    return db_settings
