"""
Database Connection Module
SQLite + SQLAlchemy 기반 DB 연결 관리
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

# DB 파일 경로
DB_DIR = Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "youtube_ai.db"

# SQLite 연결 URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 멀티스레드 지원
    echo=False  # SQL 쿼리 로깅 (개발 시 True로 설정)
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM Base 클래스
Base = declarative_base()


def get_db() -> Session:
    """
    FastAPI Dependency Injection용 DB 세션 제공

    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    데이터베이스 초기화 (테이블 생성)
    앱 시작 시 호출
    """
    from backend.models import Account, AccountSettings, JobHistory
    Base.metadata.create_all(bind=engine)
    print(f"[Database] 초기화 완료: {DB_PATH}")