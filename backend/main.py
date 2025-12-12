"""
FastAPI Backend Server for YouTube Remix System
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import sys
import os

# 로컬 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from local_cli.services.trending_searcher import TrendingSearcher
from local_cli.services.youtube_downloader import YouTubeDownloader
from local_cli.services.subtitle_translator import SubtitleTranslator
from local_cli.services.metadata_manager import MetadataManager
from local_cli.services.video_remixer import VideoRemixer

app = FastAPI(
    title="YouTube Remix System API",
    description="API for YouTube video remix automation",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 인스턴스
searcher = TrendingSearcher()
downloader = YouTubeDownloader()
translator = SubtitleTranslator()
metadata_manager = MetadataManager()
remixer = VideoRemixer()


# Request/Response 모델
class SearchTrendingRequest(BaseModel):
    region: str = "US"
    category: Optional[str] = "Science & Technology"
    max_results: int = 10
    duration: str = "short"  # short, medium, long
    min_views: int = 10000


class SearchKeywordsRequest(BaseModel):
    keywords: str
    region: str = "US"
    max_results: int = 10
    order: str = "viewCount"  # viewCount, relevance, date


class DownloadRequest(BaseModel):
    url: str
    subtitle_lang: str = "en"


class TranslateRequest(BaseModel):
    video_id: str
    target_lang: str = "ko"


class RemixRequest(BaseModel):
    video_id: str


class BatchRemixRequest(BaseModel):
    region: str = "US"
    category: Optional[str] = "Science & Technology"
    max_videos: int = 3
    duration: str = "short"
    min_views: int = 10000
    target_lang: str = "ko"


# 배치 작업 상태 저장
batch_jobs: Dict[str, Dict] = {}


# ============================================================
# 기본 엔드포인트
# ============================================================

@app.get("/")
def read_root():
    return {
        "message": "YouTube Remix System API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


@app.get("/api/stats")
async def get_stats():
    """대시보드 통계"""
    try:
        stats = metadata_manager.get_stats()

        return {
            "success": True,
            "data": {
                "totalVideos": stats['total'],
                "completed": stats['by_status'].get('completed', 0),
                "processing": stats['by_status'].get('processing', 0),
                "failed": stats['by_status'].get('failed', 0),
                "totalViews": stats['total_views'],
                "totalDuration": stats['total_duration']
            }
        }
    except Exception as e:
        print(f"❌ 통계 조회 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# 트렌딩 검색
# ============================================================

@app.post("/api/search/trending")
async def search_trending(request: SearchTrendingRequest):
    """트렌딩 영상 검색"""
    try:
        print(f"🔍 트렌딩 검색: {request.region} / {request.category}")

        videos = searcher.search_trending_videos(
            region=request.region,
            category=request.category,
            max_results=request.max_results,
            video_duration=request.duration,
            min_views=request.min_views,
            require_subtitles=True
        )

        return {
            "success": True,
            "data": {
                "videos": videos,
                "count": len(videos)
            }
        }
    except Exception as e:
        print(f"❌ 트렌딩 검색 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search/keywords")
async def search_keywords(request: SearchKeywordsRequest):
    """키워드 검색"""
    try:
        print(f"🔍 키워드 검색: {request.keywords}")

        videos = searcher.search_by_keywords(
            keywords=request.keywords,
            region=request.region,
            max_results=request.max_results,
            order=request.order,
            require_subtitles=True
        )

        return {
            "success": True,
            "data": {
                "videos": videos,
                "count": len(videos)
            }
        }
    except Exception as e:
        print(f"❌ 키워드 검색 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 다운로드
# ============================================================

@app.post("/api/download")
async def download_video(request: DownloadRequest):
    """영상 다운로드"""
    try:
        print(f"📥 다운로드: {request.url}")

        result = downloader.download_video(
            url=request.url,
            download_subtitles=True,
            subtitle_lang=request.subtitle_lang
        )

        if result['success']:
            # 메타데이터 저장
            video_info = downloader.get_video_info(request.url)
            if video_info:
                metadata = {
                    'video_id': video_info['video_id'],
                    'original': {
                        'url': request.url,
                        'title': video_info.get('title'),
                        'channel_name': video_info.get('channel'),
                        'duration': video_info.get('duration'),
                        'view_count': video_info.get('view_count', 0),
                    },
                    'processing': {
                        'status': 'downloaded',
                    },
                    'files': {
                        'original_video': result['video_path'],
                        'original_subtitle': result.get('subtitle_path'),
                    }
                }
                metadata_manager.save_video_metadata(metadata)

        return {
            "success": result['success'],
            "data": result
        }
    except Exception as e:
        print(f"❌ 다운로드 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 번역
# ============================================================

@app.post("/api/translate")
async def translate_subtitle(request: TranslateRequest):
    """자막 번역"""
    try:
        print(f"🌐 번역: {request.video_id} -> {request.target_lang}")

        # 메타데이터 조회
        metadata = metadata_manager.get_video_metadata(request.video_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="영상 메타데이터를 찾을 수 없습니다")

        subtitle_path = metadata['files'].get('original_subtitle')
        if not subtitle_path:
            raise HTTPException(status_code=404, detail="자막 파일을 찾을 수 없습니다")

        # 번역
        translated_path = subtitle_path.replace('.srt', f'.{request.target_lang}.srt')
        result = translator.translate_srt_file(
            input_path=subtitle_path,
            output_path=translated_path,
            target_lang=request.target_lang,
            batch_size=10
        )

        # 메타데이터 업데이트
        if result['success']:
            metadata['files']['translated_subtitle'] = translated_path
            metadata['processing']['status'] = 'translated'

            # 제목/설명 번역
            translated_metadata = translator.translate_metadata(
                title=metadata['original']['title'],
                description=metadata['original'].get('description', ''),
                target_lang=request.target_lang
            )
            metadata['translated'] = translated_metadata

            metadata_manager.save_video_metadata(metadata)

        return {
            "success": result['success'],
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 번역 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 리믹스
# ============================================================

@app.post("/api/remix")
async def remix_video(request: RemixRequest):
    """영상 리믹스"""
    try:
        print(f"🎬 리믹스: {request.video_id}")

        # 메타데이터 조회
        metadata = metadata_manager.get_video_metadata(request.video_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="영상 메타데이터를 찾을 수 없습니다")

        video_path = metadata['files'].get('original_video')
        subtitle_path = metadata['files'].get('translated_subtitle')

        if not video_path or not subtitle_path:
            raise HTTPException(status_code=404, detail="필요한 파일을 찾을 수 없습니다")

        # 리믹스
        output_path = f"./remixed/{request.video_id}_ko.mp4"
        result = remixer.add_translated_subtitles(
            video_path=video_path,
            subtitle_path=subtitle_path,
            output_path=output_path
        )

        # 메타데이터 업데이트
        if result:
            metadata['files']['remixed_video'] = result
            metadata['processing']['status'] = 'completed'
            metadata_manager.save_video_metadata(metadata)

            return {
                "success": True,
                "data": {
                    "output_path": result
                }
            }
        else:
            raise HTTPException(status_code=500, detail="리믹스 실패")

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 리믹스 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 배치 처리
# ============================================================

def run_batch_remix(job_id: str, params: BatchRemixRequest):
    """배치 리믹스 백그라운드 작업"""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from batch_remix import RemixBatchProcessor

    try:
        batch_jobs[job_id]['status'] = 'running'

        processor = RemixBatchProcessor()
        stats = processor.process_trending(
            region=params.region,
            category=params.category,
            max_videos=params.max_videos,
            video_duration=params.duration,
            min_views=params.min_views,
            target_lang=params.target_lang,
            skip_existing=True
        )

        batch_jobs[job_id]['status'] = 'completed'
        batch_jobs[job_id]['result'] = stats

    except Exception as e:
        batch_jobs[job_id]['status'] = 'failed'
        batch_jobs[job_id]['error'] = str(e)
        print(f"❌ 배치 작업 실패: {e}")


@app.post("/api/batch/start")
async def start_batch_remix(request: BatchRemixRequest, background_tasks: BackgroundTasks):
    """배치 리믹스 시작"""
    try:
        import uuid
        job_id = str(uuid.uuid4())[:8]

        batch_jobs[job_id] = {
            'status': 'pending',
            'params': request.dict()
        }

        # 백그라운드 작업 시작
        background_tasks.add_task(run_batch_remix, job_id, request)

        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "status": "started"
            }
        }
    except Exception as e:
        print(f"❌ 배치 시작 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/status/{job_id}")
async def get_batch_status(job_id: str):
    """배치 작업 상태 조회"""
    if job_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")

    return {
        "success": True,
        "data": batch_jobs[job_id]
    }


# ============================================================
# 메타데이터 관리
# ============================================================

@app.get("/api/videos")
async def list_videos(status: Optional[str] = None):
    """영상 목록 조회"""
    try:
        videos = metadata_manager.list_videos(status=status)

        return {
            "success": True,
            "data": {
                "videos": videos,
                "count": len(videos)
            }
        }
    except Exception as e:
        print(f"❌ 영상 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/videos/{video_id}")
async def get_video(video_id: str):
    """영상 상세 조회"""
    try:
        metadata = metadata_manager.get_video_metadata(video_id)

        if not metadata:
            raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")

        return {
            "success": True,
            "data": metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 영상 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/videos/{video_id}")
async def delete_video(video_id: str, delete_files: bool = False):
    """영상 삭제"""
    try:
        success = metadata_manager.delete_video(video_id, delete_files=delete_files)

        if not success:
            raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")

        return {
            "success": True,
            "data": {
                "message": "삭제되었습니다"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 영상 삭제 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("YouTube Remix System API Server")
    print("=" * 70)
    print("\n🚀 서버 시작 중...\n")
    print("📡 API 문서: http://localhost:8000/docs")
    print("📊 대시보드: http://localhost:3000")
    print("\n" + "=" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
