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

이 데이터를 분석하여 다음을 JSON 형식으로 제공해주세요:
1. 주요 키워드 10개 (배열)
2. 트렌딩 주제 5개 (배열)
3. 추천 콘텐츠 아이디어 3개 (배열)
4. 예상 조회수 범위

JSON 형식 예시:
{{
    "keywords": ["키워드1", "키워드2", ...],
    "topics": ["주제1", "주제2", ...],
    "content_ideas": ["아이디어1", "아이디어2", ...],
    "view_range": "10K-50K"
}}

JSON만 응답해주세요 (추가 설명 없이).
"""

        response = self.ai_service.generate_text(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.3  # 분석은 낮은 temperature
        )

        # JSON 파싱
        analysis = self._parse_json_response(response)

        print(f"✅ 트렌드 분석 완료")
        return analysis

    def _parse_json_response(self, response: str) -> Dict:
        """AI 응답에서 JSON 추출 및 파싱"""

        # JSON 부분만 추출 (```json ... ``` 제거)
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # ``` 없이 직접 JSON이 온 경우
            json_str = response

        try:
            analysis = json.loads(json_str)
            return analysis
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 실패: {e}")
            # 파싱 실패 시 기본값 반환
            return {
                "keywords": ["트렌드", "인기"],
                "topics": ["일반"],
                "content_ideas": ["트렌드 기반 콘텐츠"],
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
