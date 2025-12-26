# Phase 2: 미디어 엔진 고도화

**작업 기간**: 1.5주 (2026-01-03 ~ 2026-01-12)
**담당 모듈**: `core/asset_manager.py`, `core/editor.py`, `core/planner.py`
**우선순위**: ⭐⭐⭐⭐ (높음)
**난이도**: 🔥🔥🔥 (중상)
**의존성**: Phase 1 완료 필수

---

## 📋 개요

영상 생성 품질을 향상시키기 위해 배경음악(BGM) 자동 매칭, 템플릿 시스템, 영상 길이 정확도 개선, 수동 영상 업로드 기능을 추가합니다.

### 목표
- ✅ BGM 매니저 구현 (분위기별 자동 매칭)
- ✅ 쇼츠 템플릿 시스템 (JSON 기반)
- ✅ 영상 길이 정확도 개선 (AI 프롬프트 강화)
- ✅ 수동 영상 업로드 기능
- ✅ 영상 품질 향상 (트랜지션, 효과)

---

## 🗂️ 디렉토리 구조

```
youtube-ai/
├── assets/                  # ✨ NEW
│   └── music/               # ✨ NEW - BGM 파일 저장소
│       ├── happy/
│       ├── sad/
│       ├── energetic/
│       ├── calm/
│       └── tense/
├── templates/               # ✨ NEW
│   └── shorts/              # ✨ NEW - 쇼츠 템플릿
│       ├── basic.json
│       ├── documentary.json
│       └── entertainment.json
├── core/
│   ├── bgm_manager.py       # ✨ NEW - BGM 관리
│   ├── asset_manager.py     # 🔧 MODIFY - BGM 통합
│   ├── editor.py            # 🔧 MODIFY - 템플릿 적용
│   ├── planner.py           # 🔧 MODIFY - 시간 제약 강화
│   └── models.py            # 🔧 MODIFY - BGM/Template 모델 추가
└── scripts/
    └── download_bgm.py      # ✨ NEW - 무료 음원 다운로드
```

---

## 📦 필수 패키지 설치

`requirements.txt`에 추가:

```txt
# Audio Processing (Phase 2)
pydub>=0.25.1
```

설치:
```bash
pip install pydub
```

---

## 🏗️ 구현 단계

### Step 1: BGM 모델 및 Enum 추가 (`core/models.py`)

```python
# core/models.py에 추가

from enum import Enum
from typing import Optional
from pydantic import BaseModel

class MoodType(str, Enum):
    """BGM 분위기 타입"""
    HAPPY = "happy"           # 밝고 즐거운
    SAD = "sad"               # 슬프고 감성적인
    ENERGETIC = "energetic"   # 활기차고 신나는
    CALM = "calm"             # 차분하고 평온한
    TENSE = "tense"           # 긴장감 있는
    MYSTERIOUS = "mysterious" # 신비로운


class BGMAsset(BaseModel):
    """배경음악 에셋"""
    name: str                    # 음악 파일명
    local_path: str              # 로컬 파일 경로
    mood: MoodType               # 분위기
    duration: float              # 길이 (초)
    volume: float = 0.3          # 볼륨 (0.0 ~ 1.0)
    artist: Optional[str] = None
    license: Optional[str] = None


class TemplateConfig(BaseModel):
    """쇼츠 템플릿 설정"""
    name: str                           # 템플릿 이름
    description: str                    # 설명

    # 자막 설정
    subtitle_font: str = "malgun.ttf"   # 폰트 파일명
    subtitle_fontsize: int = 40
    subtitle_color: str = "white"
    subtitle_stroke_color: str = "black"
    subtitle_stroke_width: int = 2
    subtitle_position: str = "bottom"   # top, center, bottom
    subtitle_y_offset: int = 100        # 하단 여백

    # 자막 애니메이션
    subtitle_animation: Optional[str] = None  # pop, slide, fade, karaoke

    # 영상 효과
    transition_effect: Optional[str] = None   # fade, crossfade, none
    color_grading: Optional[str] = None       # warm, cool, bw, none

    # BGM 설정
    bgm_enabled: bool = True
    bgm_mood: Optional[MoodType] = MoodType.ENERGETIC


class AssetBundle(BaseModel):
    """에셋 번들 (기존 확장)"""
    videos: List[StockVideoAsset] = []
    audio: Optional[AudioAsset] = None
    bgm: Optional[BGMAsset] = None  # ✨ NEW
```

---

### Step 2: BGM 매니저 생성 (`core/bgm_manager.py`)

```python
"""
BGM Manager Module
배경음악 자동 매칭 및 관리
"""
import os
import json
from pathlib import Path
from typing import Optional, List
from pydub import AudioSegment

from core.models import MoodType, BGMAsset


class BGMManager:
    """배경음악 관리자"""

    def __init__(self, assets_dir: str = "./assets/music"):
        """
        BGMManager 초기화

        Args:
            assets_dir: 음악 파일 디렉토리
        """
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        # 분위기별 디렉토리 생성
        for mood in MoodType:
            (self.assets_dir / mood.value).mkdir(exist_ok=True)

        # BGM 카탈로그 로드
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> dict:
        """
        BGM 카탈로그 로드
        각 분위기별로 사용 가능한 음악 파일 스캔

        Returns:
            {mood: [BGMAsset, ...]} 형태의 딕셔너리
        """
        catalog = {}

        for mood in MoodType:
            mood_dir = self.assets_dir / mood.value
            music_files = []

            # MP3, WAV 파일 검색
            for ext in ['*.mp3', '*.wav']:
                music_files.extend(mood_dir.glob(ext))

            # BGMAsset 객체 생성
            assets = []
            for file_path in music_files:
                try:
                    # 오디오 길이 측정
                    audio = AudioSegment.from_file(str(file_path))
                    duration = len(audio) / 1000.0  # ms to seconds

                    asset = BGMAsset(
                        name=file_path.stem,
                        local_path=str(file_path),
                        mood=mood,
                        duration=duration
                    )
                    assets.append(asset)
                except Exception as e:
                    print(f"[BGM] 파일 로드 실패 ({file_path.name}): {e}")

            catalog[mood] = assets
            print(f"[BGM] {mood.value}: {len(assets)}개 로드됨")

        return catalog

    def get_bgm_for_mood(
        self,
        mood: MoodType,
        min_duration: Optional[float] = None
    ) -> Optional[BGMAsset]:
        """
        특정 분위기에 맞는 BGM 가져오기

        Args:
            mood: 요청 분위기
            min_duration: 최소 길이 (초)

        Returns:
            BGMAsset 또는 None
        """
        if mood not in self.catalog or not self.catalog[mood]:
            print(f"[BGM] {mood.value} 분위기의 음악이 없습니다.")
            return None

        # 길이 필터링
        candidates = self.catalog[mood]
        if min_duration:
            candidates = [bgm for bgm in candidates if bgm.duration >= min_duration]

        if not candidates:
            print(f"[BGM] {mood.value} 분위기의 음악 중 {min_duration}초 이상인 파일이 없습니다.")
            return None

        # 첫 번째 음악 반환 (추후 랜덤/가중치 선택 가능)
        return candidates[0]

    def auto_match_mood(self, topic: str, tone: str) -> MoodType:
        """
        주제와 톤에 따라 자동으로 분위기 매칭

        Args:
            topic: 콘텐츠 주제
            tone: 콘텐츠 톤 (정보성, 유머, 감성 등)

        Returns:
            매칭된 MoodType
        """
        # 키워드 기반 매칭 (간단한 휴리스틱)
        topic_lower = topic.lower()
        tone_lower = tone.lower()

        # 슬픈 분위기
        sad_keywords = ['슬픔', '이별', '추억', '그리움', '눈물', 'sad', 'goodbye']
        if any(kw in topic_lower or kw in tone_lower for kw in sad_keywords):
            return MoodType.SAD

        # 긴장감 있는 분위기
        tense_keywords = ['공포', '스릴러', '미스터리', '긴장', 'horror', 'thriller']
        if any(kw in topic_lower or kw in tone_lower for kw in tense_keywords):
            return MoodType.TENSE

        # 활기찬 분위기
        energetic_keywords = ['운동', '게임', '챌린지', '신남', 'energy', 'game', 'challenge']
        if any(kw in topic_lower or kw in tone_lower for kw in energetic_keywords):
            return MoodType.ENERGETIC

        # 차분한 분위기
        calm_keywords = ['명상', '힐링', '자연', '평화', 'calm', 'meditation', 'healing']
        if any(kw in topic_lower or kw in tone_lower for kw in calm_keywords):
            return MoodType.CALM

        # 유머 → 밝은 분위기
        if '유머' in tone_lower or 'funny' in tone_lower:
            return MoodType.HAPPY

        # 기본값: 밝은 분위기
        return MoodType.HAPPY

    def process_bgm(
        self,
        bgm_asset: BGMAsset,
        target_duration: float,
        output_path: str,
        volume: float = 0.3
    ) -> str:
        """
        BGM을 목표 길이에 맞게 조정하고 볼륨 조절

        Args:
            bgm_asset: BGMAsset 객체
            target_duration: 목표 길이 (초)
            output_path: 출력 파일 경로
            volume: 볼륨 (0.0 ~ 1.0)

        Returns:
            처리된 BGM 파일 경로
        """
        # 오디오 로드
        audio = AudioSegment.from_file(bgm_asset.local_path)

        # 길이 조정
        target_ms = int(target_duration * 1000)
        if len(audio) > target_ms:
            # 길면 자르기
            audio = audio[:target_ms]
        elif len(audio) < target_ms:
            # 짧으면 반복
            loops_needed = (target_ms // len(audio)) + 1
            audio = audio * loops_needed
            audio = audio[:target_ms]

        # 볼륨 조정 (dB 변환)
        # volume 0.3 → -10.5dB
        db_change = (volume - 1.0) * 35  # 간단한 변환
        audio = audio + db_change

        # 페이드 아웃 (마지막 3초)
        fade_duration = min(3000, len(audio) // 4)
        audio = audio.fade_out(fade_duration)

        # 저장
        audio.export(output_path, format="mp3")
        print(f"[BGM] 처리 완료: {output_path} ({target_duration:.2f}초)")

        return output_path
```

---

### Step 3: 템플릿 시스템 - JSON 파일 생성

**1) 기본형 템플릿 (`templates/shorts/basic.json`)**

```json
{
  "name": "basic",
  "description": "기본 쇼츠 템플릿 - 깔끔한 자막, 하단 배치",

  "subtitle_font": "malgun.ttf",
  "subtitle_fontsize": 40,
  "subtitle_color": "white",
  "subtitle_stroke_color": "black",
  "subtitle_stroke_width": 2,
  "subtitle_position": "bottom",
  "subtitle_y_offset": 100,

  "subtitle_animation": null,
  "transition_effect": null,
  "color_grading": null,

  "bgm_enabled": true,
  "bgm_mood": "happy"
}
```

**2) 다큐형 템플릿 (`templates/shorts/documentary.json`)**

```json
{
  "name": "documentary",
  "description": "다큐멘터리 스타일 - 차분한 자막, 중앙 배치",

  "subtitle_font": "malgun.ttf",
  "subtitle_fontsize": 36,
  "subtitle_color": "#EEEEEE",
  "subtitle_stroke_color": "#333333",
  "subtitle_stroke_width": 3,
  "subtitle_position": "center",
  "subtitle_y_offset": 0,

  "subtitle_animation": "fade",
  "transition_effect": "crossfade",
  "color_grading": "cool",

  "bgm_enabled": true,
  "bgm_mood": "calm"
}
```

**3) 예능형 템플릿 (`templates/shorts/entertainment.json`)**

```json
{
  "name": "entertainment",
  "description": "예능 스타일 - 큰 자막, 강렬한 색상",

  "subtitle_font": "malgun.ttf",
  "subtitle_fontsize": 48,
  "subtitle_color": "yellow",
  "subtitle_stroke_color": "black",
  "subtitle_stroke_width": 3,
  "subtitle_position": "bottom",
  "subtitle_y_offset": 120,

  "subtitle_animation": "pop",
  "transition_effect": null,
  "color_grading": "warm",

  "bgm_enabled": true,
  "bgm_mood": "energetic"
}
```

---

### Step 4: Planner 수정 - 시간 제약 강화 (`core/planner.py`)

```python
# core/planner.py

class Planner:
    def generate_content_plan(
        self,
        topic: str,
        format: VideoFormat,
        target_duration: int,  # 60초
        style: str = "정보성"
    ) -> ContentPlan:
        """
        콘텐츠 기획 생성 (시간 제약 강화)
        """
        # ✨ 시간 제약을 프롬프트에 명시적으로 추가
        duration_constraint = f"""
        **중요: 영상 길이 제약**
        - 목표 길이: 정확히 {target_duration}초
        - TTS 음성 속도: 평균 분당 150단어 (한국어 기준 분당 300음절)
        - {target_duration}초 = 약 {target_duration * 5}음절 이내로 스크립트 작성
        - 각 세그먼트는 {target_duration // 5}초 내외로 균등 배분
        - 절대 초과 금지: {target_duration}초를 1초라도 넘으면 안 됨
        """

        # AI 프롬프트에 추가
        prompt = f"""
        주제: {topic}
        포맷: {format.value}
        톤: {style}

        {duration_constraint}

        위 제약 조건을 **반드시** 준수하여 스크립트를 작성하세요.
        각 세그먼트의 텍스트 길이를 정확히 계산하여 총 {target_duration}초를 넘지 않도록 하세요.
        """

        # ... 기존 AI 호출 코드 ...
```

---

### Step 5: AssetManager 수정 - BGM 통합 (`core/asset_manager.py`)

```python
# core/asset_manager.py

from core.bgm_manager import BGMManager

class AssetManager:
    def __init__(
        self,
        stock_providers: List[str] = None,
        tts_provider: str = "gtts",
        cache_enabled: bool = True,
        download_dir: str = "./downloads",
        enable_bgm: bool = True  # ✨ NEW
    ):
        # ... 기존 코드 ...

        # ✨ BGM 매니저 초기화
        self.enable_bgm = enable_bgm
        if enable_bgm:
            self.bgm_manager = BGMManager()

    def collect_assets(
        self,
        content_plan: ContentPlan,
        download_videos: bool = True,
        generate_tts: bool = True,
        add_bgm: bool = True,  # ✨ NEW
        bgm_mood: Optional[MoodType] = None  # ✨ NEW
    ) -> Optional[AssetBundle]:
        """
        에셋 수집 (BGM 포함)
        """
        # ... 기존 영상/음성 수집 코드 ...

        # ✨ BGM 수집
        bgm_asset = None
        if add_bgm and self.enable_bgm:
            bgm_asset = self._collect_bgm(content_plan, bgm_mood)

        # AssetBundle 생성
        bundle = AssetBundle(
            videos=video_assets,
            audio=audio_asset,
            bgm=bgm_asset  # ✨ NEW
        )

        return bundle

    def _collect_bgm(
        self,
        content_plan: ContentPlan,
        mood: Optional[MoodType] = None
    ) -> Optional[BGMAsset]:
        """
        BGM 수집

        Args:
            content_plan: ContentPlan 객체
            mood: 분위기 (None이면 자동 매칭)

        Returns:
            BGMAsset 또는 None
        """
        # 분위기 자동 매칭
        if mood is None:
            mood = self.bgm_manager.auto_match_mood(
                topic=content_plan.title,
                tone=content_plan.style or "정보성"
            )
            print(f"[BGM] 자동 매칭 분위기: {mood.value}")

        # BGM 가져오기
        bgm_asset = self.bgm_manager.get_bgm_for_mood(
            mood=mood,
            min_duration=content_plan.target_duration
        )

        if bgm_asset:
            print(f"[BGM] 선택됨: {bgm_asset.name} ({bgm_asset.duration:.2f}초)")

        return bgm_asset
```

---

### Step 6: Editor 수정 - 템플릿 적용 및 BGM 믹싱 (`core/editor.py`)

```python
# core/editor.py

import json
from pydub import AudioSegment
from core.models import TemplateConfig, BGMAsset

class VideoEditor:
    def __init__(self, config: Optional[EditConfig] = None):
        # ... 기존 코드 ...

        # 템플릿 디렉토리
        self.template_dir = Path("./templates/shorts")

    def load_template(self, template_name: str = "basic") -> TemplateConfig:
        """
        템플릿 로드

        Args:
            template_name: 템플릿 파일명 (확장자 제외)

        Returns:
            TemplateConfig 객체
        """
        template_path = self.template_dir / f"{template_name}.json"

        if not template_path.exists():
            print(f"[WARNING] 템플릿 '{template_name}' 없음, 기본값 사용")
            return TemplateConfig(name="basic", description="기본 템플릿")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return TemplateConfig(**data)
        except Exception as e:
            print(f"[ERROR] 템플릿 로드 실패: {e}")
            return TemplateConfig(name="basic", description="기본 템플릿")

    def create_video(
        self,
        content_plan: ContentPlan,
        asset_bundle: AssetBundle,
        output_filename: Optional[str] = None,
        template_name: str = "basic"  # ✨ NEW
    ) -> Optional[str]:
        """
        영상 생성 (템플릿 및 BGM 적용)
        """
        # ✨ 템플릿 로드
        template = self.load_template(template_name)
        print(f"[Editor] 템플릿 적용: {template.name}")

        # ... 기존 비디오 클립 로드 코드 ...

        # ✨ BGM 믹싱
        if asset_bundle.bgm and asset_bundle.audio:
            audio_clip = self._mix_audio_with_bgm(
                voice_path=asset_bundle.audio.local_path,
                bgm_asset=asset_bundle.bgm,
                target_duration=target_duration,
                bgm_volume=0.3
            )

        # ... 기존 영상 합성 코드 ...

        # ✨ 템플릿 기반 자막 추가
        if content_plan.segments:
            final_video = self._add_subtitles_with_template(
                final_video,
                content_plan,
                audio_clip.duration if audio_clip else target_duration,
                template  # ✨ 템플릿 전달
            )

        # ... 나머지 렌더링 코드 ...

    def _mix_audio_with_bgm(
        self,
        voice_path: str,
        bgm_asset: BGMAsset,
        target_duration: float,
        bgm_volume: float = 0.3
    ):
        """
        음성과 BGM 믹싱

        Args:
            voice_path: 음성 파일 경로
            bgm_asset: BGMAsset 객체
            target_duration: 목표 길이
            bgm_volume: BGM 볼륨

        Returns:
            믹싱된 오디오 AudioFileClip
        """
        from pydub import AudioSegment

        # 음성 로드
        voice = AudioSegment.from_file(voice_path)

        # BGM 로드 및 조정
        bgm = AudioSegment.from_file(bgm_asset.local_path)

        # BGM 길이 맞추기
        target_ms = int(target_duration * 1000)
        if len(bgm) > target_ms:
            bgm = bgm[:target_ms]
        else:
            loops = (target_ms // len(bgm)) + 1
            bgm = bgm * loops
            bgm = bgm[:target_ms]

        # BGM 볼륨 조절
        db_change = (bgm_volume - 1.0) * 35
        bgm = bgm + db_change

        # BGM 페이드 아웃
        bgm = bgm.fade_out(3000)

        # 오버레이 (음성이 BGM보다 짧으면 BGM 길이에 맞춤)
        mixed = bgm.overlay(voice, position=0)

        # 임시 파일로 저장
        mixed_path = str(self.audio_dir / "mixed_audio.mp3")
        mixed.export(mixed_path, format="mp3")

        # AudioFileClip 반환
        return self.AudioFileClip(mixed_path)

    def _add_subtitles_with_template(
        self,
        video_clip,
        content_plan: ContentPlan,
        total_duration: float,
        template: TemplateConfig
    ):
        """
        템플릿 기반 자막 추가

        Args:
            video_clip: 베이스 비디오 클립
            content_plan: ContentPlan 객체
            total_duration: 총 영상 길이
            template: TemplateConfig 객체

        Returns:
            자막이 추가된 CompositeVideoClip
        """
        if not content_plan.segments:
            return video_clip

        segment_duration = total_duration / len(content_plan.segments)
        subtitle_clips = []

        for i, segment in enumerate(content_plan.segments):
            start_time = i * segment_duration

            # 텍스트 정제
            import re
            text = re.sub(r'\([^)]*\)', '', segment.text).strip()
            if not text:
                continue

            try:
                # ✨ 템플릿 설정 사용
                fontsize = template.subtitle_fontsize

                # 폰트 경로 (Windows)
                import platform
                if platform.system() == 'Windows':
                    font_path = f'C:\\Windows\\Fonts\\{template.subtitle_font}'
                else:
                    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

                # TextClip 생성
                txt_clip = self.TextClip(
                    text=text,
                    font=font_path,
                    font_size=fontsize,
                    color=template.subtitle_color,
                    stroke_color=template.subtitle_stroke_color,
                    stroke_width=template.subtitle_stroke_width,
                    method='caption',
                    size=(int(self.config.resolution[0] * 0.9), None)
                )

                # ✨ 위치 설정 (템플릿 기반)
                if template.subtitle_position == "top":
                    y_position = template.subtitle_y_offset
                elif template.subtitle_position == "center":
                    y_position = int(self.config.resolution[1] / 2)
                else:  # bottom
                    y_position = int(self.config.resolution[1] - template.subtitle_y_offset)

                txt_clip = txt_clip.with_position(('center', y_position))
                txt_clip = txt_clip.with_start(start_time).with_duration(segment_duration)

                subtitle_clips.append(txt_clip)

            except Exception as e:
                print(f"[WARNING] 자막 생성 실패 ({i+1}): {e}")

        if subtitle_clips:
            video_clip = self.CompositeVideoClip([video_clip] + subtitle_clips)
            print(f"[Editor] 자막 {len(subtitle_clips)}개 추가 (템플릿: {template.name})")

        return video_clip
```

---

### Step 7: 수동 영상 업로드 기능 (`core/asset_manager.py`)

```python
# core/asset_manager.py

class AssetManager:
    def use_manual_video(
        self,
        video_path: str,
        content_plan: ContentPlan
    ) -> Optional[AssetBundle]:
        """
        사용자가 업로드한 영상을 배경으로 사용

        Args:
            video_path: 업로드된 영상 파일 경로
            content_plan: ContentPlan 객체

        Returns:
            AssetBundle (videos에 수동 영상 포함)
        """
        if not os.path.exists(video_path):
            print(f"[ERROR] 영상 파일을 찾을 수 없음: {video_path}")
            return None

        # StockVideoAsset으로 래핑
        manual_asset = StockVideoAsset(
            id="manual_upload",
            provider="manual",
            url=video_path,
            thumbnail_url="",
            local_path=video_path,
            downloaded=True
        )

        # TTS 생성
        audio_asset = self._generate_tts(content_plan)

        # AssetBundle 생성
        bundle = AssetBundle(
            videos=[manual_asset],
            audio=audio_asset
        )

        print(f"[AssetManager] 수동 영상 사용: {video_path}")
        return bundle
```

---

### Step 8: 무료 BGM 다운로드 스크립트 (`scripts/download_bgm.py`)

```python
"""
무료 BGM 다운로드 스크립트
YouTube Audio Library 또는 Pixabay Music에서 무료 음원 다운로드
"""
import os
from pathlib import Path

# 추천 무료 음원 사이트 (직접 다운로드 필요)
RECOMMENDED_SOURCES = """
무료 BGM 다운로드 사이트:

1. YouTube Audio Library
   https://www.youtube.com/audiolibrary
   - 완전 무료, 저작권 걱정 없음
   - 분위기별 필터링 가능

2. Pixabay Music
   https://pixabay.com/music/
   - 무료, 상업적 사용 가능
   - 다양한 장르

3. Bensound
   https://www.bensound.com/
   - 무료 (크레딧 표기 필요)

다운로드 후 아래 디렉토리에 저장하세요:
- assets/music/happy/
- assets/music/sad/
- assets/music/energetic/
- assets/music/calm/
- assets/music/tense/
"""

if __name__ == "__main__":
    print(RECOMMENDED_SOURCES)

    # 디렉토리 생성
    music_dir = Path("./assets/music")
    for mood in ['happy', 'sad', 'energetic', 'calm', 'tense', 'mysterious']:
        (music_dir / mood).mkdir(parents=True, exist_ok=True)

    print("\n[SUCCESS] assets/music/ 디렉토리 생성 완료")
    print("위 사이트에서 BGM을 다운로드하여 분위기별 폴더에 저장하세요.")
```

---

## ✅ 테스트 체크리스트

### 1. BGM 매니저 테스트

```python
# tests/test_bgm_manager.py
from core.bgm_manager import BGMManager
from core.models import MoodType

bgm_manager = BGMManager()

# 분위기별 BGM 가져오기
bgm = bgm_manager.get_bgm_for_mood(MoodType.HAPPY, min_duration=60)
assert bgm is not None
print(f"BGM: {bgm.name}, {bgm.duration}초")

# 자동 매칭
mood = bgm_manager.auto_match_mood(topic="재미있는 동물 영상", tone="유머")
assert mood == MoodType.HAPPY
```

### 2. 템플릿 로드 테스트

```python
# tests/test_template.py
from core.editor import VideoEditor

editor = VideoEditor()
template = editor.load_template("entertainment")

assert template.name == "entertainment"
assert template.subtitle_color == "yellow"
print(f"템플릿: {template.description}")
```

### 3. 전체 파이프라인 테스트 (BGM 포함)

```bash
python scripts/auto_create.py --topic "AI 기술 소개" --format shorts --duration 60 --template entertainment
```

---

## 📊 성공 기준

- [x] BGM 자동 매칭 작동 (분위기별 음악 선택)
- [x] 템플릿 3종 적용 확인 (basic, documentary, entertainment)
- [x] 음성 + BGM 믹싱 성공
- [x] 영상 길이 정확도 95% 이상 (목표 60초 → 58~62초 범위)
- [x] 수동 영상 업로드 기능 작동

---

## 🚀 커밋 전략

```bash
# Step 1-2
git add core/models.py core/bgm_manager.py
git commit -m "Phase 2: Add BGM manager and mood matching"

# Step 3
git add templates/shorts/*.json
git commit -m "Phase 2: Add shorts templates (basic, documentary, entertainment)"

# Step 4
git add core/planner.py
git commit -m "Phase 2: Strengthen duration constraint in planner"

# Step 5-6
git add core/asset_manager.py core/editor.py
git commit -m "Phase 2: Integrate BGM and templates into asset manager and editor"

# Step 7
git add scripts/download_bgm.py
git commit -m "Phase 2: Add BGM download script"

# 통합 테스트
git add tests/test_bgm.py tests/test_template.py
git commit -m "Phase 2: Add BGM and template tests"
```

---

## ⚠️ 주의사항

1. **무료 BGM 라이선스 확인**
   - YouTube Audio Library: 완전 무료
   - 기타 사이트: 크레딧 표기 필요 여부 확인

2. **BGM 볼륨 밸런스**
   - 음성이 BGM에 묻히지 않도록 볼륨 조절 (기본 0.3)
   - 필요시 `bgm_volume` 파라미터 조정

3. **템플릿 확장**
   - 추후 사용자 커스텀 템플릿 업로드 기능 고려
   - JSON 스키마 검증 추가 권장

---

## 📚 다음 단계

Phase 2 완료 후:
- **Phase 3**: ElevenLabs TTS 고도화 (DB 설정 연동, 미리듣기)
- **Phase 4**: 스케줄링 시스템 (BGM/템플릿 자동 적용)

**Phase 3로 이동**: [UPGRADE_PHASE3.md](./UPGRADE_PHASE3.md)

---

**작성일**: 2025-12-26
**버전**: 1.0
**상태**: Ready for Implementation
