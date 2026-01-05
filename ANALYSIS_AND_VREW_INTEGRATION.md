# YouTube AI 소스코드 분석 및 Vrew 연계 방안

작성일: 2026-01-05
버전: v4.0 분석

---

## 📊 현재 시스템 분석

### 1. 전체 아키텍처

현재 시스템은 **완전 자동화된 파이프라인** 구조입니다:

```
[1. Planner] → [2. Asset Manager] → [3. Editor] → [4. Uploader]
   ↓               ↓                    ↓             ↓
 AI 대본 생성   영상+TTS+BGM 수집    MoviePy 편집   YouTube 업로드
```

#### 주요 모듈별 역할:

1. **ContentPlanner** (`core/planner.py`):
   - Gemini AI로 대본 생성
   - 제목, 설명, 태그, 세그먼트 생성
   - **문제점**: AI가 생성한 `image_search_query`의 품질에 전적으로 의존

2. **AssetManager** (`core/asset_manager.py`):
   - 스톡 영상 검색 (Pexels, Pixabay)
   - TTS 음성 생성 (gTTS, ElevenLabs, Typecast)
   - BGM 선택 및 처리
   - **문제점**: 검색 키워드와 실제 대본 내용의 괴리

3. **VideoEditor** (`core/editor.py`):
   - MoviePy 기반 영상 합성
   - 자막, 제목, BGM 추가
   - Ken Burns Effect, Crossfade 효과
   - **문제점**: 완전 자동화로 인한 세밀한 편집 불가

4. **Uploader** (`core/uploader.py`):
   - YouTube API 업로드
   - 메타데이터 최적화

---

## 🔍 주요 문제점 진단

### 문제 1: 대본에 맞지 않는 랜덤 이미지

#### 원인 분석:

**A. AI 프롬프트 단계 (`templates/script_prompts/shorts_script.txt`)**

프롬프트에서 다음과 같이 요구하고 있습니다:

```plaintext
image_search_query: "구체적인 동작, 사물, 장면을 묘사"
예: "happy golden retriever dog owner smiling playing outdoor"
```

**그러나 실제로는**:
- AI가 여전히 추상적인 키워드를 생성할 가능성 존재
- AI의 "구체적" 해석이 사람의 기대와 다를 수 있음
- 예시: "AI 기술"이라는 주제 → "technology innovation" (추상적) vs "person using smartphone AI assistant" (구체적)

**B. 검색 단계 (`core/asset_manager.py:160-199`)**

```python
# 검색 우선순위:
search_query = segment.image_search_query or segment.keyword

# Phase 4 Fallback:
if not assets and segment.image_search_query and segment.keyword:
    search_query = segment.keyword  # 재시도
    assets = self._search_from_providers(search_query)
```

**문제점**:
1. Pexels/Pixabay는 영어 키워드에만 잘 반응
2. 추상적 키워드 → 맥락 없는 영상 검색 결과
3. 검색 결과 중 **첫 번째 영상만 선택** (`assets[0]`) → 다양성 부족
4. 캐싱 시스템으로 인해 같은 키워드는 항상 같은 영상

**C. 세그먼트-영상 매칭 (`core/editor.py:358-503`)**

현재는 세그먼트와 영상 클립을 **순서대로 1:1 매칭**:

```python
# 클립 수 != 세그먼트 수일 경우 비례 분배
if len(clips) != len(segment_timings):
    # 비례 분배로 억지로 맞춤
```

**문제점**:
- 대본 세그먼트 5개, 영상 클립 3개 → 강제로 비율 분배
- 의미론적 매칭 없음 (대본 "강아지"인데 이전 세그먼트 영상 재사용 가능)

---

### 문제 2: TTS가 제대로 생성되지 않는 느낌

#### 원인 분석:

**A. 세그먼트별 TTS 생성 및 병합 (`core/asset_manager.py:273-479`)**

현재 구조:

```python
for segment in content_plan.segments:
    # 1. 세그먼트별 TTS 생성
    seg_filepath = self._generate_gtts(text)  # or elevenlabs, typecast

    # 2. 대기 시간 처리 "(3초 대기)" → 무음 추가
    seg_filepath = self._add_pause_to_audio(seg_filepath, pause_duration)

    # 3. 실제 TTS 길이 측정
    seg_duration = self._get_audio_duration(seg_filepath)

    # 4. ContentPlan 업데이트 (핵심!)
    content_plan.segments[i].duration = seg_duration

# 5. 모든 TTS 파일 병합
final_filepath = self._concatenate_audio_files(segment_audio_files)
```

**문제점**:
1. **gTTS의 한계**:
   - 무료지만 품질이 낮음 (로봇 음성)
   - 감정 표현 없음
   - 억양, 강세 제어 불가

2. **ElevenLabs/Typecast의 설정 복잡성**:
   - `stability`, `similarity_boost`, `style` 파라미터를 정확히 조절해야 자연스러움
   - 기본값(`stability=0.5`)이 모든 대본에 적합하지 않음
   - 예: 뉴스 → `stability=0.7` (일관성), 리뷰 → `stability=0.3` (감정 표현)

3. **세그먼트별 분할로 인한 부자연스러움**:
   - 각 세그먼트를 개별 TTS로 생성 → 톤, 템포가 약간씩 다를 수 있음
   - 병합(concatenate) 시 이음새가 부자연스러울 가능성

4. **Whisper 정렬의 선택적 사용**:
   - Whisper를 사용하면 정확한 타임스탬프 추출 가능
   - 그러나 `WHISPER_AVAILABLE` 조건부 실행 → 미설치 시 부정확

---

## 💡 개선 방안

### 방안 1: AI 프롬프트 개선 (즉시 적용 가능)

**A. 프롬프트에 Few-Shot Learning 추가**

`templates/script_prompts/shorts_script.txt`에 실제 좋은 예시를 더 추가:

```plaintext
# ✅ 최근 성공 사례 (실제 검색 결과가 좋았던 query)

주제: "건강한 아침 루틴"
- 세그먼트 1: "아침 6시에 일어나세요"
  → image_search_query: "person waking up bed stretching morning sunlight window"

- 세그먼트 2: "신선한 과일로 하루를 시작하세요"
  → image_search_query: "fresh fruit smoothie bowl berries banana kitchen table"

주제: "생산성 향상 방법"
- 세그먼트 1: "할 일 목록을 작성하세요"
  → image_search_query: "person writing checklist notebook desk pen hand close up"
```

**B. AI에게 검색 결과 검증 요청**

프롬프트에 추가:

```plaintext
# 검증 단계 (중요!)

각 image_search_query를 작성한 후, 다음을 자문하세요:
1. 이 키워드로 Pexels에서 검색하면 대사 내용과 관련된 영상이 나올까?
2. 추상적 명사(예: "success", "happiness")가 포함되어 있나? → 구체적 동작으로 변경
3. 주체(Subject) + 동작(Action) + 장소/사물(Object)이 모두 포함되어 있나?
```

---

### 방안 2: 다중 영상 검색 및 선택 (중간 난이도)

**A. 검색 결과 다양화**

`core/asset_manager.py:_search_from_providers()` 수정:

```python
def _search_from_providers(self, keyword: str, per_page: int = 3) -> List[StockVideoAsset]:
    # 현재: per_page=3개 검색 → 첫 번째만 사용
    # 개선: 3개 모두 가져와서 AI가 선택

    assets = pexels.search_videos(keyword, per_page=5)  # 더 많이 검색

    # AI에게 대본과 가장 잘 맞는 영상 선택 요청
    best_asset = self._select_best_video_with_ai(
        segment_text=segment.text,
        video_assets=assets
    )
    return [best_asset]
```

**B. AI 기반 영상 선택**

```python
def _select_best_video_with_ai(self, segment_text: str, video_assets: List[StockVideoAsset]) -> StockVideoAsset:
    """
    Gemini API로 대본과 가장 잘 맞는 영상 선택

    - 각 영상의 메타데이터(제목, 설명)를 Gemini에 전달
    - "대사: {segment_text}에 가장 적합한 영상은?"
    - 응답: 1~5번 중 선택
    """
    prompt = f"""
    다음 대사에 가장 어울리는 영상을 선택하세요.

    대사: "{segment_text}"

    영상 후보:
    1. ID: {assets[0].id}, 키워드: {assets[0].keyword}
    2. ID: {assets[1].id}, 키워드: {assets[1].keyword}
    ...

    가장 적합한 번호만 답하세요 (1-5).
    """

    response = gemini_api.generate(prompt)
    selected_index = int(response) - 1
    return video_assets[selected_index]
```

---

### 방안 3: TTS 품질 개선 (즉시 적용 가능)

**A. ElevenLabs 파라미터 자동 조정**

`core/asset_manager.py:_generate_elevenlabs()` 개선:

```python
def _auto_tune_tts_params(self, text: str, account_settings: dict) -> dict:
    """
    대본 내용에 따라 TTS 파라미터 자동 조정

    - 뉴스/정보성 → stability 높게 (0.7~0.8)
    - 리뷰/감성 → stability 낮게 (0.3~0.5)
    - 긴급/흥분 → style 높게 (0.5~0.8)
    """
    base_stability = account_settings.get("tts_stability", 0.5)

    # 텍스트 분석
    if "!" in text or "?" in text:
        # 감정 표현 많음 → stability 낮춤
        stability = base_stability - 0.2
    elif any(word in text for word in ["입니다", "됩니다", "것입니다"]):
        # 격식체 → stability 높임
        stability = base_stability + 0.2
    else:
        stability = base_stability

    return {
        "stability": max(0.0, min(1.0, stability)),
        "similarity_boost": account_settings.get("tts_similarity_boost", 0.75),
        "style": account_settings.get("tts_style", 0.0)
    }
```

**B. 전체 대본을 한 번에 TTS 생성 (선택적)**

현재는 세그먼트별 생성 → 병합 방식인데, 이를 **전체 대본 한 번에 TTS 생성** 후 Whisper로 세그먼트 분할하는 방식으로 변경:

```python
def _generate_tts_wholesome(self, content_plan: ContentPlan) -> tuple:
    """
    전체 대본을 한 번에 TTS 생성 (톤 일관성 향상)

    1. 모든 세그먼트 텍스트 병합
    2. 하나의 TTS 파일 생성
    3. Whisper로 세그먼트별 타임스탬프 추출
    """
    full_text = " ".join([seg.text for seg in content_plan.segments])

    # 한 번에 TTS 생성
    full_tts_path = self._generate_elevenlabs(full_text, ...)

    # Whisper로 정확한 구간 분할
    if WHISPER_AVAILABLE:
        segment_timings = alignment_service.align_segments_to_audio(
            content_plan.segments,
            full_tts_path
        )

    return full_tts_path, segment_timings
```

**장점**: 톤, 템포 일관성 극대화
**단점**: 대기 시간 "(3초 대기)" 처리가 까다로움

---

## 🎬 Vrew와의 연계 방안

### Vrew란?

- **Vrew (브루)**: AI 기반 영상 편집 앱
- 주요 기능:
  - AI 음성 인식 → 자동 자막 생성
  - AI TTS (250+ 목소리)
  - 자막 기반 영상 편집 (자막 삭제 → 영상 구간 삭제)
  - 템플릿, 효과, BGM

### 연계 시나리오

현재 YouTube AI 시스템은 완전 자동화되어 있어, **Vrew를 연계하려면 중간 결과물을 내보내는 "Human-in-the-Loop" 방식**이 필요합니다.

---

### 연계 방안 A: Draft 영상 생성 → Vrew 수동 편집

**워크플로우**:

```
[YouTube AI] 대본 생성 → TTS 생성 → 영상 클립 수집
                ↓
            Draft 영상 생성 (자막 SRT + 프로젝트 JSON)
                ↓
            Vrew로 Import
                ↓
            사용자가 Vrew에서 세밀하게 편집
                ↓
            최종 영상 Export → YouTube 업로드
```

**구현 방법**:

1. **SRT 자막 파일 생성**

`core/editor.py`에 새로운 메서드 추가:

```python
def export_srt(self, content_plan: ContentPlan, asset_bundle: AssetBundle, output_path: str):
    """
    자막 SRT 파일 생성 (Vrew import용)

    Format:
    1
    00:00:00,000 --> 00:00:04,500
    여러분, 이것 알고 계셨나요?

    2
    00:00:04,500 --> 00:00:09,200
    강아지는 사람의 감정을 90% 이상 인식할 수 있습니다.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, timing in enumerate(asset_bundle.segment_timings, start=1):
            start_time = self._format_srt_time(timing.start_time)
            end_time = self._format_srt_time(timing.end_time)

            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{timing.text}\n\n")

    print(f"[SRT] 자막 파일 생성: {output_path}")

def _format_srt_time(self, seconds: float) -> str:
    """초를 SRT 시간 형식으로 변환 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
```

2. **프로젝트 JSON 파일 생성**

Vrew가 직접 지원하는 형식은 아니지만, 사용자가 수동으로 import할 수 있는 정보 제공:

```python
def export_project_json(self, content_plan: ContentPlan, asset_bundle: AssetBundle, output_path: str):
    """
    Vrew import용 프로젝트 정보 JSON 생성

    - TTS 파일 경로
    - 영상 클립 경로 및 타임스탬프
    - 자막 텍스트
    """
    project_data = {
        "title": content_plan.title,
        "duration": asset_bundle.audio.duration,
        "audio": {
            "tts_path": asset_bundle.audio.local_path,
            "bgm_path": asset_bundle.bgm.local_path if asset_bundle.bgm else None
        },
        "segments": [
            {
                "index": timing.segment_index,
                "text": timing.text,
                "start_time": timing.start_time,
                "end_time": timing.end_time,
                "tts_path": timing.tts_local_path,
                "video_clip": asset_bundle.videos[timing.segment_index].local_path if timing.segment_index < len(asset_bundle.videos) else None
            }
            for timing in asset_bundle.segment_timings
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)

    print(f"[JSON] 프로젝트 파일 생성: {output_path}")
```

3. **Backend API 추가**

`backend/main.py`에 Draft 생성 엔드포인트 추가:

```python
@app.post("/api/videos/create-draft")
async def create_draft(request: VideoCreateRequest):
    """
    Draft 영상 생성 (Vrew 연계용)

    - 대본 생성
    - TTS 생성
    - 영상 클립 다운로드
    - SRT + JSON 내보내기
    - 최종 영상은 생성하지 않음
    """
    orchestrator = ContentOrchestrator()

    # 대본 + 에셋 수집까지만
    plan = orchestrator.planner.create_script(...)
    bundle = orchestrator.asset_manager.collect_assets(plan)

    # SRT 및 JSON 내보내기
    srt_path = f"./output/drafts/{job_id}.srt"
    json_path = f"./output/drafts/{job_id}.json"

    orchestrator.editor.export_srt(plan, bundle, srt_path)
    orchestrator.editor.export_project_json(plan, bundle, json_path)

    return {
        "success": True,
        "job_id": job_id,
        "srt_path": srt_path,
        "json_path": json_path,
        "tts_path": bundle.audio.local_path,
        "video_clips": [v.local_path for v in bundle.videos]
    }
```

---

### 연계 방안 B: Vrew API 직접 연동 (고급)

**현재 Vrew는 공식 API를 제공하지 않습니다** (2026년 1월 기준). 하지만 다음과 같은 방법을 고려할 수 있습니다:

1. **Vrew 프로젝트 파일 형식 리버스 엔지니어링**:
   - Vrew 프로젝트 파일(`.vrew`)은 ZIP 압축된 JSON + 미디어 파일
   - 구조를 분석하여 프로그래밍 방식으로 생성 가능

2. **Automation 스크립트**:
   - PyAutoGUI를 사용하여 Vrew 앱을 자동 조작
   - Draft 파일 import → 특정 편집 작업 수행 → Export
   - 단, 매우 불안정하고 유지보수 어려움

---

### 연계 방안 C: Hybrid 워크플로우 (추천)

**개념**:
- YouTube AI: 대본 생성 + 초안 영상 자동 생성
- Vrew: 사용자가 세밀하게 편집 (자막 수정, 영상 교체, 효과 추가)
- YouTube AI: 최종 업로드

**구체적 워크플로우**:

```
1. [YouTube AI] 대본 생성 + TTS 생성 + 영상 클립 수집
   - API: POST /api/videos/create-draft
   - 출력: SRT, JSON, TTS 파일, 영상 클립들

2. [사용자] Vrew로 수동 Import
   - TTS 파일을 Vrew로 드래그 앤 드롭
   - Vrew가 자동으로 음성 인식하여 자막 생성
   - YouTube AI가 생성한 SRT와 비교하여 수정

3. [사용자] Vrew에서 편집
   - 자막 수정 (오타, 타이밍 조정)
   - 영상 클립 교체 (YouTube AI가 추천한 클립 중 선택 or 직접 업로드)
   - 효과, 전환 추가
   - BGM 조정

4. [사용자] Vrew에서 최종 영상 Export
   - MP4 파일 생성

5. [YouTube AI] 최종 영상 업로드
   - API: POST /api/videos/upload-final
   - 메타데이터는 YouTube AI가 생성한 것 사용
```

**장점**:
- AI 자동화의 효율성 + 사람의 창의성 결합
- 대본 생성, 영상 검색의 시간 절약
- 최종 품질은 사용자가 보장

**단점**:
- 완전 자동화가 아님
- 사용자 개입 필요

---

## 🚀 실제 적용 우선순위

### Phase 1: 즉시 적용 (1-2일)

1. **AI 프롬프트 개선**
   - `templates/script_prompts/shorts_script.txt`에 Few-Shot 예시 추가
   - 검증 단계 추가

2. **TTS 파라미터 자동 조정**
   - `_auto_tune_tts_params()` 메서드 추가
   - 대본 톤에 따라 stability 자동 조정

3. **검색 결과 다양화**
   - `per_page=5`로 증가
   - 랜덤하게 2-3번째 결과도 사용 (항상 첫 번째만 선택하지 않기)

---

### Phase 2: Draft 생성 기능 (3-5일)

1. **SRT Export 기능**
   - `export_srt()` 메서드 구현
   - Vrew import 테스트

2. **프로젝트 JSON Export**
   - `export_project_json()` 구현
   - 사용자 매뉴얼 작성

3. **Backend API 추가**
   - `/api/videos/create-draft` 엔드포인트
   - Frontend에 "Draft 생성" 버튼 추가

---

### Phase 3: AI 기반 영상 선택 (1주)

1. **다중 영상 검색**
   - 5-10개 후보 검색

2. **Gemini API로 최적 영상 선택**
   - `_select_best_video_with_ai()` 구현
   - 대본과 영상 메타데이터 매칭

3. **결과 평가**
   - A/B 테스트 (기존 방식 vs AI 선택 방식)
   - 사용자 만족도 조사

---

### Phase 4: 전체 대본 TTS 생성 (선택적)

1. **`_generate_tts_wholesome()` 구현**
   - 전체 대본 한 번에 TTS
   - Whisper 필수 의존성으로 변경

2. **대기 시간 처리 개선**
   - SSML 태그 활용 (ElevenLabs 지원)
   - 또는 후처리로 무음 삽입

---

## 📈 성공 지표

개선 효과를 측정하기 위한 지표:

1. **영상-대본 일치도**:
   - 사용자 평가: 5점 척도 (1=전혀 안 맞음, 5=완벽히 일치)
   - 목표: 현재 2.5점 → 4.0점 이상

2. **TTS 자연스러움**:
   - 사용자 평가: 5점 척도
   - 목표: 현재 3.0점 → 4.5점 이상

3. **Draft → 최종 영상 편집 시간**:
   - Vrew 연계 시 평균 편집 시간
   - 목표: 20분 이내

4. **영상 조회수/참여도**:
   - 개선 전/후 비교
   - 목표: 평균 조회수 30% 증가

---

## 🎯 결론

### 현재 시스템의 강점:
- ✅ 완전 자동화된 파이프라인
- ✅ 다양한 TTS 제공자 지원
- ✅ 템플릿 시스템으로 스타일 다양화
- ✅ BGM, 자막, 효과 자동 추가

### 현재 시스템의 약점:
- ❌ AI가 생성한 검색 키워드의 품질 불안정
- ❌ 영상-대본 의미론적 매칭 부재
- ❌ TTS 품질의 일관성 부족
- ❌ 완전 자동화로 인한 세밀한 편집 불가

### Vrew 연계의 의미:
- **AI 자동화의 효율성** (대본 생성, 영상 검색, TTS)
- **사람의 창의성** (Vrew에서 세밀한 편집, 영상 교체, 효과 추가)
- **최고의 품질** (AI 초안 + 사람의 다듬기)

### 최종 권장사항:

1. **단기 (1주)**:
   - AI 프롬프트 개선
   - TTS 파라미터 자동 조정
   - 검색 결과 다양화

2. **중기 (2-3주)**:
   - Draft 생성 기능 (SRT + JSON Export)
   - Frontend에 "Draft → Vrew" 워크플로우 추가
   - 사용자 매뉴얼 작성

3. **장기 (1-2개월)**:
   - AI 기반 영상 선택 시스템
   - Vrew 프로젝트 파일 자동 생성 (리버스 엔지니어링)
   - Hybrid 워크플로우 자동화 (Draft → Vrew → 최종 업로드)

---

**작성자**: Claude Code AI Assistant
**분석 범위**: `core/planner.py`, `core/asset_manager.py`, `core/editor.py`, `providers/stock/pexels.py`, `templates/script_prompts/shorts_script.txt`
**참고 문서**: `CLAUDE.md`, `UPGRADE_PLAN.md`
