"""
Gemini AI Provider
Google Gemini API wrapper for content generation
"""
import os
import re
import json
import time
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
        self.original_model = self.model  # 원본 모델 저장 (fallback용)
        self.usage_log = []
        self.fallback_attempted = False  # fallback 시도 여부

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
            error_str = str(e)

            # 429 quota 초과 에러 감지
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                # ✨ RetryInfo에서 대기 시간 추출
                retry_delay = self._extract_retry_delay(error_str)

                # ✨ 1차: RetryInfo 대기 후 재시도
                if retry_delay and retry_delay <= 60:  # 60초 이하만 자동 대기
                    print(f"\n{'='*60}")
                    print(f"⚠️  Gemini Rate Limit 감지!")
                    print(f"{'='*60}")
                    print(f"[AUTO-RETRY] {retry_delay:.1f}초 대기 후 재시도합니다...")
                    print(f"{'='*60}\n")

                    time.sleep(retry_delay + 1)  # 여유 1초 추가

                    try:
                        response = self.client.models.generate_content(
                            model=self.model,
                            contents=full_prompt,
                            config=config
                        )

                        response_text = response.text

                        if hasattr(response, 'candidates') and response.candidates:
                            finish_reason = response.candidates[0].finish_reason
                            if finish_reason and finish_reason != 'STOP':
                                print(f"⚠️ Gemini 응답이 완전히 생성되지 않았습니다: {finish_reason}")

                        if json_mode:
                            response_text = self._clean_json_response(response_text)

                        self._log_usage(prompt, response_text, response)

                        print(f"[SUCCESS] 재시도 성공!\n")
                        return response_text

                    except Exception as retry_error:
                        print(f"[WARNING] 재시도 실패: {retry_error}")
                        # 2차 fallback으로 진행

                # ✨ 2차: gemini-2.5-flash → gemini-1.5-flash 또는 gemini-2.0-flash
                if not self.fallback_attempted:
                    # 2.5 사용 중이면 1.5로 fallback (더 안정적)
                    if "2.5" in self.model:
                        fallback_model = "gemini-1.5-flash"
                    else:
                        fallback_model = "gemini-2.0-flash"

                    print(f"\n{'='*60}")
                    print(f"⚠️  Gemini Quota 초과 - 모델 전환!")
                    print(f"{'='*60}")
                    print(f"[AUTO-FALLBACK] {self.model} → {fallback_model}")
                    print(f"[INFO] 다른 모델은 별도 quota로 계산됩니다")
                    print(f"{'='*60}\n")

                    # 모델 변경
                    self.model = fallback_model
                    self.fallback_attempted = True

                    # 재시도
                    try:
                        response = self.client.models.generate_content(
                            model=self.model,
                            contents=full_prompt,
                            config=config
                        )

                        response_text = response.text

                        if hasattr(response, 'candidates') and response.candidates:
                            finish_reason = response.candidates[0].finish_reason
                            if finish_reason and finish_reason != 'STOP':
                                print(f"⚠️ Gemini 응답이 완전히 생성되지 않았습니다: {finish_reason}")

                        if json_mode:
                            response_text = self._clean_json_response(response_text)

                        self._log_usage(prompt, response_text, response)

                        print(f"[SUCCESS] {fallback_model}로 성공적으로 처리 완료!\n")
                        return response_text

                    except Exception as fallback_error:
                        print(f"[ERROR] {fallback_model} fallback도 실패: {fallback_error}")
                        raise RuntimeError(f"Gemini API 호출 실패 (모든 fallback 실패): {fallback_error}")

            # quota 에러가 아니거나 이미 fallback을 시도했으면 그냥 에러 발생
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
        from google.genai import types

        # 시스템 프롬프트를 프롬프트에 포함
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        # JSON 모드 프롬프트 추가
        full_prompt += "\n\n⚠️ 반드시 순수 JSON 형식으로만 응답하세요. 마크다운 코드 블록(```json)이나 다른 텍스트 없이 JSON만 출력하세요."

        # 최대 2번 재시도 (MAX_TOKENS 오류 시 토큰 수 증가)
        current_max_tokens = max_tokens
        max_retries = 2

        for attempt in range(max_retries + 1):
            try:
                # 생성 설정
                config = types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=current_max_tokens,
                )

                # API 호출
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=config
                )

                # 응답 텍스트 추출
                response_text = response.text

                # 완료 상태 확인
                finish_reason = None
                if hasattr(response, 'candidates') and response.candidates:
                    finish_reason = response.candidates[0].finish_reason

                # MAX_TOKENS 오류이고 재시도 가능한 경우
                # finish_reason은 enum이므로 str() 또는 .name으로 비교
                finish_reason_str = str(finish_reason) if finish_reason else ''
                if 'MAX_TOKENS' in finish_reason_str and attempt < max_retries:
                    current_max_tokens = int(current_max_tokens * 1.5)  # 1.5배 증가
                    print(f"⚠️ MAX_TOKENS 도달! 토큰 수를 {current_max_tokens}로 증가하여 재시도... ({attempt+1}/{max_retries})")
                    continue

                # 다른 finish_reason 경고
                if finish_reason and 'STOP' not in finish_reason_str:
                    print(f"⚠️ Gemini 응답이 완전히 생성되지 않았습니다: {finish_reason}")

                # JSON 정제
                response_text = self._clean_json_response(response_text)

                # 사용량 로깅
                self._log_usage(full_prompt, response_text, response)

                # JSON 파싱
                return json.loads(response_text)

            except json.JSONDecodeError as e:
                # MAX_TOKENS 오류로 인한 파싱 실패일 가능성
                if attempt < max_retries:
                    current_max_tokens = int(current_max_tokens * 1.5)
                    print(f"❌ JSON 파싱 실패: {e}")
                    print(f"📄 토큰 수를 {current_max_tokens}로 증가하여 재시도... ({attempt+1}/{max_retries})")
                    continue
                else:
                    print(f"❌ JSON 파싱 실패 (재시도 횟수 초과): {e}")
                    print(f"📄 원본 응답:\n{response_text}")
                    raise

            except Exception as e:
                error_str = str(e)

                # ✨ Rate limit 에러 처리 (generate()와 동일)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    # 1차: RetryInfo 대기 후 재시도
                    retry_delay = self._extract_retry_delay(error_str)
                    if retry_delay and retry_delay <= 60 and attempt == 0:  # 첫 시도에서만
                        print(f"\n{'='*60}")
                        print(f"⚠️  Gemini Rate Limit 감지! (JSON 모드)")
                        print(f"{'='*60}")
                        print(f"[AUTO-RETRY] {retry_delay:.1f}초 대기 후 재시도합니다...")
                        print(f"{'='*60}\n")

                        time.sleep(retry_delay + 1)
                        continue  # 재시도

                    # 2차: 모델 전환
                    if not self.fallback_attempted and attempt == 0:
                        fallback_model = "gemini-1.5-flash" if "2.5" in self.model else "gemini-2.0-flash"
                        print(f"\n[AUTO-FALLBACK] {self.model} → {fallback_model}")
                        self.model = fallback_model
                        self.fallback_attempted = True
                        continue  # 재시도

                # 다른 에러는 즉시 발생
                raise RuntimeError(f"Gemini API 호출 실패: {e}")

        # 여기 도달하면 모든 재시도 실패
        raise RuntimeError(f"JSON 생성 실패: 최대 재시도 횟수({max_retries}) 초과")

    def _extract_retry_delay(self, error_str: str) -> Optional[float]:
        """
        에러 메시지에서 RetryInfo의 retryDelay 추출

        Args:
            error_str: 에러 메시지

        Returns:
            대기 시간(초) 또는 None
        """
        # "Please retry in 41.868561516s" 패턴
        match = re.search(r'retry in ([\d.]+)s', error_str, re.IGNORECASE)
        if match:
            return float(match.group(1))

        # "retryDelay": "41s" 패턴
        match = re.search(r'"retryDelay"\s*:\s*"([\d.]+)s"', error_str)
        if match:
            return float(match.group(1))

        return None

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
