# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI YouTube Automation** - Complete automated video production pipeline from trend analysis to YouTube upload.

This is a dual-interface system:
- **Web UI** (Next.js frontend + FastAPI backend) - Primary interface
- **CLI** (Python Click-based) - Command-line interface

The system uses AI (Gemini/Claude) for trend analysis, script generation, and metadata creation, combined with TTS, audio processing, and video synthesis to create complete YouTube videos automatically.

## Development Commands

### Web UI Development (Primary)

**Start Backend Server:**
```bash
cd backend
python main.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Start Frontend Development:**
```bash
cd frontend
npm install  # First time only
npm run dev
# Web UI runs at http://localhost:3000
```

**Both servers must run simultaneously** - Backend on port 8000, Frontend on port 3000.

### CLI Usage

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Test AI services
python local_cli/main.py test-ai --provider gemini

# Analyze trends
python local_cli/main.py analyze-trends --region KR --format short --ai gemini

# Generate scripts
python local_cli/main.py generate-script --keywords "AI,tech" --format short --duration 60 --ai gemini

# Full automation (without upload)
python local_cli/main.py full-automation --ai gemini --no-upload
```

## Architecture

### Backend Architecture (FastAPI)

**Core Services** (`local_cli/services/`):
- `ai_service.py` - **Central AI integration**. Handles both Gemini and Claude APIs with automatic fallback. Uses `google.genai` SDK (not deprecated `google-generativeai`). Implements retry logic and token tracking.
- `trend_analyzer.py` - YouTube Data API integration + AI analysis
- `script_generator.py` - AI-powered script generation with timestamps
- `tts_service.py` - Multi-provider TTS (Google Cloud, local, ElevenLabs, Azure)
- `audio_processor.py` - Audio merging, mixing with pydub
- `music_library.py` - Background music management
- `video_producer.py` - MoviePy-based video composition
- `youtube_uploader.py` - OAuth2-based YouTube upload
- `hardcoded_subtitle_processor.py` - **NEW! 하드코딩 자막 처리**. OCR로 영상에 인코딩된 자막 추출 → 번역 → 원본 자막 제거 (검은 박스) → 번역 자막 재인코딩. EasyOCR 기반, 원본 스타일 (색상, 크기, 위치) 유지

**API Endpoints** (`backend/main.py`):
- `POST /api/trends/analyze` - Returns keywords, topics, content ideas, view range
- `POST /api/scripts/generate` - Returns array of script versions
- `POST /api/videos/produce` - Currently returns development notice (not fully implemented)
- `POST /api/upload` - YouTube upload with metadata
- `POST /api/stats` - Dashboard statistics
- `POST /api/automation/full` - End-to-end automation
- `POST /api/hardcoded-subtitle/process` - **NEW!** 하드코딩 자막 추출 및 번역 (백그라운드 작업)

### Frontend Architecture (Next.js 14 App Router)

**Pages** (`frontend/app/`):
- `page.tsx` - Dashboard with stats and quick actions
- `trends/page.tsx` - Trend analysis interface
- `scripts/page.tsx` - Script generation with multiple versions
- `videos/page.tsx` - Video production (development notice)
- `upload/page.tsx` - YouTube upload (development notice)
- `automation/page.tsx` - Full automation workflow
- `costs/page.tsx` - Cost tracking
- `settings/page.tsx` - App settings with localStorage

**Components** (`frontend/components/`):
- `Sidebar.tsx` - Navigation sidebar
- `StatsCard.tsx` - Dashboard stat cards

**Settings Integration:**
- Settings are stored in `localStorage` as `appSettings`
- Trend/Scripts/Videos pages read default values from settings on mount
- Format, region, and tone preferences are synced across pages

### Key Implementation Details

**Gemini API Integration:**
- Uses latest `google-genai` SDK (v0.2.0+), NOT `google-generativeai`
- Model: `gemini-1.5-flash` (stable) or `gemini-2.5-flash` (newer)
- **Critical**: `max_output_tokens` must be 8000+ to accommodate Gemini's "thinking mode" which consumes 1900-5000 tokens internally
- Uses `types.GenerateContentConfig` for proper parameter passing
- JSON responses must be parsed with regex to strip markdown code blocks

**AI Service Fallback:**
```python
# .env
AI_PROVIDER=auto  # Tries Gemini first, falls back to Claude
AI_PROVIDER=gemini  # Gemini only (free)
AI_PROVIDER=claude  # Claude only (premium)
```

**CORS Configuration:**
Backend allows `http://localhost:3000` and `http://localhost:3001` for frontend development.

**Data Flow:**
1. Frontend fetches from backend API
2. Backend calls `local_cli/services/` modules
3. Services call external APIs (Gemini, YouTube, etc.)
4. Responses flow back with `{success: bool, data: {...}}` structure

## Environment Variables

Required `.env` file at project root:

```bash
# Required for basic functionality
GEMINI_API_KEY=AIza...          # From https://aistudio.google.com/apikey
YOUTUBE_API_KEY=...             # For trend analysis

# Optional
ANTHROPIC_API_KEY=sk-ant-...    # For Claude
GEMINI_MODEL=gemini-1.5-flash   # Model selection
AI_PROVIDER=auto                # auto/gemini/claude
```

**Important**:
- `GOOGLE_APPLICATION_CREDENTIALS` is needed for Google Cloud TTS (video production)
- `client_secrets.json` is needed for YouTube OAuth upload
- These are currently not fully implemented in Web UI

## Current Status

### ✅ Fully Implemented
- Web UI dashboard with stats API integration
- Trend analysis (YouTube Data API + AI)
- Script generation with multiple versions
- **Video Production** - Fully working! ✨
  - gTTS (Google Text-to-Speech) free service
  - FFmpeg-based audio/video processing
  - No pydub dependency (Python 3.14 compatible)
  - Real-time progress display in UI
  - File path guidance after completion
  - **NEW (2025-12-11)**: 4가지 품질 개선
    - 자막 () 효과음 자동 제거 (정규식 기반)
    - 자막 길이 자동 조절 (동적 폰트 크기 32-48px)
    - 그라데이션 배경 이미지 생성 (5가지 색상 조합)
    - 대본 자동 분할 (120자 이상 문장 단위 분할)
- Settings page with localStorage persistence
- Settings integration across all pages
- Backend API with CORS
- CLI for all features
- Gemini API integration with latest SDK
- Error handling and graceful degradation

### ⚠️ Development Notice (Not Fully Functional)
- **YouTube Upload**: Requires OAuth 2.0 client credentials setup

### 📊 Database/Persistence
- Currently uses hardcoded/default values
- Stats API returns zeros (no database yet)
- Settings stored in browser localStorage only
- TODO: Add database for actual tracking

## Common Development Patterns

### Adding a New Page

1. Create `frontend/app/newpage/page.tsx`
2. Add to sidebar in `frontend/components/Sidebar.tsx`
3. Optionally create backend endpoint in `backend/main.py`
4. Add settings integration if needed (read from localStorage)

### Adding a New Backend Service

1. Create `local_cli/services/new_service.py`
2. Follow pattern: import AIService, use `self.ai_service.generate_text()`
3. Add endpoint in `backend/main.py`
4. Import and instantiate service in endpoint handler

### API Response Format

All API endpoints return:
```json
{
  "success": true,
  "data": { ... }
}
```

Frontend should check `result.success` and access `result.data`.

## Testing Changes

**Backend changes:**
```bash
# Restart backend server (Ctrl+C, then)
python backend/main.py
```

**Frontend changes:**
- Next.js auto-reloads on file save
- Check browser console for errors
- Backend logs appear in backend terminal

**AI Service testing:**
```bash
python local_cli/main.py test-ai --provider gemini
```

## Git Workflow

- Commit messages in Korean (user preference)
- Push directly to main branch
- **WORK_LOG.md** tracks all work for cross-session continuity
- **WORKFLOW_GUIDE.md** provides workflow guidelines
- Recent changes include video production quality improvements (2025-12-11)

## Known Issues & Workarounds

1. **Gemini MAX_TOKENS**: Always use 8000+ tokens to avoid truncation from thinking mode
2. **JSON Parsing**: AI responses may include markdown code blocks - strip with regex before parsing
3. ~~**Video Production**~~: ✅ **Fixed!** Now uses gTTS + FFmpeg directly (no pydub)
4. ~~**pydub/audioop**~~: ✅ **Fixed!** Replaced with direct FFmpeg calls (Python 3.14 compatible)
5. ~~**자막 () 효과음 표시**~~: ✅ **Fixed (2025-12-11)!** 정규식 `r'\([^)]*\)'`로 자동 제거
6. ~~**자막 길이 잘림**~~: ✅ **Fixed (2025-12-11)!** 동적 폰트 크기 + 자막 너비 90%로 증가
7. ~~**단색 배경 이미지**~~: ✅ **Fixed (2025-12-11)!** 그라데이션 배경 + 키워드 텍스트 추가
8. ~~**긴 대본 문제**~~: ✅ **Fixed (2025-12-11)!** 120자 이상 자동 문장 분할
9. **Stats**: Currently returns zeros - needs database implementation
10. **Line Endings**: Git warns about LF/CRLF on Windows - this is normal
11. **YouTube Upload**: Requires OAuth 2.0 setup with credentials.json
12. **하드코딩 자막 처리**: EasyOCR + OpenCV 필요. 패키지 설치 시 컴파일러 문제 발생 가능
    - 해결: `pip install easyocr opencv-python-headless --no-deps` 후 수동으로 의존성 설치
    - 필요 패키지: torch, torchvision, pyyaml, python-bidi
    - OCR 처리는 시간이 오래 걸릴 수 있음 (백그라운드 작업 사용 권장)

## Related Documentation

- `README.md` - User-facing documentation, installation guide
- `QUICK_START.md` - 5-minute quickstart
- `PROJECT_SUMMARY.md` - Feature completion status
- `PROJECT_STATUS.md` - Current project status and recent changes
- `WEB_UI_GUIDE.md` - Web interface usage
- `TROUBLESHOOTING.md` - Common problems and solutions
- `WORK_LOG.md` - Detailed work log for token expiration recovery
- `WORKFLOW_GUIDE.md` - Development workflow guidelines
- `MUSIC_GUIDE.md` - Background music download guide
- `backend/README.md` - Backend API details
- `frontend/README.md` - Frontend tech stack and structure

## Repository URL

https://github.com/codefatal/youtube-ai
