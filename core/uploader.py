"""
YouTube Uploader Module
YouTube Data API v3 기반 영상 업로드 및 메타데이터 관리
"""
import os
import pickle
import json
import re
import time
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime

from core.models import (
    ContentPlan,
    YouTubeMetadata,
    UploadResult,
    AIProvider,
    VideoFormat
)


class YouTubeUploader:
    """YouTube Data API v3 기반 업로더"""

    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    # YouTube 카테고리 매핑
    CATEGORY_MAP = {
        "pets": "15",           # Pets & Animals
        "howto": "26",          # Howto & Style
        "education": "27",      # Education
        "entertainment": "24",  # Entertainment
        "people": "22",         # People & Blogs (기본값)
        "gaming": "20",         # Gaming
        "news": "25",           # News & Politics
        "sports": "17",         # Sports
        "science": "28",        # Science & Technology
        "travel": "19",         # Travel & Events
    }

    def __init__(
        self,
        ai_provider: str = "gemini",
        credentials_path: str = "client_secrets.json",
        token_path: str = "token.pickle"
    ):
        """
        YouTubeUploader 초기화

        Args:
            ai_provider: AI 제공자 (gemini/claude)
            credentials_path: OAuth 2.0 클라이언트 시크릿 파일 경로
            token_path: 인증 토큰 저장 경로
        """
        self.ai_provider = ai_provider
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.youtube = None

        # AI 제공자 로드 (메타데이터 생성용)
        from providers.ai import get_ai_provider
        self.ai = get_ai_provider(ai_provider)

        print(f"[Uploader] AI 제공자: {ai_provider}")

    def authenticate(self) -> bool:
        """
        YouTube OAuth 2.0 인증

        Returns:
            인증 성공 여부
        """
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request

            credentials = None

            # 기존 토큰 확인
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    credentials = pickle.load(token)

            # 토큰이 없거나 유효하지 않으면 새로 인증
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    # 토큰 갱신
                    credentials.refresh(Request())
                else:
                    # 새로운 인증
                    if not os.path.exists(self.credentials_path):
                        print(f"[ERROR] {self.credentials_path} 파일을 찾을 수 없습니다.")
                        print("[INFO] Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고 다운로드하세요.")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        self.SCOPES
                    )
                    credentials = flow.run_local_server(port=8080)

                # 토큰 저장
                with open(self.token_path, 'wb') as token:
                    pickle.dump(credentials, token)

            # YouTube 서비스 빌드
            self.youtube = build('youtube', 'v3', credentials=credentials)
            print("[SUCCESS] YouTube API 인증 완료")
            return True

        except Exception as e:
            print(f"[ERROR] 인증 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_metadata(
        self,
        content_plan: ContentPlan,
        optimize_seo: bool = True
    ) -> YouTubeMetadata:
        """
        ContentPlan으로부터 최적화된 메타데이터 생성

        Args:
            content_plan: ContentPlan 객체
            optimize_seo: SEO 최적화 활성화

        Returns:
            YouTubeMetadata 객체
        """
        print("\n[Uploader] AI로 메타데이터 생성 중...")

        # 템플릿 로드
        template_path = Path("templates/metadata_prompts/title_description.txt")

        if not template_path.exists():
            print("[WARNING] 메타데이터 템플릿을 찾을 수 없습니다. 기본 메타데이터 사용")
            return self._create_default_metadata(content_plan)

        template = template_path.read_text(encoding='utf-8')

        # 스크립트 조합
        script_text = "\n".join([seg.text for seg in content_plan.segments])

        # 프롬프트 생성
        prompt = template.format(
            script=script_text,
            format=content_plan.format.value,
            category=content_plan.category
        )

        try:
            # AI로 메타데이터 생성
            result = self.ai.generate_json(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )

            # SEO 최적화 (옵션)
            if optimize_seo:
                result = self._optimize_seo(result, content_plan)

            # YouTubeMetadata 객체 생성
            metadata = YouTubeMetadata(
                title=result.get("title", content_plan.title),
                description=result.get("description", content_plan.description),
                tags=result.get("tags", content_plan.tags),
                category_id=result.get("category_id", content_plan.category),
                privacy_status="private"  # 기본값은 비공개
            )

            print(f"[SUCCESS] 메타데이터 생성 완료")
            print(f"  - 제목: {metadata.title}")
            print(f"  - 태그 수: {len(metadata.tags)}")

            return metadata

        except Exception as e:
            print(f"[ERROR] 메타데이터 생성 실패: {e}")
            return self._create_default_metadata(content_plan)

    def _create_default_metadata(self, content_plan: ContentPlan) -> YouTubeMetadata:
        """
        기본 메타데이터 생성 (AI 실패 시 폴백)

        Args:
            content_plan: ContentPlan 객체

        Returns:
            YouTubeMetadata 객체
        """
        return YouTubeMetadata(
            title=content_plan.title[:100],  # 최대 100자
            description=content_plan.description,
            tags=content_plan.tags[:15],  # 최대 15개
            category_id=content_plan.category,
            privacy_status="private"
        )

    def _optimize_seo(self, metadata: dict, content_plan: ContentPlan) -> dict:
        """
        SEO 최적화 로직

        Args:
            metadata: 메타데이터 딕셔너리
            content_plan: ContentPlan 객체

        Returns:
            최적화된 메타데이터
        """
        # 제목 최적화
        title = metadata.get("title", "")

        # 제목 길이 체크 (50-70자 권장)
        if len(title) < 30:
            print("[WARNING] 제목이 너무 짧습니다 (30자 미만)")
        elif len(title) > 100:
            metadata["title"] = title[:100]
            print(f"[INFO] 제목이 100자로 잘렸습니다: {metadata['title']}")

        # 설명 최적화
        description = metadata.get("description", "")

        # 쇼츠의 경우 #Shorts 해시태그 추가
        if content_plan.format == VideoFormat.SHORTS and "#Shorts" not in description:
            metadata["description"] = description + "\n\n#Shorts"

        # 태그 최적화
        tags = metadata.get("tags", [])

        # 태그 수 제한 (5-15개 권장)
        if len(tags) > 15:
            metadata["tags"] = tags[:15]
            print(f"[INFO] 태그가 15개로 제한되었습니다")
        elif len(tags) < 3:
            # ContentPlan의 태그를 추가
            metadata["tags"] = list(set(tags + content_plan.tags))[:15]

        # 태그 중복 제거
        metadata["tags"] = list(dict.fromkeys(metadata["tags"]))

        return metadata

    def upload_video(
        self,
        video_path: str,
        metadata: YouTubeMetadata,
        thumbnail_path: Optional[str] = None,
        max_retries: int = 3
    ) -> UploadResult:
        """
        YouTube에 영상 업로드 (재시도 로직 포함)

        Args:
            video_path: 영상 파일 경로
            metadata: YouTubeMetadata 객체
            thumbnail_path: 썸네일 경로 (선택)
            max_retries: 최대 재시도 횟수

        Returns:
            UploadResult 객체
        """
        # 인증 확인
        if not self.youtube:
            if not self.authenticate():
                return UploadResult(
                    success=False,
                    error="YouTube API 인증 실패"
                )

        # 파일 존재 확인
        if not os.path.exists(video_path):
            return UploadResult(
                success=False,
                error=f"영상 파일을 찾을 수 없습니다: {video_path}"
            )

        print(f"\n[Uploader] 업로드 시작: {metadata.title}")
        print(f"  - 파일: {video_path}")
        print(f"  - 공개 상태: {metadata.privacy_status}")

        # 재시도 로직
        for attempt in range(1, max_retries + 1):
            try:
                from googleapiclient.http import MediaFileUpload

                # 요청 바디 구성
                body = {
                    'snippet': {
                        'title': metadata.title,
                        'description': metadata.description,
                        'tags': metadata.tags,
                        'categoryId': metadata.category_id
                    },
                    'status': {
                        'privacyStatus': metadata.privacy_status,
                        'selfDeclaredMadeForKids': False
                    }
                }

                # 예약 업로드 처리
                if metadata.publish_at:
                    # RFC 3339 형식으로 변환
                    publish_time = metadata.publish_at.isoformat() + 'Z'
                    body['status']['publishAt'] = publish_time
                    body['status']['privacyStatus'] = 'private'  # 예약 업로드는 비공개로 설정
                    print(f"  - 예약 시각: {publish_time}")

                # 미디어 파일 업로드
                media = MediaFileUpload(
                    video_path,
                    chunksize=-1,
                    resumable=True
                )

                # 업로드 요청
                request = self.youtube.videos().insert(
                    part=','.join(body.keys()),
                    body=body,
                    media_body=media
                )

                # 업로드 진행
                print(f"[Uploader] 업로드 중... (시도 {attempt}/{max_retries})")
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        print(f"  진행률: {progress}%", end='\r')

                print()  # 줄바꿈

                # 업로드 성공
                video_id = response['id']
                video_url = f"https://www.youtube.com/watch?v={video_id}"

                print(f"[SUCCESS] 업로드 완료: {video_url}")

                # 썸네일 업로드 (있는 경우)
                if thumbnail_path and os.path.exists(thumbnail_path):
                    self._upload_thumbnail(video_id, thumbnail_path)

                return UploadResult(
                    success=True,
                    video_id=video_id,
                    url=video_url
                )

            except Exception as e:
                print(f"[ERROR] 업로드 실패 (시도 {attempt}/{max_retries}): {e}")

                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 지수 백오프 (2, 4, 8초)
                    print(f"[INFO] {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                else:
                    import traceback
                    traceback.print_exc()
                    return UploadResult(
                        success=False,
                        error=str(e)
                    )

        return UploadResult(
            success=False,
            error="최대 재시도 횟수 초과"
        )

    def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """
        썸네일 업로드

        Args:
            video_id: YouTube 영상 ID
            thumbnail_path: 썸네일 파일 경로
        """
        try:
            from googleapiclient.http import MediaFileUpload

            print(f"[Uploader] 썸네일 업로드 중...")
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            )
            request.execute()
            print("[SUCCESS] 썸네일 업로드 완료")

        except Exception as e:
            print(f"[WARNING] 썸네일 업로드 실패: {e}")

    def update_metadata(
        self,
        video_id: str,
        metadata: YouTubeMetadata
    ) -> bool:
        """
        기존 영상의 메타데이터 업데이트

        Args:
            video_id: YouTube 영상 ID
            metadata: YouTubeMetadata 객체

        Returns:
            성공 여부
        """
        if not self.youtube:
            if not self.authenticate():
                return False

        try:
            print(f"[Uploader] 메타데이터 업데이트 중... (ID: {video_id})")

            # 현재 메타데이터 가져오기
            request = self.youtube.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                print(f"[ERROR] 영상을 찾을 수 없습니다: {video_id}")
                return False

            video = response['items'][0]
            snippet = video['snippet']

            # 메타데이터 업데이트
            snippet['title'] = metadata.title
            snippet['description'] = metadata.description
            snippet['tags'] = metadata.tags
            snippet['categoryId'] = metadata.category_id

            # 업데이트 요청
            update_request = self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            )
            update_request.execute()

            print("[SUCCESS] 메타데이터 업데이트 완료")
            return True

        except Exception as e:
            print(f"[ERROR] 메타데이터 업데이트 실패: {e}")
            return False

    def __repr__(self):
        return f"YouTubeUploader(ai_provider={self.ai_provider})"
