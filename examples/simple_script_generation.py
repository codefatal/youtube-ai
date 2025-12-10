"""
예제: 간단한 대본 생성

트렌드 분석 없이 직접 키워드로 대본을 생성하는 간단한 예제입니다.
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from local_cli.services.script_generator import ScriptGenerator

load_dotenv()


def main():
    # 대본 생성기 초기화
    generator = ScriptGenerator(ai_provider='gemini')  # 무료!

    # 키워드 설정
    keywords = ['AI', '인공지능', '미래기술']

    # 대본 생성 (3개 버전)
    print(f"📝 '{', '.join(keywords)}' 키워드로 대본 생성 중...\n")

    scripts = generator.generate_script(
        trend_keywords=keywords,
        video_format='short',
        duration_seconds=60,
        tone='informative',
        num_versions=3
    )

    # 결과 출력
    for i, script in enumerate(scripts, 1):
        print(f"\n{'='*60}")
        print(f"버전 {i}")
        print('='*60)
        print(script)

        # 파일로 저장
        os.makedirs('./output', exist_ok=True)
        with open(f'./output/script_v{i}.txt', 'w', encoding='utf-8') as f:
            f.write(script)


if __name__ == '__main__':
    main()
