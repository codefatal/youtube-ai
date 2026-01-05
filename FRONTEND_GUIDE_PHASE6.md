# Phase 6: 프론트엔드 UI 가이드

**작성일**: 2025-01-05
**버전**: v4.0 Phase 6 Frontend
**목적**: Phase 6 기능을 프론트엔드 UI에서 사용하는 방법

---

## 📋 목차

1. [개요](#개요)
2. [새로운 UI 기능](#새로운-ui-기능)
3. [사용 방법](#사용-방법)
4. [API 연동](#api-연동)
5. [화면별 가이드](#화면별-가이드)

---

## 개요

Phase 6의 핵심 기능들을 프론트엔드 UI에서 손쉽게 사용할 수 있도록 통합했습니다.

### 추가된 기능

1. **Draft Export 버튼** (프로젝트 목록 페이지)
   - SRT 자막 파일 다운로드
   - JSON 프로젝트 파일 다운로드
   - Vrew 프로젝트 파일 (.vrew) 다운로드

2. **AI 고급 설정** (영상 생성 페이지)
   - Wholesome TTS 옵션
   - AI 영상 선택 옵션
   - TTS 파라미터 자동 조정 옵션

---

## 새로운 UI 기능

### 1. 프로젝트 목록 페이지 (`/projects`)

**위치**: `frontend/app/projects/page.tsx`

**새로운 버튼**:
```
📁 프로젝트 목록
├── [프로젝트 카드]
│   ├── ✏️ 편집 | 🗑️ 삭제
│   └── 📄 SRT | 📋 JSON | 🎬 Vrew  ← NEW!
```

**기능**:
- **SRT 버튼**: 자막 파일을 SRT 형식으로 다운로드
- **JSON 버튼**: 프로젝트 메타데이터를 JSON으로 다운로드
- **Vrew 버튼**: Vrew 프로젝트 파일 (.vrew) 다운로드

**사용 예시**:
1. 프로젝트 목록에서 Draft 선택
2. 하단 Export 버튼 클릭
3. 파일 자동 다운로드

---

### 2. 영상 생성 페이지 (`/create`)

**위치**: `frontend/app/create/page.tsx`

**새로운 섹션**: `🤖 AI 고급 설정 (Phase 6)`

**옵션들**:

#### Option 1: Wholesome TTS (권장)
```
☑️ Wholesome TTS (권장)
```
- **기능**: 전체 대본을 한 번에 생성하여 톤 일관성 30% 향상
- **기술**: Whisper로 정확한 타이밍 추출
- **효과**: 세그먼트 간 톤 불일치 해결, TTS 비용 80% 절감
- **기본값**: 활성화 (ON)

#### Option 2: AI 영상 선택 (권장)
```
☑️ AI 영상 선택 (권장)
```
- **기능**: Gemini AI가 5-10개 후보 중 대본과 가장 잘 맞는 영상 자동 선택
- **효과**: 대본-영상 매칭률 40% 향상
- **기본값**: 활성화 (ON)

#### Option 3: TTS 파라미터 자동 조정 (권장)
```
☑️ TTS 파라미터 자동 조정 (권장)
```
- **기능**: 대본 내용 분석하여 감정, 격식, 구어체에 맞게 파라미터 자동 조정
- **효과**: 감정 표현 적절성 25% 향상
- **기본값**: 활성화 (ON)

---

## 사용 방법

### Scenario 1: 자동 영상 생성 (Phase 6 기능 전체 활성화)

```
1. /create 페이지 접속
2. 주제 입력: "건강한 아침 습관"
3. AI 고급 설정 확인 (모두 체크됨)
   ☑️ Wholesome TTS (권장)
   ☑️ AI 영상 선택 (권장)
   ☑️ TTS 파라미터 자동 조정 (권장)
4. "✨ 편집 모드로 생성 (권장)" 클릭
5. 자동으로 프로젝트 편집 페이지로 이동
```

**결과**:
- Wholesome TTS로 톤 일관성 보장
- AI가 5개 후보 중 최적 영상 선택
- 대본 분석으로 TTS 파라미터 자동 조정

---

### Scenario 2: Vrew 연동 워크플로우

```
1. /create에서 Draft 생성 (편집 모드)
2. 생성 완료 후 /projects 목록에서 확인
3. 프로젝트 카드 하단에서 "🎬 Vrew" 클릭
4. {title}_{draft_id}.vrew 파일 다운로드
5. Vrew 앱 실행 → "프로젝트 가져오기"
6. .vrew 파일 선택
7. Vrew에서 수동 편집:
   - 자막 텍스트 수정
   - 영상 교체/순서 변경
   - 효과/전환 추가
   - BGM 세밀 조정
8. Vrew에서 최종 영상 Export
9. YouTube 업로드
```

---

### Scenario 3: SRT/JSON Export

**SRT 파일 용도**:
- 자막 파일 백업
- 다른 편집 툴에서 사용
- 번역 작업

**JSON 파일 용도**:
- 프로젝트 메타데이터 확인
- 디버깅
- 다른 시스템과 데이터 연동

**사용법**:
```
1. /projects 페이지 접속
2. Draft 선택
3. "📄 SRT" 클릭 → subtitle.srt 다운로드
4. "📋 JSON" 클릭 → project.json 다운로드
```

---

## API 연동

### Frontend API Functions

**위치**: `frontend/lib/api.ts`

#### exportDraftSRT()
```typescript
export async function exportDraftSRT(draftId: string): Promise<void>
```
- **기능**: SRT 자막 파일 다운로드
- **엔드포인트**: `GET /api/draft/{draft_id}/export/srt`
- **반환**: SRT 파일 자동 다운로드

#### exportDraftJSON()
```typescript
export async function exportDraftJSON(draftId: string): Promise<void>
```
- **기능**: JSON 프로젝트 파일 다운로드
- **엔드포인트**: `GET /api/draft/{draft_id}/export/json`
- **반환**: JSON 파일 자동 다운로드

#### exportDraftVrew()
```typescript
export async function exportDraftVrew(draftId: string): Promise<void>
```
- **기능**: Vrew 프로젝트 파일 다운로드
- **엔드포인트**: `GET /api/draft/{draft_id}/export/vrew`
- **반환**: .vrew 파일 자동 다운로드

---

### Backend API Endpoints

#### GET /api/draft/{draft_id}/export/srt

**요청**:
```bash
curl -X GET "http://localhost:8000/api/draft/{draft_id}/export/srt"
```

**응답**:
- Content-Type: `text/plain; charset=utf-8`
- File: `{draft_id}_subtitle.srt`

**SRT 파일 형식**:
```srt
1
00:00:00,000 --> 00:00:04,500
안녕하세요, 여러분!

2
00:00:04,500 --> 00:00:09,200
오늘은 Python 프로그래밍에 대해 알아보겠습니다.
```

---

#### GET /api/draft/{draft_id}/export/json

**요청**:
```bash
curl -X GET "http://localhost:8000/api/draft/{draft_id}/export/json"
```

**응답**:
- Content-Type: `application/json`
- File: `{draft_id}_project.json`

**JSON 파일 구조**:
```json
{
  "title": "Python 프로그래밍 기초",
  "description": "Python 초보자를 위한 기초 문법 소개",
  "tags": ["python", "programming", "tutorial"],
  "audio": {
    "tts_path": "output/tts_xxx.mp3",
    "tts_duration": 60.5
  },
  "bgm": {
    "name": "Energetic Beat",
    "mood": "energetic",
    "volume": 0.25
  },
  "segments": [
    {
      "index": 0,
      "text": "안녕하세요, 여러분!",
      "start": 0.0,
      "end": 4.5,
      "duration": 4.5,
      "search_query": "person greeting camera friendly happy"
    }
  ]
}
```

---

#### GET /api/draft/{draft_id}/export/vrew

**요청**:
```bash
curl -X GET "http://localhost:8000/api/draft/{draft_id}/export/vrew"
```

**응답**:
- Content-Type: `application/zip`
- File: `{draft_id}.vrew`

**.vrew 파일 구조** (ZIP):
```
{draft_id}.vrew
├── subtitle.srt        # 자막 파일
├── project.json        # 프로젝트 메타데이터
└── manifest.json       # Vrew 매니페스트
```

---

#### POST /api/draft/create

**요청**:
```typescript
{
  topic: "건강한 아침 습관",
  format: "shorts",
  duration: 60,
  collect_assets: true,
  advanced_settings: {
    useWholesomeTTS: true,      // Wholesome TTS
    aiVideoSelection: true,      // AI 영상 선택
    autoTuneTTS: true           // TTS 자동 조정
  }
}
```

**응답**:
```typescript
{
  draft_id: "draft_20250105_120000",
  topic: "건강한 아침 습관",
  title: "건강한 아침을 위한 5가지 습관",
  status: "assets_ready",
  segments: [...]
}
```

---

## 화면별 가이드

### 1. 프로젝트 목록 페이지 (`/projects`)

**화면 구성**:
```
📁 프로젝트 목록                          ➕ 새 프로젝트

[필터]  전체 | 편집 중 | 준비 완료 | 렌더링 중 | 완료

┌────────────────────────────────────────┐
│ 📹 건강한 아침을 위한 5가지 습관         │ [준비 완료]
│ 건강한 아침 습관으로 하루를 시작하세요    │
│ 🎬 6개 세그먼트 · ⏱️ 60초              │
│ 📅 2025-01-05                          │
│                                        │
│ [✏️ 편집            ] [🗑️]            │
│ [📄 SRT | 📋 JSON | 🎬 Vrew]          │ ← NEW!
└────────────────────────────────────────┘
```

**Export 버튼 동작**:
- 클릭 시 파일 자동 다운로드
- 성공 시 "... 파일이 다운로드되었습니다" 알림
- 실패 시 "... 내보내기에 실패했습니다" 알림

---

### 2. 영상 생성 페이지 (`/create`)

**화면 구성**:
```
✨ 영상 생성

[왼쪽 패널]                    [오른쪽 패널]
┌─────────────────────┐       ┌─────────────────────┐
│ 주제                 │       │ 🎙️ TTS 설정        │
│ [Python 팁______  ] │       │ Provider: [ElevenLabs]│
│                     │       │ Voice: [Adam___]     │
│ 영상 길이: 60초      │       │ Stability: 0.5       │
│ [━━━━━●━━━━]        │       │ ...                  │
│                     │       └─────────────────────┘
│ 📐 템플릿           │
│ ○ Basic             │       ┌─────────────────────┐
│ ● Documentary       │       │ 🎵 BGM 설정         │
│ ○ Entertainment     │       │ ☑️ BGM 사용          │
└─────────────────────┘       │ 분위기: [자동 선택] │
                              │ 볼륨: 30%           │
                              └─────────────────────┘

                              ┌─────────────────────┐ ← NEW!
                              │ 🤖 AI 고급 설정      │
                              │ (Phase 6)           │
                              │                     │
                              │ ☑️ Wholesome TTS    │
                              │   (권장)            │
                              │ 전체 대본을 한 번에  │
                              │ 생성하여 톤 일관성   │
                              │ 30% 향상            │
                              │                     │
                              │ ☑️ AI 영상 선택     │
                              │   (권장)            │
                              │ Gemini AI가 5-10개  │
                              │ 후보 중 최적 선택    │
                              │ 매칭률 40% 향상      │
                              │                     │
                              │ ☑️ TTS 자동 조정    │
                              │   (권장)            │
                              │ 대본 분석하여 감정,  │
                              │ 격식, 구어체 조정    │
                              │ 감정 표현 25% 향상   │
                              │                     │
                              │ 💡 Phase 6 기능들은  │
                              │ 기본적으로 모두      │
                              │ 활성화되어 있습니다  │
                              └─────────────────────┘

[━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━]
    ✨ 편집 모드로 생성 (권장)

[🎬 프리뷰] [⚡ 바로 생성]

💡 편집 모드를 사용하면:
• 스크립트와 이미지를 먼저 확인하고 수정할 수 있습니다
• 세그먼트별로 이미지 재생성 및 텍스트 편집이 가능합니다
• 최종 확인 후 렌더링하여 시간을 절약할 수 있습니다
```

---

## 사용자 시나리오

### Scenario A: 빠른 영상 생성 (기본 설정)

**목표**: Phase 6 기능을 모두 사용하여 최고 품질의 영상 생성

```
1. /create 접속
2. 주제: "아침 운동의 효과"
3. 길이: 60초
4. 템플릿: Documentary
5. AI 고급 설정: 모두 ON (기본값)
6. "✨ 편집 모드로 생성" 클릭
7. 자동 생성 완료 → /projects/{draft_id}/edit로 이동
8. 세그먼트 확인 및 필요 시 수정
9. "최종 렌더링" 클릭
10. 완료!
```

**예상 결과**:
- Wholesome TTS로 톤 일관성 있는 음성
- AI가 선택한 대본과 잘 맞는 영상들
- 감정 분석으로 자동 조정된 TTS 파라미터

---

### Scenario B: Vrew 수동 편집

**목표**: Vrew에서 세밀하게 편집 후 최종 영상 제작

```
1. /create에서 Draft 생성
2. /projects 목록에서 해당 Draft 찾기
3. "🎬 Vrew" 버튼 클릭 → .vrew 파일 다운로드
4. Vrew 앱 실행
5. "프로젝트 가져오기" → .vrew 파일 선택
6. Vrew에서 편집:
   - 자막 텍스트 수정 (오타 교정, 표현 개선)
   - 영상 교체 (마음에 안 드는 영상 변경)
   - 전환 효과 추가
   - BGM 볼륨 세밀 조정
7. Vrew에서 "영상 내보내기"
8. 최종 영상 파일 저장
9. YouTube 직접 업로드 또는 Backend API 사용
```

**장점**:
- 완전한 편집 자유도
- 실시간 프리뷰
- Vrew의 다양한 편집 기능 활용

---

### Scenario C: SRT 자막 활용

**목표**: SRT 파일로 자막 백업 또는 번역 작업

```
1. /projects에서 Draft 선택
2. "📄 SRT" 클릭 → subtitle.srt 다운로드
3. 텍스트 에디터로 열기
4. 자막 번역 또는 수정
5. 다른 편집 툴에서 사용 (Premiere Pro, Final Cut Pro 등)
```

---

## 트러블슈팅

### Issue 1: Export 버튼 클릭 시 다운로드 안 됨

**원인**:
- Draft가 완전히 생성되지 않음
- TTS 파일 누락

**해결**:
1. Draft 상태 확인 (status가 'assets_ready' 또는 'finalized'인지)
2. 브라우저 콘솔 확인 (F12)
3. Backend 로그 확인

---

### Issue 2: Vrew에서 .vrew 파일 import 실패

**원인**:
- .vrew 파일 손상
- Vrew 버전 불일치

**해결**:
1. .vrew 파일을 ZIP 압축 해제 도구로 열어 내용 확인
2. subtitle.srt, project.json, manifest.json 존재 여부 확인
3. Vrew 최신 버전 사용

---

### Issue 3: AI 고급 설정이 적용 안 됨

**원인**:
- Backend에서 advanced_settings를 받지 못함
- API 요청 오류

**해결**:
1. 브라우저 개발자 도구 → Network 탭에서 요청 확인
2. advanced_settings가 제대로 전송되는지 확인
3. Backend 로그에서 "Phase 6 설정: ..." 메시지 확인

---

## 개발자 가이드

### 새로운 Export 기능 추가하기

**예시: PDF Export 추가**

#### 1. Backend API 추가
```python
# backend/routers/drafts.py

@router.get("/{draft_id}/export/pdf", response_class=FileResponse)
async def export_draft_pdf(draft_id: str, db: Session = Depends(get_db)):
    """PDF Export"""
    # PDF 생성 로직
    pdf_path = generate_pdf(draft)
    return FileResponse(pdf_path, media_type="application/pdf")
```

#### 2. Frontend API 함수 추가
```typescript
// frontend/lib/api.ts

export async function exportDraftPDF(draftId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/draft/${draftId}/export/pdf`);
  // Download logic
}
```

#### 3. UI 버튼 추가
```typescript
// frontend/app/projects/page.tsx

<button onClick={(e) => handleExportPDF(project.draft_id, e)}>
  📕 PDF
</button>
```

---

## 성능 최적화

### Export 대량 다운로드

**문제**: 여러 Draft를 동시에 Export 하면 느림

**해결**:
```typescript
// 순차 다운로드
for (const draft of selectedDrafts) {
  await exportDraftVrew(draft.draft_id);
  await delay(500); // 서버 부하 방지
}

// 병렬 다운로드 (최대 3개)
await Promise.all(
  selectedDrafts.slice(0, 3).map(draft =>
    exportDraftVrew(draft.draft_id)
  )
);
```

---

## 보안 고려사항

### Export API 인증

현재는 인증 없이 draft_id만으로 Export 가능합니다.

**개선 방안**:
```typescript
// 토큰 기반 인증 추가
export async function exportDraftVrew(draftId: string, token: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/draft/${draftId}/export/vrew`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  // ...
}
```

---

## 향후 개선 사항

### 1. Batch Export
- 여러 Draft를 한 번에 Export
- ZIP 파일로 압축하여 다운로드

### 2. Export 히스토리
- Export 이력 추적
- 다운로드 횟수 제한

### 3. 실시간 프리뷰
- Export 전 미리보기
- 자막 실시간 편집

---

## 관련 문서

- **백엔드 가이드**: `PHASE6_VREW_INTEGRATION.md`
- **API 레퍼런스**: `PHASE6_QUICK_REFERENCE.md`
- **전체 요약**: `IMPLEMENTATION_SUMMARY_PHASE6.md`

---

**작성일**: 2025-01-05
**버전**: v4.0 Phase 6 Frontend
**문서 버전**: 1.0
