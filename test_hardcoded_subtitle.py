"""
하드코딩 자막 처리 테스트
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from local_cli.services.hardcoded_subtitle_processor import HardcodedSubtitleProcessor
from local_cli.services.subtitle_translator import SubtitleTranslator


def test_hardcoded_subtitle_processing():
    """하드코딩 자막 처리 전체 테스트"""

    # 테스트할 영상 경로 입력
    video_path = input("영상 파일 경로를 입력하세요: ").strip('"')

    if not os.path.exists(video_path):
        print(f"[ERROR] 파일을 찾을 수 없습니다: {video_path}")
        return

    # 출력 디렉토리
    output_dir = './hardcoded_output'
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "="*70)
    print("하드코딩 자막 처리 테스트 시작")
    print("="*70)

    try:
        # 프로세서 초기화
        print("\n[INFO] 하드코딩 자막 프로세서 초기화 중...")
        processor = HardcodedSubtitleProcessor()

        print("[INFO] 번역기 초기화 중...")
        translator = SubtitleTranslator()

        # 전체 처리
        result = processor.process_video_with_hardcoded_subs(
            video_path=video_path,
            output_dir=output_dir,
            translator=translator,
            target_lang='ko'
        )

        if result['success']:
            print("\n" + "="*70)
            print("처리 완료!")
            print("="*70)
            print(f"추출된 자막: {result['extracted_srt']}")
            print(f"번역된 자막: {result['translated_srt']}")
            print(f"자막 제거 영상: {result['cleaned_video']}")
            print(f"최종 영상: {result['final_video']}")
            print(f"자막 개수: {result['subtitle_count']}")
        else:
            print(f"\n[ERROR] 처리 실패: {result.get('error')}")

    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_hardcoded_subtitle_processing()
