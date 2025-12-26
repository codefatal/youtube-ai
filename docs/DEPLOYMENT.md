# 배포 가이드

YouTube AI v4.0 시스템을 서버 환경에 배포하는 방법을 안내합니다.

## 🚀 개요

본 문서는 개발 환경에서 구축된 YouTube AI 시스템을 프로덕션 환경에서 안정적으로 운영하기 위한 배포 절차를 설명합니다. 주로 Linux 기반 서버(Ubuntu, CentOS 등) 및 Docker 환경을 가정합니다.

---

## 🛠️ 필수 준비물

1.  **클라우드 서버**: AWS EC2, Google Cloud Compute Engine, Azure VM 등 (권장: 4 vCPU, 8GB RAM 이상)
2.  **도메인 (선택 사항)**: HTTPS 설정을 위한 도메인 (예: `youtube-ai.yourdomain.com`)
3.  **Docker 및 Docker Compose**: 컨테이너 기반 배포를 위한 도구
4.  **Git**: 소스 코드 관리를 위한 도구
5.  **Python 3.14+**: 백엔드 애플리케이션 실행 환경
6.  **Node.js 및 npm/yarn**: 프론트엔드 애플리케이션 빌드를 위한 도구

---

## 📦 배포 절차

### 1. 서버 설정

1.  **Git 클론**:
    ```bash
    git clone https://github.com/codefatal/youtube-ai.git
    cd youtube-ai
    ```

2.  **환경 변수 설정**:
    `youtube-ai` 프로젝트 루트에 `.env` 파일을 생성하고 필요한 API 키 및 기타 환경 변수를 설정합니다. `.env.example` 파일을 참고하십시오.

    ```bash
    # AI Provider
    GEMINI_API_KEY=your_gemini_api_key

    # Stock Videos
    PEXELS_API_KEY=your_pexels_api_key

    # TTS (선택)
    ELEVENLABS_API_KEY=your_elevenlabs_api_key

    # YouTube (OAuth 클라이언트 ID, Secret, API Key)
    YOUTUBE_CLIENT_ID=your_youtube_oauth_client_id
    YOUTUBE_CLIENT_SECRET=your_youtube_oauth_client_secret
    YOUTUBE_API_KEY=your_youtube_api_key
    ```
    **주의**: `YOUTUBE_CLIENT_ID`와 `YOUTUBE_CLIENT_SECRET`는 YouTube Data API 사용을 위한 OAuth 2.0 클라이언트 자격 증명입니다. 이 값들은 민감하므로 Git에 커밋되지 않도록 `.gitignore`에 추가되어 있는지 확인하십시오.

3.  **데이터베이스 초기화**:
    프로덕션 환경에서는 SQLite 대신 PostgreSQL 또는 MySQL과 같은 외부 데이터베이스 사용을 권장합니다.
    `backend/database.py`에서 `SQLALCHEMY_DATABASE_URL`을 적절히 변경해야 합니다.
    ```bash
    # (외부 DB 사용 시) SQLALCHEMY_DATABASE_URL 환경 변수 설정
    export SQLALCHEMY_DATABASE_URL="postgresql://user:password@host:port/dbname"

    # Alembic 마이그레이션 실행
    alembic upgrade head

    # (선택) v3에서 v4로 마이그레이션할 데이터가 있다면 실행
    python scripts/migrate_v3_to_v4.py
    ```

### 2. 백엔드 배포 (FastAPI)

FastAPI 애플리케이션은 Gunicorn과 Nginx(리버스 프록시) 조합으로 배포하는 것을 권장합니다.

1.  **가상 환경 생성 및 의존성 설치**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install gunicorn  # Gunicorn 설치
    ```

2.  **Gunicorn으로 실행**:
    ```bash
    gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    ```
    이 명령을 `systemd` 서비스로 등록하여 서버 부팅 시 자동으로 실행되도록 설정할 수 있습니다.

### 3. 프론트엔드 배포 (Next.js)

Next.js 애플리케이션은 빌드 후 Nginx로 정적 파일을 서비스하는 방식으로 배포할 수 있습니다.

1.  **의존성 설치 및 빌드**:
    ```bash
    cd frontend
    npm install
    npm run build
    ```

2.  **Nginx 설정**:
    Nginx 설정 파일(`nginx.conf` 또는 `sites-available/your_domain.conf`)에 다음과 같이 프록시 설정 및 정적 파일 서빙 설정을 추가합니다.

    ```nginx
    server {
        listen 80;
        server_name yourdomain.com; # 도메인 설정 (또는 IP)

        location /api/ {
            proxy_pass http://localhost:8000; # 백엔드 Gunicorn 포트
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
            root /path/to/your/youtube-ai/frontend/out; # npm run build 결과물 경로
            try_files $uri $uri/ /index.html;
        }
    }
    ```
    `npm run build` 결과물은 `frontend/out` 디렉토리에 생성됩니다.

### 4. Docker Compose를 이용한 배포 (권장)

`docker-compose.yml` 파일을 사용하여 백엔드, 프론트엔드, 데이터베이스를 컨테이너로 묶어 배포하는 것을 권장합니다.

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine # 프로덕션용 DB (SQLite 대신)
    environment:
      POSTGRES_DB: youtube_ai_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - db_data:/var/lib/postgresql/data
    restart: always

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/youtube_ai_db
      # .env 파일 내용은 여기에 environment 변수로 직접 명시하거나, Docker secrets 사용
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - PEXELS_API_KEY=${PEXELS_API_KEY}
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - YOUTUBE_CLIENT_ID=${YOUTUBE_CLIENT_ID}
      - YOUTUBE_CLIENT_SECRET=${YOUTUBE_CLIENT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000 # 백엔드 API URL
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: always

volumes:
  db_data:
```

**`Dockerfile.backend` 예시**:

```dockerfile
# Dockerfile.backend
FROM python:3.14-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn uvicorn[standard] psycopg2-binary # 프로덕션용 설치

COPY . .

# 마이그레이션 실행
RUN alembic upgrade head

EXPOSE 8000

CMD ["gunicorn", "backend.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**`Dockerfile.frontend` 예시**:

```dockerfile
# Dockerfile.frontend
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend .
RUN npm run build

FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

CMD ["npm", "start"]
```

**배포 실행**:
```bash
docker compose up -d --build
```

---

## 🔒 보안 고려사항

1.  **환경 변수 관리**: `.env` 파일은 Git에 커밋하지 말고, 프로덕션에서는 Docker Secrets, Kubernetes Secrets 또는 클라우드 제공자의 Secret Manager를 사용하십시오.
2.  **HTTPS**: Nginx 또는 클라우드 로드 밸런서를 통해 반드시 HTTPS를 적용하십시오.
3.  **데이터베이스 보안**: 외부 DB 사용 시 네트워크 접근 제어(방화벽) 및 강력한 비밀번호를 사용하십시오.
4.  **YouTube OAuth**: `client_secrets.json` 파일은 절대 Git에 커밋하지 마십시오.

---

**마지막 업데이트**: 2025-12-26
**문서 버전**: 1.0
