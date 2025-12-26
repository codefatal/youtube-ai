"""
Orchestrator Module
전체 콘텐츠 생성 파이프라인 관리 및 오케스트레이션
"""
import os
import json
import logging
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Lock

from core.models import (
    ContentJob,
    ContentPlan,
    ContentStatus,
    VideoFormat,
    AssetBundle,
    UploadResult,
    JobHistory,
    SystemConfig
)
from core.planner import ContentPlanner
from core.asset_manager import AssetManager
from core.editor import VideoEditor
from core.uploader import YouTubeUploader


class ContentOrchestrator:
    """콘텐츠 생성 파이프라인 오케스트레이터"""

    def __init__(
        self,
        config: Optional[SystemConfig] = None,
        log_file: Optional[str] = "logs/orchestrator.log",
        progress_callback: Optional[Callable[[str, int], None]] = None
    ):
        """
        ContentOrchestrator 초기화

        Args:
            config: 시스템 설정 (None이면 기본값 사용)
            log_file: 로그 파일 경로 (None이면 파일 로깅 비활성화)
            progress_callback: 진행 상황 콜백 함수 (message: str, progress: int)
        """
        self.config = config or SystemConfig()
        self.progress_callback = progress_callback

        # 로깅 설정
        self._setup_logging(log_file)

        # 작업 큐
        self.job_queue: Queue[ContentJob] = Queue()
        self.job_lock = Lock()

        # 작업 히스토리
        self.history = JobHistory()
        self.history_file = Path("data/job_history.json")

        # 히스토리 파일 로드
        self._load_history()

        # 모듈 초기화 (lazy loading)
        self._planner: Optional[ContentPlanner] = None
        self._asset_manager: Optional[AssetManager] = None
        self._editor: Optional[VideoEditor] = None
        self._uploader: Optional[YouTubeUploader] = None

        self.logger.info("Orchestrator 초기화 완료")

    def _setup_logging(self, log_file: Optional[str]):
        """
        로깅 시스템 설정

        Args:
            log_file: 로그 파일 경로
        """
        self.logger = logging.getLogger("orchestrator")
        self.logger.setLevel(logging.INFO)

        # 기존 핸들러 제거
        self.logger.handlers.clear()

        # 포맷터
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 파일 핸들러 (옵션)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _load_history(self):
        """작업 히스토리 파일 로드"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = JobHistory(**data)
                self.logger.info(f"히스토리 로드 완료: {len(self.history.jobs)}개 작업")
            except Exception as e:
                self.logger.warning(f"히스토리 로드 실패: {e}")

    def _save_history(self):
        """작업 히스토리 파일 저장"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                # Pydantic 모델을 JSON으로 변환
                json.dump(self.history.model_dump(), f, indent=2, ensure_ascii=False, default=str)
            self.logger.debug("히스토리 저장 완료")
        except Exception as e:
            self.logger.error(f"히스토리 저장 실패: {e}")

    def _update_progress(self, message: str, progress: int):
        """
        진행 상황 업데이트

        Args:
            message: 진행 메시지
            progress: 진행률 (0-100)
        """
        self.logger.info(f"[{progress}%] {message}")

        if self.progress_callback:
            try:
                self.progress_callback(message, progress)
            except Exception as e:
                self.logger.warning(f"진행 상황 콜백 실패: {e}")

    def _get_planner(self) -> ContentPlanner:
        """Planner 모듈 가져오기 (lazy loading)"""
        if not self._planner:
            self._planner = ContentPlanner(
                ai_provider=self.config.ai_provider.value
            )
        return self._planner

    def _get_asset_manager(self) -> AssetManager:
        """Asset Manager 모듈 가져오기 (lazy loading)"""
        if not self._asset_manager:
            self._asset_manager = AssetManager(
                stock_providers=['pexels', 'pixabay'],
                tts_provider=self.config.tts_provider.value,
                cache_enabled=True
            )
        return self._asset_manager

    def _get_editor(self) -> VideoEditor:
        """Editor 모듈 가져오기 (lazy loading)"""
        if not self._editor:
            self._editor = VideoEditor()
        return self._editor

    def _get_uploader(self) -> YouTubeUploader:
        """Uploader 모듈 가져오기 (lazy loading)"""
        if not self._uploader:
            self._uploader = YouTubeUploader(
                ai_provider=self.config.ai_provider.value
            )
        return self._uploader

    def create_content(
        self,
        topic: str,
        video_format: VideoFormat = VideoFormat.SHORTS,
        target_duration: int = 60,
        upload: bool = False,
        job_id: Optional[str] = None,
        account_id: Optional[int] = None  # ✨ NEW
    ) -> ContentJob:
        """
        전체 콘텐츠 생성 파이프라인 실행

        Args:
            topic: 주제
            video_format: 영상 포맷
            target_duration: 목표 길이(초)
            upload: YouTube 업로드 여부
            job_id: 작업 ID (None이면 자동 생성)
            account_id: 계정 ID (Phase 3 TTS 연동)

        Returns:
            ContentJob 객체
        """
        # 작업 ID 생성
        if not job_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            job_id = f"job_{timestamp}"

        # ContentJob 생성
        job = ContentJob(
            job_id=job_id,
            status=ContentStatus.PLANNING
        )

        # 히스토리에 추가
        with self.job_lock:
            self.history.jobs.append(job)
            self.history.total_jobs += 1
            self._save_history()

        self.logger.info(f"작업 시작: {job_id} (주제: {topic})")
        self._update_progress(f"작업 시작: {topic}", 0)

        try:
            # 1. Planner: 스크립트 생성
            self._update_job_status(job, ContentStatus.SCRIPTING)
            self._update_progress("스크립트 생성 중...", 10)

            planner = self._get_planner()
            content_plan = planner.create_script(
                topic=topic,
                format=video_format,
                target_duration=target_duration
            )

            if not content_plan:
                raise Exception("스크립트 생성 실패")

            job.plan = content_plan
            self.logger.info(f"스크립트 생성 완료: {content_plan.title}")
            self._update_progress(f"스크립트 완료: {content_plan.title}", 25)

            # 2. Asset Manager: 에셋 수집
            self._update_job_status(job, ContentStatus.ASSET_GATHERING)
            self._update_progress("에셋 수집 중 (영상 + 음성)...", 30)

            asset_manager = self._get_asset_manager()
            asset_bundle = asset_manager.collect_assets(
                content_plan,
                download_videos=True,
                generate_tts=True,
                account_id=account_id  # Phase 3에서 구현한 기능 사용
            )

            if not asset_bundle:
                raise Exception("에셋 수집 실패")

            job.assets = asset_bundle
            self.logger.info(f"에셋 수집 완료: 영상 {len(asset_bundle.videos)}개")
            self._update_progress(f"에셋 완료: 영상 {len(asset_bundle.videos)}개", 50)

            # 3. Editor: 영상 편집
            self._update_job_status(job, ContentStatus.EDITING)
            self._update_progress("영상 편집 중...", 55)

            editor = self._get_editor()
            output_filename = f"{job_id}.mp4"
            video_path = editor.create_video(
                content_plan=content_plan,
                asset_bundle=asset_bundle,
                output_filename=output_filename
            )

            if not video_path:
                raise Exception("영상 편집 실패")

            job.output_video_path = video_path
            self.logger.info(f"영상 편집 완료: {video_path}")
            self._update_progress(f"영상 완료: {video_path}", 75)

            # 4. Uploader: YouTube 업로드 (옵션)
            if upload or self.config.auto_upload:
                self._update_job_status(job, ContentStatus.UPLOADING)
                self._update_progress("YouTube 업로드 중...", 80)

                uploader = self._get_uploader()

                # 메타데이터 생성
                metadata = uploader.generate_metadata(content_plan, optimize_seo=True)

                # 인증 (최초 1회만)
                if not uploader.youtube:
                    uploader.authenticate()

                # 업로드
                upload_result = uploader.upload_video(
                    video_path=video_path,
                    metadata=metadata,
                    max_retries=3
                )

                job.upload_result = upload_result

                if upload_result.success:
                    self.logger.info(f"YouTube 업로드 완료: {upload_result.url}")
                    self._update_progress(f"업로드 완료: {upload_result.url}", 95)
                else:
                    raise Exception(f"업로드 실패: {upload_result.error}")

            # 5. 완료
            self._update_job_status(job, ContentStatus.COMPLETED)
            self._update_progress("모든 작업 완료!", 100)

            # 완료 작업 수 증가
            with self.job_lock:
                self.history.completed_jobs += 1
                self._save_history()

            self.logger.info(f"작업 완료: {job_id}")
            return job

        except Exception as e:
            # 에러 처리
            self.logger.error(f"작업 실패 ({job_id}): {e}")
            job.error_log.append(f"[{datetime.now()}] {str(e)}")
            self._update_job_status(job, ContentStatus.FAILED)

            # 실패 작업 수 증가
            with self.job_lock:
                self.history.failed_jobs += 1
                self._save_history()

            import traceback
            traceback.print_exc()

            return job

    def _update_job_status(self, job: ContentJob, status: ContentStatus):
        """
        작업 상태 업데이트

        Args:
            job: ContentJob 객체
            status: 새로운 상태
        """
        job.status = status
        job.updated_at = datetime.now()

        with self.job_lock:
            self._save_history()

    def add_to_queue(self, job: ContentJob):
        """
        작업 큐에 추가

        Args:
            job: ContentJob 객체
        """
        self.job_queue.put(job)
        self.logger.info(f"작업 큐 추가: {job.job_id} (큐 크기: {self.job_queue.qsize()})")

    def process_queue(self, max_jobs: Optional[int] = None):
        """
        작업 큐 처리 (순차 실행)

        Args:
            max_jobs: 최대 처리 작업 수 (None이면 전체)
        """
        processed = 0

        while not self.job_queue.empty():
            if max_jobs and processed >= max_jobs:
                break

            job = self.job_queue.get()

            self.logger.info(f"큐에서 작업 처리 시작: {job.job_id}")

            # 작업 실행 (기존 job 객체 사용)
            if job.plan:
                self.create_content(
                    topic=job.plan.title,
                    video_format=job.plan.format,
                    target_duration=job.plan.target_duration,
                    upload=self.config.auto_upload,
                    job_id=job.job_id
                )

            processed += 1
            self.job_queue.task_done()

        self.logger.info(f"큐 처리 완료: {processed}개 작업")

    def get_job(self, job_id: str) -> Optional[ContentJob]:
        """
        작업 ID로 작업 조회

        Args:
            job_id: 작업 ID

        Returns:
            ContentJob 또는 None
        """
        for job in self.history.jobs:
            if job.job_id == job_id:
                return job
        return None

    def get_recent_jobs(self, limit: int = 10) -> List[ContentJob]:
        """
        최근 작업 목록 조회

        Args:
            limit: 조회 개수

        Returns:
            ContentJob 리스트
        """
        return sorted(
            self.history.jobs,
            key=lambda j: j.created_at,
            reverse=True
        )[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """
        통계 정보 조회

        Returns:
            통계 딕셔너리
        """
        return {
            "total_jobs": self.history.total_jobs,
            "completed_jobs": self.history.completed_jobs,
            "failed_jobs": self.history.failed_jobs,
            "success_rate": (
                self.history.completed_jobs / self.history.total_jobs * 100
                if self.history.total_jobs > 0 else 0
            ),
            "queue_size": self.job_queue.qsize()
        }

    def __repr__(self):
        return f"ContentOrchestrator(total_jobs={self.history.total_jobs}, queue_size={self.job_queue.qsize()})"
