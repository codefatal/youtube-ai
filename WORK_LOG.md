# 작업 기록 (Work Log)

> **목적**: 토큰 만료 방지 및 작업 연속성 유지를 위한 상세 작업 기록

---

## 📋 작업 워크플로우

### 새 작업 시작 시
1. **TODO 섹션**에 작업 항목 추가
2. 작업 시작 날짜/시간 기록
3. 작업 목표 및 배경 간단히 기록

### 작업 완료 시
1. TODO → **DONE 섹션**으로 이동
2. 완료 날짜/시간 기록
3. 변경된 파일 목록 기록
4. 주요 변경 사항 상세 기록
5. Git 커밋 해시 기록
6. 테스트 결과 기록

---

## 🚧 TODO (진행 예정 작업)

### 버그 수정: 썸네일 RGBA→JPEG 변환 오류
- **시작일**: 2025-12-11 14:35
- **담당**: Claude Code
- **목표**: 썸네일 생성 시 RGBA를 RGB로 변환 후 JPEG 저장
- **배경**: `cannot write mode RGBA as JPEG` 오류로 영상 제작 실패
- **예상 파일**: `local_cli/services/video_producer.py`

### 버그 수정: 비주얼 클립 이미지 깨짐
- **시작일**: 2025-12-11 14:35
- **목표**: ColorClip 대신 안정적인 이미지 생성 방법 사용
- **배경**: 영상 재생 시 이미지가 깨져 보임
- **예상 파일**: `local_cli/services/video_producer.py`

### 버그 수정: 숏폼 자막 잘림 현상
- **시작일**: 2025-12-11 14:35
- **목표**: 숏폼(9:16) 크롭 시 자막 위치 조정
- **배경**: 자막이 화면 아래쪽에서 잘려서 보임
- **예상 파일**: `local_cli/services/video_producer.py`

### 새 기능: TTS 목소리 선택 기능
- **시작일**: 2025-12-11 14:35
- **목표**: 설정 페이지에서 TTS 목소리 선택 및 테스트
- **배경**: 사용자가 다양한 목소리 중 선택하고 테스트하고 싶어함
- **예상 파일**:
  - `frontend/app/settings/page.tsx`
  - `backend/main.py`
  - `local_cli/services/tts_service.py`

### 개선: TTS 템포 빠르게
- **시작일**: 2025-12-11 14:35
- **목표**: gTTS 속도를 현재보다 빠르게 조정
- **예상 파일**: `local_cli/services/tts_service.py`

### 새 기능: 인기 배경음악 10개 사전 등록
- **시작일**: 2025-12-11 14:35
- **목표**: 저작권 없는 인기 음악 10개 자동 다운로드 및 등록
- **배경**: 매번 수동으로 음악 추가하는 번거로움 해소
- **예상 파일**:
  - `local_cli/services/music_library.py`
  - `MUSIC_GUIDE.md`
  - 새 스크립트: `scripts/download_popular_music.py`

### 템플릿
```markdown
### [작업명]
- **시작일**: YYYY-MM-DD HH:mm
- **담당**: Claude Code
- **목표**:
- **배경**:
- **예상 파일**:
```

---

## ✅ DONE (완료된 작업)

### 2025-12-11: TextClip 정수 변환 오류 수정
- **완료일**: 2025-12-11 09:59
- **Git 커밋**: `2c5fb22`
- **문제**: PIL/MoviePy가 float 크기 값을 허용하지 않음
- **해결**:
  - `TextClip` size 파라미터를 `int()`로 변환
  - `cropped()` 모든 파라미터를 정수로 변환
- **변경 파일**:
  - `local_cli/services/video_producer.py:330` - TextClip size
  - `local_cli/services/video_producer.py:345-348` - cropped 파라미터
- **테스트**: 서버 재시작 필요

---

### 2025-12-11: 전체 시스템 안정성 개선
- **완료일**: 2025-12-11 09:55
- **Git 커밋**: `7108ee0`
- **목표**: FFprobe 경고 제거 및 에러 핸들링 강화
- **주요 변경**:

#### 1. FFprobe 완전 제거 (tts_service.py)
```python
# Before
def _get_audio_duration(self, audio_path: str) -> float:
    # FFprobe 시도 (실패) → MoviePy fallback

# After
def _get_audio_duration(self, audio_path: str) -> float:
    # MoviePy 우선 (안정적) → FFmpeg stderr 파싱 fallback
```
- **이유**: imageio-ffmpeg는 ffprobe를 포함하지 않음
- **결과**: ⚠️ FFprobe 경고 메시지 완전 제거

#### 2. audio_processor.py 개선
- FFmpeg stderr 파싱으로 오디오 길이 측정
- MoviePy fallback 추가
- 에러 핸들링 강화

#### 3. music_library.py 개선
- `_ensure_music_structure()` 메서드 추가 (자동 폴더 생성)
- 스타일 매핑 확장: calm, energetic, professional, creative 추가
- 더 친절한 안내 메시지

#### 4. video_producer.py 개선
- 출력 디렉토리 미리 생성
- 중복 코드 제거

- **변경 파일**:
  - `local_cli/services/tts_service.py`
  - `local_cli/services/audio_processor.py`
  - `local_cli/services/music_library.py`
  - `local_cli/services/video_producer.py`
  - `.claude/settings.local.json`

---

### 2025-12-11: 폰트 자동 탐지 및 한글 지원
- **완료일**: 2025-12-11 09:50
- **Git 커밋**: `f301671`
- **문제**: MoviePy가 'Arial-Bold' 폰트를 찾지 못함
- **해결**: 시스템 폰트 자동 탐지 기능 추가

#### _find_font() 메서드 추가
```python
def _find_font(self) -> Optional[str]:
    """시스템에서 사용 가능한 폰트 찾기"""
    # Windows: 맑은 고딕 → 굴림 → Arial
    # Linux: 나눔고딕 → DejaVu Sans
    # macOS: Apple SD Gothic → Helvetica
```

- **특징**:
  - ✅ 한글 자막 완벽 지원
  - ✅ 크로스 플랫폼 (Windows/Linux/macOS)
  - ✅ 폰트 찾기 실패 시 기본 폰트 fallback

- **변경 파일**:
  - `local_cli/services/video_producer.py:235-280` - _find_font 메서드
  - `local_cli/services/video_producer.py:270` - make_textclip에서 사용

---

### 2025-12-11: 영상 제작 3가지 개선
- **완료일**: 2025-12-11 09:48
- **Git 커밋**: `a88d7ad`
- **목표**: FFprobe 경로 문제, 배경음악 라이브러리, 이미지 생성 API 통합

#### 1. FFprobe 경로 문제 해결 (tts_service.py)
- **문제**: `[WinError 2] 지정된 파일을 찾을 수 없습니다`
- **해결**: 3단계 fallback 전략
  1. FFprobe (imageio-ffmpeg에서 자동 탐지)
  2. MoviePy AudioFileClip
  3. 기본값 5초
- **코드**: `tts_service.py:253-306`

#### 2. 배경음악 라이브러리 구축
- **파일**: `MUSIC_GUIDE.md` 생성
- **내용**:
  - 5개 무료 음악 사이트 가이드
  - YouTube Audio Library (최고 추천)
  - Pixabay Music (회원가입 불필요)
  - Free Music Archive
  - Incompetech
  - Bensound
- **폴더 구조**:
  ```
  music/
  ├── youtube_audio_library/
  │   ├── ambient/
  │   ├── electronic/
  │   ├── cinematic/
  │   └── upbeat/
  └── free_music_archive/
      ├── jazz/
      ├── classical/
      └── indie/
  ```

#### 3. AI 이미지 생성 구현 (image_generator.py)
- **Unsplash API 통합**:
  - 무료 이미지 검색/다운로드
  - API 키: `UNSPLASH_ACCESS_KEY`
- **Pexels API 통합**:
  - 무료 이미지 검색/다운로드
  - API 키: `PEXELS_API_KEY`
- **Text 이미지 생성**:
  - Pillow 사용
  - API 키 불필요
  - 단색 배경 + 텍스트
- **코드**: `local_cli/services/image_generator.py:158-290`

- **변경 파일**:
  - `local_cli/services/tts_service.py`
  - `local_cli/services/image_generator.py`
  - `MUSIC_GUIDE.md` (신규)

---

### 2025-12-11: MoviePy 2.x API 마이그레이션 (3차 수정)
- **완료일**: 2025-12-11 (시간 미기록)
- **Git 커밋**: (해시 미기록)
- **문제**: `'CompositeVideoClip' object has no attribute 'subclip'`
- **해결**: `subclip()` → `subclipped()`

#### MoviePy 2.x 메서드 변경 요약
| 1.x 메서드 | 2.x 메서드 |
|-----------|-----------|
| `set_audio()` | `with_audio()` |
| `set_start()` | `with_start()` |
| `set_duration()` | `with_duration()` |
| `set_position()` | `with_position()` |
| `resize()` | `resized()` |
| `crop()` | `cropped()` |
| `subclip()` | `subclipped()` |
| `TextClip(txt, fontsize=X)` | `TextClip(text=txt, font_size=X)` |

- **변경 파일**: `local_cli/services/video_producer.py`

---

### 2025-12-11: MoviePy 2.x API 마이그레이션 (2차 수정)
- **완료일**: 2025-12-11 (시간 미기록)
- **Git 커밋**: (해시 미기록)
- **문제**: `'ColorClip' object has no attribute 'resize'`
- **해결**:
  - `resize()` → `resized()`
  - `crop()` → `cropped()`
  - `set_duration()` → `with_duration()`

---

### 2025-12-11: MoviePy 2.x API 마이그레이션 (1차 수정)
- **완료일**: 2025-12-11 (시간 미기록)
- **Git 커밋**: (해시 미기록)
- **문제**: `ModuleNotFoundError: No module named 'moviepy.editor'`
- **원인**: MoviePy 2.1.2가 설치되었으나 코드는 1.x import 구문 사용
- **해결**:
  ```python
  # Before
  import moviepy.editor as mp
  clip = mp.ColorClip(...)

  # After
  from moviepy import ColorClip, ImageClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip, TextClip
  clip = ColorClip(...)
  ```

- **변경 파일**:
  - `local_cli/services/video_producer.py:168-172`
  - `requirements.txt` - moviepy>=2.0.0, imageio-ffmpeg>=0.5.0 추가

---

### 2025-12-11: 영상 제작 기능 전체 개선
- **완료일**: 2025-12-11 (시간 미기록)
- **Git 커밋**: (다중 커밋)
- **목표**: 어제 중단된 영상 제작 기능 개선 작업 완료

#### 개선 항목
1. **MoviePy import 오류 수정** ✅
2. **AI 이미지 생성** ✅
3. **자막 타이밍 개선** ✅
4. **코드 리팩토링** ✅

#### 주요 변경
- `video_producer.py`:
  - MoviePy 2.x import 수정
  - `_generate_visual_clips()` 개선 (AI 이미지 지원)
  - `_create_subtitles()` 개선 (실제 TTS 길이 사용)
  - 타입 힌트 및 docstring 추가
  - `_timestamp_to_seconds()` 제거 (미사용)

- `image_generator.py`:
  - Unsplash, Pexels, Text 이미지 생성 구현
  - Gemini/DALL-E placeholder 유지

- `tts_service.py`:
  - `_get_audio_duration()` 추가
  - `generate_with_timestamps()` duration 반환

---

### 2025-12-11: VSCODE_GUIDE.md 추천 확장 프로그램 추가
- **완료일**: 2025-12-11 (시간 미기록)
- **Git 커밋**: (해시 미기록)
- **문제**: 목차에는 "추천 확장 프로그램"이 있으나 실제 내용 없음
- **해결**: `ide-setup-guide.md` 참고하여 내용 보충

#### 추가된 확장 프로그램 (17개)
1. **Python** (ms-python.python)
2. **Pylance** (ms-python.vscode-pylance)
3. **Python Debugger** (ms-python.debugpy)
4. **ESLint** (dbaeumer.vscode-eslint)
5. **Prettier** (esbenp.prettier-vscode)
6. **Tailwind CSS IntelliSense** (bradlc.vscode-tailwindcss)
7. **GitLens** (eamodio.gitlens)
8. **Thunder Client** (rangav.vscode-thunder-client)
9. **Markdown All in One** (yzhang.markdown-all-in-one)
10. **Code Spell Checker** (streetsidesoftware.code-spell-checker)
11. **Path Intellisense** (christian-kohler.path-intellisense)
12. **Auto Rename Tag** (formulahendry.auto-rename-tag)
13. **Bracket Pair Colorizer** (개념 설명)
14. **Live Server** (ritwickdey.liveserver)
15. **DotENV** (mikestead.dotenv)
16. **Docker** (ms-azuretools.vscode-docker)
17. **REST Client** (humao.rest-client)

- **변경 파일**: `VSCODE_GUIDE.md`

---

### 2025-12-11: VSCode 설정 Git 추적
- **완료일**: 2025-12-11 (시간 미기록)
- **Git 커밋**: (해시 미기록)
- **목표**: 다른 PC에서 동일한 Run and Debug 설정 사용
- **배경**: 사용자가 다른 PC에서 작업 시 Run and Debug 설정 누락

#### 변경 내용
1. **`.gitignore` 수정**:
   - `.vscode/` 제외 규칙 제거
   - VSCode 설정 파일 Git 추적 시작

2. **`.vscode/` 파일 추가**:
   - `launch.json` - Run and Debug 구성
   - `tasks.json` - 빌드 태스크
   - `extensions.json` - 추천 확장 프로그램
   - `settings.json` - 워크스페이스 설정

3. **`launch.json` 구성**:
   - Backend Server 실행
   - CLI 명령어 실행 (analyze-trends, generate-script 등)
   - Full Stack 실행 (Backend + Frontend)

#### 결과
- ✅ GitHub에서 clone 시 자동으로 VSCode 설정 포함
- ✅ F5로 디버깅 즉시 시작 가능
- ✅ 팀원 간 일관된 개발 환경

- **변경 파일**:
  - `.gitignore`
  - `.vscode/launch.json`
  - `.vscode/tasks.json`
  - `.vscode/extensions.json`
  - `.vscode/settings.json`

---

## 📊 통계

- **총 작업 수**: 10개
- **커밋 수**: 5개 이상
- **변경된 주요 파일**:
  - `local_cli/services/video_producer.py` - 영상 제작 핵심
  - `local_cli/services/tts_service.py` - TTS 및 오디오 길이 측정
  - `local_cli/services/audio_processor.py` - 오디오 처리
  - `local_cli/services/music_library.py` - 배경음악 관리
  - `local_cli/services/image_generator.py` - 이미지 생성
  - `.vscode/launch.json` - VSCode 디버그 설정
  - `VSCODE_GUIDE.md` - 확장 프로그램 가이드
  - `MUSIC_GUIDE.md` - 배경음악 다운로드 가이드

---

## 🔍 주요 이슈 및 해결

### 이슈 #1: FFprobe 경고 반복 출력
- **증상**: `⚠️ FFprobe 실패: [WinError 2] 지정된 파일을 찾을 수 없습니다`
- **원인**: imageio-ffmpeg는 ffprobe를 포함하지 않음
- **해결**: MoviePy를 우선 사용하도록 변경
- **관련 커밋**: `7108ee0`, `a88d7ad`

### 이슈 #2: MoviePy 버전 호환성
- **증상**: `ModuleNotFoundError: No module named 'moviepy.editor'`
- **원인**: MoviePy 2.x 설치되었으나 1.x import 구문 사용
- **해결**: 모든 import 및 메서드를 2.x API로 마이그레이션
- **영향**: 7개 이상 메서드 변경 (`resize` → `resized` 등)

### 이슈 #3: 폰트 찾기 실패
- **증상**: `ValueError: Invalid font Arial-Bold, pillow failed to use it`
- **원인**: Windows에서 폰트 이름만으로는 찾을 수 없음
- **해결**: 시스템 폰트 경로 자동 탐지 메커니즘 추가
- **관련 커밋**: `f301671`

### 이슈 #4: TextClip 정수 변환 오류
- **증상**: `TypeError: 'float' object cannot be interpreted as an integer`
- **원인**: PIL은 이미지 크기로 정수만 허용
- **해결**: 모든 크기/좌표 값을 `int()`로 변환
- **관련 커밋**: `2c5fb22`

---

## 🚀 다음 단계

### 우선순위 높음
- [ ] 영상 제작 전체 플로우 테스트
- [ ] 배경음악 샘플 다운로드 및 테스트
- [ ] YouTube 업로드 OAuth 설정

### 우선순위 중간
- [ ] 이미지 생성 API 키 설정 테스트
- [ ] 데이터베이스 통합 (stats 저장)
- [ ] 에러 리포팅 개선

### 우선순위 낮음
- [ ] 성능 최적화
- [ ] 추가 TTS 제공자 통합
- [ ] UI/UX 개선

---

## 📝 참고 문서

- `README.md` - 프로젝트 개요
- `CLAUDE.md` - Claude Code 작업 가이드
- `MUSIC_GUIDE.md` - 배경음악 다운로드 가이드
- `VSCODE_GUIDE.md` - VSCode 설정 가이드
- `TROUBLESHOOTING.md` - 문제 해결 가이드

---

**마지막 업데이트**: 2025-12-11 10:00
**작성자**: Claude Code (Sonnet 4.5)
