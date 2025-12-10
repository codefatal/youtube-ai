"""
AI Service - Gemini와 Claude API를 통합하는 서비스
"""
import os
from typing import Literal, Optional
from datetime import datetime


class AIService:
    """Claude와 Gemini를 통합하는 AI 서비스"""

    def __init__(self, provider: Literal['claude', 'gemini', 'auto'] = 'auto'):
        self.provider = provider
        self.usage_log = []

        # Claude 초기화
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                import anthropic
                self.claude = anthropic.Anthropic(
                    api_key=os.getenv('ANTHROPIC_API_KEY')
                )
            except ImportError:
                print("⚠️ anthropic 패키지가 설치되지 않았습니다. pip install anthropic")
                self.claude = None
        else:
            self.claude = None

        # Gemini 초기화 (최신 SDK)
        if os.getenv('GEMINI_API_KEY'):
            try:
                from google import genai
                self.genai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
                # 모델 선택: 환경변수로 설정 가능, 기본값은 2.5-flash
                self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            except ImportError:
                print("⚠️ google-genai 패키지가 설치되지 않았습니다. pip install google-genai")
                self.genai_client = None
                self.gemini_model = None
        else:
            self.genai_client = None
            self.gemini_model = None

        # Auto 모드: Gemini 우선 (무료), 실패 시 Claude
        if provider == 'auto':
            self.primary = 'gemini' if self.genai_client else 'claude'
            self.fallback = 'claude' if self.primary == 'gemini' and self.claude else None
        else:
            self.primary = provider
            self.fallback = None

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """텍스트 생성 (Claude/Gemini 자동 선택)"""

        try:
            if self.primary == 'gemini':
                return self._generate_with_gemini(
                    prompt, max_tokens, temperature, system_prompt
                )
            elif self.primary == 'claude':
                return self._generate_with_claude(
                    prompt, max_tokens, temperature, system_prompt
                )
        except Exception as e:
            print(f"⚠️ {self.primary} 오류: {e}")

            # 폴백 시도
            if self.fallback:
                print(f"🔄 {self.fallback}로 재시도...")
                if self.fallback == 'claude':
                    return self._generate_with_claude(
                        prompt, max_tokens, temperature, system_prompt
                    )

            raise

    def _generate_with_gemini(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Gemini로 생성 (최신 SDK 사용)"""

        if not self.genai_client:
            raise ValueError("Gemini API 키가 설정되지 않았습니다")

        # 시스템 프롬프트를 프롬프트에 포함
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        # 생성 설정
        config = {
            'max_output_tokens': max_tokens,
            'temperature': temperature,
        }

        # API 호출 (최신 SDK 방식)
        response = self.genai_client.models.generate_content(
            model=self.gemini_model,
            contents=full_prompt,
            config=config
        )

        # 응답 텍스트 추출
        response_text = response.text

        # 디버깅: 응답 길이 출력
        print(f"🤖 Gemini 응답 길이: {len(response_text)} 문자")

        # 사용량 로깅
        self._log_usage('gemini', prompt, response_text)

        return response_text

    def _generate_with_claude(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: Optional[str]
    ) -> str:
        """Claude로 생성"""

        if not self.claude:
            raise ValueError("Claude API 키가 설정되지 않았습니다")

        # API 호출
        message = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text

        # 사용량 로깅
        self._log_usage('claude', prompt, response_text)

        return response_text

    def _log_usage(self, provider: str, prompt: str, response: str):
        """API 사용량 로깅"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'prompt_length': len(prompt),
            'response_length': len(response),
        }
        self.usage_log.append(log_entry)

    def get_usage_stats(self) -> str:
        """사용량 통계 반환"""
        if not self.usage_log:
            return "사용 기록 없음"

        claude_count = sum(1 for log in self.usage_log if log['provider'] == 'claude')
        gemini_count = sum(1 for log in self.usage_log if log['provider'] == 'gemini')

        total_prompts = sum(log['prompt_length'] for log in self.usage_log)
        total_responses = sum(log['response_length'] for log in self.usage_log)

        # 대략적인 토큰 수 계산 (1 토큰 ≈ 4 글자)
        total_tokens = (total_prompts + total_responses) // 4

        # 비용 추정
        claude_cost = (claude_count / len(self.usage_log)) * total_tokens * 3 / 1_000_000
        gemini_cost = 0  # 무료

        return f"""
📊 AI API 사용 통계:
- Claude 호출: {claude_count}회
- Gemini 호출: {gemini_count}회
- 총 토큰: 약 {total_tokens:,}
- 예상 비용: ${claude_cost:.2f} (Gemini는 무료)
        """


# 전역 AI 서비스 인스턴스
def get_ai_service(provider: Optional[str] = None) -> AIService:
    """AI 서비스 인스턴스 가져오기"""
    if provider is None:
        provider = os.getenv('AI_PROVIDER', 'auto')

    return AIService(provider=provider)
