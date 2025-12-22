# 프로젝트 현황 (2025-12-22)

## 📊 전체 시스템 상태

### ✅ 완전 구현 완료 (Production Ready)

**리믹스 시스템 (Phase 1-3 완료)**
- [x] YouTube 트렌딩 영상 검색 (14개 카테고리)
- [x] 키워드 기반 영상 검색 (영상 길이, 최소 조회수 필터)
- [x] 영상 + 자막 다운로드 (yt-dlp)
- [x] SRT 자막 번역 (Gemini API, 타임스탬프 유지)
- [x] 영상 리믹스 (번역 자막 합성)
- [x] 메타데이터 자동 관리 (출처 기록)
- [x] 배치 자동화 (검색 → 다운로드 → 번역 → 리믹스)
- [x] **하드코딩 자막 처리** (OCR 추출 → 번역 → 재인코딩) - NEW!

**웹 UI (전면 개편 완료)**
- [x] 대시보드 (통계)
- [x] 영상 검색 페이지 (트렌딩/키워드)
- [x] 다운로드 관리
- [x] 영상 목록 (상태 필터링)
- [x] 배치 처리 (실시간 진행 모니터링)
- [x] 설정 (localStorage)
- [x] 하드코딩 자막 처리 버튼 (영상 목록)

**Backend API**
- [x] 모든 엔드포인트 구현
- [x] CORS 설정
- [x] 백그라운드 작업 (배치, OCR)
- [x] Job 상태 추적

**CLI**
- [x] 5개 리믹스 명령어
- [x] 테스트 스크립트

---

## 🚀 최근 업데이트 (2025-12-22)

### 1. 카테고리 확장
- 4개 → 14개 카테고리로 확장
- 추가된 카테고리: 게임, 스포츠, 뉴스/정치, 생활/노하우, 영화/애니메이션, 코미디, 사람/블로그, 자동차, 동물, 여행/이벤트

### 2. 키워드 검색 개선
- 영상 길이 필터 추가 (전체/숏폼/중간/롱폼)
- 최소 조회수 필터 추가
- 프론트엔드 UI 업데이트

### 2-1. 날짜 범위 검색 & 정렬 기능 추가 (NEW!)
**백엔드:**
- `trending_searcher.py`: `published_after`, `published_before`, `order` 파라미터 추가
- 트렌딩 검색에 search() API 사용 (날짜 범위/정렬 지원)
- 키워드 검색에 날짜 범위 파라미터 추가
- RFC 3339 형식 날짜 지원

**프론트엔드:**
- 트렌딩 검색: 정렬 옵션 (조회수/날짜/평점/관련성) + 날짜 범위 선택
- 키워드 검색: 정렬 옵션 (평점 추가) + 날짜 범위 선택
- 날짜 입력 필드 (type="date")로 RFC 3339 자동 변환

**사용 예시:**
- "2024년 1월 이후 업로드된 AI 관련 영상만 검색"
- "최근 1주일 내 조회수 10만 이상 숏폼 검색"
- "날짜순 정렬로 최신 트렌드 파악"

### 3. 하드코딩 자막 처리 구현 (NEW!)
**파일:**
- `local_cli/services/hardcoded_subtitle_processor.py` (489 라인)
- `test_hardcoded_subtitle.py` (테스트 스크립트)
- Backend API 엔드포인트 추가
- 프론트엔드 스캔 버튼 추가

**기능:**
- EasyOCR로 영상 내 자막 추출
- 자막 위치, 색상, 크기 분석
- 원본 자막 제거 (검은 박스)
- 번역 자막 재인코딩 (흰색 테두리 + 원본 스타일 유지)

**처리 과정:**
1. OCR로 자막 추출 (하단 30% 영역)
2. 자막 속성 분석 (bbox, color, font_size)
3. SRT 파일 생성
4. Gemini API로 번역
5. 원본 자막 영역 마스킹
6. 번역 자막 합성

**필요 패키지:**
```bash
pip install easyocr opencv-python-headless torch torchvision
```

### 4. 문서 업데이트
- `README.md` - 완전히 새로 작성 (리믹스 시스템 설명)
- `CLAUDE.md` - 하드코딩 자막 처리 추가
- `requirements.txt` - OCR 패키지 추가

---

## 🏗️ 아키텍처 개요

### Backend Services (16개)
```
local_cli/services/
├── ai_service.py                    # Gemini/Claude API 통합
├── trend_analyzer.py                 # YouTube 트렌드 분석 (구 시스템)
├── script_generator.py               # AI 대본 생성 (구 시스템)
├── tts_service.py                    # TTS (구 시스템)
├── audio_processor.py                # 오디오 처리 (구 시스템)
├── music_library.py                  # 배경음악 (구 시스템)
├── video_producer.py                 # 영상 합성 (구 시스템)
├── youtube_uploader.py               # YouTube 업로드 (구 시스템)
├── image_generator.py                # 이미지 생성 (구 시스템)
│
├── trending_searcher.py              # ⭐ 트렌딩/키워드 검색 (리믹스)
├── youtube_downloader.py             # ⭐ yt-dlp 다운로드 (리믹스)
├── subtitle_translator.py            # ⭐ 자막 번역 (리믹스)
├── video_remixer.py                  # ⭐ 영상 리믹스 (리믹스)
├── metadata_manager.py               # ⭐ 메타데이터 관리 (리믹스)
└── hardcoded_subtitle_processor.py   # ⭐ 하드코딩 자막 처리 (리믹스) - NEW!
```

### Frontend Pages (7개)
```
frontend/app/
├── page.tsx           # 대시보드
├── search/page.tsx    # ⭐ 영상 검색 (트렌딩/키워드)
├── videos/page.tsx    # ⭐ 영상 목록 (하드코딩 자막 버튼 포함)
├── batch/page.tsx     # ⭐ 배치 처리
├── downloads/page.tsx # 다운로드 안내
├── remix/page.tsx     # 리믹스 안내
└── settings/page.tsx  # 설정
```

### API Endpoints (13개)
```
기본:
- GET  /api/stats

검색:
- POST /api/search/trending          # 트렌딩 검색
- POST /api/search/keywords           # 키워드 검색

다운로드/처리:
- POST /api/download                  # 영상 다운로드
- POST /api/translate                 # 자막 번역
- POST /api/remix                     # 영상 리믹스
- POST /api/hardcoded-subtitle/process # 하드코딩 자막 처리 (NEW!)

배치:
- POST /api/batch/start               # 배치 시작
- GET  /api/batch/status/{job_id}    # 배치 상태

영상 관리:
- GET    /api/videos                  # 영상 목록
- GET    /api/videos/{video_id}      # 영상 상세
- DELETE /api/videos/{video_id}      # 영상 삭제
```

---

## 🔄 시스템 전환 내역

### 구 시스템 (AI 자동 생성) → 리믹스 시스템
**전환 일시:** 2025-12-11

**구 시스템 (Phase 1-2):**
- AI가 트렌드 분석 → 대본 생성 → TTS → 이미지 생성 → 영상 합성
- 문제: 품질 불안정, 복잡한 파이프라인, 비용 발생

**신 시스템 (리믹스 시스템, Phase 1-3):**
- YouTube 검색 → 다운로드 → 자막 번역 → 리믹스
- 장점: 검증된 고품질 영상, 간단한 파이프라인, 완전 무료

**마이그레이션 상태:**
- 구 시스템 코드: 유지 (호환성)
- 신 시스템 코드: 완전 구현
- 웹 UI: 신 시스템 전용으로 개편
- CLI: 구/신 시스템 모두 지원

---

## 📈 기능 완성도

| 기능 | 상태 | 완성도 | 비고 |
|------|------|--------|------|
| **트렌딩 검색** | ✅ 완료 | 100% | 14개 카테고리, 필터링, 날짜 범위, 정렬 |
| **키워드 검색** | ✅ 완료 | 100% | 영상 길이, 조회수 필터, 날짜 범위, 정렬 |
| **영상 다운로드** | ✅ 완료 | 100% | yt-dlp, SRT 자막 포함 |
| **자막 번역** | ✅ 완료 | 100% | Gemini API, 타임스탬프 유지 |
| **영상 리믹스** | ✅ 완료 | 100% | MoviePy 2.x |
| **하드코딩 자막** | ✅ 완료 | 90% | OCR 정확도는 영상에 따라 다름 |
| **메타데이터 관리** | ✅ 완료 | 100% | JSON 기반, 출처 자동 기록 |
| **배치 자동화** | ✅ 완료 | 100% | 백그라운드 작업, 상태 추적 |
| **웹 UI** | ✅ 완료 | 100% | Next.js 14, 반응형 |
| **Backend API** | ✅ 완료 | 100% | FastAPI, CORS |
| **CLI** | ✅ 완료 | 100% | Click 기반 |
| **YouTube 업로드** | ⚠️ 구현됨 | 80% | OAuth 2.0 설정 필요 |
| **통계/대시보드** | ⚠️ 부분 | 50% | 하드코딩된 값, DB 미연결 |

---

## ⚠️ 알려진 제한사항

### 1. OCR 정확도
- **문제**: 폰트, 배경, 해상도에 따라 정확도 차이
- **해결책**: 고품질 영상 선택, 샘플링 간격 조정

### 2. YouTube API 할당량
- **제한**: 하루 10,000 유닛
- **사용량**: 검색 1회 = 100 유닛
- **해결책**: `max_results` 조절, 캐싱

### 3. 하드코딩 자막 처리 시간
- **소요 시간**: 1분 영상 ≈ 5-10분 (OCR)
- **해결책**: 백그라운드 작업, SRT 자막 우선 사용

### 4. 저작권
- **위험**: 일반 영상 재업로드 시 저작권 침해
- **해결책**: Creative Commons 영상만 사용, 출처 명시

### 5. 패키지 설치
- **문제**: EasyOCR, OpenCV 빌드 오류 (Visual Studio 요구)
- **해결책**: `--no-deps` 옵션 사용, wheel 파일 설치

---

## 🎯 다음 작업 (선택)

### 우선순위 높음
- [ ] Creative Commons 필터 기본값으로 설정
- [ ] OCR 성능 최적화 (샘플링, 멀티프로세싱)
- [ ] 통계 데이터베이스 연결

### 우선순위 중간
- [ ] YouTube 업로드 OAuth 간소화
- [ ] 배치 작업 스케줄러 (cron 통합)
- [ ] 영상 미리보기 기능

### 우선순위 낮음
- [ ] 다중 언어 번역 지원
- [ ] 커스텀 자막 스타일
- [ ] 영상 편집 기능 (트림, 크롭)

---

## 📦 배포 상태

**개발 환경:**
- Python 3.14
- Node.js 18+
- Windows/Linux/Mac 지원

**필요 서비스:**
- Gemini API (무료)
- YouTube Data API v3 (무료, 할당량 제한)

**선택 서비스:**
- Claude API (유료)

**배포 방법:**
- 로컬 실행 (개발 모드)
- Docker (준비 중)
- 클라우드 배포 (AWS, GCP - 준비 중)

---

## 📊 시스템 통계

**코드 라인 수:**
- Backend Services: ~7,000 라인
- Frontend: ~2,000 라인
- CLI: ~1,000 라인

**파일 수:**
- Python: 16 services + 테스트
- TypeScript/React: 7 pages + 2 components
- 문서: 19 MD 파일

**테스트 커버리지:**
- 수동 테스트: 100%
- 자동 테스트: 0% (TODO)

---

## 🔐 보안 & 컴플라이언스

**환경 변수:**
- `.env` 파일로 API 키 관리
- `.gitignore`에 포함

**저작권:**
- 메타데이터에 출처 자동 기록
- Creative Commons 필터 지원
- 출처 표시 자동 생성

**데이터:**
- 로컬 파일 시스템 저장
- 외부 전송 없음 (API 호출 제외)

---

## 📝 변경 이력

### v2.0.0 (2025-12-22) - 하드코딩 자막 처리
- ✅ EasyOCR 기반 자막 추출
- ✅ 원본 자막 제거 + 번역 자막 재인코딩
- ✅ 웹 UI 스캔 버튼 추가
- ✅ 카테고리 14개로 확장
- ✅ 키워드 검색 필터 개선
- ✅ 문서 전면 업데이트

### v1.0.0 (2025-12-11) - 리믹스 시스템 전환
- ✅ Phase 1-3 완전 구현
- ✅ 웹 UI 전면 개편
- ✅ 배치 자동화
- ✅ 메타데이터 관리

### v0.5.0 (2025-12-10) - AI 자동 생성 시스템
- ⚠️ 구 시스템 (유지 중)
- 트렌드 분석 → 대본 생성 → TTS → 영상 합성

---

**마지막 업데이트:** 2025-12-22
**상태:** Production Ready (리믹스 시스템)
**다음 마일스톤:** OCR 성능 최적화, DB 통합
