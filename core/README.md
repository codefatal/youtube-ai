# Core Modules

YouTube AI v3.0의 핵심 모듈들입니다.

## 모듈 구성

### `models.py`
- Pydantic 기반 데이터 모델 정의
- 타입 안정성 및 검증 제공
- 모든 모듈에서 공통으로 사용

### `planner.py` (예정)
- AI 기반 콘텐츠 기획
- 주제 생성 및 스크립트 작성
- 키워드 추출

### `asset_manager.py` (예정)
- 무료 스톡 영상 수집 (Pexels/Pixabay)
- AI TTS 음성 생성
- 에셋 다운로드 및 관리

### `editor.py` (예정)
- MoviePy 기반 영상 편집
- 자막 생성 및 싱크
- 트랜지션 효과

### `uploader.py` (예정)
- YouTube Data API v3 연동
- 메타데이터 최적화
- 예약 업로드

### `orchestrator.py` (예정)
- 전체 파이프라인 관리
- 작업 상태 추적
- 에러 핸들링

## 사용 예시

```python
from core.models import ContentPlan, ScriptSegment, VideoFormat

# 콘텐츠 기획 생성
plan = ContentPlan(
    title="강아지와 함께하는 행복한 하루",
    description="강아지와 공원에서 즐거운 시간을 보내는 모습",
    format=VideoFormat.SHORTS,
    segments=[
        ScriptSegment(
            text="강아지는 사람의 가장 좋은 친구입니다.",
            keyword="happy dog playing park"
        )
    ]
)
```

## 개발 상태

- ✅ `models.py` - 완료
- ⏳ `planner.py` - Phase 2
- ⏳ `asset_manager.py` - Phase 3
- ⏳ `editor.py` - Phase 4
- ⏳ `uploader.py` - Phase 5
- ⏳ `orchestrator.py` - Phase 6
