"""
Gemini API 테스트 스크립트 (최신 SDK)
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini_new_sdk():
    """최신 google-genai SDK 테스트"""
    print("🧪 Gemini API 테스트 (최신 SDK)\n")

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        print("💡 .env 파일에 GEMINI_API_KEY를 추가하세요.")
        return

    try:
        from google import genai
        print("✅ google-genai 패키지 로드 성공")
    except ImportError:
        print("❌ google-genai 패키지가 설치되지 않았습니다.")
        print("💡 pip install google-genai 실행하세요.")
        return

    try:
        # 클라이언트 초기화
        client = genai.Client(api_key=api_key)
        print("✅ Gemini 클라이언트 초기화 성공")

        # 텍스트 생성 테스트
        print("\n📝 텍스트 생성 테스트...")
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents="AI 기술의 미래에 대해 3문장으로 설명해주세요.",
            config={
                'max_output_tokens': 500,
                'temperature': 0.7,
            }
        )

        print("✅ 응답 성공!\n")
        print("=" * 50)
        print(response.text)
        print("=" * 50)

        print("\n✅ 모든 테스트 통과!")
        print("💰 비용: 무료 (Gemini 2.0 Flash)")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n💡 문제 해결:")
        print("1. API 키가 올바른지 확인")
        print("2. https://aistudio.google.com/apikey 에서 키 확인")
        print("3. pip install --upgrade google-genai 실행")


def test_ai_service():
    """ai_service.py 통합 테스트"""
    print("\n" + "=" * 50)
    print("🧪 AI Service 통합 테스트")
    print("=" * 50 + "\n")

    try:
        from local_cli.services.ai_service import get_ai_service

        # Auto 모드 (Gemini 우선)
        ai = get_ai_service('auto')
        print(f"✅ AI 서비스 초기화 성공 (primary: {ai.primary})")

        # 텍스트 생성 테스트
        print("\n📝 대본 생성 테스트...")
        response = ai.generate_text(
            prompt="유튜브 쇼츠용 AI 기술 소개 대본을 30초 분량으로 작성해주세요.",
            max_tokens=500,
            temperature=0.8,
            system_prompt="당신은 전문 유튜브 대본 작가입니다."
        )

        print("✅ 대본 생성 성공!\n")
        print("=" * 50)
        print(response)
        print("=" * 50)

        # 사용량 통계
        print("\n" + ai.get_usage_stats())

        print("\n✅ 모든 통합 테스트 통과!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 1. 최신 SDK 직접 테스트
    test_gemini_new_sdk()

    # 2. ai_service.py 통합 테스트
    test_ai_service()
