# YouTube AI 프로젝트 리팩토링 계획

## 프로젝트 방향 전환

**기존**: 해외 쇼츠 다운로드 → 번역 → 재업로드 (저작권 문제)
**신규**: AI 기반 독창적 콘텐츠 자동 생성 (법적 안정성 확보)

---

## 새로운 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    YouTube AI v3.0                          │
│              AI-Powered Original Content Creator            │
└─────────────────────────────────────────────────────────────┘

1. PLANNER (기획 모듈)
   ├─ AI 주제 생성 (Gemini/Claude)
   ├─ 스크립트 작성
   └─ 키워드 추출

2. ASSET MANAGER (소재 수집 모듈)
   ├─ 무료 스톡 영상 (Pexels/Pixabay API)
   ├─ AI TTS (ElevenLabs/Google Cloud TTS)
   └─ 배경 음악 (기존 music_library 활용)

3. EDITOR (편집 모듈)
   ├─ MoviePy 기반 영상 합성
   ├─ 자막 생성 및 싱크
   └─ 효과 및 트랜지션

4. UPLOADER (업로드 모듈)
   ├─ YouTube Data API v3
   ├─ 메타데이터 최적화 (SEO)
   └─ 예약 업로드

5. ORCHESTRATOR (오케스트레이터)
   └─ 전체 파이프라인 관리 및 상태 추적
```

---

## 리팩토링 단계별 체크리스트

### Phase 1: 기반 구조 설계 ✅ (이번 세션)
- [x] 리팩토링 계획 문서 작성
- [x] 작업 흐름도 작성
- [x] 진행 상황 추적 시스템 설계
- [ ] 새로운 디렉토리 구조 설계
- [ ] 데이터 모델 정의

### Phase 2: Planner 모듈 구현
- [ ] AI 프롬프트 템플릿 작성
- [ ] 주제 생성 로직 구현
- [ ] 스크립트 생성 및 JSON 파싱
- [ ] 키워드 추출 알고리즘
- [ ] 테스트 및 검증

### Phase 3: Asset Manager 구현
- [ ] Pexels API 연동
- [ ] Pixabay API 연동
- [ ] 키워드 기반 영상 검색
- [ ] 자동 다운로드 및 캐싱
- [ ] AI TTS 통합 (ElevenLabs 우선, Google Cloud TTS 폴백)

### Phase 4: Editor 모듈 개선
- [ ] MoviePy 설정 최적화 (ImageMagick 경로 등)
- [ ] 멀티스레딩 지원
- [ ] 자막 애니메이션 추가
- [ ] 트랜지션 효과
- [ ] 성능 개선 (해상도 고정, threads 옵션)

### Phase 5: Uploader 모듈 구현
- [ ] YouTube Data API v3 연동 확인
- [ ] 메타데이터 자동 생성 (제목, 설명, 태그)
- [ ] SEO 최적화 로직
- [ ] 예약 업로드 기능
- [ ] 업로드 실패 재시도 로직

### Phase 6: Orchestrator 구현
- [ ] 파이프라인 상태 머신 설계
- [ ] 작업 큐 관리
- [ ] 진행 상황 실시간 추적
- [ ] 에러 핸들링 및 롤백
- [ ] 로깅 시스템 개선

### Phase 7: 자동화 및 스케줄링
- [ ] GitHub Actions 워크플로우 작성
- [ ] 로컬 스케줄링 설정 (crontab/Task Scheduler)
- [ ] Google Sheets CMS 연동
- [ ] 환경 변수 관리 개선

### Phase 8: 테스트 및 최적화 ✅ (완료)
- [x] 통합 테스트 (test_integration.py)
- [x] 성능 벤치마크 (scripts/benchmark.py)
- [x] 에러 케이스 처리 (test_error_cases.py)
- [x] 문서화 업데이트

---

## 새로운 디렉토리 구조 (제안)

```
youtube-ai/
├── core/                    # 핵심 엔진
│   ├── planner.py          # AI 기획 모듈
│   ├── asset_manager.py    # 소재 관리
│   ├── editor.py           # 영상 편집
│   ├── uploader.py         # 업로드
│   └── orchestrator.py     # 파이프라인 관리
│
├── providers/              # 외부 API 연동
│   ├── ai/
│   │   ├── gemini.py
│   │   └── claude.py
│   ├── stock/
│   │   ├── pexels.py
│   │   └── pixabay.py
│   └── tts/
│       ├── elevenlabs.py
│       └── google_tts.py
│
├── utils/                  # 유틸리티
│   ├── video_utils.py
│   ├── text_utils.py
│   └── state_manager.py   # 상태 추적
│
├── templates/              # 프롬프트 템플릿
│   ├── script_prompts/
│   └── metadata_prompts/
│
├── config/                 # 설정 파일
│   ├── default.yaml
│   └── production.yaml
│
├── workflows/              # GitHub Actions
│   └── auto_create.yml
│
├── .refactor_state.json   # 진행 상황 추적
└── REFACTOR_PLAN.md       # 이 문서
```

---

## 진행 상황 추적 시스템

상태 파일 (`.refactor_state.json`)을 사용하여 진행 상황을 저장합니다.

```json
{
  "version": "3.0.0-alpha",
  "current_phase": "Phase 1",
  "last_updated": "2025-12-22T15:00:00Z",
  "completed_tasks": [
    "리팩토링 계획 문서 작성",
    "작업 흐름도 작성"
  ],
  "current_task": "디렉토리 구조 설계",
  "blocked_tasks": [],
  "notes": [
    "토큰 사용률 47% - Phase 1 완료 후 다음 세션 진행",
    "기존 코드 백업 완료"
  ]
}
```

---

## 마이그레이션 전략

### 기존 코드 유지
- `local_cli/` → `legacy/` 로 이동 (참고용)
- 기존 Web UI는 유지 (관리 인터페이스로 활용)

### 점진적 전환
1. **Phase 1-2**: 새로운 Planner 모듈 독립 실행
2. **Phase 3**: Asset Manager 통합
3. **Phase 4-5**: Editor + Uploader 통합
4. **Phase 6**: 전체 파이프라인 연결
5. **Phase 7-8**: 자동화 및 최적화

---

## 기술 스택 변경

### 교체
- ~~`pytube`~~ → **`yt-dlp`** (안정성)
- 기존 하드코딩 자막 방식 → **AI 스크립트 기반**

### 추가
- **Pexels API** (무료 스톡 영상)
- **Pixabay API** (무료 스톡 영상)
- **ElevenLabs API** (고품질 TTS)
- **GitHub Actions** (자동화)

### 유지
- **Gemini API** (AI 엔진)
- **MoviePy** (영상 편집)
- **FastAPI + Next.js** (관리 UI)
- **YouTube Data API v3** (업로드)

---

## 주요 개선 포인트

### 1. 법적 안정성
- ✅ 저작권 프리 소재만 사용
- ✅ AI 생성 스크립트 (독창성)
- ✅ 원본 콘텐츠로 분류

### 2. 기술적 안정성
- ✅ yt-dlp로 안정성 향상
- ✅ JSON 파싱 오류 방지
- ✅ ImageMagick 설정 자동화

### 3. 자동화
- ✅ GitHub Actions 스케줄링
- ✅ Google Sheets CMS
- ✅ 상태 추적 시스템

### 4. 확장성
- ✅ 모듈화된 아키텍처
- ✅ 다양한 AI 프로바이더 지원
- ✅ 다양한 TTS 엔진 지원

---

## 다음 세션 시작 방법

### 토큰 만료 또는 다른 PC에서 작업 시

1. **이 문서 읽기**: `REFACTOR_PLAN.md`
2. **상태 확인**: `.refactor_state.json` 체크
3. **다음 작업 확인**: 체크리스트에서 다음 단계 찾기
4. **Claude Code에 요청**:
   ```
   "REFACTOR_PLAN.md의 Phase X 작업을 계속 진행해주세요.
   현재 .refactor_state.json 상태를 확인하고 다음 작업을 시작해주세요."
   ```

---

## 참고 자료

- **YouTube 자동화 예제**: https://www.youtube.com/watch?v=mkZsaDA2JnA
- **Pexels API 문서**: https://www.pexels.com/api/documentation/
- **ElevenLabs API**: https://elevenlabs.io/docs
- **GitHub Actions Cron**: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule

---

## 예상 일정

- **Phase 1**: 설계 (완료)
- **Phase 2-3**: Planner + Asset Manager (2-3 세션)
- **Phase 4-5**: Editor + Uploader (2-3 세션)
- **Phase 6**: Orchestrator (1-2 세션)
- **Phase 7-8**: 자동화 + 테스트 (1-2 세션)

**총 예상**: 8-12 Claude Code 세션

---

## 중요 주의사항

⚠️ **기존 코드 백업**: 새로운 구조로 전환하기 전에 현재 코드를 백업하세요.
⚠️ **점진적 마이그레이션**: 한 번에 모든 것을 바꾸지 말고 모듈별로 진행하세요.
⚠️ **테스트**: 각 Phase마다 반드시 테스트를 수행하세요.
⚠️ **문서화**: 각 모듈의 사용법을 README에 추가하세요.
