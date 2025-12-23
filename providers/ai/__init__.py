"""
AI Providers Package
Gemini, Claude, OpenAI 등 AI API wrapper
"""
from .gemini import GeminiProvider


def get_ai_provider(provider: str = "gemini", api_key=None, model=None):
    """
    AI Provider 팩토리 함수

    Args:
        provider: AI 제공자 ("gemini", "claude", "openai")
        api_key: API 키 (None이면 환경변수에서 가져옴)
        model: 사용할 모델 (None이면 기본값)

    Returns:
        AI Provider 인스턴스

    Raises:
        NotImplementedError: 지원하지 않는 제공자인 경우
    """
    provider = provider.lower()

    if provider == "gemini":
        return GeminiProvider(api_key=api_key, model=model)
    elif provider == "claude":
        # TODO: Claude provider 구현
        raise NotImplementedError("Claude provider는 아직 구현되지 않았습니다")
    elif provider == "openai":
        # TODO: OpenAI provider 구현
        raise NotImplementedError("OpenAI provider는 아직 구현되지 않았습니다")
    else:
        raise ValueError(f"알 수 없는 AI 제공자: {provider}")


__all__ = ['GeminiProvider', 'get_ai_provider']
