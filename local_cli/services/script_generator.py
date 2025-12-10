"""
Script Generator - AI 대본 생성 서비스
"""
from typing import List, Dict
from .ai_service import get_ai_service


class ScriptGenerator:
    """AI 대본 생성"""

    def __init__(self, ai_provider: str = 'auto'):
        self.ai_service = get_ai_service(ai_provider)

    def generate_script(
        self,
        trend_keywords: List[str],
        video_format: str,  # 'short' or 'long'
        duration_seconds: int,
        tone: str = 'informative',
        num_versions: int = 1
    ) -> List[str]:
        """대본 생성 (Gemini/Claude 자동 선택)"""

        duration_guide = {
            'short': '30-60초 분량, 빠른 템포, 강력한 훅',
            'long': f'{duration_seconds//60}분 분량, 상세한 설명, 단계별 구성'
        }

        system_prompt = """당신은 전문 유튜브 대본 작가입니다.
시청자의 관심을 끌고 유지율을 높이는 대본을 작성합니다."""

        prompt = f"""
유튜브 {video_format} 영상 대본을 작성해주세요.

트렌드 키워드: {', '.join(trend_keywords)}
영상 길이: {duration_seconds}초 ({duration_guide[video_format]})
톤: {tone}

요구사항:
1. 첫 3초에 강력한 후킹 포인트 (질문, 놀라운 사실 등)
2. 타임스탬프 포함: [00:00] 형식
3. 시청자 유지율을 고려한 구성
4. 명확한 CTA(Call-to-Action) 포함
5. 자연스러운 말투 (너무 격식적이지 않게)

형식 예시:
[00:00] 여러분, 지금 이 영상을 보시면...
[00:05] 오늘은 {trend_keywords[0]}에 대해...
[00:15] 첫 번째로...

대본을 작성해주세요.
"""

        scripts = []
        for i in range(num_versions):
            print(f"📝 대본 버전 {i+1}/{num_versions} 생성 중...")

            response = self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=8000,  # thinking 토큰 + 출력 토큰
                temperature=0.7 + (i * 0.1),  # 버전마다 다양성 증가
                system_prompt=system_prompt
            )

            scripts.append(response)
            print(f"✅ 버전 {i+1} 완료 ({len(response)}자)")

        return scripts

    def generate_script_from_idea(
        self,
        content_idea: str,
        video_format: str = 'short',
        duration_seconds: int = 60,
        tone: str = 'informative'
    ) -> str:
        """특정 아이디어로 대본 생성"""

        system_prompt = """당신은 전문 유튜브 대본 작가입니다.
시청자의 관심을 끌고 유지율을 높이는 대본을 작성합니다."""

        prompt = f"""
다음 아이디어를 바탕으로 유튜브 {video_format} 영상 대본을 작성해주세요.

콘텐츠 아이디어: {content_idea}
영상 길이: {duration_seconds}초
톤: {tone}

요구사항:
1. 첫 3초에 강력한 후킹 포인트
2. 타임스탬프 포함: [00:00] 형식
3. 시청자 유지율을 고려한 구성
4. 명확한 CTA 포함
5. 자연스러운 말투

대본을 작성해주세요.
"""

        print(f"📝 '{content_idea}' 대본 생성 중...")

        response = self.ai_service.generate_text(
            prompt=prompt,
            max_tokens=8000,  # thinking 토큰 + 출력 토큰
            temperature=0.7,
            system_prompt=system_prompt
        )

        print(f"✅ 대본 생성 완료 ({len(response)}자)")

        return response

    def improve_script(self, original_script: str, feedback: str) -> str:
        """기존 대본 개선"""

        prompt = f"""
다음 유튜브 영상 대본을 개선해주세요.

원본 대본:
{original_script}

개선 요청:
{feedback}

개선된 대본을 작성해주세요. 타임스탬프 형식 [00:00]을 유지해주세요.
"""

        print(f"✏️ 대본 개선 중...")

        response = self.ai_service.generate_text(
            prompt=prompt,
            max_tokens=8000,  # thinking 토큰 + 출력 토큰
            temperature=0.7
        )

        print(f"✅ 대본 개선 완료")

        return response
