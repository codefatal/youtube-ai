"""
Phase 2 통합 테스트 - 전체 리믹스 워크플로우
다운로드 → 번역 → 메타데이터 저장 → 영상 합성
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from local_cli.services.youtube_downloader import YouTubeDownloader
from local_cli.services.subtitle_translator import SubtitleTranslator
from local_cli.services.metadata_manager import MetadataManager
from local_cli.services.video_remixer import VideoRemixer

print("=" * 70)
print("Phase 2: 전체 리믹스 워크플로우 테스트")
print("=" * 70)

# 테스트할 영상 URL
# "Me at the zoo" - YouTube 최초 영상 (19초, 자막 있음)
test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"

print(f"\n[INFO] 테스트 영상: {test_url}")
print("[INFO] 참고: 실제 다운로드는 주석 처리되어 있습니다")
print("[INFO] 테스트하려면 아래 주석을 해제하세요\n")

# =====================================================================
# Step 1: 영상 정보 확인
# =====================================================================
print("\n" + "=" * 70)
print("STEP 1: 영상 정보 확인")
print("=" * 70)

downloader = YouTubeDownloader(download_dir='./downloads')
info = downloader.get_video_info(test_url)

if info:
    print(f"\n[OK] 영상 정보 추출 성공")
    print(f"  - 제목: {info['title']}")
    print(f"  - 채널: {info['channel']}")
    print(f"  - 길이: {info['duration']}초")
    print(f"  - 조회수: {info.get('view_count', 0):,}")
    print(f"  - 자막 있음: {info.get('has_subtitles', False)}")

    video_id = info['video_id']
else:
    print("[ERROR] 영상 정보 추출 실패")
    sys.exit(1)

# =====================================================================
# Step 2: 영상 + 자막 다운로드 (주석 처리 - 용량 고려)
# =====================================================================
print("\n" + "=" * 70)
print("STEP 2: 영상 + 자막 다운로드 (SKIPPED - 주석 해제하여 테스트)")
print("=" * 70)

# 실제 다운로드를 테스트하려면 아래 주석 해제
"""
download_result = downloader.download_video(
    test_url,
    download_subtitles=True,
    subtitle_lang='en'
)

if download_result['success']:
    print(f"\n[OK] 다운로드 성공")
    print(f"  - 영상: {download_result['video_path']}")
    print(f"  - 자막: {download_result['subtitle_path']}")

    video_path = download_result['video_path']
    subtitle_path = download_result['subtitle_path']
else:
    print(f"[ERROR] 다운로드 실패: {download_result.get('error')}")
    sys.exit(1)
"""

# 테스트용 더미 경로
video_path = f"./downloads/{video_id}.mp4"
subtitle_path = f"./downloads/{video_id}.en.srt"
print(f"\n[INFO] 다운로드 스킵 (주석 해제하여 실행 가능)")
print(f"  - 영상 경로: {video_path}")
print(f"  - 자막 경로: {subtitle_path}")

# =====================================================================
# Step 3: 자막 번역 (주석 처리 - 파일 필요)
# =====================================================================
print("\n" + "=" * 70)
print("STEP 3: 자막 번역 (SKIPPED - 실제 파일 필요)")
print("=" * 70)

# 실제 번역을 테스트하려면 아래 주석 해제 (Step 2도 필요)
"""
translator = SubtitleTranslator()

translated_subtitle_path = f"./downloads/{video_id}.ko.srt"

translation_result = translator.translate_srt_file(
    input_path=subtitle_path,
    output_path=translated_subtitle_path,
    target_lang='ko',
    batch_size=10
)

if translation_result['success']:
    print(f"\n[OK] 번역 성공")
    print(f"  - 번역된 자막: {translated_subtitle_path}")
    print(f"  - 번역 개수: {translation_result['translated']}/{translation_result['total']}")
else:
    print(f"[ERROR] 번역 실패: {translation_result.get('error')}")
    sys.exit(1)
"""

# 테스트용 더미 경로
translated_subtitle_path = f"./downloads/{video_id}.ko.srt"
print(f"\n[INFO] 번역 스킵 (주석 해제하여 실행 가능)")
print(f"  - 번역 자막 경로: {translated_subtitle_path}")

# =====================================================================
# Step 4: 메타데이터 저장 (실행 가능)
# =====================================================================
print("\n" + "=" * 70)
print("STEP 4: 메타데이터 저장")
print("=" * 70)

manager = MetadataManager(metadata_dir='./metadata')

# 메타데이터 구성
metadata = {
    'video_id': video_id,
    'original': {
        'url': test_url,
        'title': info.get('title'),
        'description': info.get('description', '')[:500],
        'channel_name': info.get('channel'),
        'channel_url': info.get('channel_url'),
        'views': info.get('view_count', 0),
        'likes': info.get('like_count', 0),
        'duration': info.get('duration'),
        'upload_date': info.get('upload_date'),
        'license': info.get('license', 'Standard YouTube License'),
        'category': info.get('categories', ['Unknown'])[0] if info.get('categories') else 'Unknown',
        'tags': info.get('tags', [])[:10],
    },
    'translated': {
        'title': '[번역 예정]',
        'description': '[번역 예정]',
        'subtitle_path': translated_subtitle_path,
    },
    'processing': {
        'status': 'pending',
    },
    'files': {
        'original_video': video_path,
        'original_subtitle': subtitle_path,
        'translated_subtitle': translated_subtitle_path,
        'remixed_video': f'./remixed/{video_id}_ko.mp4',
    },
    'copyright': {
        'attribution': f'Original: "{info.get("title")}" by {info.get("channel")}',
        'license': info.get('license', 'Standard YouTube License'),
        'commercial_use': False,  # 기본적으로 보수적으로 설정
        'modifications': True,
    }
}

# 메타데이터 저장
save_success = manager.save_video_metadata(metadata)

if save_success:
    print(f"\n[OK] 메타데이터 저장 성공")
    print(f"  - 위치: ./metadata/videos.json")

    # 출처 표시 텍스트 생성
    print("\n[INFO] 출처 표시 텍스트:")
    print("-" * 70)
    attribution = manager.generate_attribution_text(video_id, format='full')
    print(attribution)
    print("-" * 70)
else:
    print("[ERROR] 메타데이터 저장 실패")

# =====================================================================
# Step 5: 영상 리믹스 (주석 처리 - 파일 필요)
# =====================================================================
print("\n" + "=" * 70)
print("STEP 5: 영상 리믹스 (SKIPPED - 실제 파일 필요)")
print("=" * 70)

# 실제 리믹스를 테스트하려면 아래 주석 해제 (Step 2, 3 필요)
"""
remixer = VideoRemixer()

output_video_path = f'./remixed/{video_id}_ko.mp4'

remix_result = remixer.add_translated_subtitles(
    video_path=video_path,
    subtitle_path=translated_subtitle_path,
    output_path=output_video_path
)

if remix_result:
    print(f"\n[OK] 리믹스 성공")
    print(f"  - 출력 영상: {remix_result}")

    # 메타데이터 업데이트
    manager.update_status(video_id, 'completed', remix_path=remix_result)
else:
    print("[ERROR] 리믹스 실패")
    manager.update_status(video_id, 'failed')
"""

print(f"\n[INFO] 리믹스 스킵 (주석 해제하여 실행 가능)")
print(f"  - 출력 경로: ./remixed/{video_id}_ko.mp4")

# =====================================================================
# 결과 확인
# =====================================================================
print("\n" + "=" * 70)
print("테스트 결과 요약")
print("=" * 70)

stats = manager.get_stats()
print(f"\n[통계]")
print(f"  - 전체 영상: {stats['total']}개")
print(f"  - 상태별: {stats['by_status']}")

print(f"\n[영상 목록]")
videos = manager.list_videos()
for v in videos:
    print(f"  - {v['video_id']}: {v['original']['title'][:50]}... ({v['processing']['status']})")

print("\n" + "=" * 70)
print("Phase 2 테스트 완료!")
print("=" * 70)

print("\n[다음 단계]")
print("1. 실제 다운로드/번역/리믹스 테스트를 위해 주석 해제")
print("2. Phase 3: 트렌딩 검색 기능 구현")
print("3. Phase 4: CLI 통합")
print("4. Phase 5: 웹 UI")
