"""
Image Generator - AI 이미지 생성 서비스
"""
import os
import requests
from typing import Dict, List, Optional
from pathlib import Path


class ImageGenerator:
    """AI를 사용한 이미지 생성 서비스

    현재 지원:
    - Unsplash API (무료 이미지 검색)
    - Pexels API (무료 이미지 검색)
    - Text Image (Pillow로 텍스트 이미지 생성)
    - Gemini Imagen (향후 지원 예정)
    - DALL-E (향후 지원 예정)
    """

    def __init__(self, provider: str = 'none'):
        """ImageGenerator 초기화

        Args:
            provider: 이미지 생성 제공자
                     ('unsplash', 'pexels', 'text', 'gemini', 'dalle', 'none')
        """
        self.provider = provider
        self.enabled = provider != 'none'

        # API 키 가져오기
        self.unsplash_api_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.pexels_api_key = os.getenv('PEXELS_API_KEY')

        if provider == 'unsplash':
            self._init_unsplash()
        elif provider == 'pexels':
            self._init_pexels()
        elif provider == 'text':
            self._init_text_image()
        elif provider == 'gemini':
            self._init_gemini()
        elif provider == 'dalle':
            self._init_dalle()

    def _init_unsplash(self):
        """Unsplash API 초기화"""
        if not self.unsplash_api_key:
            print("⚠️ UNSPLASH_ACCESS_KEY 환경변수가 설정되지 않았습니다")
            print("   https://unsplash.com/developers 에서 API 키 발급")
            self.enabled = False
        else:
            print("✅ Unsplash API 활성화")

    def _init_pexels(self):
        """Pexels API 초기화"""
        if not self.pexels_api_key:
            print("⚠️ PEXELS_API_KEY 환경변수가 설정되지 않았습니다")
            print("   https://www.pexels.com/api/ 에서 API 키 발급")
            self.enabled = False
        else:
            print("✅ Pexels API 활성화")

    def _init_text_image(self):
        """텍스트 이미지 생성기 초기화"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            self.pil_available = True
            print("✅ 텍스트 이미지 생성 활성화")
        except ImportError:
            print("⚠️ Pillow가 설치되지 않았습니다. pip install pillow")
            self.enabled = False
            self.pil_available = False

    def _init_gemini(self):
        """Gemini Imagen 초기화"""
        # TODO: Gemini Imagen API 설정
        # 현재 Gemini API는 텍스트 생성만 지원
        # Imagen-3는 별도 API 필요
        print("⚠️ Gemini Imagen은 아직 구현되지 않았습니다")
        self.enabled = False

    def _init_dalle(self):
        """DALL-E 초기화"""
        # TODO: OpenAI DALL-E API 설정
        print("⚠️ DALL-E는 아직 구현되지 않았습니다")
        self.enabled = False

    def generate_image_for_segment(
        self,
        text: str,
        style_preset: str,
        output_path: str,
        width: int = 1920,
        height: int = 1080
    ) -> Optional[str]:
        """세그먼트 텍스트에 맞는 이미지 생성

        Args:
            text: 세그먼트 텍스트 (이미지 생성 프롬프트로 사용)
            style_preset: 스타일 프리셋
            output_path: 출력 이미지 경로
            width: 이미지 너비
            height: 이미지 높이

        Returns:
            Optional[str]: 생성된 이미지 경로, 실패 시 None
        """
        if not self.enabled:
            return None

        try:
            # 프롬프트 생성
            query = self._create_search_query(text, style_preset)

            if self.provider == 'unsplash':
                return self._fetch_from_unsplash(query, output_path, width, height)
            elif self.provider == 'pexels':
                return self._fetch_from_pexels(query, output_path, width, height)
            elif self.provider == 'text':
                return self._generate_text_image(text, output_path, width, height)
            elif self.provider == 'gemini':
                return self._generate_with_gemini(query, output_path, width, height)
            elif self.provider == 'dalle':
                return self._generate_with_dalle(query, output_path, width, height)

        except Exception as e:
            print(f"⚠️ 이미지 생성 실패: {e}")
            return None

    def _create_search_query(self, text: str, style_preset: str) -> str:
        """이미지 검색 쿼리 생성

        Args:
            text: 원본 텍스트
            style_preset: 스타일 프리셋

        Returns:
            str: 이미지 검색 쿼리
        """
        # 스타일별 키워드
        style_keywords = {
            'calm': 'peaceful calm serene',
            'energetic': 'dynamic vibrant energetic',
            'professional': 'professional business modern',
            'creative': 'creative artistic colorful',
        }

        keyword = style_keywords.get(style_preset, 'abstract background')

        # 텍스트에서 키워드 추출 (간단하게 처음 3단어)
        words = text.split()[:3]
        text_keywords = ' '.join(words) if words else ''

        query = f"{keyword} {text_keywords}".strip()
        return query[:100]  # API 제한을 위해 100자로 제한

    def _fetch_from_unsplash(
        self,
        query: str,
        output_path: str,
        width: int,
        height: int
    ) -> Optional[str]:
        """Unsplash에서 이미지 다운로드"""
        try:
            url = "https://api.unsplash.com/photos/random"
            headers = {"Authorization": f"Client-ID {self.unsplash_api_key}"}
            params = {
                "query": query,
                "orientation": "landscape" if width > height else "portrait"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            image_url = data['urls']['regular']

            # 이미지 다운로드
            img_response = requests.get(image_url, timeout=10)
            img_response.raise_for_status()

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(img_response.content)

            print(f"✅ Unsplash 이미지 다운로드: {query}")
            return output_path

        except Exception as e:
            print(f"⚠️ Unsplash 다운로드 실패: {e}")
            return None

    def _fetch_from_pexels(
        self,
        query: str,
        output_path: str,
        width: int,
        height: int
    ) -> Optional[str]:
        """Pexels에서 이미지 다운로드"""
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_api_key}
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "landscape" if width > height else "portrait"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if not data.get('photos'):
                print(f"⚠️ Pexels에서 '{query}' 이미지를 찾을 수 없습니다")
                return None

            image_url = data['photos'][0]['src']['large']

            # 이미지 다운로드
            img_response = requests.get(image_url, timeout=10)
            img_response.raise_for_status()

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(img_response.content)

            print(f"✅ Pexels 이미지 다운로드: {query}")
            return output_path

        except Exception as e:
            print(f"⚠️ Pexels 다운로드 실패: {e}")
            return None

    def _generate_text_image(
        self,
        text: str,
        output_path: str,
        width: int,
        height: int
    ) -> Optional[str]:
        """텍스트 기반 이미지 생성 (Pillow 사용)"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import random

            # 배경 색상 (그라데이션 효과)
            colors = [
                (30, 30, 60),    # 진한 파란색
                (60, 30, 30),    # 진한 빨간색
                (30, 60, 30),    # 진한 초록색
                (60, 60, 30),    # 노란색
                (60, 30, 60),    # 보라색
            ]
            bg_color = random.choice(colors)

            # 이미지 생성
            image = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(image)

            # 텍스트 (처음 50자)
            text_display = text[:50] + ('...' if len(text) > 50 else '')

            # 폰트 (기본 폰트 사용)
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()

            # 텍스트 위치 (중앙)
            bbox = draw.textbbox((0, 0), text_display, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((width - text_width) // 2, (height - text_height) // 2)

            # 텍스트 그리기
            draw.text(position, text_display, fill=(255, 255, 255), font=font)

            # 저장
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)

            print(f"✅ 텍스트 이미지 생성: {text[:30]}...")
            return output_path

        except Exception as e:
            print(f"⚠️ 텍스트 이미지 생성 실패: {e}")
            return None

    def _generate_with_gemini(
        self,
        prompt: str,
        output_path: str,
        width: int,
        height: int
    ) -> Optional[str]:
        """Gemini Imagen으로 이미지 생성

        TODO: Gemini Imagen API 구현
        """
        # Placeholder - 실제 구현 필요
        print(f"🎨 Gemini로 이미지 생성: {prompt[:50]}...")
        return None

    def _generate_with_dalle(
        self,
        prompt: str,
        output_path: str,
        width: int,
        height: int
    ) -> Optional[str]:
        """DALL-E로 이미지 생성

        TODO: OpenAI DALL-E API 구현
        """
        # Placeholder - 실제 구현 필요
        print(f"🎨 DALL-E로 이미지 생성: {prompt[:50]}...")
        return None

    def generate_images_for_script(
        self,
        voice_segments: List[Dict],
        style_preset: str,
        output_dir: str
    ) -> List[Optional[str]]:
        """스크립트 전체에 대한 이미지 생성

        Args:
            voice_segments: TTS 세그먼트 리스트
            style_preset: 스타일 프리셋
            output_dir: 출력 디렉토리

        Returns:
            List[Optional[str]]: 생성된 이미지 경로 리스트
        """
        if not self.enabled:
            return [None] * len(voice_segments)

        os.makedirs(output_dir, exist_ok=True)

        images = []
        for i, segment in enumerate(voice_segments):
            output_path = os.path.join(output_dir, f'image_{i}.png')
            image_path = self.generate_image_for_segment(
                segment['text'],
                style_preset,
                output_path
            )
            images.append(image_path)

        return images
