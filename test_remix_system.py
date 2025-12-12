"""
리믹스 시스템 통합 테스트
영상 다운로드 → 자막 번역 테스트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from local_cli.services.youtube_downloader import YouTubeDownloader
from local_cli.services.subtitle_translator import SubtitleTranslator

print("=" * 70)
print("YouTube 리믹스 시스템 테스트")
print("=" * 70)

# 1. 영상 정보 추출 테스트
print("\n[1] 영상 정보 추출 테스트")
print("-" * 70)

downloader = YouTubeDownloader()
test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" (YouTube 최초 영상)

info = downloader.get_video_info(test_url)
if info:
    print(f"제목: {info['title']}")
    print(f"채널: {info['channel']}")
    print(f"길이: {info['duration']}초")
    print(f"조회수: {info.get('view_count', 0):,}")
    print(f"자막 있음: {info.get('has_subtitles', False)}")
else:
    print("[ERROR] 정보 추출 실패")

# 2. 자막 번역 테스트
print("\n[2] 자막 번역 테스트")
print("-" * 70)

translator = SubtitleTranslator()

# 단일 텍스트 번역
test_text = "Hello! Welcome to this amazing video about AI technology."
print(f"원문: {test_text}")

translated = translator.translate_text(test_text, target_lang='ko')
print(f"번역: {translated}")

# 3. 메타데이터 번역 테스트
print("\n[3] 메타데이터 번역 테스트")
print("-" * 70)

metadata = translator.translate_metadata(
    title="10 Amazing AI Tools You Must Try Today",
    description="In this video, we explore the top 10 AI tools that can revolutionize your workflow and boost productivity.",
    target_lang='ko'
)

print(f"제목 번역: {metadata['title']}")
print(f"설명 번역: {metadata['description']}")

print("\n" + "=" * 70)
print("테스트 완료!")
print("=" * 70)

print("\n[INFO] 다음 단계:")
print("1. 실제 영상 다운로드 테스트 (주의: 파일 크기)")
print("2. SRT 자막 파일 번역 테스트")
print("3. 영상 + 번역 자막 합성 테스트")
