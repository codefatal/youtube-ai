# 웹 UI 사용 가이드 🎨

Next.js 기반의 직관적인 웹 인터페이스로 YouTube AI 자동화를 쉽게 사용할 수 있습니다.

## 📋 목차

- [설치 및 실행](#설치-및-실행)
- [기능 소개](#기능-소개)
- [화면별 가이드](#화면별-가이드)
- [문제 해결](#문제-해결)

## 설치 및 실행

### 1. 백엔드 서버 실행

```bash
# 프로젝트 디렉토리로 이동
cd youtube-ai

# Python 의존성 설치 (처음 한 번만)
pip install -r requirements.txt

# 백엔드 서버 실행
cd backend
python main.py
```

✅ 백엔드 서버가 `http://localhost:8000`에서 실행됩니다.

API 문서: http://localhost:8000/docs

### 2. 프론트엔드 실행

```bash
# 새 터미널 창 열기
cd youtube-ai/frontend

# Node.js 의존성 설치 (처음 한 번만)
npm install

# 개발 서버 실행
npm run dev
```

✅ 웹 UI가 `http://localhost:3000`에서 실행됩니다.

## 기능 소개

### 🏠 대시보드

- **통계 확인**: 총 영상 수, 조회수, AI 비용 등
- **빠른 액션**: 자주 사용하는 기능에 빠르게 접근

### 📈 트렌드 분석

1. **지역 선택**: US, KR, JP, GB 등
2. **형식 선택**: 숏폼 또는 롱폼
3. **분석 시작** 버튼 클릭

**결과:**
- 주요 키워드 (클릭 가능한 태그)
- 트렌딩 주제 목록
- 추천 콘텐츠 아이디어
- 예상 조회수 범위

### ✍️ 대본 생성

1. **키워드 입력**: 쉼표로 구분 (예: AI, 기술, 미래)
2. **영상 설정**:
   - 형식: 숏폼/롱폼
   - 길이: 초 단위
   - 톤: 정보 제공/재미/교육적
   - 버전 수: A/B 테스트용 (1-5개)
3. **대본 생성** 버튼 클릭

**결과:**
- 여러 버전의 대본 (타임스탬프 포함)
- 각 버전 복사 버튼

### 🎬 영상 제작

*(구현 예정)*

### 📤 업로드

*(구현 예정)*

### ⚡ 전체 자동화

**원클릭으로 모든 과정 실행!**

1. **자동화 시작** 버튼 클릭
2. 진행 상황 실시간 확인:
   - ⏳ 트렌드 분석
   - ⏳ 대본 생성
   - ⏳ 영상 제작
   - ⏳ YouTube 업로드

각 단계별 상태와 메시지를 확인할 수 있습니다.

### 💰 비용 관리

- AI API 사용 통계
- 월별 비용 분석
- Provider별 비용 비교

### ⚙️ 설정

- API 키 관리
- AI Provider 선택 (Gemini/Claude/Auto)
- TTS Provider 설정
- 기타 환경 설정

## 화면별 가이드

### 대시보드 화면

![Dashboard](docs/images/dashboard.png)

**주요 기능:**
- 통계 카드: 클릭하면 상세 페이지로 이동
- 빠른 액션: 자주 사용하는 작업에 빠르게 접근

### 트렌드 분석 화면

**사용 팁:**
1. 지역을 한국(KR)로 설정하면 한국 트렌드 분석
2. 키워드를 클릭하면 자동으로 대본 생성 페이지로 이동
3. 아이디어를 복사하여 대본 생성에 활용

### 대본 생성 화면

**사용 팁:**
1. 여러 버전 생성으로 A/B 테스트 가능
2. 복사 버튼으로 쉽게 클립보드에 복사
3. 타임스탬프 형식이 자동으로 포함됨

### 자동화 화면

**주의사항:**
- 전체 프로세스는 10-15분 소요
- 진행 중 페이지를 닫지 마세요
- 각 단계별 오류 발생 시 자동으로 중단

## 문제 해결

### 백엔드 연결 오류

**증상:**
```
Failed to fetch
Network Error
```

**해결:**
1. 백엔드 서버가 실행 중인지 확인
   ```bash
   # 백엔드 터미널에서 확인
   # "Uvicorn running on http://0.0.0.0:8000" 메시지 확인
   ```

2. 포트 충돌 확인
   ```bash
   # Windows
   netstat -ano | findstr :8000

   # Linux/Mac
   lsof -i :8000
   ```

### 프론트엔드 실행 오류

**증상:**
```
Module not found
Cannot find module
```

**해결:**
```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

### API 키 오류

**증상:**
```
500 Internal Server Error
API key not set
```

**해결:**
1. `.env` 파일 확인
2. 백엔드 서버 재시작

### CORS 오류

**증상:**
```
CORS policy blocked
Access-Control-Allow-Origin
```

**해결:**
- `backend/main.py`의 CORS 설정 확인
- 프론트엔드 URL이 `http://localhost:3000`인지 확인

## 개발 모드 vs 프로덕션

### 개발 모드 (현재)

```bash
# 백엔드
python main.py

# 프론트엔드
npm run dev
```

### 프로덕션 배포

**프론트엔드 빌드:**
```bash
cd frontend
npm run build
npm start
```

**백엔드 프로덕션:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 추가 기능 (예정)

- [ ] 영상 제작 페이지
- [ ] 업로드 페이지
- [ ] 영상 목록 및 관리
- [ ] 스케줄링 기능
- [ ] 분석 대시보드 (조회수 추적)
- [ ] 다크 모드
- [ ] 다국어 지원

## 기여하기

웹 UI 개선 아이디어나 버그 리포트는 GitHub Issues로 제출해주세요!

## 라이선스

MIT License
