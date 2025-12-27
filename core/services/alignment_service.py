"""
Alignment Service (SHORTS_SPEC.md 기준)
Whisper를 사용하여 오디오에서 정확한 단어별 타임스탬프 추출
"""
from typing import List, Dict, Optional
from pathlib import Path
import sys

# config 불러오기
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.config import WHISPER_MODEL, WHISPER_WORD_TIMESTAMPS, WHISPER_LANGUAGE


class AlignmentService:
    """
    TTS 오디오를 Whisper로 분석하여 정확한 타임스탬프 추출

    SHORTS_SPEC.md 요구사항:
    - word_timestamps=True로 단어별 {word, start, end} 추출
    - 추출된 타임스탬프로 자막 싱크 정확도 향상
    """

    def __init__(self, model_size: str = WHISPER_MODEL):
        """
        Args:
            model_size: Whisper 모델 크기 (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None

    def _load_model(self):
        """Whisper 모델 로드 (lazy loading)"""
        if self.model is None:
            try:
                import whisper
                print(f"[Whisper] 모델 로드 중: {self.model_size}")
                self.model = whisper.load_model(self.model_size)
                print(f"[Whisper] 모델 로드 완료")
            except ImportError:
                print("[ERROR] openai-whisper 패키지가 설치되지 않았습니다.")
                print("[INFO] 설치: pip install openai-whisper")
                raise ImportError("openai-whisper is required")

    def extract_word_timestamps(
        self,
        audio_path: str,
        language: str = WHISPER_LANGUAGE
    ) -> List[Dict[str, any]]:
        """
        오디오 파일에서 단어별 타임스탬프 추출

        Args:
            audio_path: TTS 오디오 파일 경로
            language: 언어 코드 (ko, en, etc.)

        Returns:
            단어별 타임스탬프 리스트
            [
                {"word": "안녕하세요", "start": 0.0, "end": 0.8},
                {"word": "반갑습니다", "start": 0.9, "end": 1.5},
                ...
            ]
        """
        self._load_model()

        try:
            print(f"[Whisper] 타임스탬프 추출 중: {audio_path}")

            # Whisper 실행 (word_timestamps=True)
            result = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=WHISPER_WORD_TIMESTAMPS,
                verbose=False
            )

            # 단어별 타임스탬프 추출
            word_timestamps = []

            for segment in result.get('segments', []):
                # segment에 words가 있으면 word-level 타임스탬프 사용
                if 'words' in segment:
                    for word_info in segment['words']:
                        word_timestamps.append({
                            "word": word_info['word'].strip(),
                            "start": word_info['start'],
                            "end": word_info['end']
                        })
                else:
                    # words가 없으면 segment-level 사용 (fallback)
                    word_timestamps.append({
                        "word": segment['text'].strip(),
                        "start": segment['start'],
                        "end": segment['end']
                    })

            print(f"[Whisper] 추출 완료: {len(word_timestamps)}개 단어")

            return word_timestamps

        except Exception as e:
            print(f"[ERROR] Whisper 타임스탬프 추출 실패: {e}")
            import traceback
            traceback.print_exc()
            return []

    def align_segments_to_audio(
        self,
        segments: List[Dict[str, str]],
        audio_path: str
    ) -> List[Dict[str, any]]:
        """
        스크립트 세그먼트와 오디오를 정렬 (SHORTS_SPEC.md 요구사항)

        Args:
            segments: ContentPlan의 세그먼트 리스트
                [{"text": "안녕하세요", ...}, {"text": "반갑습니다", ...}]
            audio_path: TTS 오디오 파일 경로

        Returns:
            정렬된 세그먼트 (duration이 실제 TTS 길이로 업데이트됨)
            [
                {"text": "안녕하세요", "start": 0.0, "end": 0.8, "duration": 0.8},
                {"text": "반갑습니다", "start": 0.9, "end": 1.5, "duration": 0.6},
                ...
            ]
        """
        # Whisper로 단어별 타임스탬프 추출
        word_timestamps = self.extract_word_timestamps(audio_path)

        if not word_timestamps:
            print("[WARNING] Whisper 타임스탬프 추출 실패. 예측값 사용")
            return segments

        # 세그먼트와 타임스탬프 정렬
        aligned_segments = []
        word_index = 0

        for i, segment in enumerate(segments):
            # 효과음 제거
            import re
            text = re.sub(r'\([^)]*\)', '', segment.get('text', '')).strip()

            if not text:
                continue

            # 세그먼트 시작 시간 = 현재 word_index의 start
            if word_index < len(word_timestamps):
                start_time = word_timestamps[word_index]['start']

                # 세그먼트의 단어 수만큼 word_index 이동
                segment_words = text.split()
                word_count = len(segment_words)

                # 종료 시간 계산
                end_index = min(word_index + word_count, len(word_timestamps))
                if end_index > word_index:
                    end_time = word_timestamps[end_index - 1]['end']
                else:
                    end_time = start_time + 1.0  # fallback

                duration = end_time - start_time

                aligned_segments.append({
                    "text": segment.get('text', ''),
                    "keyword": segment.get('keyword', ''),
                    "start": start_time,
                    "end": end_time,
                    "duration": duration
                })

                word_index = end_index
            else:
                # 타임스탬프가 부족하면 마지막 시간 + 1초
                if aligned_segments:
                    last_end = aligned_segments[-1]['end']
                    aligned_segments.append({
                        "text": segment.get('text', ''),
                        "keyword": segment.get('keyword', ''),
                        "start": last_end,
                        "end": last_end + 1.0,
                        "duration": 1.0
                    })

        print(f"[Whisper] 정렬 완료: {len(aligned_segments)}개 세그먼트")

        return aligned_segments


# 싱글톤 인스턴스
_alignment_service = None


def get_alignment_service() -> AlignmentService:
    """AlignmentService 싱글톤 인스턴스 반환"""
    global _alignment_service
    if _alignment_service is None:
        _alignment_service = AlignmentService()
    return _alignment_service
