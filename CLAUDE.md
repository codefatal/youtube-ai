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

**API Endpoints** (`backend/main.py`):
- `POST /api/trends/analyze` - Returns keywords, topics, content ideas, view range
- `POST /api/scripts/generate` - Returns array of script versions
- `POST /api/videos/produce` - Currently returns development notice (not fully implemented)
- `POST /api/upload` - YouTube upload with metadata
- `POST /api/stats` - Dashboard statistics
- `POST /api/automation/full` - End-to-end automation

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
- Recent changes include settings integration and development notices

## Known Issues & Workarounds

1. **Gemini MAX_TOKENS**: Always use 8000+ tokens to avoid truncation from thinking mode
2. **JSON Parsing**: AI responses may include markdown code blocks - strip with regex before parsing
3. ~~**Video Production**~~: ✅ **Fixed!** Now uses gTTS + FFmpeg directly (no pydub)
4. ~~**pydub/audioop**~~: ✅ **Fixed!** Replaced with direct FFmpeg calls (Python 3.14 compatible)
5. **Stats**: Currently returns zeros - needs database implementation
6. **Line Endings**: Git warns about LF/CRLF on Windows - this is normal
7. **YouTube Upload**: Requires OAuth 2.0 setup with credentials.json

## Related Documentation

- `README.md` - User-facing documentation, installation guide
- `QUICK_START.md` - 5-minute quickstart
- `PROJECT_SUMMARY.md` - Feature completion status
- `WEB_UI_GUIDE.md` - Web interface usage
- `TROUBLESHOOTING.md` - Common problems and solutions
- `backend/README.md` - Backend API details
- `frontend/README.md` - Frontend tech stack and structure

## Repository URL

https://github.com/codefatal/youtube-ai
