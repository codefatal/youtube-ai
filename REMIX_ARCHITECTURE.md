# YouTube 영상 리믹스 시스템 아키텍처

> 해외 인기 영상을 번역하여 한국어 자막 숏폼/롱폼 제작

마지막 업데이트: 2025-12-12 (Phase 2 완료)

---

## 🎯 목표

기존: AI 트렌드 분석 → 대본 생성 → 이미지 생성 → 영상 합성
**신규: 해외 인기 영상 다운로드 → 번역 → 자막 합성 → 출처 명시**

### 핵심 가치
- ✅ **고품질 보장**: 이미 검증된 인기 영상 사용
- ✅ **빠른 제작**: 다운로드 → 번역 → 합성 (단순)
- ✅ **저작권 준수**: 출처 명시 + Creative Commons 우선
- ✅ **대량 생산**: 하루 10-20개 영상 자동 처리

---

## 📊 새로운 워크플로우

```
1. [검색] 트렌딩 영상 검색 (YouTube Data API)
   ↓
2. [다운로드] 영상 + 자막 다운로드 (yt-dlp)
   ↓
3. [번역] 자막/제목/설명 번역 (Gemini API)
   ↓
4. [합성] 원본 영상 + 번역 자막 합성 (MoviePy)
   ↓
5. [기록] 출처 및 메타데이터 저장 (JSON/SQLite)
   ↓
6. [업로드] YouTube 업로드 + 출처 명시
```

---

## 🗂️ 새로운 파일 구조

```
local_cli/services/
├── youtube_downloader.py      # NEW: yt-dlp 기반 영상/자막 다운로드
├── subtitle_translator.py     # NEW: SRT 자막 번역 (Gemini)
├── metadata_manager.py         # NEW: 출처/메타데이터 관리
├── video_remixer.py            # NEW: 영상 + 번역 자막 합성
├── trending_searcher.py        # NEW: 트렌딩 영상 검색
│
├── ai_service.py               # KEEP: Gemini/Claude 통합
├── youtube_uploader.py         # KEEP: 업로드 (출처 명시 추가)
└── (기타 기존 파일들)

downloads/                      # NEW: 다운로드된 원본 영상
├── {video_id}.mp4
├── {video_id}.en.srt
└── {video_id}.info.json

remixed/                        # NEW: 번역 합성된 영상
├── {video_id}_ko.mp4
└── {video_id}_ko.srt

metadata/                       # NEW: 메타데이터 (출처 기록)
└── videos.json
```

---

## 🎬 메타데이터 스키마

각 영상마다 저장되는 정보:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "original": {
    "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
    "title": "Amazing AI Technology Explained",
    "description": "In this video, we explore...",
    "channel_name": "Tech Insider",
    "channel_url": "https://youtube.com/@techinsider",
    "views": 1500000,
    "likes": 50000,
    "duration": 62,
    "upload_date": "2024-11-15",
    "license": "Creative Commons Attribution",
    "category": "Science & Technology",
    "tags": ["AI", "technology", "explained"]
  },
  "translated": {
    "title": "놀라운 AI 기술 설명",
    "description": "이 영상에서는 AI 기술을...",
    "subtitle_path": "./downloads/dQw4w9WgXcQ.ko.srt"
  },
  "processing": {
    "download_date": "2025-12-12T10:30:00",
    "translation_date": "2025-12-12T10:35:00",
    "remix_date": "2025-12-12T10:40:00",
    "status": "completed"
  },
  "files": {
    "original_video": "./downloads/dQw4w9WgXcQ.mp4",
    "original_subtitle": "./downloads/dQw4w9WgXcQ.en.srt",
    "translated_subtitle": "./downloads/dQw4w9WgXcQ.ko.srt",
    "remixed_video": "./remixed/dQw4w9WgXcQ_ko.mp4"
  },
  "copyright": {
    "attribution": "Original: Amazing AI Technology Explained by Tech Insider",
    "license": "CC-BY 3.0",
    "commercial_use": true,
    "modifications": true
  }
}
```

---

## 🛠️ 핵심 모듈 상세

### 1. `youtube_downloader.py`

**기능:**
- yt-dlp로 영상 다운로드
- 자동 자막 추출 (en, en-US 등)
- 메타데이터 추출 (제목, 설명, 채널, 조회수 등)

**주요 메서드:**
```python
class YouTubeDownloader:
    def download_video(url: str) -> dict
    def extract_subtitles(video_id: str) -> str
    def get_video_info(url: str) -> dict
    def search_trending(region: str, category: str, max_results: int) -> list
```

**의존성:**
- `yt-dlp` (설치 필요)
- `youtube-data-api` (이미 있음)

---

### 2. `subtitle_translator.py`

**기능:**
- SRT 파일 파싱
- Gemini API로 각 라인 번역
- 타임스탬프 유지
- 번역된 SRT 저장

**주요 메서드:**
```python
class SubtitleTranslator:
    def __init__(ai_service: AIService)
    def parse_srt(srt_path: str) -> list
    def translate_subtitle(subtitle_text: str, target_lang: str) -> str
    def save_srt(subtitles: list, output_path: str)
    def translate_file(input_srt: str, output_srt: str, target_lang: str)
```

**SRT 형식:**
```srt
1
00:00:00,000 --> 00:00:03,500
Hello, welcome to this amazing video!

2
00:00:03,500 --> 00:00:07,000
Today we're going to explore AI technology.
```

---

### 3. `metadata_manager.py`

**기능:**
- 영상별 메타데이터 저장/조회
- 출처 정보 관리
- JSON 또는 SQLite 기반

**주요 메서드:**
```python
class MetadataManager:
    def save_video_metadata(video_data: dict)
    def get_video_metadata(video_id: str) -> dict
    def list_videos(status: str = None) -> list
    def generate_attribution_text(video_id: str) -> str
    def update_status(video_id: str, status: str)
```

**Attribution 예시:**
```
원본 영상: "Amazing AI Technology Explained" by Tech Insider
출처: https://youtube.com/watch?v=dQw4w9WgXcQ
라이선스: Creative Commons Attribution (CC-BY 3.0)
```

---

### 4. `video_remixer.py`

**기능:**
- 원본 영상 + 번역 자막 합성
- 자막 스타일 적용 (기존 MoviePy 코드 재사용)
- 인트로/아웃트로 추가 (선택)

**주요 메서드:**
```python
class VideoRemixer:
    def add_translated_subtitles(
        video_path: str,
        subtitle_path: str,
        output_path: str,
        style: dict
    ) -> str

    def add_attribution_overlay(
        video_path: str,
        attribution_text: str,
        output_path: str
    ) -> str
```

---

### 5. `trending_searcher.py`

**기능:**
- YouTube Data API로 트렌딩 영상 검색
- 필터링 (조회수, 길이, 카테고리)
- 자막 유무 확인

**주요 메서드:**
```python
class TrendingSearcher:
    def search_trending_shorts(
        region: str = 'US',
        category: str = 'Science & Technology',
        max_results: int = 10
    ) -> list

    def filter_by_duration(videos: list, min_sec: int, max_sec: int) -> list
    def filter_by_subtitles(videos: list) -> list
    def filter_by_license(videos: list, license_type: str = 'creativeCommon') -> list
```

---

## 🔄 데이터 흐름

```
[사용자] "미국 트렌딩 AI 영상 5개 리믹스"
    ↓
[TrendingSearcher] YouTube API 검색
    → 결과: [video1, video2, video3, video4, video5]
    ↓
[YouTubeDownloader] 각 영상 다운로드
    → downloads/video1.mp4
    → downloads/video1.en.srt
    → downloads/video1.info.json
    ↓
[SubtitleTranslator] 자막 번역
    → downloads/video1.ko.srt
    ↓
[MetadataManager] 출처 정보 저장
    → metadata/videos.json
    ↓
[VideoRemixer] 영상 + 번역 자막 합성
    → remixed/video1_ko.mp4
    ↓
[YouTubeUploader] 업로드 (출처 명시)
    → YouTube에 게시
```

---

## 📝 업로드 시 설명 템플릿

```markdown
[번역된 제목]

[번역된 설명]

---
📌 원본 영상 정보
제목: [원본 제목]
채널: [채널명]
출처: [YouTube URL]
라이선스: [라이선스 유형]

이 영상은 원작자의 허가 하에 번역 및 재업로드되었습니다.
Original video translated and reuploaded with permission.

#[태그1] #[태그2] #한국어자막 #번역
```

---

## ⚖️ 저작권 준수 전략

### 우선순위

1. **Creative Commons 영상 우선**
   - YouTube 검색 필터: `creativeCommon`
   - 상업적 이용 가능
   - 수정 가능
   - Attribution만 표시

2. **Fair Use 원칙**
   - 교육 목적 명시
   - 원작자 크레딧 명시
   - 변형적 사용 (번역, 자막)

3. **리스크 관리**
   - 저작권 신고 시 즉시 삭제
   - 3번 신고 = 채널 정지 주의
   - 백업 채널 운영 고려

---

## 🚀 구현 단계

### Phase 1: 기본 기능 ✅ 완료 (2025-12-12)
- [x] `youtube_downloader.py` 구현
- [x] `subtitle_translator.py` 구현
- [x] 1개 영상 테스트 (다운로드 → 번역 → 확인)

### Phase 2: 메타데이터 & 영상 합성 ✅ 완료 (2025-12-12)
- [x] `metadata_manager.py` 구현
- [x] `video_remixer.py` 구현
- [x] 출처 정보 저장
- [x] Attribution 텍스트 생성
- [x] 번역 자막 스타일 적용
- [x] 통합 테스트 (test_phase2_integration.py)

### Phase 3: 트렌딩 검색 & 자동화 (예정)
- [ ] `trending_searcher.py` 구현
- [ ] YouTube Data API 트렌딩 검색
- [ ] Creative Commons 필터링
- [ ] 배치 처리 스크립트
- [ ] CLI 통합

### Phase 4: 웹 UI (예정)
- [ ] 영상 검색 페이지
- [ ] 다운로드 진행 상황
- [ ] 메타데이터 관리 페이지
- [ ] 업로드 페이지 (출처 자동 입력)

---

## 🔧 필요한 의존성

```bash
# 새로 설치 필요
pip install yt-dlp
pip install pysrt  # SRT 파싱

# 이미 있음
# - google-genai (번역)
# - moviepy (합성)
# - google-api-python-client (YouTube API)
```

---

## 📊 예상 성과

### 기존 방식
- 영상 1개 제작: 30-60분
- 품질: 불안정 (AI 이미지)
- 비용: API 호출 많음

### 새 방식
- 영상 1개 제작: 5-10분
- 품질: 고품질 (원본 영상)
- 비용: 번역만 (Gemini 무료)
- 대량 생산: 하루 20-30개 가능

---

## ⚠️ 주의사항

1. **저작권**: Creative Commons 우선, 항상 출처 명시
2. **API 한도**: YouTube Data API 하루 10,000 quota
3. **스토리지**: 영상 파일 용량 관리 (자동 삭제 설정)
4. **품질**: 저해상도 영상 필터링 (최소 720p)
5. **언어**: 자막 있는 영상만 선택

---

## 📚 관련 문서

- `README.md` - 전체 프로젝트 개요
- `CLAUDE.md` - 개발 가이드
- `WORK_LOG.md` - 작업 기록
- `API_DOCS.md` - API 문서 (추가 예정)
