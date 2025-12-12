"""
Image Generator - AI 이미지 생성 서비스
"""
import os
import requests
import hashlib
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

        # 이미지 캐시 디렉토리 (다운로드한 이미지 재사용)
        self.cache_dir = './cache/images'
        os.makedirs(self.cache_dir, exist_ok=True)

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
            print("[WARNING] UNSPLASH_ACCESS_KEY 환경변수가 설정되지 않았습니다")
            print("   https://unsplash.com/developers 에서 API 키 발급")
            self.enabled = False
        else:
            print("[OK] Unsplash API 활성화")

    def _init_pexels(self):
        """Pexels API 초기화"""
        if not self.pexels_api_key:
            print("[WARNING] PEXELS_API_KEY 환경변수가 설정되지 않았습니다")
            print("   https://www.pexels.com/api/ 에서 API 키 발급")
            self.enabled = False
        else:
            print("[OK] Pexels API 활성화")

    def _init_text_image(self):
        """텍스트 이미지 생성기 초기화"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            self.pil_available = True
            print("[OK] 텍스트 이미지 생성 활성화")
        except ImportError:
            print("[WARNING] Pillow가 설치되지 않았습니다. pip install pillow")
            self.enabled = False
            self.pil_available = False

    def _init_gemini(self):
        """Gemini Imagen 초기화"""
        # TODO: Gemini Imagen API 설정
        # 현재 Gemini API는 텍스트 생성만 지원
        # Imagen-3는 별도 API 필요
        print("[WARNING] Gemini Imagen은 아직 구현되지 않았습니다")
        self.enabled = False

    def _init_dalle(self):
        """DALL-E 초기화"""
        # TODO: OpenAI DALL-E API 설정
        print("[WARNING] DALL-E는 아직 구현되지 않았습니다")
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
            print(f"[WARNING] 이미지 생성 실패: {e}")
            return None

    def _create_search_query(self, text: str, style_preset: str) -> str:
        """이미지 검색 쿼리 생성 (실제 내용 기반)

        Args:
            text: 원본 텍스트
            style_preset: 스타일 프리셋

        Returns:
            str: 이미지 검색 쿼리
        """
        # 불용어 목록 (이미지 검색에 도움 안 되는 단어들)
        stopwords = {
            # 한글 불용어
            '은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로',
            '와', '과', '도', '만', '하고', '그리고', '그러나', '하지만',
            '입니다', '습니다', '있습니다', '합니다', '됩니다', '입니까', '습니까',
            # 영어 불용어
            'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then',
            'this', 'that', 'these', 'those', 'with', 'for', 'from', 'to',
            'in', 'on', 'at', 'by', 'about', 'as', 'of', 'it', 'its'
        }

        # 텍스트에서 의미있는 키워드 추출
        words = text.split()

        # 불용어 제거 및 키워드 추출
        keywords = []
        for word in words:
            # 불용어가 아니고, 2글자 이상인 단어만 선택
            if word.lower() not in stopwords and len(word) > 1:
                keywords.append(word)
                # 최대 5개 키워드만
                if len(keywords) >= 5:
                    break

        # 키워드가 없으면 원본 텍스트의 처음 3단어 사용
        if not keywords:
            keywords = words[:3]

        # 키워드만으로 검색 쿼리 생성 (스타일 키워드 제거)
        query = ' '.join(keywords).strip()

        # 쿼리가 너무 짧으면 스타일 힌트 추가 (선택적)
        if len(query) < 10 and style_preset:
            # 간단한 스타일 힌트만 추가
            style_hint = {
                'calm': 'nature peaceful',
                'energetic': 'dynamic action',
                'professional': 'business',
                'creative': 'artistic'
            }.get(style_preset, '')
            if style_hint:
                query = f"{query} {style_hint}".strip()

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

            print(f"[OK] Unsplash 이미지 다운로드: {query}")
            return output_path

        except Exception as e:
            print(f"[WARNING] Unsplash 다운로드 실패: {e}")
            return None

    def _fetch_from_pexels(
        self,
        query: str,
        output_path: str,
        width: int,
        height: int
    ) -> Optional[str]:
        """Pexels에서 이미지 다운로드 (캐싱 지원)"""
        try:
            # 캐시 확인 (query 해시로 캐시 파일명 생성)
            query_hash = hashlib.md5(query.encode()).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"{query_hash}.jpg")

            # 캐시에 이미 있으면 복사해서 사용
            if os.path.exists(cache_path):
                import shutil
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shutil.copy(cache_path, output_path)
                print(f"[CACHE] Pexels 이미지 캐시 사용: {query}")
                return output_path

            # 캐시에 없으면 API로 다운로드
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
                print(f"[WARNING] Pexels에서 '{query}' 이미지를 찾을 수 없습니다")
                return None

            image_url = data['photos'][0]['src']['large']

            # 이미지 다운로드
            img_response = requests.get(image_url, timeout=10)
            img_response.raise_for_status()

            # output_path와 캐시 둘 다 저장
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            with open(cache_path, 'wb') as f:
                f.write(img_response.content)

            print(f"[OK] Pexels 이미지 다운로드 및 캐시 저장: {query}")
            return output_path

        except Exception as e:
            print(f"[WARNING] Pexels 다운로드 실패: {e}")
            return None

    def _generate_text_image(
        self,
        text: str,
        output_path: str,
        width: int,
        height: int
    ) -> Optional[str]:
        """텍스트 기반 이미지 생성 (Pillow 사용 - 그라데이션 배경)"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import random
            import numpy as np

            # 그라데이션 배경 색상 조합
            gradient_colors = [
                ((20, 30, 70), (60, 90, 180)),    # 파란색 그라데이션
                ((70, 20, 50), (180, 60, 130)),   # 핑크/자주 그라데이션
                ((20, 60, 50), (60, 160, 130)),   # 청록색 그라데이션
                ((60, 40, 20), (180, 120, 60)),   # 주황색 그라데이션
                ((30, 20, 60), (90, 60, 150)),    # 보라색 그라데이션
            ]
            color1, color2 = random.choice(gradient_colors)

            # 그라데이션 이미지 생성 (세로 방향)
            image = Image.new('RGB', (width, height))
            pixels = image.load()

            for y in range(height):
                # 세로 방향 그라데이션 (위에서 아래로)
                ratio = y / height
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)

                for x in range(width):
                    pixels[x, y] = (r, g, b)

            draw = ImageDraw.Draw(image)

            # 텍스트에서 키워드 추출 (처음 3-5단어)
            words = text.split()[:5]
            keywords = ' '.join(words) if words else text[:30]

            # 폰트 로드 (Windows 맑은 고딕 또는 Arial)
            try:
                # 한글 폰트 시도
                font_large = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 80)
                font_small = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 50)
            except:
                try:
                    font_large = ImageFont.truetype("arial.ttf", 80)
                    font_small = ImageFont.truetype("arial.ttf", 50)
                except:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()

            # 키워드를 큰 글씨로 중앙에
            bbox = draw.textbbox((0, 0), keywords, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 화면 너비를 초과하면 작은 폰트 사용
            if text_width > width * 0.9:
                bbox = draw.textbbox((0, 0), keywords, font=font_small)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                use_font = font_small
            else:
                use_font = font_large

            position = ((width - text_width) // 2, (height - text_height) // 2)

            # 텍스트 그림자 효과
            shadow_offset = 4
            draw.text((position[0] + shadow_offset, position[1] + shadow_offset),
                     keywords, fill=(0, 0, 0, 128), font=use_font)

            # 메인 텍스트
            draw.text(position, keywords, fill=(255, 255, 255), font=use_font)

            # 저장
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path, quality=95)

            print(f"[OK] 텍스트 이미지 생성: {keywords}")
            return output_path

        except Exception as e:
            print(f"[WARNING] 텍스트 이미지 생성 실패: {e}")
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
