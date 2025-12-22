# 🚀 리팩토링 빠른 시작 가이드

## 다음 세션 시작 시 (토큰 만료 또는 새 PC)

### 1️⃣ 즉시 실행할 명령어

```bash
# 상태 확인
cat .refactor_state.json

# 계획 문서 확인
cat REFACTOR_PLAN.md
```

### 2️⃣ Claude Code에 이렇게 요청

```
안녕하세요! YouTube AI 프로젝트 리팩토링을 계속 진행하려고 합니다.

1. .refactor_state.json 파일을 읽고 현재 진행 상황을 확인해주세요.
2. REFACTOR_PLAN.md의 다음 Phase 작업을 시작해주세요.
3. 작업 완료 후 .refactor_state.json을 업데이트해주세요.
```

---

## 현재 상태 (2025-12-22)

### ✅ 완료된 작업
- 리팩토링 계획 문서 작성
- 작업 흐름도 작성
- 진행 상황 추적 시스템 설계

### 🔄 진행 중
- **Phase 1**: 기반 구조 설계

### 📋 다음 작업
1. 새로운 디렉토리 구조 설계
2. 데이터 모델 정의
3. Phase 2: Planner 모듈 구현 시작

---

## Phase별 체크포인트

### Phase 1: 기반 구조 설계 (현재)
```bash
# 진행률: 60%
✅ 리팩토링 계획 문서
✅ 작업 흐름도
✅ 진행 상황 추적
⏳ 디렉토리 구조
⏳ 데이터 모델
```

### Phase 2: Planner 모듈
```bash
# 목표: AI 기반 주제 및 스크립트 생성
- AI 프롬프트 템플릿
- 주제 생성 로직
- 스크립트 JSON 파싱
- 키워드 추출
```

### Phase 3: Asset Manager
```bash
# 목표: 무료 스톡 영상 + AI TTS
- Pexels API 연동
- Pixabay API 연동
- ElevenLabs TTS
- 자동 다운로드
```

---

## 긴급 참조

### API 키 필요 (나중에 추가)
```env
# Pexels
PEXELS_API_KEY=

# Pixabay
PIXABAY_API_KEY=

# ElevenLabs
ELEVENLABS_API_KEY=

# 기존 (유지)
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
YOUTUBE_API_KEY=
```

### 새로운 패키지 설치 예정
```bash
pip install yt-dlp
pip install requests  # API 호출
pip install pyyaml    # 설정 파일
```

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

- **토큰 사용**: ~50%
- **완료 Phase**: 0.6/8
- **예상 남은 세션**: 7-11회
- **현재 브랜치**: main

---

## 다음 세션 목표

✅ Phase 1 완료 (디렉토리 구조 + 데이터 모델)
🎯 Phase 2 시작 (Planner 모듈 초안)

---

**마지막 업데이트**: 2025-12-22 15:55 KST
**다음 작업자**: 이 가이드를 Claude Code에 보여주세요!
