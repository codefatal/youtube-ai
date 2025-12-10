"""
YouTube Uploader - 유튜브 업로드 및 메타데이터 생성 서비스
"""
import os
import pickle
import json
import re
from typing import Dict, List, Tuple, Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .ai_service import get_ai_service


class YouTubeUploader:
    """YouTube 업로드 및 메타데이터 관리"""

    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    def __init__(self, ai_provider: str = 'auto'):
        self.youtube = self._get_authenticated_service()
        self.ai_service = get_ai_service(ai_provider)

    def _get_authenticated_service(self):
        """OAuth 인증"""
        credentials = None

        # 기존 토큰 확인
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)

        # 토큰이 없거나 유효하지 않으면 새로 인증
        if not credentials or not credentials.valid:
            if not os.path.exists('client_secrets.json'):
                raise FileNotFoundError(
                    "client_secrets.json 파일이 없습니다. "
                    "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고 다운로드하세요."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                self.SCOPES
            )
            credentials = flow.run_local_server(port=8080)

            # 토큰 저장
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)

        return build('youtube', 'v3', credentials=credentials)

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        category_id: str = '22',
        privacy_status: str = 'public',
        thumbnail_path: Optional[str] = None
    ) -> Tuple[str, str]:
        """비디오 업로드"""

        print(f"\n📤 유튜브 업로드 시작...")
        print(f"제목: {title}")
        print(f"태그: {', '.join(tags)}")

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }

        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True
        )

        request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        print("📤 업로드 중...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"진행률: {progress}%", end='\r')

        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # 썸네일 업로드 (있는 경우)
        if thumbnail_path and os.path.exists(thumbnail_path):
            print(f"\n📸 썸네일 업로드 중...")
            self.upload_thumbnail(video_id, thumbnail_path)

        print(f"\n✅ 업로드 완료: {video_url}")
        return video_id, video_url

    def upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """썸네일 업로드"""
        try:
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            )
            request.execute()
            print("✅ 썸네일 업로드 완료")
        except Exception as e:
            print(f"⚠️ 썸네일 업로드 실패: {e}")

    def generate_metadata(
        self,
        script: Dict,
        trend_keywords: List[str]
    ) -> Dict[str, any]:
        """AI로 자동 메타데이터 생성 (Gemini/Claude)"""

        print("📝 AI로 메타데이터 생성 중...")

        prompt = f"""
다음 영상 대본과 트렌드 키워드를 바탕으로 유튜브 메타데이터를 생성해주세요:

대본 (일부):
{script['content'][:500]}...

키워드: {', '.join(trend_keywords)}

다음 형식의 JSON으로 응답해주세요:
{{
    "title": "클릭을 유도하는 제목 (50자 이내, 이모지 포함 가능)",
    "description": "상세 설명 (500자 이내, 타임스탬프 포함 추천)",
    "tags": ["태그1", "태그2", ...] (10-15개, 관련성 높은 태그)
}}

JSON만 응답해주세요.
"""

        response = self.ai_service.generate_text(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )

        # JSON 파싱
        metadata = self._parse_json_response(response, trend_keywords)

        print(f"✅ 메타데이터 생성 완료")
        return metadata

    def _parse_json_response(
        self,
        response: str,
        trend_keywords: List[str]
    ) -> Dict[str, any]:
        """AI 응답에서 JSON 추출 및 파싱"""

        # JSON 부분만 추출 (```json ... ``` 제거)
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response

        try:
            metadata = json.loads(json_str)
            return metadata
        except json.JSONDecodeError:
            # 파싱 실패 시 기본값
            print("⚠️ JSON 파싱 실패, 기본 메타데이터 사용")
            return {
                "title": f"{trend_keywords[0]} - 필수 시청!",
                "description": f"오늘은 {trend_keywords[0]}에 대해 알아봅니다.",
                "tags": trend_keywords
            }

    def update_video_metadata(
        self,
        video_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        """기존 비디오의 메타데이터 업데이트"""

        print(f"📝 비디오 메타데이터 업데이트 중... (ID: {video_id})")

        # 현재 메타데이터 가져오기
        request = self.youtube.videos().list(
            part='snippet',
            id=video_id
        )
        response = request.execute()

        if not response['items']:
            raise ValueError(f"비디오를 찾을 수 없습니다: {video_id}")

        video = response['items'][0]
        snippet = video['snippet']

        # 업데이트할 항목만 변경
        if title:
            snippet['title'] = title
        if description:
            snippet['description'] = description
        if tags:
            snippet['tags'] = tags

        # 업데이트 요청
        update_request = self.youtube.videos().update(
            part='snippet',
            body={
                'id': video_id,
                'snippet': snippet
            }
        )

        update_request.execute()
        print("✅ 메타데이터 업데이트 완료")
