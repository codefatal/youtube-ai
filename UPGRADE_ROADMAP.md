# YouTube AI 고도화 로드맵

**프로젝트**: YouTube AI v3.0 → v4.0 업그레이드
**시작일**: 2025-12-26
**예상 완료**: 2026-01-31
**목표**: 엔터프라이즈급 다중 계정 관리 및 자동화 시스템 구축

---

## 📊 전체 개요

### 현재 상태 (v3.0)
- ✅ AI 기반 콘텐츠 생성 (Gemini)
- ✅ 스톡 영상 수집 (Pexels, Pixabay)
- ✅ TTS 음성 생성 (gTTS, ElevenLabs)
- ✅ 영상 편집 및 합성 (MoviePy)
- ✅ YouTube 업로드 (OAuth 2.0)
- ✅ 파이프라인 자동화 (Orchestrator)
- ✅ GitHub Actions 스케줄링

### 업그레이드 목표 (v4.0)
- 🎯 **멀티 계정 관리**: 여러 YouTube 채널 동시 운영
- 🎯 **데이터베이스 도입**: SQLite/SQLAlchemy ORM
- 🎯 **고급 미디어 기능**: BGM 자동 매칭, 템플릿 시스템
- 🎯 **TTS 고도화**: ElevenLabs 상세 제어, 미리듣기
- 🎯 **자동 스케줄링**: APScheduler 기반 백그라운드 작업
- 🎯 **현대적 UI**: 다크 모드 대시보드, 계정별 설정

---

## 🗺️ 6단계 업그레이드 계획

### Phase 1: 백엔드 구조 개편 및 DB 도입 ✨
**예상 기간**: 1주 (2025-12-26 ~ 2026-01-02)
**담당 모듈**: `backend/`, `config/`, `data/`

#### 주요 작업
1. SQLAlchemy ORM 도입
2. Account 테이블 (멀티 계정)
3. AccountSettings 테이블 (계정별 설정)
4. JobHistory 테이블 (작업 이력)
5. REST API 엔드포인트 (CRUD)

#### 산출물
- `backend/database.py` - DB 연결
- `backend/models.py` - ORM 모델
- `backend/routers/accounts.py` - API 라우터
- `alembic/` - 마이그레이션

#### 상세 문서
→ [UPGRADE_PHASE1.md](./UPGRADE_PHASE1.md)

---

### Phase 2: 미디어 엔진 고도화 🎨
**예상 기간**: 1.5주 (2026-01-03 ~ 2026-01-12)
**담당 모듈**: `core/asset_manager.py`, `core/editor.py`, `core/planner.py`

#### 주요 작업
1. BGM 매니저 (분위기별 자동 매칭)
2. 쇼츠 템플릿 시스템 (JSON 기반)
3. 영상 길이 정확도 개선
4. 수동 영상 업로드 기능

#### 산출물
- `core/bgm_manager.py`
- `templates/shorts/*.json` (3종)
- `assets/music/` (무료 음원 DB)

#### 상세 문서
→ [UPGRADE_PHASE2.md](./UPGRADE_PHASE2.md)

---

### Phase 3: ElevenLabs TTS 고도화 🗣️
**예상 기간**: 0.5주 (2026-01-13 ~ 2026-01-16)
**담당 모듈**: `core/asset_manager.py` (TTS 부분)

#### 주요 작업
1. Stability, Similarity Boost, Style 파라미터
2. TTS 미리듣기 API
3. 해시 기반 스마트 캐싱
4. AccountSettings 연동

#### 산출물
- `backend/routers/tts.py` (미리듣기 API)
- 업데이트된 `_generate_elevenlabs()` 메소드

#### 상세 문서
→ [UPGRADE_PHASE3.md](./UPGRADE_PHASE3.md)

---

### Phase 4: 스케줄링 및 자동화 시스템 🤖
**예상 기간**: 1주 (2026-01-17 ~ 2026-01-23)
**담당 모듈**: `backend/scheduler.py`

#### 주요 작업
1. APScheduler 도입
2. 계정별 스케줄 관리
3. 자동 생성 및 업로드 Worker
4. 작업 이력 로깅

#### 산출물
- `backend/scheduler.py`
- `backend/workers.py`
- 업데이트된 `main.py` (스케줄러 통합)

#### 상세 문서
→ [UPGRADE_PHASE4.md](./UPGRADE_PHASE4.md)

---

### Phase 5: 프론트엔드 UI/UX 전면 개편 🖥️
**예상 기간**: 1.5주 (2026-01-24 ~ 2026-01-30)
**담당 모듈**: `frontend/`

#### 주요 작업
1. 계정 선택 사이드바
2. 영상 생성 페이지 (TTS 설정, 템플릿 선택)
3. 계정 관리 페이지
4. 다크 모드 디자인

#### 산출물
- `frontend/app/accounts/` (계정 관리)
- `frontend/app/create/` (영상 생성 개선)
- `frontend/components/AccountSidebar.tsx`
- 업데이트된 CSS/Tailwind

#### 상세 문서
→ [UPGRADE_PHASE5.md](./UPGRADE_PHASE5.md)

---

### Phase 6: 통합 테스트 및 마무리 🧪
**예상 기간**: 0.5주 (2026-01-31)
**담당 모듈**: `tests/`

#### 주요 작업
1. API 테스트 코드
2. 전체 파이프라인 점검
3. README 업데이트
4. 배포 준비

#### 산출물
- `tests/test_accounts.py`
- `tests/test_tts_preview.py`
- `tests/test_integration_v4.py`
- 업데이트된 `README.md`

#### 상세 문서
→ [UPGRADE_PHASE6.md](./UPGRADE_PHASE6.md)

---

## 📅 타임라인

```
2025-12-26 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2026-01-31

Phase 1: DB 도입        [████████]
Phase 2: 미디어 엔진   [████████████]
Phase 3: TTS 고도화           [████]
Phase 4: 스케줄링                  [████████]
Phase 5: 프론트엔드                      [████████████]
Phase 6: 테스트                                  [████]
```

---

## 🎯 Phase별 우선순위

| Phase | 중요도 | 난이도 | 의존성 |
|-------|--------|--------|--------|
| 1 | ⭐⭐⭐⭐⭐ | 🔥🔥🔥 | 없음 |
| 2 | ⭐⭐⭐⭐ | 🔥🔥🔥 | Phase 1 |
| 3 | ⭐⭐⭐ | 🔥🔥 | Phase 1 |
| 4 | ⭐⭐⭐⭐⭐ | 🔥🔥🔥🔥 | Phase 1, 2 |
| 5 | ⭐⭐⭐⭐ | 🔥🔥 | Phase 1, 2, 3 |
| 6 | ⭐⭐⭐ | 🔥 | All |

---

## 🔧 기술 스택 변경

### 추가되는 기술
- **SQLAlchemy**: ORM
- **Alembic**: DB 마이그레이션
- **APScheduler**: 백그라운드 작업 스케줄링
- **Pydantic v2**: 향상된 데이터 검증
- **Tailwind CSS**: 현대적 UI (이미 사용 중)

### 유지되는 기술
- **FastAPI**: 백엔드 프레임워크
- **Next.js 14**: 프론트엔드 프레임워크
- **MoviePy 2.x**: 영상 편집
- **ElevenLabs**: TTS
- **Gemini**: AI 엔진

---

## 📝 작업 시작 방법

### 1. 새 세션에서 시작할 때

```bash
# 1. 저장소 클론 및 브랜치 생성
git clone https://github.com/codefatal/youtube-ai.git
cd youtube-ai
git checkout -b upgrade/phase-1

# 2. 환경 설정
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt

# 3. Phase 문서 읽기
cat UPGRADE_PHASE1.md
```

### 2. Phase별 작업 순서

1. **Phase 문서 읽기**: `UPGRADE_PHASE*.md` 읽고 요구사항 파악
2. **현재 코드 분석**: 해당 모듈 구조 파악
3. **작업 수행**: Phase 문서의 체크리스트 따라 진행
4. **테스트**: 각 단계마다 동작 검증
5. **커밋 및 푸시**: Phase 완료 후 커밋
6. **다음 Phase**: 다음 Phase 문서로 이동

### 3. AI 에이전트 활용

Claude Code나 Gemini CLI에 다음과 같이 요청:

```
UPGRADE_PHASE1.md 파일을 읽고, Phase 1 작업을 시작해줘.
현재 프로젝트 구조를 먼저 분석하고, 체크리스트를 따라 진행해줘.
```

---

## ⚠️ 주의사항

### 1. 브랜치 전략
- 각 Phase마다 별도 브랜치 생성 (`upgrade/phase-1`, `upgrade/phase-2`, ...)
- Phase 완료 후 `main`에 PR
- 충돌 발생 시 최신 `main` 브랜치 merge

### 2. 하위 호환성
- 기존 v3.0 API는 `/api/v3/` 경로로 유지
- 새 API는 `/api/v4/` 경로 사용
- 점진적 마이그레이션 지원

### 3. 데이터 마이그레이션
- `job_history.json` → DB 마이그레이션 스크립트 제공
- 백업 필수: `cp data/job_history.json data/job_history.json.backup`

### 4. 환경변수
- `.env.example` 업데이트 필수
- 새 환경변수 추가 시 README에 문서화

---

## 📊 진행 상황 추적

| Phase | 상태 | 시작일 | 완료일 | 담당자 | 비고 |
|-------|------|--------|--------|--------|------|
| Phase 1 | ⏳ 대기 | - | - | - | - |
| Phase 2 | ⏳ 대기 | - | - | - | - |
| Phase 3 | ⏳ 대기 | - | - | - | - |
| Phase 4 | ⏳ 대기 | - | - | - | - |
| Phase 5 | ⏳ 대기 | - | - | - | - |
| Phase 6 | ⏳ 대기 | - | - | - | - |

**범례**:
- ⏳ 대기
- 🔄 진행 중
- ✅ 완료
- ⚠️ 블로킹
- ❌ 취소

---

## 🎯 성공 기준

### Phase 1 완료 조건
- [ ] SQLite DB 생성 확인
- [ ] Account CRUD API 작동
- [ ] Alembic 마이그레이션 성공

### Phase 2 완료 조건
- [ ] BGM 자동 매칭 작동
- [ ] 템플릿 3종 적용 확인
- [ ] 영상 길이 정확도 95% 이상

### Phase 3 완료 조건
- [ ] TTS 파라미터 조절 작동
- [ ] 미리듣기 API 응답 1초 이내
- [ ] 캐싱으로 API 호출 50% 감소

### Phase 4 완료 조건
- [ ] 스케줄러 24시간 안정 동작
- [ ] 자동 업로드 100% 성공률
- [ ] 작업 이력 DB 저장 확인

### Phase 5 완료 조건
- [ ] 계정 선택 UI 작동
- [ ] 다크 모드 적용
- [ ] 모바일 반응형 지원

### Phase 6 완료 조건
- [ ] 테스트 커버리지 80% 이상
- [ ] README 최신화
- [ ] 배포 가능 상태

---

## 📚 참고 문서

- [PROMPTS.md](./PROMPTS.md) - 원본 고도화 계획
- [REFACTOR_PLAN.md](./REFACTOR_PLAN.md) - v3.0 리팩토링 계획
- [README.md](./README.md) - 프로젝트 메인 문서
- [CLAUDE.md](./CLAUDE.md) - 개발자 가이드

---

## 💬 문의 및 피드백

- **GitHub Issues**: https://github.com/codefatal/youtube-ai/issues
- **Discussions**: https://github.com/codefatal/youtube-ai/discussions

---

**Last Updated**: 2025-12-26
**Version**: 1.0
**Status**: Planning
