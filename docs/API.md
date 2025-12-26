# API 문서

FastAPI 백엔드의 API 엔드포인트에 대한 문서입니다.

## 🚀 개요

이 문서는 YouTube AI v4.0 백엔드 API의 주요 엔드포인트와 사용 방법을 설명합니다. 모든 API는 `http://localhost:8000` (개발 환경 기준)에서 접근할 수 있습니다.

### 자동 생성된 문서

FastAPI는 OpenAPI 표준을 따르는 자동 생성된 API 문서를 제공합니다.

-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`

이 문서는 주로 주요 API 그룹에 대한 간략한 소개를 포함합니다. 상세한 스키마 정의 및 요청/응답 예시는 위 자동 생성 문서를 참조하십시오.

---

## 🔑 인증

현재 API는 별도의 인증 절차를 요구하지 않습니다. (개발 편의성 목적)
프로덕션 환경에서는 적절한 인증(예: OAuth2, JWT)을 구현해야 합니다.

---

## 📁 API 그룹

### 1. 계정 관리 (Accounts)

**엔드포인트**: `/api/accounts/`
**설명**: YouTube 채널 계정 및 관련 설정을 관리합니다.

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/api/accounts/` | 새 계정 생성 |
| `GET` | `/api/accounts/` | 모든 계정 목록 조회 |
| `GET` | `/api/accounts/{account_id}` | 특정 계정 상세 정보 조회 |
| `PUT` | `/api/accounts/{account_id}/settings` | 특정 계정 설정 업데이트 |
| `DELETE` | `/api/accounts/{account_id}` | 특정 계정 삭제 |

### 2. TTS (Text-to-Speech)

**엔드포인트**: `/api/tts/`
**설명**: ElevenLabs TTS 미리듣기 및 Voice 목록을 관리합니다.

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/api/tts/preview` | TTS 미리듣기 음성 생성 |
| `GET` | `/api/tts/voices` | 사용 가능한 ElevenLabs Voice 목록 조회 |
| `DELETE` | `/api/tts/cache` | TTS 미리듣기 캐시 삭제 |

### 3. 스케줄러 (Scheduler)

**엔드포인트**: `/api/scheduler/`
**설명**: 자동화된 영상 생성 및 업로드 스케줄을 관리합니다.

| 메서드 | 경로 | 설명 |
|---|---|---|
| `GET` | `/api/scheduler/jobs` | 현재 등록된 모든 스케줄 Job 조회 |
| `POST` | `/api/scheduler/reload` | DB에서 스케줄을 다시 로드 |
| `POST` | `/api/scheduler/trigger/{account_id}` | 특정 계정의 자동 작업을 즉시 실행 |
| `DELETE` | `/api/scheduler/jobs/{job_id}` | 특정 스케줄 Job 제거 |

### 4. 콘텐츠 생성 (Videos)

**엔드포인트**: `/api/videos/`
**설명**: AI를 통한 영상 콘텐츠 생성 작업을 시작합니다.

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/api/videos/create` | 영상 생성 작업 시작 (백그라운드) |

### 5. 작업 관리 (Jobs)

**엔드포인트**: `/api/jobs/`
**설명**: 백그라운드 작업(영상 생성)의 상태를 조회합니다.

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/api/jobs/status` | 특정 Job의 현재 상태 조회 |
| `GET` | `/api/jobs/recent` | 최근 작업 목록 조회 |

### 6. 시스템 정보 (System)

**엔드포인트**: `/api/`
**설명**: 시스템 상태 및 설정 정보를 조회합니다.

| 메서드 | 경로 | 설명 |
|---|---|---|
| `GET` | `/health` | API 서버 헬스 체크 |
| `GET` | `/api/stats` | 전체 작업 통계 조회 |
| `GET` | `/api/config` | 현재 시스템 설정 조회 |

---

## 📝 요청 및 응답

각 엔드포인트의 구체적인 요청 바디(Request Body) 및 응답 구조(Response Schema)는 FastAPI가 제공하는 Swagger UI (`/docs`) 또는 ReDoc (`/redoc`)을 참조하십시오. Pydantic 모델을 기반으로 자동 생성됩니다.

---

**마지막 업데이트**: 2025-12-26
**문서 버전**: 1.0
