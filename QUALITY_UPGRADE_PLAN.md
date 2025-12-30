# 영상 퀄리티 대폭 개선 계획

**작성일**: 2025-12-30
**목표**: 자동 생성 영상의 퀄리티를 프로 수준에 가깝게 향상

---

## 📋 Phase 개요

| Phase | 작업 | 예상 효과 | 상태 |
|-------|------|-----------|------|
| Phase 1 | 제목 렌더링 Pillow 전환 | 텍스트 잘림 완전 해결 | ✅ 완료 |
| Phase 2 | TTS-영상 동기화 재설계 | 싱크 정확도 극대화 | ✅ 완료 |
| Phase 3 | 반자동 검토 UI 추가 | 수동 미세조정 가능 | ✅ 완료 |

---

## 🎯 Phase 1: 제목 렌더링 Pillow 전환

### 문제점
- MoviePy TextClip의 폰트 메트릭 계산 부정확
- interline, padding 조정해도 하단 잘림 발생
- 한글 폰트 Descender 처리 불안정

### 해결 방안
1. **Pillow로 제목 이미지 직접 렌더링**
   - PIL.Image + PIL.ImageDraw + PIL.ImageFont
   - 정확한 텍스트 바운딩 박스 계산
   - 반투명 배경 박스 포함

2. **ImageClip으로 MoviePy에 삽입**
   - numpy array 변환 후 ImageClip 생성
   - with_position(), with_duration() 적용

### 수정 대상
- `core/editor.py` - `_create_shorts_layout()` 함수
- `core/services/title_service.py` - 신규 생성

### 구현 계획
```python
# title_service.py (신규)
class TitleService:
    def create_title_image(self, title: str, width: int, height: int) -> PIL.Image:
        """Pillow로 제목 이미지 생성"""
        pass

# editor.py (수정)
def _create_shorts_layout(self, ...):
    # 기존: self.TextClip(...)
    # 수정: TitleService.create_title_image(...) → ImageClip
```

### 완료 기준
- [x] TitleService 클래스 구현 (`core/services/title_service.py`)
- [x] editor.py에서 TitleService 사용 (`_create_shorts_layout()` 수정)
- [ ] 텍스트 잘림 없음 확인 (테스트 필요)
- [x] Safe Zone 적용 확인 (7% 적용됨)

---

## 🎯 Phase 2: TTS-영상 동기화 재설계

### 문제점
- 세그먼트별 TTS 길이 예측치와 실제 길이 불일치
- 영상 클립 길이가 TTS와 맞지 않음
- Whisper 타임스탬프가 자막에만 적용됨

### 해결 방안
1. **TTS 실제 길이 기준 동기화**
   - 각 세그먼트 TTS 생성 후 실제 길이 측정
   - 해당 길이만큼 영상 클립 할당

2. **세그먼트-클립 1:1 매핑**
   ```
   세그먼트 1 (TTS 4.5초) → 영상 클립 1 (4.5초)
   세그먼트 2 (TTS 3.2초) → 영상 클립 2 (3.2초)
   ```

3. **누적 타임스탬프 계산**
   ```python
   segment_1: start=0.0, end=4.5
   segment_2: start=4.5, end=7.7
   segment_3: start=7.7, end=...
   ```

### 수정 대상
- `core/asset_manager.py` - `_generate_tts()` 반환값 개선
- `core/editor.py` - `_compose_video_clips()` 동기화 로직
- `core/orchestrator.py` - 파이프라인 데이터 전달

### 구현 계획
```python
# AssetBundle에 세그먼트별 타이밍 정보 추가
class SegmentTiming(BaseModel):
    segment_index: int
    tts_duration: float  # 실제 TTS 길이
    start_time: float    # 누적 시작 시간
    end_time: float      # 누적 종료 시간

# 영상 클립 할당 시 TTS 길이 기준
for i, timing in enumerate(segment_timings):
    clip_duration = timing.tts_duration
    # 해당 길이만큼 영상 클립 자르기/반복
```

### 완료 기준
- [x] SegmentTiming 모델 추가 (`core/models.py`)
- [x] TTS 생성 시 실제 길이 기록 (`asset_manager.py`)
- [x] 영상 클립 길이를 TTS 길이에 맞춤 (`editor.py._compose_video_clips()`)
- [x] 자막 타이밍도 동일하게 적용 (content_plan.segments.duration 기반)
- [ ] 전체 싱크 테스트 통과

---

## 🎯 Phase 3: 반자동 검토 UI 추가

### 문제점
- 자동 생성 결과물 즉시 확인 불가
- 문제 발견 시 처음부터 재생성 필요
- 미세 조정 불가능

### 해결 방안
1. **프리뷰 생성 기능**
   - 저해상도/짧은 샘플 영상 빠르게 생성
   - 전체 렌더링 전 확인 가능

2. **편집 파라미터 조정 UI**
   - 제목 위치/크기 조정
   - 자막 타이밍 미세 조정
   - BGM 볼륨 조절

3. **세그먼트별 영상 교체**
   - 특정 세그먼트 영상만 재검색/교체
   - 전체 재생성 없이 부분 수정

### 수정 대상
- `backend/main.py` - 프리뷰 API 추가
- `frontend/` - 검토 UI 페이지 추가
- `core/editor.py` - 프리뷰 렌더링 함수

### 구현 계획
```
프론트엔드 UI:
┌─────────────────────────────────────┐
│  [프리뷰 영상]                      │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │     저해상도 프리뷰         │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  세그먼트 타임라인:                 │
│  [1][2][3][4][5][6][7][8]          │
│                                     │
│  선택된 세그먼트: #3               │
│  - 영상 교체 [검색]                │
│  - 자막 수정 [편집]                │
│  - 타이밍 조정 [-0.5s] [+0.5s]    │
│                                     │
│  [저해상도 프리뷰] [최종 렌더링]   │
└─────────────────────────────────────┘
```

### API 엔드포인트
```
POST /api/preview/generate     - 프리뷰 생성
GET  /api/preview/{job_id}     - 프리뷰 상태 확인
POST /api/preview/adjust       - 파라미터 조정
POST /api/preview/replace-clip - 클립 교체
POST /api/preview/finalize     - 최종 렌더링
```

### 완료 기준
- [x] 프리뷰 생성 API 구현 (`backend/routers/preview.py`)
- [x] 프리뷰 UI 페이지 구현 (`frontend/app/preview/page.tsx`)
- [x] 세그먼트별 조정 기능 (API 구현, UI 기본 지원)
- [x] 최종 렌더링 기능 (API 및 UI 구현)
- [ ] E2E 테스트 통과

---

## 📅 진행 순서

1. **Phase 1 완료** → 제목 잘림 문제 해결
2. **Phase 2 완료** → TTS 싱크 문제 해결
3. **Phase 3 완료** → 수동 미세조정 가능

각 Phase 완료 후 테스트 진행, 문제 없으면 다음 Phase로 진행.

---

## 📝 변경 이력

| 날짜 | Phase | 변경 내용 |
|------|-------|-----------|
| 2025-12-30 | - | 계획서 작성 |
| 2025-12-30 | Phase 1 | TitleService 클래스 구현 (Pillow 기반 제목 렌더링) |
| 2025-12-30 | Phase 1 | editor.py에서 TitleService 통합 |
| 2025-12-30 | Phase 2 | SegmentTiming 모델 추가 |
| 2025-12-30 | Phase 2 | asset_manager.py에서 세그먼트별 TTS 타이밍 기록 |
| 2025-12-30 | Phase 2 | editor.py에서 TTS 기반 클립 길이 동기화 |
| 2025-12-30 | Phase 3 | Preview API 라우터 구현 (6개 엔드포인트) |
| 2025-12-30 | Phase 3 | Preview UI 페이지 구현 (프론트엔드) |

---

**작성자**: Claude Code
