"""
Planner Module
AI 기반 콘텐츠 기획 및 스크립트 생성
"""
import os
import re
from typing import Optional, List, Dict, Any
from pathlib import Path

from core.models import (
    ContentPlan,
    ScriptSegment,
    VideoFormat,
    AIProvider
)
from providers.ai import GeminiProvider


class ContentPlanner:
    """AI 기반 콘텐츠 기획자"""

    def __init__(
        self,
        ai_provider: str = "gemini",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        ContentPlanner 초기화

        Args:
            ai_provider: AI 제공자 ("gemini", "claude", "openai")
            api_key: API 키 (None이면 환경변수에서 가져옴)
            model: 사용할 모델 (None이면 기본값)
        """
        self.ai_provider = ai_provider.lower()

        # AI Provider 초기화
        if self.ai_provider == "gemini":
            self.ai = GeminiProvider(api_key=api_key, model=model)
        else:
            raise NotImplementedError(f"{ai_provider} 제공자는 아직 구현되지 않았습니다")

        # 프로젝트 루트 경로
        self.project_root = Path(__file__).parent.parent
        self.templates_dir = self.project_root / "templates"

    def generate_topic_ideas(
        self,
        category: str,
        count: int = 5,
        tone: str = "친근하고 활기찬"
    ) -> List[str]:
        """
        주제 아이디어 생성

        Args:
            category: 카테고리 (예: "반려동물", "IT", "요리")
            count: 생성할 주제 개수
            tone: 톤앤매너

        Returns:
            주제 아이디어 리스트
        """
        prompt = f"""
        YouTube 쇼츠 콘텐츠 주제를 {count}개 생성해주세요.

        **카테고리**: {category}
        **톤**: {tone}
        **요구사항**:
        - 시청자의 관심을 끌 수 있는 주제
        - 60초 이내로 전달 가능한 내용
        - 트렌디하고 검색이 잘 되는 주제

        **출력 형식** (JSON):
        {{
          "topics": [
            "주제 1",
            "주제 2",
            "주제 3"
          ]
        }}
        """

        try:
            result = self.ai.generate_json(prompt, temperature=0.8)
            return result.get("topics", [])
        except Exception as e:
            print(f"[ERROR] 주제 생성 실패: {e}")
            return []

    def create_script(
        self,
        topic: str,
        format: VideoFormat = VideoFormat.SHORTS,
        category: str = "22",
        target_duration: int = 60,
        tone: str = "친근하고 활기찬",
        additional_requirements: str = ""
    ) -> Optional[ContentPlan]:
        """
        AI 스크립트 생성

        Args:
            topic: 영상 주제
            format: 영상 포맷 (shorts, landscape, square)
            category: YouTube 카테고리 ID
            target_duration: 목표 길이 (초)
            tone: 톤앤매너
            additional_requirements: 추가 요구사항

        Returns:
            ContentPlan 객체 또는 None (실패 시)
        """
        # 프롬프트 템플릿 로드
        template = self._load_template(format)
        if not template:
            print(f"[ERROR] {format} 템플릿을 찾을 수 없습니다")
            return None

        # 변수 치환
        prompt = template.format(
            topic=topic,
            category=category,
            tone=tone,
            target_duration=target_duration,
            additional_requirements=additional_requirements or "없음"
        )

        # AI로 스크립트 생성
        try:
            print(f"[AI] 스크립트 생성 중... (주제: {topic})")
            result = self.ai.generate_json(
                prompt=prompt,
                temperature=0.7,
                max_tokens=8000
            )

            # ContentPlan 객체 생성
            content_plan = ContentPlan(
                title=result.get("title", ""),
                description=result.get("description", ""),
                tags=result.get("tags", []),
                category=result.get("category", category),
                format=VideoFormat(result.get("format", format)),
                target_duration=result.get("target_duration", target_duration),
                segments=[
                    ScriptSegment(**segment)
                    for segment in result.get("segments", [])
                ],
                ai_provider=AIProvider(self.ai_provider)
            )

            # Phase 2: 시간 제약 검증 및 조정
            content_plan = self._validate_and_adjust_duration(content_plan)

            print(f"[SUCCESS] 스크립트 생성 완료: {content_plan.title}")
            print(f"[INFO] 세그먼트 수: {len(content_plan.segments)}")

            return content_plan

        except Exception as e:
            print(f"[ERROR] 스크립트 생성 실패: {e}")
            return None

    def optimize_metadata(
        self,
        script: str,
        format: VideoFormat = VideoFormat.SHORTS,
        category: str = "22"
    ) -> Dict[str, Any]:
        """
        메타데이터 최적화 (제목, 설명, 태그)

        Args:
            script: 원본 스크립트
            format: 영상 포맷
            category: YouTube 카테고리 ID

        Returns:
            최적화된 메타데이터 딕셔너리
        """
        # 메타데이터 프롬프트 템플릿 로드
        template_path = self.templates_dir / "metadata_prompts" / "title_description.txt"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            print(f"[ERROR] 메타데이터 템플릿을 찾을 수 없습니다: {template_path}")
            return {}

        # 변수 치환
        prompt = template.format(
            script=script,
            format=format.value,
            category=category
        )

        # AI로 메타데이터 생성
        try:
            result = self.ai.generate_json(prompt, temperature=0.6)
            return result
        except Exception as e:
            print(f"[ERROR] 메타데이터 생성 실패: {e}")
            return {}

    def extract_keywords(self, content_plan: ContentPlan) -> List[str]:
        """
        스크립트에서 키워드 추출

        Args:
            content_plan: ContentPlan 객체

        Returns:
            키워드 리스트
        """
        keywords = []

        # 각 세그먼트에서 키워드 추출
        for segment in content_plan.segments:
            if segment.keyword:
                keywords.append(segment.keyword)

        # 태그도 키워드로 추가
        keywords.extend(content_plan.tags)

        # 중복 제거
        unique_keywords = list(set(keywords))

        return unique_keywords

    def _load_template(self, format: VideoFormat) -> Optional[str]:
        """
        프롬프트 템플릿 로드

        Args:
            format: 영상 포맷

        Returns:
            템플릿 문자열 또는 None
        """
        # 템플릿 파일 경로
        if format == VideoFormat.SHORTS:
            template_file = "shorts_script.txt"
        elif format == VideoFormat.LANDSCAPE:
            template_file = "landscape_script.txt"
        else:
            template_file = "shorts_script.txt"  # 기본값

        template_path = self.templates_dir / "script_prompts" / template_file

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"[ERROR] 템플릿 파일을 찾을 수 없습니다: {template_path}")
            return None

    def _validate_and_adjust_duration(self, content_plan: ContentPlan) -> ContentPlan:
        """
        세그먼트 시간 검증 및 조정 (Phase 2)

        Args:
            content_plan: 검증할 ContentPlan

        Returns:
            조정된 ContentPlan
        """
        target_duration = content_plan.target_duration
        segments = content_plan.segments

        # 1. 각 세그먼트에 duration이 없으면 자동 계산
        for segment in segments:
            if segment.duration is None or segment.duration == 0:
                # TTS 읽기 속도 기준: 평균 3글자/초 (한국어)
                estimated_duration = len(segment.text) / 3.0
                segment.duration = round(estimated_duration, 1)

        # 2. 총 시간 계산
        total_duration = sum(seg.duration for seg in segments if seg.duration)

        print(f"[Planner] 총 세그먼트 시간: {total_duration:.1f}초 / 목표: {target_duration}초")

        # 3. 목표 시간과 차이가 5초 이상이면 조정
        duration_diff = abs(total_duration - target_duration)

        if duration_diff > 5.0:
            print(f"[Planner] 시간 차이 {duration_diff:.1f}초 감지. 세그먼트 조정 중...")

            # 비율 조정 (proportional scaling)
            scale_factor = target_duration / total_duration if total_duration > 0 else 1.0

            for segment in segments:
                if segment.duration:
                    segment.duration = round(segment.duration * scale_factor, 1)

            # 재계산
            total_duration = sum(seg.duration for seg in segments if seg.duration)
            print(f"[Planner] 조정 후 총 시간: {total_duration:.1f}초")

        # 4. 미세 조정 (±2초 이내로 맞추기)
        final_diff = target_duration - total_duration

        if abs(final_diff) > 0.5 and segments:
            # 마지막 세그먼트에 차이 추가/제거
            last_segment = segments[-1]
            if last_segment.duration:
                last_segment.duration = max(0.5, last_segment.duration + final_diff)
                print(f"[Planner] 마지막 세그먼트 미세 조정: {last_segment.duration:.1f}초")

        return content_plan

    def save_plan(self, content_plan: ContentPlan, output_dir: str = "./output/plans"):
        """
        ContentPlan을 JSON 파일로 저장

        Args:
            content_plan: ContentPlan 객체
            output_dir: 출력 디렉토리
        """
        import json
        from datetime import datetime

        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)

        # 파일명 생성 (타임스탬프 기반)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plan_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        # JSON 저장
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content_plan.model_dump(), f, ensure_ascii=False, indent=2)
            print(f"[SUCCESS] 기획안 저장 완료: {filepath}")
            return filepath
        except Exception as e:
            print(f"[ERROR] 기획안 저장 실패: {e}")
            return None

    def get_usage_stats(self) -> Dict[str, Any]:
        """AI 사용량 통계 반환"""
        return self.ai.get_usage_stats()
