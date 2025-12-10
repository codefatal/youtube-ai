"""
Trend Analyzer - YouTube 트렌드 분석 서비스
"""
import os
import json
import re
from typing import Optional, List, Dict
from googleapiclient.discovery import build
from .ai_service import get_ai_service


class TrendAnalyzer:
    """YouTube 트렌드 분석"""

    def __init__(self, ai_provider: str = 'auto'):
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        if not youtube_api_key:
            raise ValueError("YOUTUBE_API_KEY가 설정되지 않았습니다")

        self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        self.ai_service = get_ai_service(ai_provider)

    def fetch_trending_videos(
        self,
        region: str = 'US',
        category_id: Optional[str] = None,
        max_results: int = 50
    ) -> Dict:
        """YouTube 트렌딩 비디오 가져오기"""

        print(f"🔍 {region} 지역의 트렌딩 비디오 수집 중... (최대 {max_results}개)")

        request = self.youtube.videos().list(
            part='snippet,statistics',
            chart='mostPopular',
            regionCode=region,
            videoCategoryId=category_id,
            maxResults=max_results
        )

        response = request.execute()
        print(f"✅ {len(response.get('items', []))}개의 비디오를 가져왔습니다")

        return response

    def analyze_with_ai(self, video_data: Dict, video_format: str = 'short') -> Dict:
        """AI로 트렌드 분석 (Gemini/Claude 자동 선택)"""

        print(f"🤖 AI로 {video_format} 트렌드 분석 중...")

        # 비디오 데이터를 텍스트로 변환
        video_summaries = []
        for video in video_data.get('items', [])[:20]:  # 상위 20개만
            snippet = video['snippet']
            stats = video['statistics']

            summary = f"""
제목: {snippet['title']}
조회수: {stats.get('viewCount', 0)}
좋아요: {stats.get('likeCount', 0)}
댓글: {stats.get('commentCount', 0)}
"""
            video_summaries.append(summary)

        videos_text = "\n---\n".join(video_summaries)

        prompt = f"""
다음은 YouTube에서 현재 트렌딩 중인 {video_format} 영상들입니다.

{videos_text}

이 데이터를 분석하여 JSON 형식으로 응답해주세요.

반드시 다음 형식을 정확히 따라주세요:
{{
    "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5", "키워드6", "키워드7", "키워드8", "키워드9", "키워드10"],
    "topics": ["주제1", "주제2", "주제3", "주제4", "주제5"],
    "content_ideas": ["아이디어1", "아이디어2", "아이디어3"],
    "view_range": "10K-50K"
}}

중요:
- 모든 필드를 반드시 포함하세요
- JSON만 출력하고 다른 텍스트는 포함하지 마세요
- 완전한 JSON으로 끝까지 작성하세요
"""

        response = self.ai_service.generate_text(
            prompt=prompt,
            max_tokens=2000,  # JSON 응답을 위해 충분한 토큰
            temperature=0.3  # 분석은 낮은 temperature
        )

        # JSON 파싱
        analysis = self._parse_json_response(response)

        print(f"✅ 트렌드 분석 완료")
        return analysis

    def _parse_json_response(self, response: str) -> Dict:
        """AI 응답에서 JSON 추출 및 파싱"""

        if not response or not response.strip():
            print(f"⚠️ 빈 응답 수신")
            return self._get_default_analysis()

        # 코드 블록 제거 (```json ... ``` 또는 ``` ... ```)
        # 먼저 모든 백틱과 json 키워드 제거
        json_str = response.strip()

        # ```json 제거
        json_str = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
        # ``` 제거 (시작)
        json_str = re.sub(r'^```\s*', '', json_str, flags=re.MULTILINE)
        # ``` 제거 (끝)
        json_str = re.sub(r'\s*```$', '', json_str, flags=re.MULTILINE)

        json_str = json_str.strip()

        # { ... } 형식이 아니면 직접 찾기
        if not json_str.startswith('{'):
            if '{' in json_str and '}' in json_str:
                start = json_str.find('{')
                end = json_str.rfind('}') + 1
                json_str = json_str[start:end]

        try:
            analysis = json.loads(json_str)
            return analysis
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 실패: {e}")
            print(f"📄 원본 응답 전체:\n{response}")
            print(f"📄 파싱 시도한 문자열 전체:\n{json_str}")
            return self._get_default_analysis()

    def _get_default_analysis(self) -> Dict:
        """기본 분석 결과 반환"""
        return {
            "keywords": ["트렌드", "인기", "바이럴"],
            "topics": ["일반 트렌드"],
            "content_ideas": ["트렌드 기반 콘텐츠 제작"],
            "view_range": "알 수 없음"
        }

    def get_trending_keywords(
        self,
        region: str = 'US',
        video_format: str = 'short',
        max_results: int = 50
    ) -> List[str]:
        """트렌딩 키워드만 간단히 가져오기"""

        videos = self.fetch_trending_videos(region, max_results=max_results)
        analysis = self.analyze_with_ai(videos, video_format)

        return analysis.get('keywords', [])
