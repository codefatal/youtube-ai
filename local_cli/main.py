"""
AI YouTube Automation CLI - 메인 CLI 도구
"""
import os
import click
from dotenv import load_dotenv
from services.trend_analyzer import TrendAnalyzer
from services.script_generator import ScriptGenerator
from services.video_producer import VideoProducer
from services.youtube_uploader import YouTubeUploader
from services.ai_service import get_ai_service
from services.music_library import MusicLibrary

# .env 파일 로드
load_dotenv()


@click.group()
def cli():
    """AI YouTube Automation CLI - 트렌드 분석부터 업로드까지 자동화"""
    pass


@cli.command()
@click.option('--provider', type=click.Choice(['claude', 'gemini', 'auto']),
              default='auto', help='AI provider')
def test_ai(provider):
    """AI 서비스 테스트"""
    click.echo(f"🤖 {provider} 테스트 중...\n")

    ai_service = get_ai_service(provider)

    response = ai_service.generate_text(
        prompt="안녕하세요! 간단한 자기소개를 해주세요.",
        max_tokens=200
    )

    click.echo(f"\n응답:\n{response}\n")
    click.echo(ai_service.get_usage_stats())


@cli.command()
@click.option('--region', default='US', help='YouTube region (US, KR, etc.)')
@click.option('--format', type=click.Choice(['short', 'long']), required=True,
              help='Video format')
@click.option('--ai', type=click.Choice(['claude', 'gemini', 'auto']),
              default='auto', help='AI provider')
@click.option('--max-results', default=50, help='Maximum number of videos to analyze')
def analyze_trends(region, format, ai, max_results):
    """트렌드 분석"""
    analyzer = TrendAnalyzer(ai_provider=ai)

    click.echo(f"🔍 {region} 지역의 {format} 트렌드 분석 중...")
    videos = analyzer.fetch_trending_videos(region=region, max_results=max_results)
    analysis = analyzer.analyze_with_ai(videos, video_format=format)

    click.echo("\n✅ 트렌드 분석 완료:")
    click.echo(f"\n주요 키워드: {', '.join(analysis['keywords'])}")
    click.echo(f"\n주제: {', '.join(analysis['topics'])}")
    click.echo(f"\n콘텐츠 아이디어:")
    for i, idea in enumerate(analysis['content_ideas'], 1):
        click.echo(f"  {i}. {idea}")
    click.echo(f"\n예상 조회수: {analysis['view_range']}")


@cli.command()
@click.option('--keywords', required=True, help='Comma-separated keywords')
@click.option('--format', type=click.Choice(['short', 'long']), required=True,
              help='Video format')
@click.option('--duration', type=int, required=True, help='Duration in seconds')
@click.option('--tone', default='informative', help='Script tone')
@click.option('--versions', type=int, default=3, help='Number of versions')
@click.option('--ai', type=click.Choice(['claude', 'gemini', 'auto']),
              default='auto', help='AI provider')
@click.option('--output', help='Output file path for script')
def generate_script(keywords, format, duration, tone, versions, ai, output):
    """대본 생성"""
    generator = ScriptGenerator(ai_provider=ai)

    keyword_list = [k.strip() for k in keywords.split(',')]

    click.echo(f"✍️ 대본 생성 중... ({format}, {duration}초, {versions}개 버전)")
    scripts = generator.generate_script(
        trend_keywords=keyword_list,
        video_format=format,
        duration_seconds=duration,
        tone=tone,
        num_versions=versions
    )

    for i, script in enumerate(scripts, 1):
        click.echo(f"\n{'='*60}")
        click.echo(f"버전 {i}")
        click.echo('='*60)
        click.echo(script)

        # 파일로 저장 (요청된 경우)
        if output:
            output_path = output.replace('.txt', f'_v{i}.txt')
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script)
            click.echo(f"\n💾 저장됨: {output_path}")


@cli.command()
@click.option('--script', required=True, help='Script text or file path')
@click.option('--format', type=click.Choice(['short', 'long']), required=True,
              help='Video format')
@click.option('--style', default='short_trendy', help='Video style preset')
@click.option('--output', default='./output/video.mp4', help='Output path')
def produce_video(script, format, style, output):
    """영상 제작"""
    producer = VideoProducer()

    # 스크립트 로드
    if os.path.isfile(script):
        with open(script, 'r', encoding='utf-8') as f:
            script_content = f.read()
    else:
        script_content = script

    script_dict = {
        'content': script_content,
        'video_format': format
    }

    click.echo("🎬 영상 제작 시작...")
    os.makedirs(os.path.dirname(output), exist_ok=True)

    video_path, thumbnail_path = producer.produce_video(
        script=script_dict,
        style_preset=style,
        output_path=output
    )

    click.echo(f"\n✅ 완료!")
    click.echo(f"영상: {video_path}")
    click.echo(f"썸네일: {thumbnail_path}")


@cli.command()
@click.option('--video', required=True, help='Video file path')
@click.option('--keywords', required=True, help='Comma-separated keywords')
@click.option('--script', help='Script file path for metadata generation')
@click.option('--ai', type=click.Choice(['claude', 'gemini', 'auto']),
              default='gemini', help='AI provider for metadata')
@click.option('--privacy', type=click.Choice(['public', 'private', 'unlisted']),
              default='public', help='Privacy status')
def upload(video, keywords, script, ai, privacy):
    """유튜브 업로드"""
    uploader = YouTubeUploader(ai_provider=ai)

    keyword_list = [k.strip() for k in keywords.split(',')]

    # 대본 로드 (있는 경우)
    script_content = ""
    if script and os.path.isfile(script):
        with open(script, 'r', encoding='utf-8') as f:
            script_content = f.read()

    click.echo("📝 메타데이터 생성 중...")
    metadata = uploader.generate_metadata(
        script={'content': script_content},
        trend_keywords=keyword_list
    )

    click.echo(f"\n제목: {metadata['title']}")
    click.echo(f"설명: {metadata['description'][:100]}...")
    click.echo(f"태그: {', '.join(metadata['tags'])}")

    if not click.confirm('\n업로드하시겠습니까?'):
        click.echo("취소됨")
        return

    # 썸네일 경로 확인
    thumbnail_path = video.replace('.mp4', '_thumb.jpg')
    if not os.path.exists(thumbnail_path):
        thumbnail_path = None

    video_id, video_url = uploader.upload_video(
        video_path=video,
        title=metadata['title'],
        description=metadata['description'],
        tags=metadata['tags'],
        privacy_status=privacy,
        thumbnail_path=thumbnail_path
    )

    click.echo(f"\n🎉 업로드 완료: {video_url}")


@cli.command()
@click.option('--region', default='US', help='YouTube region')
@click.option('--format', type=click.Choice(['short', 'long']), default='short',
              help='Video format')
@click.option('--ai', type=click.Choice(['claude', 'gemini', 'auto']),
              default='gemini', help='AI provider')
@click.option('--duration', type=int, default=60, help='Video duration in seconds')
@click.option('--no-upload', is_flag=True, help='Skip upload step')
def full_automation(region, format, ai, duration, no_upload):
    """전체 파이프라인 자동 실행"""
    click.echo("🚀 전체 자동화 시작...\n")
    click.echo(f"AI Provider: {ai}\n")

    # 1. 트렌드 분석
    click.echo("1️⃣ 트렌드 분석")
    analyzer = TrendAnalyzer(ai_provider=ai)
    videos = analyzer.fetch_trending_videos(region=region, max_results=50)
    analysis = analyzer.analyze_with_ai(videos, video_format=format)

    keywords = analysis['keywords'][:3]
    click.echo(f"키워드: {', '.join(keywords)}")

    # 2. 대본 생성
    click.echo("\n2️⃣ 대본 생성")
    generator = ScriptGenerator(ai_provider=ai)
    scripts = generator.generate_script(
        trend_keywords=keywords,
        video_format=format,
        duration_seconds=duration,
        tone='informative',
        num_versions=1
    )

    # 대본 저장
    os.makedirs('./output', exist_ok=True)
    script_path = './output/auto_script.txt'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(scripts[0])

    # 3. 영상 제작
    click.echo("\n3️⃣ 영상 제작")
    producer = VideoProducer()

    video_path, thumbnail_path = producer.produce_video(
        script={'content': scripts[0], 'video_format': format},
        style_preset='short_trendy' if format == 'short' else 'long_educational',
        output_path='./output/auto_video.mp4'
    )

    # 4. 업로드
    if not no_upload:
        click.echo("\n4️⃣ 유튜브 업로드")
        uploader = YouTubeUploader(ai_provider=ai)
        metadata = uploader.generate_metadata(
            {'content': scripts[0]},
            keywords
        )

        if click.confirm('업로드하시겠습니까?'):
            video_id, video_url = uploader.upload_video(
                video_path=video_path,
                title=metadata['title'],
                description=metadata['description'],
                tags=metadata['tags'],
                thumbnail_path=thumbnail_path
            )

            click.echo(f"\n✅ 전체 프로세스 완료!")
            click.echo(f"영상 URL: {video_url}")
        else:
            click.echo("\n✅ 영상 제작 완료 (업로드 건너뜀)")
            click.echo(f"영상: {video_path}")
    else:
        click.echo("\n✅ 영상 제작 완료 (업로드 건너뜀)")
        click.echo(f"영상: {video_path}")

    # 사용량 통계
    ai_service = get_ai_service(ai)
    click.echo("\n" + ai_service.get_usage_stats())


@cli.command()
def setup_music():
    """음악 폴더 구조 생성"""
    library = MusicLibrary()
    library.create_default_music_structure()


@cli.command()
def list_music():
    """사용 가능한 음악 목록"""
    library = MusicLibrary()
    available = library.list_available_music()

    click.echo("\n🎵 사용 가능한 음악:\n")

    for source, genres in available.items():
        click.echo(f"📁 {source}:")
        for genre, files in genres.items():
            click.echo(f"  - {genre}: {len(files)}개")
            for file in files[:3]:  # 처음 3개만 표시
                click.echo(f"    • {file}")
            if len(files) > 3:
                click.echo(f"    ... 외 {len(files) - 3}개")


if __name__ == '__main__':
    cli()
