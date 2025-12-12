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

### 2025-12-12: 웹 UI 전면 개편 - 리믹스 시스템 적용
- **완료일**: 2025-12-12 14:27
- **Git 커밋**: `c31f90c`
- **목표**: 프론트엔드를 리믹스 시스템에 맞게 전면 재구성
- **배경**: Phase 3까지 완료 후, 웹 UI가 기존 AI 생성 시스템으로 되어 있어 사용 불가능
- **변경 파일**:
  - `backend/main.py` - 완전 새로 작성 (490줄)
  - `frontend/components/Sidebar.tsx` - 메뉴 변경
  - `frontend/app/page.tsx` - 대시보드 개편
  - `frontend/app/search/page.tsx` - 트렌딩 검색 페이지 (새로 작성)
  - `frontend/app/batch/page.tsx` - 배치 처리 페이지 (새로 작성)
  - `frontend/app/videos/page.tsx` - 영상 목록 페이지 (재작성)
  - `frontend/app/downloads/page.tsx` - 안내 페이지
  - `frontend/app/remix/page.tsx` - 안내 페이지
  - `WEB_UI_REMIX_GUIDE.md` - 웹 UI 사용 가이드 (새로 작성)

- **주요 내용**:
  1. **백엔드 API 완전 개편**:
     - 기존: 트렌드 분석 → 대본 생성 → 영상 제작
     - 신규: 영상 검색 → 다운로드 → 번역 → 리믹스
     - 엔드포인트: `/api/search/trending`, `/api/search/keywords`, `/api/download`, `/api/translate`, `/api/remix`, `/api/batch/start`, `/api/videos`
     - 배치 작업: 백그라운드 작업 지원 (BackgroundTasks)
     - 메타데이터 통합: MetadataManager 연동

  2. **프론트엔드 페이지 재구성**:
     - **대시보드**: 전체/완료/처리중/실패 통계, 빠른 작업
     - **영상 검색**: 트렌딩/키워드 탭, 다운로드 버튼
     - **배치 처리**: 자동 리믹스 설정, 실시간 상태 모니터링
     - **영상 목록**: 상태별 필터, 삭제 기능, 파일 정보
     - **사이드바**: 7개 메뉴 (대시보드/검색/다운로드/리믹스/배치/영상목록/설정)

  3. **새 기능**:
     - 실시간 배치 작업 상태 (3초 폴링)
     - 영상 상태 배지 (색상 코딩)
     - 원본 영상 정보 표시 (채널, 조회수, 길이)
     - 번역 제목 표시
     - 파일 경로 상세 보기 (펼치기)

  4. **사용자 경험**:
     - 탭 기반 검색 (트렌딩 vs 키워드)
     - 확인 대화상자
     - 로딩 인디케이터
     - 반응형 디자인 (Tailwind CSS)

#### 페이지 흐름
```
대시보드 → 영상 검색 → 다운로드 → (자동 번역) → (자동 리믹스) → 영상 목록
            ↓
       배치 처리 (자동으로 모든 과정 실행)
```

#### API 엔드포인트 (9개)
1. `GET /api/stats` - 대시보드 통계
2. `POST /api/search/trending` - 트렌딩 검색
3. `POST /api/search/keywords` - 키워드 검색
4. `POST /api/download` - 영상 다운로드
5. `POST /api/translate` - 자막 번역
6. `POST /api/remix` - 영상 리믹스
7. `POST /api/batch/start` - 배치 시작
8. `GET /api/batch/status/{job_id}` - 배치 상태
9. `GET /api/videos` - 영상 목록
10. `DELETE /api/videos/{video_id}` - 영상 삭제

---

### 2025-12-12: Phase 3 - 트렌딩 검색 & 자동화 구현
- **완료일**: 2025-12-12 14:14
- **Git 커밋**: `31211c2`
- **목표**: YouTube 트렌딩 검색 및 전체 워크플로우 자동화
- **배경**: Phase 2 완료 후, 영상 자동 발굴 및 배치 처리 필요
- **새 파일**:
  - `local_cli/services/trending_searcher.py` (400줄) - YouTube 트렌딩 검색
  - `batch_remix.py` (300줄) - 배치 자동 처리
  - `test_phase3_integration.py` (190줄) - Phase 3 통합 테스트
- **수정 파일**:
  - `local_cli/main.py` - 5개 CLI 명령어 추가
- **주요 내용**:
  1. **TrendingSearcher 클래스**:
     - YouTube Data API v3 통합
     - 트렌딩 영상 검색 (지역, 카테고리별)
     - 키워드 검색 (정렬: 조회수, 날짜, 관련성)
     - 필터링: 영상 길이 (short/medium/long), 최소 조회수, 자막 유무
     - 정렬: 조회수, 참여도 (좋아요 + 댓글)
     - 숏폼/롱폼 필터링 함수
     - ISO 8601 duration 파싱 (PT1H2M3S → 초)
  2. **RemixBatchProcessor 클래스**:
     - 전체 워크플로우 자동화
     - 트렌딩 검색 → 다운로드 → 번역 → 리믹스
     - 이미 처리된 영상 자동 스킵
     - API 한도 보호 (1초 대기)
     - 통계 추적 (검색, 다운로드, 번역, 리믹스, 실패)
  3. **CLI 통합 (5개 명령어)**:
     - `search-trending`: 트렌딩 영상 검색
     - `download-video <url>`: 영상 + 자막 다운로드
     - `translate-subtitle <file>`: SRT 자막 번역
     - `remix-video <video> <subtitle>`: 영상 + 자막 합성
     - `batch-remix`: 전체 자동 처리
  4. **통합 테스트**:
     - 트렌딩 검색: Science & Technology (미국)
     - 키워드 검색: "AI technology" (3개 결과)
     - 필터링: 10개 중 9개 숏폼 추출
     - 메타데이터 연동 확인

#### 테스트 결과
```
키워드 검색: 3개 영상 발견
- 조회수: 3,594만 ~ 1,648만
필터링: 10개 → 9개 숏폼 (≤60초)
메타데이터: 1개 영상 (pending)
```

#### CLI 사용 예시
```bash
# 1. 트렌딩 검색
python local_cli/main.py search-trending --region US --category "Science & Technology"

# 2. 배치 처리
python local_cli/main.py batch-remix --max-videos 3 --duration short

# 3. 배치 스크립트 직접 실행
python batch_remix.py --region US --max-videos 5 --min-views 50000
```

---

### 2025-12-12: Phase 2 - 리믹스 시스템 메타데이터 & 영상 합성 구현
- **완료일**: 2025-12-12 11:59
- **Git 커밋**: `bc7b2f0`
- **목표**: YouTube 리믹스 시스템의 메타데이터 관리 및 영상 합성 기능 구현
- **배경**: Phase 1 (다운로드 + 번역) 완료 후, 출처 기록 및 영상 리믹스 기능 필요
- **새 파일**:
  - `local_cli/services/metadata_manager.py` (280줄) - 메타데이터 관리
  - `local_cli/services/video_remixer.py` (350줄) - 영상 + 자막 합성
  - `test_phase2_integration.py` (250줄) - Phase 2 통합 테스트
  - `metadata/videos.json` - 메타데이터 DB
- **주요 내용**:
  1. **MetadataManager 클래스**:
     - JSON 기반 영상 메타데이터 저장/조회
     - 출처 정보, 저작권 정보, 처리 상태 추적
     - 출처 표시 텍스트 자동 생성 (full/short/markdown)
     - 전체 통계 조회 (상태별 개수, 총 조회수 등)
     - 영상 삭제 시 관련 파일 자동 정리
  2. **VideoRemixer 클래스**:
     - MoviePy 기반 원본 영상 + 번역 자막 합성
     - SRT 타임스탬프 정확히 보존
     - 텍스트 길이에 따른 자동 폰트 크기 조정 (30-48px)
     - 자막 위치 자동 설정 (하단 중앙, 영상 크기의 95%)
     - 출처 표시 오버레이 추가 (시작/끝)
     - 롱폼 → 숏폼 클립 추출 기능
  3. **통합 테스트**:
     - 전체 워크플로우 검증 (영상 정보 → 메타데이터 → 출처 표시)
     - "Me at the zoo" 테스트 케이스 (3억 7천만 뷰)
     - 실제 다운로드/번역/합성은 주석 처리 (용량 고려)

#### 테스트 결과
```
전체 영상: 1개
상태별: {'pending': 1}
영상: Me at the zoo (jNQXAC9IVRw)
출처: Original: "Me at the zoo" by jawed
```

#### 다음 단계
- Phase 3: 트렌딩 검색 기능 (trending_searcher.py)
- Phase 4: CLI 통합 및 배치 처리
- Phase 5: 웹 UI

---

### 2025-12-11: 대본 길이 자동 분할 기능 추가
- **완료일**: 2025-12-11 15:48
- **Git 커밋**: `faf9aff`
- **목표**: 너무 긴 텍스트를 문장 단위로 자동 분할하여 자연스러운 TTS 생성
- **배경**: 120자 이상의 긴 대본은 한 번에 읽으면 부자연스럽고, 영상도 길어짐
- **변경 파일**:
  - `local_cli/services/tts_service.py:348-408`
- **주요 내용**:
  1. **자동 분할 로직**: 120자 이상 텍스트를 문장 단위로 분할
  2. **`_split_into_sentences()` 메서드 추가**:
     - 한국어/영어 문장 구분자 지원: `. ! ? 。 ！ ？`
     - 정규식 패턴: `r'([.!?。！？]+\s*)'`
     - 구분자와 텍스트를 함께 유지
  3. **세그먼트 인덱싱 개선**: `segment_index` 변수로 분할된 문장도 올바르게 인덱싱
  4. **각 문장이 별도 오디오 파일**로 생성되어 더 자연스러운 영상 제작

#### 코드 예시
```python
# 120자 이상 텍스트 자동 분할
if len(text_clean) > 120:
    sentences = self._split_into_sentences(text_clean)
    for sentence in sentences:
        # 각 문장을 별도 오디오 파일로 생성
        output_path = os.path.join(output_dir, f"segment_{segment_index}.mp3")
        self.generate_speech(sentence.strip(), output_path)
        segment_index += 1
```

---

### 2025-12-11: 이미지 생성 그라데이션 배경 개선
- **완료일**: 2025-12-11 15:30
- **Git 커밋**: `43e8a94`
- **목표**: 단색 배경을 그라데이션과 텍스트가 있는 시각적으로 매력적인 이미지로 개선
- **배경**: 기존 단색 배경이 너무 평범하고 전문적이지 않음
- **변경 파일**:
  - `local_cli/services/video_producer.py:37-40` - 이미지 생성 기본 활성화
  - `local_cli/services/image_generator.py:237-326` - 그라데이션 배경 구현
- **주요 내용**:
  1. **그라데이션 배경**: 5가지 색상 조합 (파란색, 핑크/보라, 청록, 주황, 보라)
  2. **키워드 추출**: 텍스트에서 처음 3-5단어 추출하여 이미지에 표시
  3. **한글 폰트 지원**: 맑은 고딕(Malgun Gothic) 사용
  4. **텍스트 효과**:
     - 그림자 효과 (shadow_offset=4)
     - 동적 폰트 크기 조절 (화면 너비 초과 시 자동 축소)
     - 중앙 정렬
  5. **IMAGE_PROVIDER 기본값**: `'none'` → `'text'`로 변경

#### 시각적 개선
- Before: 단색 배경 (50, 50, 100)
- After: 그라데이션 배경 + 큰 텍스트 + 그림자 효과

---

### 2025-12-11: 자막 () 효과음 제거 및 길이 조절 기능 추가
- **완료일**: 2025-12-11 15:20
- **Git 커밋**: `c64e2d6`
- **목표**: 자막에서 효과음 표시 제거 및 긴 자막 잘림 현상 수정
- **배경**:
  - (박수 소리), (웃음) 등이 자막과 TTS에 출력되어 부자연스러움
  - 긴 자막이 화면을 벗어나서 잘림
- **변경 파일**:
  - `local_cli/services/tts_service.py:339-346` - () 효과음 제거
  - `local_cli/services/video_producer.py:344-377` - 동적 폰트 크기

#### 1. () 효과음 제거
```python
# 정규식으로 () 안의 내용 모두 제거
text_clean = re.sub(r'\([^)]*\)', '', text).strip()

# 효과음만 있고 실제 텍스트가 없으면 건너뛰기
if not text_clean:
    continue
```

#### 2. 자막 길이 조절
- **동적 폰트 크기**:
  - 숏폼: <30자=45px, 30-60자=38px, 60+자=32px
  - 긴 영상: <40자=48px, 40-80자=40px, 80+자=34px
- **자막 너비**: 85% → **90%**로 증가
- **자막 위치**: 숏폼 75%, 긴 영상 85%

---

### 2025-12-11: 인기 배경음악 TOP 10 추천 목록 추가
- **완료일**: 2025-12-11 14:40
- **Git 커밋**: `cce5174`
- **목표**: 사용자가 쉽게 배경음악을 찾고 다운로드할 수 있도록 추천 목록 제공
- **변경 파일**:
  - `MUSIC_GUIDE.md` - TOP 10 섹션 추가
- **내용**:
  - Pixabay & YouTube Audio Library에서 엄선한 10곡
  - 장르별 분류: Ambient 3곡, Upbeat 3곡, Cinematic 2곡, Electronic 2곡
  - 각 곡의 다운로드 링크, 길이, 분위기, 추천 용도 포함

---

### 2025-12-11: TTS 목소리 선택 기능 추가
- **완료일**: 2025-12-11 14:39
- **Git 커밋**: `6d3609b`
- **목표**: 설정 페이지에서 TTS 언어, 속도, 피치를 선택하고 테스트할 수 있게 함
- **변경 파일**:
  - `frontend/app/settings/page.tsx` - TTS 설정 UI 추가
  - `backend/main.py` - `/api/tts/test` 엔드포인트 추가
  - `local_cli/services/tts_service.py` - `_generate_gtts_with_lang()` 메서드 추가

#### 주요 기능
1. **언어 선택**: 한국어, 영어, 일본어, 중국어, 스페인어, 프랑스어
2. **속도 조절**: 0.5x ~ 2.0x 슬라이더
3. **피치 조절**: -5 ~ +5 슬라이더
4. **테스트 버튼**: 현재 설정으로 "안녕하세요. TTS 테스트 음성입니다." 재생

#### 기술 구현
- FFmpeg `atempo` 필터로 속도 조절
- FFmpeg `asetrate` + `aresample`로 피치 조절
- FastAPI FileResponse로 MP3 스트리밍

---

### 2025-12-11: 영상 제작 버그 4개 수정 및 TTS 속도 개선
- **완료일**: 2025-12-11 14:36
- **Git 커밋**: `bb80c62`
- **목표**: 영상 제작 시 발생하는 모든 오류 수정 및 TTS 템포 개선

#### 1. 썸네일 RGBA→JPEG 변환 오류 수정
- **문제**: `cannot write mode RGBA as JPEG`
- **해결**: PIL로 RGBA를 RGB로 변환 후 JPEG 저장
- **코드**: `video_producer.py:142-153`

#### 2. 비주얼 클립 이미지 깨짐 수정
- **문제**: ColorClip 사용 시 영상 재생 중 이미지 깨짐
- **해결**: PIL로 단색 이미지 생성 → numpy array → ImageClip 변환
- **코드**: `video_producer.py:215-223`

#### 3. 숏폼 자막 잘림 현상 수정
- **문제**: 9:16 크롭 후 자막이 화면 아래쪽에서 잘림
- **해결**:
  - 크롭을 자막 추가 전에 먼저 수행
  - 자막 위치를 75%(숏폼)/85%(긴 영상)로 조정
  - 자막 크기를 85%로 줄여 여백 확보
- **코드**: `video_producer.py:332-371`

#### 4. TTS 템포 20% 빠르게 조정
- **문제**: 기본 TTS 속도가 너무 느림
- **해결**: FFmpeg `atempo` 필터로 1.2배 속도 적용
- **코드**: `tts_service.py:116-163`

---

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

- **총 작업 수**: 19개 (오늘 9개 추가)
- **커밋 수**: 14개
- **오늘 작업 (2025-12-11)**:
  - ✅ 9개 작업 완료
  - ✅ 8개 커밋
  - ✅ 버그 7개 수정 (자막 2개, 이미지 1개, 기존 4개)
  - ✅ 새 기능 3개 추가 (대본 자동 분할, 기존 2개)
- **변경된 주요 파일**:
  - `local_cli/services/tts_service.py` - TTS, 오디오 길이 측정, () 효과음 제거, 대본 자동 분할
  - `local_cli/services/video_producer.py` - 영상 제작 핵심, 자막 길이 조절, 이미지 생성 활성화
  - `local_cli/services/image_generator.py` - 이미지 생성 (그라데이션 배경 개선)
  - `local_cli/services/audio_processor.py` - 오디오 처리
  - `local_cli/services/music_library.py` - 배경음악 관리
  - `frontend/app/settings/page.tsx` - TTS 설정 UI 추가
  - `backend/main.py` - TTS 테스트 API 추가
  - `.vscode/launch.json` - VSCode 디버그 설정
  - `VSCODE_GUIDE.md` - 확장 프로그램 가이드
  - `MUSIC_GUIDE.md` - 배경음악 다운로드 가이드 + TOP 10 추가
  - `WORK_LOG.md` - 작업 기록
  - `WORKFLOW_GUIDE.md` - 워크플로우 가이드

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

**마지막 업데이트**: 2025-12-11 15:50
**작성자**: Claude Code (Sonnet 4.5)
