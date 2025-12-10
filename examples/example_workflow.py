"""
예제: 전체 워크플로우 실행

이 예제는 Python 스크립트로 전체 파이프라인을 실행하는 방법을 보여줍니다.
CLI 대신 직접 서비스를 호출할 수 있습니다.
"""
import os
import sys
from dotenv import load_dotenv

# 상위 디렉토리의 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from local_cli.services.trend_analyzer import TrendAnalyzer
from local_cli.services.script_generator import ScriptGenerator
from local_cli.services.video_producer import VideoProducer
from local_cli.services.youtube_uploader import YouTubeUploader
from local_cli.services.ai_service import get_ai_service

# 환경 변수 로드
load_dotenv()


def main():
    """전체 파이프라인 실행"""

    print("🚀 AI YouTube 자동화 시작\n")

    # AI Provider 설정
    ai_provider = 'gemini'  # 또는 'claude', 'auto'

    # 1. 트렌드 분석
    print("=" * 60)
    print("1️⃣ 트렌드 분석")
    print("=" * 60)

    analyzer = TrendAnalyzer(ai_provider=ai_provider)
    videos = analyzer.fetch_trending_videos(region='US', max_results=50)
    analysis = analyzer.analyze_with_ai(videos, video_format='short')

    print(f"\n주요 키워드: {', '.join(analysis['keywords'][:5])}")
    print(f"콘텐츠 아이디어:")
    for i, idea in enumerate(analysis['content_ideas'], 1):
        print(f"  {i}. {idea}")

    # 상위 3개 키워드 사용
    keywords = analysis['keywords'][:3]

    # 2. 대본 생성
    print("\n" + "=" * 60)
    print("2️⃣ 대본 생성")
    print("=" * 60)

    generator = ScriptGenerator(ai_provider=ai_provider)
    scripts = generator.generate_script(
        trend_keywords=keywords,
        video_format='short',
        duration_seconds=60,
        tone='informative',
        num_versions=1
    )

    script = scripts[0]
    print(f"\n생성된 대본 (첫 200자):\n{script[:200]}...")

    # 대본 저장
    os.makedirs('./output', exist_ok=True)
    script_path = './output/generated_script.txt'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    print(f"\n💾 대본 저장: {script_path}")

    # 3. 영상 제작
    print("\n" + "=" * 60)
    print("3️⃣ 영상 제작")
    print("=" * 60)

    producer = VideoProducer()
    video_path, thumbnail_path = producer.produce_video(
        script={
            'content': script,
            'video_format': 'short'
        },
        style_preset='short_trendy',
        output_path='./output/final_video.mp4'
    )

    print(f"\n✅ 영상 제작 완료:")
    print(f"  - 영상: {video_path}")
    print(f"  - 썸네일: {thumbnail_path}")

    # 4. 메타데이터 생성
    print("\n" + "=" * 60)
    print("4️⃣ 메타데이터 생성")
    print("=" * 60)

    uploader = YouTubeUploader(ai_provider=ai_provider)
    metadata = uploader.generate_metadata(
        script={'content': script},
        trend_keywords=keywords
    )

    print(f"\n제목: {metadata['title']}")
    print(f"설명: {metadata['description'][:150]}...")
    print(f"태그: {', '.join(metadata['tags'][:5])}")

    # 5. 업로드 (옵션)
    print("\n" + "=" * 60)
    print("5️⃣ 업로드 (스킵됨)")
    print("=" * 60)

    print("""
업로드하려면:
python local_cli/main.py upload \\
  --video ./output/final_video.mp4 \\
  --keywords "AI,기술,트렌드" \\
  --script ./output/generated_script.txt
    """)

    # 사용량 통계
    print("\n" + "=" * 60)
    print("📊 사용량 통계")
    print("=" * 60)

    ai_service = get_ai_service(ai_provider)
    print(ai_service.get_usage_stats())


if __name__ == '__main__':
    main()
