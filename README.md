# YouTube AI v4.0

**엔터프라이즈급 다중 계정 YouTube 자동화 시스템**

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 v4.0 주요 기능

### 🆕 v3.0 대비 추가 기능

- **멀티 계정 관리**: 여러 YouTube 채널 동시 운영
- **데이터베이스**: SQLite + SQLAlchemy ORM
- **BGM 자동 매칭**: 분위기별 배경음악
- **템플릿 시스템**: 커스터마이징 가능한 쇼츠 스타일
- **ElevenLabs TTS 고도화**: 상세 파라미터 제어, 미리듣기
- **자동 스케줄링**: APScheduler 기반 백그라운드 작업
- **현대적 UI**: 다크 모드 대시보드

### ⚡ 기존 기능 (v3.0)

- AI 기반 콘텐츠 생성 (Gemini/Claude)
- 스톡 영상 수집 (Pexels, Pixabay)
- TTS 음성 생성 (gTTS, ElevenLabs, Google Cloud)
- 영상 편집 및 합성 (MoviePy 2.x)
- YouTube 업로드 (OAuth 2.0)

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/codefatal/youtube-ai.git
cd youtube-ai

# 가상환경 생성
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일 생성:

```bash
# AI Provider
GEMINI_API_KEY=your_gemini_api_key

# Stock Videos
PEXELS_API_KEY=your_pexels_api_key

# TTS (선택)
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# YouTube
YOUTUBE_API_KEY=your_youtube_api_key
```

### 3. 데이터베이스 초기화

```bash
# Alembic 마이그레이션
alembic upgrade head

# (선택) v3 데이터 마이그레이션
python scripts/migrate_v3_to_v4.py
```

### 4. 서버 시작

**백엔드**:
```bash
python backend/main.py
# → http://localhost:8000
```

**프론트엔드**:
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## 📚 사용 방법

### 계정 추가

1. 웹 UI에서 "계정 관리" 메뉴
2. "+ 새 계정 추가" 클릭
3. 채널 정보 입력 (이름, 타입, 스케줄)
4. OAuth 2.0 인증 완료

### 영상 생성

1. "영상 생성" 메뉴
2. 주제 입력 (또는 AI 자동 생성)
3. TTS 설정, 템플릿 선택
4. "영상 생성 시작" 클릭

### 자동 스케줄 설정

1. 계정 상세 페이지
2. "스케줄" 탭
3. Cron 포맷 입력 (예: `0 9 * * *` = 매일 오전 9시)
4. 저장 후 스케줄러 재로드

---

## 📖 문서

- [API 문서](./docs/API.md)
- [배포 가이드](./docs/DEPLOYMENT.md)
- [개발자 가이드](./CLAUDE.md)
- [업그레이드 로드맵](./UPGRADE_ROADMAP.md)

---

## 🧪 테스트

```bash
# 전체 테스트
pytest tests/

# 특정 테스트
pytest tests/test_accounts_api.py
pytest tests/test_integration_v4.py
```

---

## 📊 프로젝트 상태

**버전**: 4.0.0
**상태**: Production Ready
**완료도**: 100% (6/6 Phases)

---

## 🤝 기여

Pull Request는 언제나 환영입니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License - [LICENSE](./LICENSE) 참조

---

## 🙏 감사

- OpenAI, Anthropic, Google (AI 모델)
- Pexels, Pixabay (스톡 영상)
- ElevenLabs (TTS)
- MoviePy (영상 편집)

---

**Made with ❤️ by codefatal**