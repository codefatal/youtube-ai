"""
Phase 3 통합 테스트 - 트렌딩 검색 & 자동화
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from local_cli.services.trending_searcher import TrendingSearcher

print("=" * 70)
print("Phase 3: 트렌딩 검색 & CLI 통합 테스트")
print("=" * 70)

# =====================================================================
# Test 1: 트렌딩 영상 검색
# =====================================================================
print("\n" + "=" * 70)
print("TEST 1: 트렌딩 영상 검색 (미국, Science & Technology)")
print("=" * 70)

searcher = TrendingSearcher()

videos = searcher.search_trending_videos(
    region='US',
    category='Science & Technology',
    max_results=5,
    video_duration='short',  # 숏폼만 (<4분)
    min_views=10000,
    require_subtitles=True
)

if videos:
    print(f"\n[OK] {len(videos)}개 영상 발견")
    for i, video in enumerate(videos, 1):
        # Windows console 인코딩 에러 방지
        title = video['title'][:60].encode('ascii', 'replace').decode('ascii')
        channel = video['channel_name'].encode('ascii', 'replace').decode('ascii')
        print(f"\n[{i}] {title}...")
        print(f"    채널: {channel}")
        print(f"    조회수: {video['view_count']:,}")
        print(f"    길이: {video['duration']}초")
        print(f"    자막: {video.get('caption')}")
        print(f"    URL: {video['url']}")
else:
    print("[WARNING] 검색 결과 없음")

# =====================================================================
# Test 2: 키워드 검색
# =====================================================================
print("\n" + "=" * 70)
print("TEST 2: 키워드 검색 'AI technology'")
print("=" * 70)

videos = searcher.search_by_keywords(
    keywords='AI technology',
    region='US',
    max_results=3,
    order='viewCount',
    require_subtitles=True
)

if videos:
    print(f"\n[OK] {len(videos)}개 영상 발견")
    for i, video in enumerate(videos, 1):
        title = video['title'][:60].encode('ascii', 'replace').decode('ascii')
        print(f"\n[{i}] {title}...")
        print(f"    조회수: {video['view_count']:,}")
        print(f"    길이: {video['duration']}초")
else:
    print("[WARNING] 검색 결과 없음")

# =====================================================================
# Test 3: 필터링 기능
# =====================================================================
print("\n" + "=" * 70)
print("TEST 3: 필터링 기능")
print("=" * 70)

# 먼저 다양한 길이의 영상 검색
all_videos = searcher.search_trending_videos(
    region='US',
    category='Science & Technology',
    max_results=10,
    video_duration='any',  # 모든 길이
    min_views=1000,
    require_subtitles=False  # 자막 필수 해제
)

print(f"\n[INFO] 전체 영상: {len(all_videos)}개")

# 숏폼 필터링
shorts = searcher.filter_shorts(all_videos, max_duration=60)
print(f"\n[숏폼 (≤60초)]: {len(shorts)}개")
for video in shorts[:3]:
    title = video['title'][:40].encode('ascii', 'replace').decode('ascii')
    print(f"  - {title}... ({video['duration']}초)")

# 롱폼 필터링
long_videos = searcher.filter_long_form(all_videos, min_duration=180)
print(f"\n[롱폼 (≥180초)]: {len(long_videos)}개")
for video in long_videos[:3]:
    title = video['title'][:40].encode('ascii', 'replace').decode('ascii')
    print(f"  - {title}... ({video['duration']}초)")

# 조회수 정렬
sorted_videos = searcher.sort_by_views(all_videos)
print(f"\n[조회수 Top 3]:")
for i, video in enumerate(sorted_videos[:3], 1):
    title = video['title'][:40].encode('ascii', 'replace').decode('ascii')
    print(f"  {i}. {title}... ({video['view_count']:,} 조회)")

# =====================================================================
# Test 4: CLI 명령어 테스트 (시뮬레이션)
# =====================================================================
print("\n" + "=" * 70)
print("TEST 4: CLI 명령어 사용 예시")
print("=" * 70)

print("""
[사용 가능한 CLI 명령어]

1. 트렌딩 영상 검색:
   python local_cli/main.py search-trending --region US --category "Science & Technology"

2. 영상 다운로드:
   python local_cli/main.py download-video "https://youtube.com/watch?v=..."

3. 자막 번역:
   python local_cli/main.py translate-subtitle ./downloads/video.en.srt

4. 영상 리믹스:
   python local_cli/main.py remix-video ./downloads/video.mp4 ./downloads/video.ko.srt

5. 배치 자동 처리:
   python local_cli/main.py batch-remix --region US --max-videos 3

또는 배치 스크립트 직접 실행:
   python batch_remix.py --region US --max-videos 3 --duration short
""")

# =====================================================================
# Test 5: 메타데이터 연동 확인
# =====================================================================
print("\n" + "=" * 70)
print("TEST 5: 메타데이터 연동 확인")
print("=" * 70)

from local_cli.services.metadata_manager import MetadataManager

manager = MetadataManager()
stats = manager.get_stats()

print(f"\n[현재 메타데이터 통계]")
print(f"  - 전체 영상: {stats['total']}개")
print(f"  - 상태별: {stats['by_status']}")

if stats['total'] > 0:
    videos_list = manager.list_videos()
    print(f"\n[저장된 영상 목록]")
    for video in videos_list[:5]:  # 최대 5개만 표시
        title = video['original']['title'][:40].encode('ascii', 'replace').decode('ascii')
        print(f"  - {video['video_id']}: {title}...")
        print(f"    상태: {video['processing']['status']}")

# =====================================================================
# 결과
# =====================================================================
print("\n" + "=" * 70)
print("Phase 3 테스트 완료!")
print("=" * 70)

print("""
[구현 완료 기능]
[OK] 트렌딩 영상 검색 (trending_searcher.py)
[OK] 키워드 검색
[OK] 필터링 (길이, 조회수, 자막)
[OK] 정렬 (조회수, 참여도)
[OK] 배치 처리 스크립트 (batch_remix.py)
[OK] CLI 통합 (5개 명령어)

[다음 단계: Phase 4 - 웹 UI]
- 트렌딩 검색 페이지
- 다운로드 진행 상황 표시
- 메타데이터 관리 인터페이스
- 리믹스 작업 대시보드
""")
