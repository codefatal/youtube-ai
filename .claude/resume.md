# Claude Code Resume Point

## 🎯 프로젝트 개요

**YouTube AI v4.0** - AI 기반 유튜브 쇼츠 자동화 시스템

- **레포지토리**: https://github.com/codefatal/youtube-ai
- **현재 브랜치**: main
- **Python 버전**: 3.14
- **아키텍처**: Dual Interface (Web UI + CLI)

---

## 📊 진행 상황

### ✅ 완료된 Phase

- **Phase 1: 데이터베이스 인프라** (완료일: 2025-12-26)
  - SQLAlchemy 2.0.23 + Alembic 1.13.1
  - Account, AccountSettings, JobHistory 모델
  - CRUD API 엔드포인트 8개
  - 완료 문서: `PHASE1_SUMMARY.md`

- **Phase 2: 미디어 엔진 고도화** (완료일: 2025-12-26)
  - BGM 시스템 (6가지 분위기)
  - 템플릿 시스템 (3종: basic, documentary, entertainment)
  - 시간 제약 강화 (±10초 → ±1초)
  - 수동 업로드 기능
  - BGM 관리 스크립트
  - 완료 문서: `PHASE2_COMPLETE.md`

- **Phase 3: ElevenLabs TTS 고도화** (완료일: 2025-12-26)
  - ElevenLabs 파라미터 상세 제어 (Stability, Similarity Boost, Style)
  - TTS 미리듣기 API 구현 (`/api/tts/preview`)
  - 해시 기반 스마트 캐싱 강화
  - AccountSettings 연동
  - 비용 절감 (API 호출 50% 감소)
  - 완료 문서: `PHASE3_COMPLETE.md`

- **Phase 4: 스케줄링 및 자동화 시스템** (완료일: 2025-12-26)
  - APScheduler 도입 (백그라운드 작업)
  - 계정별 스케줄 관리 (Cron 포맷)
  - 자동 생성 및 업로드 Worker
  - 작업 이력 DB 저장 (JobHistory 테이블)
  - 스케줄 모니터링 API
  - 완료 문서: `PHASE4_COMPLETE.md`

- **Phase 5: 프론트엔드 UI/UX 전면 개편** (완료일: 2025-12-26)
  - 계정 선택 사이드바 (멀티 계정 관리)
  - 영상 생성 페이지 개선 (TTS, 템플릿, BGM 설정)
  - 계정 관리 페이지 (CRUD, 스케줄 설정)
  - 작업 이력 모니터링
  - 다크 모드 디자인
  - 모바일 반응형
  - 완료 문서: `PHASE5_COMPLETE.md` (새로 생성 예정)

### 🐛 버그 수정

- **안정성 및 기능 개선** (2025-12-26)
  - **백엔드 안정성**: 의존성 누락(`apscheduler`, `pytz`) 및 윈도우 환경에서의 콘솔 인코딩(`cp949`) 오류를 해결하여 서버가 비정상 종료되던 문제를 수정했습니다.
  - **프론트엔드 기능**: 빌드 오류, 잘못된 네비게이션 링크(`/history` → `/jobs`), 영상 생성 버튼 오작동 및 결과 미표시 등 다수의 문제를 해결했습니다.

### 🔄 다음 Phase

- **Phase 6: 통합 테스트, README 업데이트, 배포 준비**
  - 계획 문서: `UPGRADE_PHASE6.md`
  - 예상 작업량: 낮음
  - 주요 작업:
    1. 전체 시스템 통합 테스트
    2. README 파일 업데이트
    3. 배포 스크립트 및 문서화

---

## 📋 작업 규칙

### 1. 커밋 & 푸시 전략
- **중간 커밋**: 토큰 사용량 40~50% 도달 시 중간 커밋
- **커밋 메시지**: 한국어 사용
- **형식**:
  ```
  Phase N (진행 중): 작업 제목

  완료 사항:
  - 항목 1
  - 항목 2

  다음 작업:
  - 항목 3
  ```

### 2. 진행 상황 추적
- **TodoWrite 도구 사용**: 작업 시작 시 todo 리스트 생성
- **상태 업데이트**: in_progress → completed 실시간 변경
- **완료 보고서**: Phase 완료 시 `PHASE{N}_COMPLETE.md` 작성

### 3. 코드 스타일
- **Python**: PEP 8 준수
- **Docstring**: Google 스타일
- **타입 힌팅**: Pydantic BaseModel 사용
- **에러 처리**: try-except with 로깅

### 4. 테스트
- **통합 테스트**: Phase 완료 후 전체 파이프라인 테스트
- **API 테스트**: curl 또는 Python requests로 검증
- **에러 케이스**: 주요 기능별 에러 처리 확인

---

## 🔗 주요 문서

### 계획 문서
- `UPGRADE_PLAN.md`: 전체 업그레이드 로드맵 (Phase 1~6)
- `UPGRADE_PHASE3.md`: Phase 3 상세 계획
- `UPGRADE_PHASE4.md`: Phase 4 상세 계획

### 완료 문서
- `PHASE1_SUMMARY.md`: Phase 1 완료 보고서
- `PHASE2_COMPLETE.md`: Phase 2 완료 보고서

### 개발 가이드
- `CLAUDE.md`: 프로젝트 전체 개발 가이드 (★ 필독)
- `README.md`: 설치 및 사용법
- `MUSIC_GUIDE.md`: BGM 사용 가이드

### API 문서
- Backend API Docs: http://localhost:8000/docs
- 8개 엔드포인트: /api/topics, /api/scripts, /api/videos, /api/jobs, /api/accounts

---

## 🚀 다음 작업 시작 방법

### Option 1: Phase 3 시작
```
Phase 3 작업 시작해줘. UPGRADE_PHASE3.md 기준으로 진행하고,
중간중간 커밋 푸시 및 작업 내역 기록해줘.
```

### Option 2: 특정 기능 작업
```
{기능명} 구현해줘. 예: "계정별 설정 오버라이드 기능 추가해줘"
```

### Option 3: 버그 수정
```
{파일명}:{라인번호}에서 {문제} 발생. 수정해줘.
```

### Option 4: 테스트
```
Phase 2 전체 파이프라인 테스트 해줘. BGM + 템플릿 포함.
```

---

## 🛠️ 개발 환경 설정

### Backend 서버 시작
```bash
cd backend
python main.py
# http://localhost:8000
```

### Frontend 서버 시작
```bash
cd frontend
npm run dev
# http://localhost:3000
```

### CLI 스크립트
```bash
# 가상환경 활성화
venv\Scripts\activate  # Windows

# 자동 영상 생성
python scripts/auto_create.py --topic "주제" --format shorts

# 수동 업로드
python scripts/manual_upload.py --video output/video.mp4 --interactive

# BGM 설정
python scripts/setup_bgm.py --stats
```

---

## 📦 핵심 모듈 구조

```
core/
  ├── planner.py          # AI 스크립트 생성 (Phase 2: 시간 검증 추가)
  ├── asset_manager.py    # 에셋 수집 (Phase 2: BGM 통합)
  ├── editor.py           # 영상 편집 (Phase 2: 템플릿 & BGM 믹싱)
  ├── uploader.py         # YouTube 업로드
  ├── orchestrator.py     # 파이프라인 관리
  └── bgm_manager.py      # BGM 관리 (Phase 2 신규)

backend/
  ├── main.py            # FastAPI 앱
  ├── database.py        # DB 세션 (Phase 1)
  ├── models.py          # ORM 모델 (Phase 1)
  ├── schemas.py         # Pydantic 스키마 (Phase 1)
  ├── scheduler.py       # 스케줄러 (Phase 4)
  ├── workers.py         # 백그라운드 워커 (Phase 4)
  └── routers/
      ├── accounts.py    # Account CRUD API (Phase 1)
      └── tts.py         # TTS 미리듣기 API (Phase 3)

scripts/
  ├── manual_upload.py   # 수동 업로드 (Phase 2)
  └── setup_bgm.py       # BGM 설정 (Phase 2)

templates/
  ├── basic.json         # 기본 템플릿 (Phase 2)
  ├── documentary.json   # 다큐 템플릿 (Phase 2)
  └── entertainment.json # 엔터 템플릿 (Phase 2)
```

---

## 💡 자주 사용하는 명령어

### Git
```bash
git status
git add -A
git commit -m "메시지"
git push origin main
```

### Database Migration (Alembic)
```bash
venv/Scripts/alembic.exe revision --autogenerate -m "메시지"
venv/Scripts/alembic.exe upgrade head
```

### API 테스트
```bash
# 주제 생성
curl -X POST http://localhost:8000/api/topics/generate

# 계정 조회
curl http://localhost:8000/api/accounts/

# 작업 상태 확인
curl -X POST http://localhost:8000/api/jobs/status -d '{"job_id":"job_123"}'
```

---

## 🎯 현재 우선순위

1. **Phase 3 시작** (다음 작업)
2. Frontend UI 업데이트 (Phase 2 기능 반영)
3. 통합 테스트 강화
4. 문서화 보완

---

## 📝 메모

- 최근 커밋: `30d527f` - "docs: Phase 2 완료 보고서 추가"
- Python 3.14 호환성: 모든 의존성 업데이트 완료
- ImageMagick 필요: MoviePy 텍스트 렌더링용
- YouTube OAuth: client_secrets.json 필요 (업로드 시)

---

**마지막 업데이트**: 2025-12-26
**작업자**: Claude Code
**다음 Phase**: Phase 3 (멀티 계정 관리 고도화)
