# 프로젝트 리팩토링 계획: 유튜브 쇼츠 자동화 (YouTube Shorts Automation)

이 문서는 'youtube-ai' 프로젝트의 고도화를 위한 기술 명세서입니다. 핵심 목표는 **UI Safe Zone(안전 영역)을 강제하여 자막 잘림을 방지**하고, **Whisper를 도입하여 정확한 자막 싱크(Word-Level Sync)를 구현**하는 것입니다.

---

## 1. 시스템 아키텍처 변경 (System Architecture)

코드의 복잡도를 낮추고 유지보수성을 높이기 위해 다음과 같이 모듈화를 진행해야 합니다.

### A. 설정 관리 (`config.py`)
- **목표:** 로직 파일 내에 존재하는 모든 하드코딩된 값(좌표, 경로 등)을 제거합니다.
- **내용:** 해상도, Safe Zone 비율, 폰트 경로, 색상 테마 등을 정의합니다.

### B. 자막 생성 서비스 (`services/subtitle_service.py`)
- **목표:** 영상 편집 로직에서 자막 생성 로직을 완전히 분리합니다.
- **역할:**
  1. 텍스트와 오디오 파일 경로를 입력받음.
  2. (선택사항) STT(Whisper)를 수행하여 정밀 타임스탬프 획득.
  3. Pillow 라이브러리를 사용해 자막 이미지 생성.
  4. 정확한 시작/종료 시간이 적용된 `ImageClip` 객체 리스트를 반환.

---

## 2. 레이아웃 및 Safe Zone 명세 (Layout Specification)

YouTube Shorts는 앱 자체 UI(좋아요, 설명란 등)가 영상을 가리기 때문에, 텍스트가 절대 침범해서는 안 되는 "Safe Zone"을 정의해야 합니다.

### 해상도 표준
- **Canvas:** 1080 (가로) x 1920 (세로)

### Safe Zone 제약 조건 (Grid System)
| 영역 | 비율 / 값 | 목적 |
| :--- | :--- | :--- |
| **상단 여백 (Top)** | 15% (약 288px) | 배터리, 상태바, 검색 버튼 회피 |
| **하단 여백 (Bottom)** | 30% (약 576px) | 영상 제목, 설명란, 채널명, 사운드바 회피 |
| **좌우 여백 (Side)** | 10% (약 108px) | 좋아요/댓글 버튼 및 엣지 잘림 방지 |

### 구현 로직
1. **동적 계산:**
   ```python
   # 예시 로직
   SAFE_TOP = HEIGHT * 0.15
   SAFE_BOTTOM = HEIGHT * 0.70  # (1.0 - 0.30)
   MAX_TEXT_WIDTH = WIDTH * 0.80 # (1.0 - 0.10 * 2)

2. 좌표 보정 (Clamping): 모든 텍스트 요소의 Y 좌표는 반드시 SAFE_TOP보다 커야 하고, (Y + 텍스트높이)는 SAFE_BOTTOM보다 작아야 함.

3. 자막 싱크 고도화 (Whisper Alignment)
단순한 전체시간 / 글자수 계산 방식은 싱크가 맞지 않습니다. 생성된 오디오를 역으로 분석하여 타임스탬프를 추출하는 방식을 사용합니다.

작업 흐름 (Workflow)
TTS 생성: 기존 로직대로 스크립트를 TTS로 변환하여 audio.mp3 생성.

타임스탬프 추출 (신규 단계):

openai-whisper 라이브러리를 사용하여 audio.mp3를 분석 (word_timestamps=True 옵션 필수).

각 단어(word)별 {word, start, end} 정보가 담긴 세그먼트 추출.

클립 생성: 추출된 정확한 start, end 시간을 기반으로 자막 클립 생성.

필수 의존성
openai-whisper

ffmpeg (Whisper 구동을 위해 필요)

4. 텍스트 렌더링 (Design System)
MoviePy의 기본 TextClip은 에러가 잦고 스타일링에 한계가 있습니다. Python 이미지 처리 라이브러리인 Pillow (PIL)를 사용하여 텍스트 이미지를 직접 생성합니다.

스타일 규칙
폰트: 시스템 기본 폰트 사용 금지. 가독성이 높은 굵은 고딕 계열 폰트 파일(.ttf) 사용 (예: Paperlogy, GmarketSansBold 등).

색상: 기본 흰색 텍스트 (#FFFFFF), 강조 단어는 노란색 (#FFD700).

가독성 옵션 (택 1):

Type A (외곽선): 글자 주위에 2~4px 두께의 검은색 외곽선(Stroke) 적용.

Type B (박스): 글자 뒤에 반투명 검은색 박스 (rgba(0,0,0,150)) 배경 적용 (가장 안전함).

줄바꿈 (Word Wrap)
config.py에서 정의한 MAX_TEXT_WIDTH를 초과하지 않도록 텍스트를 자동으로 줄바꿈 처리하는 함수 구현 필수.

5. Claude Code 작업 지시 순서 (Action Items)
리팩토링 진행 시 다음 순서를 준수하십시오:

config.py 생성: 해상도, 색상 상수, Safe Zone 비율을 정의.

AlignmentService 구현: 오디오 파일을 입력받아 Whisper로 JSON 타임스탬프를 반환하는 함수 작성.

SubtitleGenerator 리팩토링:

TextClip 대신 PIL.Image -> ImageClip 방식으로 변경.

텍스트 위치 결정 시 Safe Zone 로직 적용 (하단 침범 시 강제로 위로 올리거나 폰트 크기 조절).

통합 (Integration): 메인 파이프라인(main.py 등)에서 위 서비스들을 호출하도록 수정.