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

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import JobHistory as DBJobHistory, JobStatus
from core.models import (
    ContentPlan,
    VideoFormat,
    AssetBundle,
    UploadResult,
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

        # DB 세션
        self.db: Session = SessionLocal()

        # 모듈 초기화 (lazy loading)
        self._planner: Optional[ContentPlanner] = None
        self._asset_manager: Optional[AssetManager] = None
        self._editor: Optional[VideoEditor] = None
        self._uploader: Optional[YouTubeUploader] = None

        self.logger.info("Orchestrator 초기화 완료 (DB 모드)")

    def _setup_logging(self, log_file: Optional[str]):
        """
        로깅 시스템 설정

        Args:
            log_file: 로그 파일 경로
        """
        self.logger = logging.getLogger("orchestrator")
        self.logger.setLevel(logging.INFO)

        # 기존 핸들러 제거
        if self.logger.hasHandlers():
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
                ai_provider=self.config.ai_provider.value,
                model=self.config.gemini_model if self.config.ai_provider.value == "gemini" else None
            )
        return self._planner

    def _get_asset_manager(self) -> AssetManager:
        """Asset Manager 모듈 가져오기 (lazy loading)"""
        if not self._asset_manager:
            self._asset_manager = AssetManager(
                stock_providers=['pexels', 'pixabay'],
                tts_provider=self.config.tts_provider.value,
                cache_enabled=True,
                bgm_enabled=True  # Phase 5: BGM 자동 선택 활성화
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
        account_id: Optional[int] = None,
        template: Optional[str] = None,
        tts_settings: Optional[Dict[str, Any]] = None
    ) -> DBJobHistory:
        """
        전체 콘텐츠 생성 파이프라인 실행 (DB 기반)

        Args:
            topic: 주제
            video_format: 영상 포맷
            target_duration: 목표 길이(초)
            upload: YouTube 업로드 여부
            job_id: 작업 ID (None이면 자동 생성)
            account_id: 계정 ID (DB 설정 조회용)
            template: 사용할 템플릿 이름
            tts_settings: TTS 설정 오버라이드

        Returns:
            JobHistory ORM 객체
        """
        # 작업 ID 생성
        if not job_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            job_id = f"job_{timestamp}"

        self.logger.info(f"작업 시작: {job_id} (주제: {topic})")
        self._update_progress(f"작업 시작: {topic}", 0)

        # DB에 작업 기록 생성
        db_job = DBJobHistory(
            job_id=job_id,
            account_id=account_id,
            topic=topic or "AI 생성 주제",
            status=JobStatus.PENDING,
            format=video_format.value,
            duration=target_duration
        )
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)

        try:
            # 1. Planner: 스크립트 생성
            self._update_job_status(db_job, JobStatus.PLANNING, "스크립트 생성 중...")

            # ✨ DEBUG: target_duration 로그
            print(f"\n[Orchestrator] ========== 파이프라인 시작 ==========")
            print(f"[Orchestrator] 주제: {topic}")
            print(f"[Orchestrator] target_duration: {target_duration}초 ⬅️ 중요!")
            print(f"[Orchestrator] ===========================================\n")

            planner = self._get_planner()
            content_plan = planner.create_script(
                topic=topic,
                format=video_format,
                target_duration=target_duration
            )
            if not content_plan:
                raise Exception("스크립트 생성 실패")

            # ✨ DEBUG: 생성된 ContentPlan의 target_duration 확인
            print(f"[Orchestrator] ContentPlan 생성 완료:")
            print(f"[Orchestrator]   - 제목: {content_plan.title}")
            print(f"[Orchestrator]   - target_duration: {content_plan.target_duration}초 ⬅️ 확인!")

            self.logger.info(f"스크립트 생성 완료: {content_plan.title}")

            # 2. Asset Manager: 에셋 수집
            self._update_job_status(db_job, JobStatus.COLLECTING_ASSETS, "에셋 수집 중 (영상 + 음성)...")
            asset_manager = self._get_asset_manager()
            asset_bundle = asset_manager.collect_assets(
                content_plan,
                download_videos=True,
                generate_tts=True,
                account_id=account_id,
                tts_settings_override=tts_settings
            )
            if not asset_bundle:
                raise Exception("에셋 수집 실패")
            self.logger.info(f"에셋 수집 완료: 영상 {len(asset_bundle.videos)}개")

            # 3. Editor: 영상 편집
            self._update_job_status(db_job, JobStatus.EDITING, "영상 편집 중...")
            editor = self._get_editor()
            output_filename = f"{job_id}.mp4"
            video_path = editor.create_video(
                content_plan=content_plan,
                asset_bundle=asset_bundle,
                output_filename=output_filename,
                template_name=template
            )
            if not video_path:
                raise Exception("영상 편집 실패")
            db_job.output_video_path = str(video_path)
            self.logger.info(f"영상 편집 완료: {video_path}")

            # 4. Uploader: YouTube 업로드 (옵션)
            if upload or self.config.auto_upload:
                self._update_job_status(db_job, JobStatus.UPLOADING, "YouTube 업로드 중...")
                uploader = self._get_uploader()
                metadata = uploader.generate_metadata(content_plan, optimize_seo=True)
                if not uploader.youtube:
                    uploader.authenticate(account_id=account_id) # 계정별 인증

                upload_result = uploader.upload_video(
                    video_path=str(video_path),
                    metadata=metadata,
                    max_retries=3
                )
                if upload_result.success:
                    db_job.youtube_url = upload_result.url
                    db_job.youtube_video_id = upload_result.video_id
                    self.logger.info(f"YouTube 업로드 완료: {upload_result.url}")
                else:
                    raise Exception(f"업로드 실패: {upload_result.error}")

            # 5. 완료
            self._update_job_status(db_job, JobStatus.COMPLETED, "모든 작업 완료!", 100)
            db_job.completed_at = datetime.utcnow()
            self.db.commit()
            self.logger.info(f"작업 완료: {job_id}")
            return db_job

        except Exception as e:
            import traceback
            error_message = str(e)
            self.logger.error(f"작업 실패 ({job_id}): {error_message}")
            traceback.print_exc()

            db_job.status = JobStatus.FAILED
            db_job.error_message = error_message
            db_job.completed_at = datetime.utcnow()
            self.db.commit()
            return db_job

    def _update_job_status(self, db_job: DBJobHistory, status: JobStatus, message: str, progress: Optional[int] = None):
        """
        DB 기반 작업 상태 업데이트
        """
        db_job.status = status
        self.db.commit()
        
        # 진행률 계산 (대략적)
        if progress is None:
            progress_map = {
                JobStatus.PLANNING: 10,
                JobStatus.COLLECTING_ASSETS: 30,
                JobStatus.EDITING: 55,
                JobStatus.UPLOADING: 80,
                JobStatus.COMPLETED: 100,
                JobStatus.FAILED: 100,
            }
            progress = progress_map.get(status, 0)
            
        self._update_progress(message, progress)

    def __repr__(self):
        return f"ContentOrchestrator(mode=db)"
