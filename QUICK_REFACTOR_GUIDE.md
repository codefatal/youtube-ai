# 🚀 리팩토링 빠른 시작 가이드

## 다음 세션 시작 시 (토큰 만료 또는 새 PC)

### 1️⃣ 즉시 실행할 명령어

```bash
# 상태 확인
cat .refactor_state.json

# 계획 문서 확인
cat REFACTOR_PLAN.md

# 최근 완료된 Phase 요약 확인
ls PHASE*.md
```

### 2️⃣ Claude Code에 이렇게 요청

```
안녕하세요! YouTube AI 프로젝트 리팩토링을 계속 진행하려고 합니다.

1. .refactor_state.json 파일을 읽고 현재 진행 상황을 확인해주세요.
2. REFACTOR_PLAN.md의 다음 Phase 작업을 시작해주세요.
3. 작업 완료 후 .refactor_state.json을 업데이트해주세요.
```

---

## 현재 상태 (2025-12-23)

### ✅ 완료된 작업
- ✅ Phase 1: 기반 구조 설계 (100%)
- ✅ Phase 2: Planner 모듈 (100%)
- ✅ Phase 3: Asset Manager (100%)
- ✅ Phase 4: Editor 모듈 (100%)
- ✅ Phase 5: Uploader 모듈 (100%)
- ✅ Phase 6: Orchestrator (100%)
- ✅ Phase 7: 자동화 및 스케줄링 (100%)

### 🔄 진행 중
- **Phase 8**: 테스트 및 최적화

### 📋 다음 작업
1. 통합 테스트 작성
2. 성능 벤치마크
3. 에러 케이스 처리
4. 문서화 최종 업데이트

---

## Phase별 체크포인트

### Phase 1: 기반 구조 설계 ✅
```bash
# 진행률: 100%
✅ 리팩토링 계획 문서
✅ 디렉토리 구조
✅ 데이터 모델 (15개 Pydantic 모델)
✅ 설정 파일
```

### Phase 2: Planner 모듈 ✅
```bash
# 진행률: 100%
✅ AI 프롬프트 템플릿
✅ Gemini API wrapper
✅ 주제 생성 로직
✅ 스크립트 JSON 파싱
✅ 키워드 추출
```

### Phase 3: Asset Manager ✅
```bash
# 진행률: 100%
✅ Pexels API 연동
✅ Pixabay API 연동
✅ gTTS 통합
✅ 자동 다운로드 및 캐싱
```

### Phase 4: Editor 모듈 ✅
```bash
# 진행률: 100%
✅ MoviePy 2.x 설정
✅ 영상 합성 로직
✅ 자막 생성 및 싱크
✅ 트랜지션 효과
```

### Phase 5: Uploader 모듈 ✅
```bash
# 진행률: 100%
✅ YouTube Data API v3 연동
✅ OAuth 2.0 인증
✅ 메타데이터 자동 생성
✅ SEO 최적화
✅ 예약 업로드
✅ 업로드 실패 재시도
```

### Phase 6: Orchestrator ✅
```bash
# 진행률: 100%
✅ 파이프라인 상태 머신
✅ 작업 큐 관리
✅ 진행 상황 실시간 추적
✅ 에러 핸들링 및 롤백
✅ 로깅 시스템
```

### Phase 7: 자동화 및 스케줄링 ✅
```bash
# 진행률: 100%
✅ GitHub Actions 워크플로우
✅ 로컬 스케줄링 스크립트
✅ 환경 변수 관리
✅ 자동 실행 스크립트
```

### Phase 8: 테스트 및 최적화 ⏳
```bash
# 진행률: 0%
⏳ 통합 테스트
⏳ 성능 벤치마크
⏳ 에러 케이스 처리
⏳ 문서화 업데이트
```

---

## 긴급 참조

### API 키 설정

`.env` 파일 (`.env.example` 참고):

```env
# 필수
GEMINI_API_KEY=your_key_here
PEXELS_API_KEY=your_key_here  # 또는 PIXABAY_API_KEY

# 선택
ANTHROPIC_API_KEY=your_key_here
PIXABAY_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here
```

### 빠른 테스트

```bash
# 1. Planner 테스트
python tests/test_planner.py

# 2. Asset Manager 테스트
python tests/test_asset_manager.py

# 3. Editor 테스트
python tests/test_editor.py

# 4. Uploader 테스트
python tests/test_uploader.py

# 5. Orchestrator 테스트
python tests/test_orchestrator.py

# 6. 전체 파이프라인 테스트 (수동 실행)
python scripts/auto_create.py --topic "테스트 주제" --no-upload
```

---

## 사용 방법

### 1. 자동 콘텐츠 생성 (CLI)

```bash
# 기본 사용
python scripts/auto_create.py \
  --topic "강아지 훈련 팁" \
  --format shorts \
  --duration 60 \
  --upload

# AI가 주제 자동 생성
python scripts/auto_create.py --upload
```

### 2. 로컬 스케줄러 (매일 자동 실행)

```bash
# 스케줄러 시작 (매일 오전 9시 실행)
python scripts/schedule_local.py

# 테스트 실행
python scripts/schedule_local.py --test
```

### 3. Python 코드로 사용

```python
from core.orchestrator import ContentOrchestrator
from core.models import VideoFormat

orchestrator = ContentOrchestrator()

job = orchestrator.create_content(
    topic="강아지 훈련 팁",
    video_format=VideoFormat.SHORTS,
    upload=True
)

print(f"완료: {job.output_video_path}")
print(f"YouTube: {job.upload_result.url}")
```

---

## GitHub Actions (자동 실행)

### Secrets 설정

GitHub Repository → Settings → Secrets and variables → Actions

다음 secrets 추가:
- `GEMINI_API_KEY`
- `PEXELS_API_KEY`
- `PIXABAY_API_KEY` (선택)
- `YOUTUBE_API_KEY` (선택)

### 수동 실행

GitHub → Actions → "Auto Create YouTube Content" → Run workflow

### 스케줄 실행

매일 오전 9시 (KST) 자동 실행

---

## 작업 원칙

1. **토큰 효율성**: 큰 코드 작성보다 계획과 설계 우선
2. **점진적 마이그레이션**: 기존 코드를 한 번에 바꾸지 않음
3. **상태 추적**: 매 작업 후 `.refactor_state.json` 업데이트
4. **문서화**: 새로운 모듈은 반드시 README 작성
5. **테스트**: Phase별 완료 시 통합 테스트

---

## 긴급 복구

### 실수로 파일 삭제 시
```bash
git checkout REFACTOR_PLAN.md
git checkout .refactor_state.json
git checkout QUICK_REFACTOR_GUIDE.md
```

### 원본 코드 복구
```bash
# 기존 코드는 git에 저장되어 있음
git log --oneline
git checkout [commit-hash] -- [file]
```

---

## 현재 세션 통계

- **토큰 사용**: ~55%
- **완료 Phase**: 7/8
- **예상 남은 세션**: 1-2회
- **현재 브랜치**: main
- **전체 완성도**: 87.5%

---

## 다음 세션 목표

✅ Phase 7 완료 (자동화 및 스케줄링)
🎯 Phase 8 시작 (테스트 및 최적화)
🎯 프로젝트 최종 완료!

---

**마지막 업데이트**: 2025-12-23
**다음 작업자**: 이 가이드를 Claude Code에 보여주세요!
**GitHub**: https://github.com/codefatal/youtube-ai
