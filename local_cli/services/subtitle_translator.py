"""
Subtitle Translator - SRT 자막 번역
Gemini API로 자막 파일 번역 (타임스탬프 유지)
"""
import os
import pysrt
from typing import List, Dict, Optional
from .ai_service import AIService


class SubtitleTranslator:
    """SRT 자막 파일 번역"""

    def __init__(self, ai_service: Optional[AIService] = None):
        """
        Args:
            ai_service: AIService 인스턴스 (없으면 자동 생성)
        """
        self.ai_service = ai_service or AIService()

    def translate_srt_file(
        self,
        input_path: str,
        output_path: str,
        target_lang: str = 'ko',
        batch_size: int = 10
    ) -> Dict:
        """SRT 파일 번역

        Args:
            input_path: 입력 SRT 파일 경로
            output_path: 출력 SRT 파일 경로
            target_lang: 목표 언어 (ko, ja, zh 등)
            batch_size: 한 번에 번역할 자막 개수 (API 효율성)

        Returns:
            Dict: 번역 결과
                - success: bool
                - total: 전체 자막 수
                - translated: 번역된 자막 수
                - output_path: 출력 파일 경로
        """
        print(f"\n[INFO] 자막 번역 시작: {os.path.basename(input_path)}")
        print(f"[INFO] 목표 언어: {target_lang}")

        try:
            # SRT 파일 로드
            subs = pysrt.open(input_path, encoding='utf-8')
            total = len(subs)
            print(f"[INFO] 총 {total}개 자막 로드됨")

            # 배치 단위로 번역
            translated_count = 0

            for i in range(0, total, batch_size):
                batch = subs[i:i + batch_size]
                print(f"[INFO] 번역 중... ({i+1}-{min(i+batch_size, total)}/{total})")

                # 배치 텍스트 추출
                texts = [sub.text for sub in batch]

                # 번역
                translated_texts = self._translate_batch(texts, target_lang)

                # 번역된 텍스트 적용 (타임스탬프는 유지)
                for j, translated in enumerate(translated_texts):
                    if translated:
                        batch[j].text = translated
                        translated_count += 1

            # 번역된 SRT 저장
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            subs.save(output_path, encoding='utf-8')

            print(f"[OK] 번역 완료: {translated_count}/{total}개")
            print(f"[OK] 저장: {output_path}")

            return {
                'success': True,
                'total': total,
                'translated': translated_count,
                'output_path': output_path
            }

        except Exception as e:
            print(f"[ERROR] 번역 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _translate_batch(self, texts: List[str], target_lang: str) -> List[str]:
        """여러 자막을 한번에 번역 (효율성)

        Args:
            texts: 번역할 텍스트 리스트
            target_lang: 목표 언어

        Returns:
            List[str]: 번역된 텍스트 리스트
        """
        lang_names = {
            'ko': '한국어',
            'ja': '일본어',
            'zh': '중국어',
            'es': '스페인어',
            'fr': '프랑스어',
            'de': '독일어'
        }
        target_lang_name = lang_names.get(target_lang, target_lang)

        # 번역 프롬프트
        prompt = f"""다음 영상 자막들을 {target_lang_name}로 번역해주세요.

**중요 규칙:**
1. 각 줄을 정확히 번역하되, 줄 수는 그대로 유지
2. 번역만 제공 (설명, 주석 없음)
3. 자연스러운 구어체로 번역
4. 영상 자막 스타일 유지

**원문 자막:**
"""

        # 각 자막에 번호 붙이기
        for i, text in enumerate(texts, 1):
            prompt += f"\n{i}. {text}"

        prompt += f"\n\n**{target_lang_name} 번역:**"

        try:
            # AI로 번역
            response = self.ai_service.generate_text(prompt)

            # 응답 파싱 (번호별로 분리)
            lines = response.strip().split('\n')
            translated = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # "1. 번역된 텍스트" 형식에서 번역 부분만 추출
                if '. ' in line:
                    parts = line.split('. ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        translated.append(parts[1])
                    else:
                        translated.append(line)
                else:
                    translated.append(line)

            # 원본과 개수 맞추기 (부족하면 빈 문자열 추가)
            while len(translated) < len(texts):
                translated.append(texts[len(translated)])  # 번역 실패한 것은 원문 유지

            return translated[:len(texts)]  # 원본 개수만큼만 반환

        except Exception as e:
            print(f"[WARNING] 배치 번역 실패: {e}, 원문 유지")
            return texts  # 실패하면 원문 그대로 반환

    def translate_text(self, text: str, target_lang: str = 'ko') -> str:
        """단일 텍스트 번역

        Args:
            text: 번역할 텍스트
            target_lang: 목표 언어

        Returns:
            str: 번역된 텍스트
        """
        result = self._translate_batch([text], target_lang)
        return result[0] if result else text

    def translate_metadata(
        self,
        title: str,
        description: str,
        target_lang: str = 'ko'
    ) -> Dict[str, str]:
        """제목과 설명 번역

        Args:
            title: 영상 제목
            description: 영상 설명
            target_lang: 목표 언어

        Returns:
            Dict: {'title': 번역된 제목, 'description': 번역된 설명}
        """
        lang_names = {
            'ko': '한국어',
            'ja': '일본어',
            'zh': '중국어',
        }
        target_lang_name = lang_names.get(target_lang, target_lang)

        prompt = f"""다음 YouTube 영상의 제목과 설명을 {target_lang_name}로 번역해주세요.

**제목:**
{title}

**설명:**
{description[:500]}

**번역 규칙:**
1. 제목: 클릭하고 싶은 매력적인 제목으로
2. 설명: 자연스럽고 읽기 쉽게
3. 형식은 아래와 같이 정확히 지켜주세요

**번역 결과:**
제목: [번역된 제목]
설명: [번역된 설명]
"""

        try:
            response = self.ai_service.generate_text(prompt)

            # 파싱
            translated_title = title
            translated_desc = description

            lines = response.strip().split('\n')
            for line in lines:
                if line.startswith('제목:'):
                    translated_title = line.replace('제목:', '').strip()
                elif line.startswith('설명:'):
                    translated_desc = line.replace('설명:', '').strip()

            return {
                'title': translated_title,
                'description': translated_desc
            }

        except Exception as e:
            print(f"[WARNING] 메타데이터 번역 실패: {e}")
            return {
                'title': title,
                'description': description
            }


# 테스트 코드
if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

    from local_cli.services.ai_service import AIService

    translator = SubtitleTranslator()

    # 단일 텍스트 번역 테스트
    print("=== 단일 텍스트 번역 테스트 ===")
    text = "Hello, welcome to this amazing video about artificial intelligence!"
    translated = translator.translate_text(text)
    print(f"원문: {text}")
    print(f"번역: {translated}")

    # 메타데이터 번역 테스트
    print("\n=== 메타데이터 번역 테스트 ===")
    result = translator.translate_metadata(
        title="Top 10 AI Tools You Must Try in 2024",
        description="In this video, we explore the best AI tools that can boost your productivity."
    )
    print(f"제목: {result['title']}")
    print(f"설명: {result['description']}")

    # SRT 파일 번역 테스트는 실제 파일이 필요하므로 주석 처리
    # result = translator.translate_srt_file('test.en.srt', 'test.ko.srt')
