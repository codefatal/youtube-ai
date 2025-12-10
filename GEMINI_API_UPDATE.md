# Gemini API 업데이트 가이드

## 변경 사항 요약

최신 Gemini API 공식 문서(https://ai.google.dev/gemini-api/docs)를 기반으로 코드를 업데이트했습니다.

### 주요 변경 사항

1. **SDK 변경**
   - 이전: `google-generativeai` (구 SDK)
   - 현재: `google-genai` (최신 SDK) ✨

2. **모델 업그레이드**
   - 이전: `gemini-1.5-flash`
   - 현재: `gemini-2.5-flash` (최신 안정 버전) 🚀

3. **API 사용법 변경**

**이전 방식:**
```python
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt, generation_config=config)
```

**최신 방식:**
```python
from google import genai

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=config
)
```

## 업데이트된 파일

### 1. `requirements.txt`
```diff
- google-generativeai>=0.3.0
+ google-genai>=0.2.0
```

### 2. `local_cli/services/ai_service.py`

**변경된 초기화 코드:**
```python
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
```

**변경된 생성 메서드:**
```python
def _generate_with_gemini(self, prompt, max_tokens, temperature, system_prompt):
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

    return response.text
```

### 3. `README.md`

**API 키 발급 URL 업데이트:**
```diff
- https://makersuite.google.com/app/apikey
+ https://aistudio.google.com/apikey
```

### 4. `.env.example` (신규 생성)
```env
# Gemini API (무료!) - https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Claude API (선택) - https://console.anthropic.com/
ANTHROPIC_API_KEY=your_claude_api_key_here

# AI 프로바이더 선택: auto (Gemini 우선), gemini, claude
AI_PROVIDER=auto
```

## 마이그레이션 가이드

### 1. 의존성 재설치

```bash
# 가상환경 활성화
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 최신 패키지 설치
pip install --upgrade google-genai

# 구 SDK 제거 (선택사항)
pip uninstall google-generativeai
```

### 2. 환경 변수 확인

`.env` 파일에 API 키가 설정되어 있는지 확인:

```bash
GEMINI_API_KEY=your_api_key_here
```

API 키가 없다면:
1. https://aistudio.google.com/apikey 방문
2. "Create API Key" 클릭
3. 생성된 키를 `.env`에 저장

### 3. 테스트

```bash
# Gemini API 테스트
python test_gemini.py

# 또는 개별 테스트
python -c "from local_cli.services.ai_service import get_ai_service; ai = get_ai_service('gemini'); print(ai.generate_text('Hello!'))"
```

## 새로운 기능

### Gemini 2.0 Flash의 장점

1. **더 빠른 속도** ⚡
   - 응답 시간 단축
   - 더 효율적인 토큰 처리

2. **향상된 품질** ✨
   - 더 자연스러운 한국어 생성
   - 문맥 이해 능력 향상

3. **여전히 무료** 💰
   - Gemini 2.0 Flash는 무료 티어에서 사용 가능
   - 요금 걱정 없이 사용 가능

### 사용 가능한 모델

현재 지원하는 Gemini 모델:

- **Gemini 2.5 Flash**: `gemini-2.5-flash` (기본값) ✨
  - 최신 안정 버전
  - 빠른 속도와 높은 품질
  - 무료 티어 지원

- **Gemini 2.5 Pro**: `gemini-2.5-pro`
  - 고급 추론 모델
  - 더 강력하지만 느림
  - 유료 (더 높은 품질 필요 시)

- **Gemini 1.5 Flash**: `gemini-1.5-flash` (레거시)
  - 이전 안정 버전
  - 무료 티어 지원

모델을 변경하려면 `.env` 파일에 설정:

```env
# 기본 (2.5 Flash)
GEMINI_MODEL=gemini-2.5-flash

# 고급 모델 (2.5 Pro)
GEMINI_MODEL=gemini-2.5-pro

# 레거시 (1.5 Flash)
GEMINI_MODEL=gemini-1.5-flash
```

## 문제 해결

### ImportError: cannot import name 'genai' from 'google'

**원인**: 구 SDK와 신 SDK가 충돌

**해결방법**:
```bash
pip uninstall google-generativeai
pip install --upgrade google-genai
```

### API 키 오류

**원인**: 잘못된 API 키 또는 권한 부족

**해결방법**:
1. https://aistudio.google.com/apikey 에서 키 확인
2. `.env` 파일에 올바르게 복사했는지 확인
3. API 키에 공백이나 특수문자가 없는지 확인

### ModuleNotFoundError: No module named 'google.genai'

**원인**: 최신 SDK가 설치되지 않음

**해결방법**:
```bash
pip install google-genai
```

## 참고 자료

- **Gemini API 공식 문서**: https://ai.google.dev/gemini-api/docs
- **API 키 발급**: https://aistudio.google.com/apikey
- **Python SDK GitHub**: https://github.com/google/generative-ai-python
- **가격 정책**: https://ai.google.dev/pricing (무료 티어 확인)

## 이전 버전과의 호환성

기존 코드에 영향을 주지 않도록 설계되었습니다:

- `get_ai_service()` 함수는 동일하게 작동
- `generate_text()` 메서드 시그니처 동일
- 환경 변수 이름 동일 (`GEMINI_API_KEY`)

백엔드 API와 프론트엔드는 수정 없이 그대로 사용 가능합니다! ✅
