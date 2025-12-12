# YouTube Remix System - 웹 UI 가이드

> 리믹스 시스템을 위한 웹 인터페이스 사용 가이드

마지막 업데이트: 2025-12-12

---

## 🎯 개요

YouTube Remix System의 웹 UI는 트렌딩 영상 검색부터 리믹스까지 모든 과정을 시각적으로 관리할 수 있는 인터페이스를 제공합니다.

### 시스템 구조
- **백엔드**: FastAPI (Python) - `backend/main.py`
- **프론트엔드**: Next.js 14 (React, TypeScript) - `frontend/`
- **API 통신**: REST API (`http://localhost:8000`)

---

## 🚀 시작하기

### 1. 백엔드 서버 시작

```bash
cd backend
python main.py
```

서버가 http://localhost:8000 에서 실행됩니다.
- API 문서: http://localhost:8000/docs

### 2. 프론트엔드 서버 시작

```bash
cd frontend
npm install  # 처음 한 번만
npm run dev
```

웹 UI가 http://localhost:3000 에서 실행됩니다.

---

## 📱 페이지 구성

### 1. 대시보드 (`/`)
- 전체 통계 확인
  - 전체 영상 수
  - 완료/처리 중/실패 개수
  - 총 조회수
  - 총 영상 길이
- 빠른 작업 바로가기

### 2. 영상 검색 (`/search`)
**트렌딩 검색**:
- 지역 선택 (US, KR, JP, GB)
- 카테고리 (과학/기술, 교육, 엔터테인먼트, 음악)
- 영상 길이 (숏폼/중간/롱폼)
- 최소 조회수 설정

**키워드 검색**:
- 키워드 입력
- 정렬 기준 (조회수/관련성/날짜)

**기능**:
- 검색 결과 목록 표시
- 각 영상 다운로드 버튼
- YouTube에서 보기 링크

### 3. 배치 처리 (`/batch`)
**자동 리믹스**:
- 검색 조건 설정
- 최대 영상 수 지정
- 번역 언어 선택

**진행 상황**:
- Job ID 표시
- 실시간 상태 업데이트
- 결과 통계 (검색/다운로드/번역/리믹스/실패/스킵)

### 4. 영상 목록 (`/videos`)
**필터링**:
- 전체
- 대기
- 다운로드 완료
- 번역 완료
- 완료
- 실패

**영상 카드**:
- 원본 제목 및 상태 배지
- 채널, 조회수, 길이
- 번역된 제목 (있으면)
- 원본 보기 링크
- 삭제 버튼
- 파일 정보 (펼치기)

### 5. 다운로드 관리 (`/downloads`)
영상 목록에 통합됨 (안내 페이지)

### 6. 리믹스 (`/remix`)
배치 처리에 통합됨 (안내 페이지)

### 7. 설정 (`/settings`)
기존 설정 페이지 유지

---

## 🔧 API 엔드포인트

### 통계
```
GET /api/stats
→ 대시보드 통계 조회
```

### 검색
```
POST /api/search/trending
Body: { region, category, duration, min_views, max_results }
→ 트렌딩 영상 검색

POST /api/search/keywords
Body: { keywords, region, order, max_results }
→ 키워드 검색
```

### 다운로드
```
POST /api/download
Body: { url, subtitle_lang }
→ 영상 다운로드
```

### 번역
```
POST /api/translate
Body: { video_id, target_lang }
→ 자막 번역
```

### 리믹스
```
POST /api/remix
Body: { video_id }
→ 영상 리믹스
```

### 배치 처리
```
POST /api/batch/start
Body: { region, category, max_videos, duration, min_views, target_lang }
→ 배치 작업 시작

GET /api/batch/status/{job_id}
→ 배치 작업 상태 조회
```

### 영상 관리
```
GET /api/videos?status={status}
→ 영상 목록 조회

GET /api/videos/{video_id}
→ 영상 상세 조회

DELETE /api/videos/{video_id}?delete_files={bool}
→ 영상 삭제
```

---

## 💡 사용 시나리오

### 시나리오 1: 개별 영상 리믹스
1. **영상 검색** → 트렌딩 또는 키워드로 영상 찾기
2. **다운로드** → 원하는 영상 다운로드 버튼 클릭
3. **영상 목록** → 다운로드 상태 확인
4. (자동) 백엔드에서 번역 및 리믹스 처리
5. **영상 목록** → 완료된 영상 확인

### 시나리오 2: 배치 자동 처리
1. **배치 처리** 페이지 이동
2. **설정** 입력 (지역, 카테고리, 최대 영상 수)
3. **배치 처리 시작** 버튼 클릭
4. **실시간 상태** 확인 (검색 → 다운로드 → 번역 → 리믹스)
5. **완료 후** 영상 목록에서 결과 확인

---

## 🎨 UI 컴포넌트

### 재사용 컴포넌트
- `Sidebar.tsx` - 네비게이션 사이드바
- `StatsCard.tsx` - 통계 카드

### 아이콘
- Lucide React 라이브러리 사용
- Film, Search, Download, Languages, Zap 등

---

## ⚙️ 환경 변수

`frontend/.env.local` 파일:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🔍 디버깅

### 백엔드 로그
```bash
# backend/main.py에서 출력
🔍 트렌딩 검색: US / Science & Technology
📥 다운로드: https://youtube.com/watch?v=...
🌐 번역: video_id -> ko
🎬 리믹스: video_id
```

### 프론트엔드 개발자 도구
- Network 탭에서 API 요청/응답 확인
- Console에서 오류 확인

---

## 📌 주요 특징

1. **실시간 업데이트**: 배치 작업 상태 3초마다 폴링
2. **필터링**: 영상 상태별 필터 (전체/대기/완료/실패)
3. **상태 배지**: 시각적 상태 표시 (색상 코딩)
4. **반응형 디자인**: Tailwind CSS 기반
5. **사용자 친화적**: 확인 대화상자, 로딩 인디케이터

---

## 🚧 알려진 제한사항

1. **실시간 진행률**: 배치 작업의 세부 진행률은 폴링으로만 확인 가능
2. **파일 다운로드**: 리믹스된 영상 파일은 서버에 저장됨 (웹에서 직접 다운로드 불가)
3. **동시 작업**: 한 번에 하나의 배치 작업만 실행 권장

---

## 📚 관련 문서

- `REMIX_ARCHITECTURE.md` - 시스템 아키텍처
- `backend/README.md` - 백엔드 API 상세
- `CLAUDE.md` - 개발 가이드
