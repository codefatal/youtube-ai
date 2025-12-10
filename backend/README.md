# Backend API Server

FastAPI 기반 백엔드 API 서버

## 설치

```bash
cd backend
pip install -r requirements.txt
```

## 실행

```bash
# 개발 모드
python main.py

# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 문서

서버 실행 후:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 엔드포인트

- `GET /` - API 정보
- `GET /api/health` - 헬스 체크
- `POST /api/trends/analyze` - 트렌드 분석
- `POST /api/scripts/generate` - 대본 생성
- `POST /api/videos/produce` - 영상 제작
- `POST /api/upload` - YouTube 업로드
- `POST /api/automation/full` - 전체 자동화
