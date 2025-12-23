# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**YouTube AI v3.0** - Complete AI-powered original content creation system for YouTube automation.

This is a dual-interface system:
- **Web UI** (Next.js frontend + FastAPI backend) - Primary interface
- **CLI** (Python Click-based) - Command-line interface

The system uses AI (Gemini/Claude) for content planning, script generation, and metadata creation, combined with TTS, stock videos, and video synthesis to create complete YouTube videos automatically.

## Development Commands

### Backend Development

**Start Backend Server:**
```bash
cd backend
python main.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend Development

**Start Frontend:**
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

# Auto-create content
python scripts/auto_create.py --topic "AI 기술 소개" --format shorts --duration 60

# Full automation with upload
python scripts/auto_create.py --upload

# Local scheduler (daily automation)
python scripts/schedule_local.py

# Run tests
python tests/test_integration.py

# Performance benchmark
python scripts/benchmark.py
```

## Architecture

### Core Modules (`core/`)

- **planner.py** - AI-based content planning and script generation
  - `generate_topic_ideas()` - AI topic generation (trending or custom)
  - `generate_content_plan()` - Full script with segments, keywords, timing

- **asset_manager.py** - Asset collection (stock videos + TTS)
  - `collect_assets()` - Collect videos and generate TTS audio
  - Supports Pexels, Pixabay (stock videos)
  - Supports gTTS, ElevenLabs, Google Cloud TTS

- **editor.py** - MoviePy-based video editing
  - `create_video()` - Full video composition (clips + subtitles + audio)
  - Automatic subtitle generation and timing
  - Resolution: 1080x1920 (Shorts) or 1920x1080 (Landscape)

- **uploader.py** - YouTube upload automation
  - `upload_video()` - OAuth 2.0 based YouTube upload
  - `generate_metadata()` - AI-generated title, description, tags

- **orchestrator.py** - Pipeline management
  - `create_content()` - Full pipeline: Plan → Assets → Edit → Upload
  - Job queue management
  - Progress tracking and error handling

### Provider System (`providers/`)

**AI Providers** (`providers/ai/`):
- **gemini.py** - Google Gemini API (free, fast)
- **claude.py** - Anthropic Claude API (premium)

**Stock Video Providers** (`providers/stock/`):
- **pexels.py** - Pexels API (free, high quality)
- **pixabay.py** - Pixabay API (free, fallback)

**TTS Providers** (`providers/tts/`):
- **gtts_provider.py** - Google TTS (free, fast)
- **elevenlabs.py** - ElevenLabs (premium, natural)
- **google_cloud.py** - Google Cloud TTS (premium)

### Backend API (`backend/main.py`)

**Key Endpoints**:
- `POST /api/topics/generate` - Generate AI topics
- `POST /api/scripts/generate` - Generate AI scripts
- `POST /api/videos/create` - Create video (full pipeline)
- `POST /api/jobs/status` - Check job status
- `GET /api/jobs/recent` - Recent jobs list
- `GET /api/stats` - Statistics (total/completed/failed)
- `GET /api/config` - Current system configuration

**Response Format**:
```json
{
  "success": true,
  "data": { ... }
}
```

### Data Models (`core/models.py`)

**Core Models**:
- `ContentPlan` - Full content plan with segments
- `ScriptSegment` - Individual script segment (text, keyword, duration)
- `AssetBundle` - Collection of videos + audio
- `ContentJob` - Job tracking (status, progress, output)
- `SystemConfig` - System configuration (AI provider, TTS provider, format)

**Enums**:
- `VideoFormat` - SHORTS, LANDSCAPE, SQUARE
- `AIProvider` - GEMINI, CLAUDE, OPENAI
- `TTSProvider` - GTTS, ELEVENLABS, GOOGLE_CLOUD
- `ContentStatus` - PLANNING, COLLECTING_ASSETS, EDITING, UPLOADING, COMPLETED, FAILED

## Environment Variables

Required `.env` file at project root:

```bash
# Required for basic functionality
GEMINI_API_KEY=AIza...          # From https://aistudio.google.com/apikey

# Stock Videos (at least one)
PEXELS_API_KEY=...              # From https://www.pexels.com/api/
PIXABAY_API_KEY=...             # From https://pixabay.com/api/docs/

# Optional
ANTHROPIC_API_KEY=sk-ant-...    # For Claude
ELEVENLABS_API_KEY=...          # For premium TTS
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json  # For Google Cloud TTS
YOUTUBE_API_KEY=...             # For trend analysis (optional)
```

**YouTube Upload** requires `client_secrets.json` for OAuth 2.0.

## Current Status

### ✅ Fully Implemented
- Core pipeline (Planner → Asset Manager → Editor → Uploader → Orchestrator)
- AI providers (Gemini, Claude)
- Stock video providers (Pexels, Pixabay)
- TTS providers (gTTS, ElevenLabs, Google Cloud)
- Video editing (MoviePy with subtitles, audio mixing)
- YouTube upload (OAuth 2.0)
- Automation (GitHub Actions, local scheduler)
- Testing (integration tests, error cases, benchmarks)
- Backend API (FastAPI with 8 endpoints)

### 🚧 In Progress
- Frontend UI update (adapting to new backend)

### 📊 Project Completion

```
✅ Phase 1: Foundation (100%)
✅ Phase 2: Planner (100%)
✅ Phase 3: Asset Manager (100%)
✅ Phase 4: Editor (100%)
✅ Phase 5: Uploader (100%)
✅ Phase 6: Orchestrator (100%)
✅ Phase 7: Automation (100%)
✅ Phase 8: Testing & Optimization (100%)
```

**Overall: 100% Complete (8/8 Phases)**

## Common Development Patterns

### Creating Content Programmatically

```python
from core.orchestrator import ContentOrchestrator
from core.models import VideoFormat

# Create orchestrator
orchestrator = ContentOrchestrator()

# Create video (full pipeline)
job = orchestrator.create_content(
    topic="Python 프로그래밍 팁",  # Or None for AI-generated topic
    video_format=VideoFormat.SHORTS,
    target_duration=60,
    upload=True  # Upload to YouTube
)

print(f"Video created: {job.output_video_path}")
print(f"YouTube URL: {job.youtube_url}")
```

### Using Individual Modules

```python
# 1. Generate topics
from core.planner import Planner

planner = Planner()
topics = await planner.generate_topic_ideas(count=3, trending=True)

# 2. Generate script
plan = await planner.generate_content_plan(
    topic=topics[0],
    format=VideoFormat.SHORTS,
    target_duration=60,
    style="정보성"
)

# 3. Collect assets
from core.asset_manager import AssetManager

asset_manager = AssetManager()
bundle = await asset_manager.collect_assets(plan)

# 4. Create video
from core.editor import Editor

editor = Editor()
video_path = await editor.create_video(plan, bundle)

# 5. Upload to YouTube
from core.uploader import Uploader

uploader = Uploader()
metadata = await uploader.generate_metadata(plan)
youtube_url = await uploader.upload_video(video_path, metadata)
```

## Testing Changes

**Backend changes:**
```bash
# Restart backend server (Ctrl+C, then)
python backend/main.py

# Test specific endpoint
curl -X POST http://localhost:8000/api/topics/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 3, "trending": true}'
```

**Frontend changes:**
- Next.js auto-reloads on file save
- Check browser console for errors
- Backend logs appear in backend terminal

**Run tests:**
```bash
# Integration tests
python tests/test_integration.py

# Error cases
python tests/test_error_cases.py

# Performance benchmark
python scripts/benchmark.py
```

## Git Workflow

- Commit messages in Korean (user preference)
- Push directly to main branch
- Phase summary documents (PHASE1_SUMMARY.md ~ PHASE8_SUMMARY.md) track progress

## Known Issues & Solutions

1. **ImageMagick Required**: MoviePy needs ImageMagick for text rendering
   - Windows: Download from https://imagemagick.org/
   - Set path in `moviepy/config_defaults.py`

2. **API Keys**: Ensure `.env` file exists with required keys
   - Minimum: `GEMINI_API_KEY`, `PEXELS_API_KEY` (or `PIXABAY_API_KEY`)

3. **YouTube Upload**: Requires OAuth 2.0 setup
   - Create project at https://console.cloud.google.com/
   - Download `client_secrets.json`
   - Run upload once to authorize

4. **Python 3.14 Compatibility**: All dependencies updated for Python 3.14
   - numpy >= 2.3.0
   - Pillow >= 11.0.0

5. **Performance**: First run is slower due to model downloads
   - Gemini API: 10-30s
   - Stock video download: 5-15s per video
   - TTS generation: 2-5s
   - Video editing: 30-60s for 60s video

## API Usage Examples

### Generate Topics

```bash
curl -X POST http://localhost:8000/api/topics/generate \
  -H "Content-Type: application/json" \
  -d '{"count": 3, "trending": true}'
```

### Generate Script

```bash
curl -X POST http://localhost:8000/api/scripts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python 기초",
    "format": "shorts",
    "duration": 60,
    "style": "정보성"
  }'
```

### Create Video

```bash
curl -X POST http://localhost:8000/api/videos/create \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI 기술 소개",
    "format": "shorts",
    "duration": 60,
    "upload": false
  }'
```

### Check Job Status

```bash
curl -X POST http://localhost:8000/api/jobs/status \
  -H "Content-Type: application/json" \
  -d '{"job_id": "job_20251223_123456"}'
```

## Related Documentation

- `README.md` - Project overview, installation guide
- `REFACTOR_PLAN.md` - Refactoring plan and progress
- `PHASE1_SUMMARY.md` ~ `PHASE8_SUMMARY.md` - Phase completion reports
- `MUSIC_GUIDE.md` - Background music guide
- `tests/` - Test files with usage examples
- `scripts/` - Automation scripts

## Repository URL

https://github.com/codefatal/youtube-ai
