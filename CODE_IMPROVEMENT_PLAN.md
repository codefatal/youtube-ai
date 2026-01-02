# YouTube AI v4.5 - 품질 혁신 및 인터랙티브 피드백 시스템 구축 계획

**작성일**: 2026-01-02
**목표**: 단순 자동화를 넘어, 사용자가 개입하여 품질을 완성하는 'Human-in-the-Loop' 시스템 구축

---

## 🚀 핵심 개선 전략 (4대 기둥)

### 1. 🎵 BGM 시스템: "On-demand"에서 "Local Library"로 전환
**현재 문제**: 매번 다운로드 시도 → 실패 잦음, 어울리지 않는 곡 선정, 네트워크 지연.
**개선 방안**:
- **로컬 라이브러리 구축**: `assets/bgm/{mood}/` 폴더 구조화 (Happy, Sad, Intense 등).
- **사전 다운로드 스크립트**: YouTube DL이나 수동 파일 추가를 통해 장르별 10~20곡 확보.
- **랜덤 & 셔플 로직**: API 호출 없이 로컬 폴더에서 랜덤 `pick`.
- **오디오 노멀라이즈**: `ffmpeg`를 사용해 미리 모든 음원의 볼륨을 평준화(-14 LUFS).

### 2. 🗣️ TTS & 자막 싱크: "추정(Estimation)"에서 "확정(Exact)"으로
**현재 문제**: 글자 수 기반 추정(`char * 0.17`) 사용 → 말하는 속도 차이로 인해 자막과 오디오가 어긋남.
**개선 방안**:
- **선(先) TTS, 후(後) 영상**: `planner` 단계에서 시간을 확정 짓지 않음.
- **정확한 길이 측정**: TTS 파일 생성 직후 `mutagen`이나 `ffmpeg`로 **밀리초 단위의 정확한 길이(duration)**를 추출.
- **타임라인 강제 동기화**: `ScriptSegment` 객체에 `exact_duration` 필드를 추가하고, `MoviePy` 편집 시 이 값을 **절대 기준**으로 영상 클립 길이를 자름.
- **Whisper 타임스탬프 (옵션)**: 문장 단위가 아닌 단어 단위 싱크가 필요할 경우, 생성된 TTS를 다시 OpenAI Whisper에 넣어 `.srt` 타임스탬프를 역추출.

### 3. 🖼️ 시각적 연관성: "키워드(Keyword)"에서 "비주얼 프롬프트(Visual Prompt)"로
**현재 문제**: 텍스트("도전하세요") → 추상적 키워드("Challenge") → 뜬금없는 영상(산에 오르는 사람 vs 문맥은 다이어트).
**개선 방안**:
- **LLM 역할 분리**: 스크립트 생성 시, 나레이션과 별도로 **"화면 묘사(Visual Description)"** 필드 요청.
    - 예) 나레이션: "꾸준한 운동이 중요해요."
    - 예) 검색어: "Person running in park morning sunlight", "Close up tying running shoes"
- **Fallback 이미지**: Pexels 검색 실패 시, 사전에 준비된 고퀄리티 '추상적 배경(Abstract Motion Background)' 폴더에서 랜덤 사용.

### 4. 🔁 인터랙티브 피드백 루프 (Interactive Feedback Loop)
**현재 문제**: 한 번 생성하면 수정 불가. 마음에 안 들면 처음부터 다시 생성해야 함 (비용/시간 낭비).
**개선 방안**: **"생성(Generate) → 미리보기(Preview) → 수정(Refine) → 렌더링(Render)"** 워크플로우 도입.

#### 🏗️ 아키텍처 변경
1.  **Draft Mode**: 저해상도(480p), 빠른 렌더링으로 '초안' 생성.
2.  **Web UI 수정 기능**:
    - **타임라인 뷰**: 세그먼트별 이미지/영상, 자막, TTS 표시.
    - **재생성 버튼**: 특정 세그먼트의 영상이 마음에 안 들면 "이 구간만 이미지 교체" 버튼 클릭.
    - **텍스트 수정**: 오타나 어색한 자막을 UI에서 직접 수정 → TTS/자막 재생성.
    - **싱크 미세조정**: 자막 시작/종료 시간을 ±0.1초 단위로 조정.
3.  **Partial Rendering**: 전체를 다시 렌더링하지 않고, 변경된 구간만 다시 처리하거나 수정 사항을 반영해 최종 고화질 렌더링.

---

## 🛠️ 상세 구현 가이드

### Phase 1: 기반 다지기 (BGM & Sync)
**목표**: 리소스 누수 해결 및 기본 퀄리티(싱크, 사운드) 확보

1.  **`core/asset_manager.py` 리팩토링**
    - BGM 다운로드 로직 제거 → 로컬 파일 스캔 로직으로 변경.
    - TTS 생성 시 `get_audio_duration()` 함수로 정확한 길이 반환하도록 수정.

2.  **`core/editor.py` 리팩토링**
    - **Strict Sync Logic**:
      ```python
      # 예시 로직
      clip_duration = tts_audio.duration
      video_clip = video_clip.subclip(0, clip_duration) # 영상 길이를 오디오에 강제로 맞춤
      subtitle_clip = TextClip(..., duration=clip_duration)
      ```
    - 리소스 누수(메모리 해제) 코드 추가.

### Phase 2: 검색 품질 향상 (Visual Relevance)
**목표**: 상황에 딱 맞는 영상 매칭

1.  **`core/planner.py` 프롬프트 수정**
    - Gemini에게 JSON 요청 시 `visual_search_query` 필드 추가.
    - "Don't use abstract nouns. Describe the visual scene physically." 지침 추가.

2.  **`providers/stock/pexels.py` 개선**
    - 검색 결과가 없을 때의 Fallback 로직 강화 (기본 에셋 폴더 사용).

### Phase 3: 인터랙티브 UI 백엔드 (Feedback Loop)
**목표**: 수정 가능한 API 구축

1.  **Backend API 추가 (`backend/main.py`)**
    - `POST /api/projects/{id}/draft`: 초안 생성 (빠름).
    - `GET /api/projects/{id}/timeline`: 세그먼트 데이터 조회 (이미지 URL, 스크립트, 시간).
    - `PUT /api/projects/{id}/segments/{seg_id}`: 특정 세그먼트의 스크립트나 검색어 수정.
    - `POST /api/projects/{id}/regenerate-segment`: 특정 구간 에셋만 다시 뽑기.
    - `POST /api/projects/{id}/render-final`: 최종 고화질 렌더링 시작.

2.  **데이터 모델 변경 (`core/models.py`)**
    - `ContentPlan`을 DB에 저장 가능한 형태로 확장 (JSON 컬럼 활용).
    - 프로젝트 상태 관리: `DRAFT` -> `EDITING` -> `RENDERING` -> `COMPLETED`.

---

## 📅 실행 우선순위

1.  **Critical Fixes**: 리소스 누수 해결, BGM 로컬화. (1주차)
2.  **Quality Fixes**: TTS-자막 싱크 정확도 100% 달성. (1주차)
3.  **Visual Logic**: Gemini 프롬프트 수정 및 검색 로직 개선. (2주차)
4.  **UI/UX Backend**: 미리보기 및 수정 API 개발. (3주차)
5.  **Frontend Update**: 타임라인 편집기 구현. (4주차)

---

**참고**: 이 계획은 기존 `CODE_ANALYSIS_ISSUES.md`의 기술적 부채 해결과 병행되어야 합니다.