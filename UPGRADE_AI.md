@CLAUDE.md
현재 내 프로젝트(youtube-ai)의 영상 완성도를 높이고, 작동하지 않는 BGM 기능을 수리하기 위해 대대적인 리팩토링을 요청한다. 아래의 분석 내용과 지침을 바탕으로 코드를 수정해줘.

## 🎯 목표
1. **BGM 기능 완전 복구**: `bgm_manager.py`와 `editor.py`의 연동 문제를 해결하고 오디오 더킹(Audio Ducking) 구현.
2. **시각적 완성도 향상**: 검색어 최적화 및 영상 효과(Zoom, Transition) 추가.
3. **자막 가독성 개선**: 자막 스타일 고도화.

---

## 🛠️ Task 1: BGM 시스템 디버깅 및 고도화 (최우선 순위)
현재 `bgm_enabled=True`임에도 영상에 BGM이 들리지 않거나 적용되지 않고 있다. 다음 로직으로 `core/editor.py`와 `core/bgm_manager.py`를 점검하고 수정해라.

1. **파일 검증 로직 추가**: `asset_manager`가 BGM 파일을 다운로드한 후, 해당 파일이 실제로 존재하고 유효한지(용량이 0이 아닌지) 체크하는 방어 코드를 넣어라.
2. **MoviePy Audio Mixing 수정**:
   - `editor.py`의 `create_video` 함수에서 `AudioFileClip`으로 BGM을 로드할 때, 반드시 `volumex`를 사용하여 볼륨을 조절해라 (기본 0.1~0.2).
   - BGM의 길이를 영상 전체 길이(`final_clip.duration`)에 맞춰 `afx.audio_loop`를 사용해 반복 재생되도록 설정해라.
   - **중요**: `CompositeAudioClip`을 사용할 때 `[bgm_clip, tts_clip]` 순서로 합성하되, TTS 오디오가 BGM에 묻히지 않도록 처리해야 한다.
3. **오디오 더킹(Audio Ducking) 구현**:
   - TTS가 재생되는 구간에서는 BGM 볼륨을 0.1로, TTS가 없는 구간에서는 0.3으로 조절하는 로직을 추가할 수 있다면 제안하고, 어렵다면 전체 BGM 볼륨을 안전하게 0.15로 고정해라.

## 🎨 Task 2: 영상 검색 품질 향상 (LLM Prompt Engineering)
`core/planner.py`에서 Gemini/Claude에게 영상 검색 키워드를 요청할 때의 프롬프트를 수정해라.

- **문제점**: "성공"이라는 키워드로 검색하면 추상적인 이미지가 나옴.
- **수정 지침**: "검색 키워드는 추상적 명사가 아니라, **실제로 화면에 보여질 동작이나 사물**이어야 한다"는 지침을 시스템 프롬프트에 추가해라.
  - 예시: "Success" (X) -> "Man raising hands in office", "People cheering" (O)
  - 예시: "Diet" (X) -> "Healthy salad bowl", "Person running in park" (O)

## ✨ Task 3: 시각 효과(VFX) 및 자막 개선 (`core/editor.py`)
영상이 너무 정적이다. `MoviePy`를 사용하여 다음 효과를 추가해라.

1. **Ken Burns Effect (Zoom)**:
   - 정적인 이미지나 영상 클립에 대해 아주 천천히(1.1배~1.2배) 줌인(Zoom-in)하는 효과를 함수로 구현하여 적용해라.
2. **부드러운 전환 (Transition)**:
   - 클립과 클립 사이에 0.3초 정도의 `crossfadein` / `crossfadeout` 효과를 적용해라.
3. **자막 가독성 (Subtitle Style)**:
   - `TextClip` 생성 시, `stroke_color='black'`, `stroke_width=2`를 추가하여 외곽선을 주거나,
   - 자막 뒤에 반투명한 검은색 박스(`ColorClip` 활용)를 배치하는 옵션을 추가해라.

## 🚀 실행 계획
위 3가지 Task를 순서대로 진행하되, 각 단계마다 수정된 코드의 핵심 로직을 설명하고, 특히 **Task 1(BGM)**에 대해서는 왜 기존 코드가 작동하지 않았는지 원인을 분석해서 보고해라. 지금 바로 Task 1부터 시작해.