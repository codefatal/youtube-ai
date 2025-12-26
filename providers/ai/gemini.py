"""
Gemini AI Provider
Google Gemini API wrapper for content generation
"""
import os
import re
import json
from typing import Optional, Dict, Any
from datetime import datetime


class GeminiProvider:
    """Google Gemini API 제공자"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Gemini Provider 초기화

        Args:
            api_key: Gemini API 키 (None이면 환경변수에서 가져옴)
            model: 사용할 모델 (기본값: gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다")

        self.model = model or os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.usage_log = []

        # Google GenAI 클라이언트 초기화
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "google-genai 패키지가 설치되지 않았습니다. "
                "pip install google-genai를 실행하세요."
            )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8000,
        json_mode: bool = False
    ) -> str:
        """
        텍스트 생성

        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트 (선택)
            temperature: 창의성 수준 (0.0-1.0)
            max_tokens: 최대 출력 토큰 수
            json_mode: JSON 응답 강제 여부

        Returns:
            생성된 텍스트
        """
        from google.genai import types

        # 시스템 프롬프트를 프롬프트에 포함
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        # JSON 모드일 경우 프롬프트에 명시
        if json_mode:
            full_prompt += "\n\n⚠️ 반드시 순수 JSON 형식으로만 응답하세요. 마크다운 코드 블록(```json)이나 다른 텍스트 없이 JSON만 출력하세요."

        # 생성 설정
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        # API 호출
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=config
            )

            # 응답 텍스트 추출
            response_text = response.text

            # 완료 상태 확인
            if hasattr(response, 'candidates') and response.candidates:
                finish_reason = response.candidates[0].finish_reason
                if finish_reason and finish_reason != 'STOP':
                    print(f"⚠️ Gemini 응답이 완전히 생성되지 않았습니다: {finish_reason}")

            # JSON 모드일 경우 마크다운 코드 블록 제거
            if json_mode:
                response_text = self._clean_json_response(response_text)

            # 사용량 로깅
            self._log_usage(prompt, response_text, response)

            return response_text

        except Exception as e:
            raise RuntimeError(f"Gemini API 호출 실패: {e}")

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8000
    ) -> Dict[str, Any]:
        """
        JSON 응답 생성 및 파싱

        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            temperature: 창의성 수준
            max_tokens: 최대 출력 토큰 수

        Returns:
            파싱된 JSON 딕셔너리

        Raises:
            json.JSONDecodeError: JSON 파싱 실패 시
        """
        response_text = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True
        )

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 실패: {e}")
            print(f"📄 원본 응답:\n{response_text}")
            raise

    def _clean_json_response(self, text: str) -> str:
        """
        마크다운 코드 블록 제거 및 JSON 정제

        Args:
            text: 원본 응답 텍스트

        Returns:
            정제된 JSON 문자열
        """
        # 마크다운 코드 블록 제거
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = text.strip()

        # JSON 부분만 추출 (첫 번째 { 부터 마지막 } 까지)
        match = re.search(r'\{.*\}', text, flags=re.DOTALL)
        if match:
            return match.group(0)

        return text

    def _log_usage(self, prompt: str, response: str, api_response):
        """
        API 사용량 로깅

        Args:
            prompt: 입력 프롬프트
            response: 출력 응답
            api_response: Gemini API 응답 객체
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'model': self.model,
            'prompt_length': len(prompt),
            'response_length': len(response),
        }

        # 토큰 사용량 추가 (가능한 경우)
        if hasattr(api_response, 'usage_metadata'):
            usage = api_response.usage_metadata
            log_entry['prompt_tokens'] = getattr(usage, 'prompt_token_count', 0)
            log_entry['response_tokens'] = getattr(usage, 'candidates_token_count', 0)
            log_entry['total_tokens'] = getattr(usage, 'total_token_count', 0)

        self.usage_log.append(log_entry)

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        사용량 통계 반환

        Returns:
            사용량 통계 딕셔너리
        """
        if not self.usage_log:
            return {
                'total_calls': 0,
                'total_tokens': 0,
                'estimated_cost': 0.0
            }

        total_calls = len(self.usage_log)
        total_tokens = sum(log.get('total_tokens', 0) for log in self.usage_log)
        total_prompt_tokens = sum(log.get('prompt_tokens', 0) for log in self.usage_log)
        total_response_tokens = sum(log.get('response_tokens', 0) for log in self.usage_log)

        return {
            'total_calls': total_calls,
            'total_tokens': total_tokens,
            'prompt_tokens': total_prompt_tokens,
            'response_tokens': total_response_tokens,
            'estimated_cost': 0.0,  # Gemini은 현재 무료
            'model': self.model
        }

    def __repr__(self):
        return f"GeminiProvider(model={self.model})"
