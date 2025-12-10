"""
FastAPI Backend Server for YouTube AI Automation
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# 로컬 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from local_cli.services.trend_analyzer import TrendAnalyzer
from local_cli.services.script_generator import ScriptGenerator
from local_cli.services.video_producer import VideoProducer
from local_cli.services.youtube_uploader import YouTubeUploader

app = FastAPI(
    title="YouTube AI Automation API",
    description="API for automated YouTube video creation",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001"  # 포트 변경 시 대비
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response 모델
class TrendAnalysisRequest(BaseModel):
    region: str = "US"
    format: str = "short"
    max_results: int = 50


class ScriptGenerationRequest(BaseModel):
    keywords: List[str]
    format: str
    duration: int
    tone: str = "informative"
    versions: int = 1


class VideoProductionRequest(BaseModel):
    script: str
    format: str
    style: str = "short_trendy"


class UploadRequest(BaseModel):
    video_path: str
    keywords: List[str]
    script: Optional[str] = None
    privacy: str = "public"


# 엔드포인트
@app.get("/")
def read_root():
    return {
        "message": "YouTube AI Automation API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


@app.post("/api/trends/analyze")
async def analyze_trends(request: TrendAnalysisRequest):
    """트렌드 분석"""
    try:
        analyzer = TrendAnalyzer(ai_provider='auto')
        videos = analyzer.fetch_trending_videos(
            region=request.region,
            max_results=request.max_results
        )
        analysis = analyzer.analyze_with_ai(videos, video_format=request.format)

        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        import traceback
        print(f"❌ 에러 발생: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scripts/generate")
async def generate_scripts(request: ScriptGenerationRequest):
    """대본 생성"""
    try:
        generator = ScriptGenerator(ai_provider='auto')
        scripts = generator.generate_script(
            trend_keywords=request.keywords,
            video_format=request.format,
            duration_seconds=request.duration,
            tone=request.tone,
            num_versions=request.versions
        )

        return {
            "success": True,
            "scripts": scripts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/videos/produce")
async def produce_video(request: VideoProductionRequest):
    """영상 제작"""
    try:
        producer = VideoProducer()

        script_dict = {
            'content': request.script,
            'video_format': request.format
        }

        output_path = f"./output/video_{int(time.time())}.mp4"
        video_path, thumbnail_path = producer.produce_video(
            script=script_dict,
            style_preset=request.style,
            output_path=output_path
        )

        return {
            "success": True,
            "video_path": video_path,
            "thumbnail_path": thumbnail_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_video(request: UploadRequest):
    """YouTube 업로드"""
    try:
        uploader = YouTubeUploader(ai_provider='auto')

        # 메타데이터 생성
        metadata = uploader.generate_metadata(
            script={'content': request.script or ''},
            trend_keywords=request.keywords
        )

        # 업로드
        video_id, video_url = uploader.upload_video(
            video_path=request.video_path,
            title=metadata['title'],
            description=metadata['description'],
            tags=metadata['tags'],
            privacy_status=request.privacy
        )

        return {
            "success": True,
            "video_id": video_id,
            "video_url": video_url,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/automation/full")
async def full_automation(
    region: str = "US",
    format: str = "short",
    duration: int = 60,
    upload: bool = True
):
    """전체 자동화 프로세스"""
    try:
        results = {}

        # 1. 트렌드 분석
        analyzer = TrendAnalyzer(ai_provider='auto')
        videos = analyzer.fetch_trending_videos(region=region, max_results=50)
        analysis = analyzer.analyze_with_ai(videos, video_format=format)
        results['trends'] = analysis

        keywords = analysis['keywords'][:3]

        # 2. 대본 생성
        generator = ScriptGenerator(ai_provider='auto')
        scripts = generator.generate_script(
            trend_keywords=keywords,
            video_format=format,
            duration_seconds=duration,
            tone='informative',
            num_versions=1
        )
        results['script'] = scripts[0]

        # 3. 영상 제작
        producer = VideoProducer()
        import time
        output_path = f"./output/auto_video_{int(time.time())}.mp4"

        video_path, thumbnail_path = producer.produce_video(
            script={'content': scripts[0], 'video_format': format},
            style_preset='short_trendy' if format == 'short' else 'long_educational',
            output_path=output_path
        )
        results['video'] = {
            'path': video_path,
            'thumbnail': thumbnail_path
        }

        # 4. 업로드 (옵션)
        if upload:
            uploader = YouTubeUploader(ai_provider='auto')
            metadata = uploader.generate_metadata(
                {'content': scripts[0]},
                keywords
            )

            video_id, video_url = uploader.upload_video(
                video_path=video_path,
                title=metadata['title'],
                description=metadata['description'],
                tags=metadata['tags']
            )

            results['upload'] = {
                'video_id': video_id,
                'video_url': video_url
            }

        return {
            "success": True,
            "data": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
