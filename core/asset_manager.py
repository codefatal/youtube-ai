"""
Asset Manager Module
스톡 영상, TTS 음성 등 에셋 수집 및 관리
"""
import os
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any

from backend.database import SessionLocal  # Phase 3
from backend.models import AccountSettings  # Phase 3

from core.models import (
    ContentPlan,
    StockVideoAsset,
    AudioAsset,
    AssetBundle,
    BGMAsset,
    TTSProvider,
    MoodType
)
from providers.stock import PexelsProvider, PixabayProvider
from core.bgm_manager import BGMManager


class AssetManager:
    """에셋 수집 및 관리 모듈"""

    def __init__(
        self,
        stock_providers: List[str] = None,
        tts_provider: str = "gtts",
        cache_enabled: bool = True,
        download_dir: str = "./downloads",
        bgm_enabled: bool = False
    ):
        """
        AssetManager 초기화

        Args:
            stock_providers: 사용할 스톡 영상 제공자 리스트 (기본: pexels, pixabay)
            tts_provider: TTS 제공자 (gtts, elevenlabs, google_cloud)
            cache_enabled: 캐시 사용 여부
            download_dir: 다운로드 디렉토리
            bgm_enabled: BGM 사용 여부 (Phase 2)
        """
        self.stock_providers = stock_providers or ['pexels', 'pixabay']
        self.tts_provider = tts_provider
        self.cache_enabled = cache_enabled
        self.download_dir = Path(download_dir)
        self.bgm_enabled = bgm_enabled

        # 디렉토리 생성
        self.video_dir = self.download_dir / "stock_videos"
        self.audio_dir = self.download_dir / "audio"
        self.cache_dir = self.download_dir / "cache"

        for dir_path in [self.video_dir, self.audio_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 스톡 영상 제공자 초기화
        self.providers = {}
        self._init_providers()

        # Phase 2: BGM 매니저 초기화
        self.bgm_manager = BGMManager() if bgm_enabled else None
        if self.bgm_enabled:
            print(f"[AssetManager] BGM 매니저 초기화 완료")

    def _init_providers(self):
        """스톡 영상 제공자 초기화"""
        for provider_name in self.stock_providers:
            try:
                if provider_name == 'pexels':
                    self.providers['pexels'] = PexelsProvider()
                elif provider_name == 'pixabay':
                    self.providers['pixabay'] = PixabayProvider()
                print(f"[AssetManager] {provider_name} 초기화 완료")
            except ValueError as e:
                print(f"[WARNING] {provider_name} 초기화 실패: {e}")

    def collect_assets(
        self,
        content_plan: ContentPlan,
        download_videos: bool = True,
        generate_tts: bool = True,
        select_bgm: bool = True,
        account_id: Optional[int] = None, # ✨ NEW
        tts_settings_override: Optional[Dict[str, Any]] = None # ✨ NEW
    ) -> Optional[AssetBundle]:
        """
        ContentPlan을 기반으로 모든 에셋 수집

        Args:
            content_plan: ContentPlan 객체
            download_videos: 영상 다운로드 여부
            generate_tts: TTS 생성 여부
            select_bgm: BGM 선택 여부
            account_id: 계정 ID (DB 설정 조회용)
            tts_settings_override: TTS 설정 오버라이드 (프론트엔드 직접 설정용)

        Returns:
            AssetBundle 객체 또는 None
        """
        print(f"\n[AssetManager] 에셋 수집 시작: {content_plan.title}")

        # 1. 스톡 영상 수집
        video_assets = []
        if download_videos:
            video_assets = self._collect_stock_videos(content_plan)

        # 2. TTS 음성 생성
        audio_asset = None
        if generate_tts:
            audio_asset = self._generate_tts(content_plan, account_id, tts_settings_override)

        # 3. Phase 2: BGM 선택
        bgm_asset = None
        if select_bgm and self.bgm_enabled and self.bgm_manager:
            bgm_asset = self._select_bgm(content_plan)

        # 4. AssetBundle 생성
        bundle = AssetBundle(
            videos=video_assets,
            audio=audio_asset,
            bgm=bgm_asset
        )

        bgm_msg = f", BGM {1 if bgm_asset else 0}개" if self.bgm_enabled else ""
        print(f"[SUCCESS] 에셋 수집 완료: 영상 {len(video_assets)}개, 음성 {1 if audio_asset else 0}개{bgm_msg}")
        return bundle

    def _collect_stock_videos(self, content_plan: ContentPlan) -> List[StockVideoAsset]:
        """
        스크립트 세그먼트별로 스톡 영상 검색 및 다운로드

        Args:
            content_plan: ContentPlan 객체

        Returns:
            StockVideoAsset 리스트
        """
        all_assets = []

        for i, segment in enumerate(content_plan.segments, 1):
            keyword = segment.keyword
            print(f"\n[{i}/{len(content_plan.segments)}] 키워드: '{keyword}' 검색 중...")

            # 캐시 확인
            cached_asset = self._get_cached_video(keyword)
            if cached_asset:
                print(f"[Cache] 캐시에서 영상 가져옴: {cached_asset.id}")
                all_assets.append(cached_asset)
                continue

            # 여러 제공자에서 검색
            assets = self._search_from_providers(keyword)

            if assets:
                # 첫 번째 영상 다운로드
                asset = assets[0]
                filepath = self._download_video(asset)

                if filepath:
                    asset.local_path = filepath
                    asset.downloaded = True
                    all_assets.append(asset)

                    # 캐시 저장
                    self._cache_video(keyword, asset)
                else:
                    print(f"[WARNING] '{keyword}' 다운로드 실패")
            else:
                print(f"[WARNING] '{keyword}' 검색 결과 없음")

        return all_assets

    def _search_from_providers(self, keyword: str, per_page: int = 3) -> List[StockVideoAsset]:
        """
        여러 제공자에서 영상 검색

        Args:
            keyword: 검색 키워드
            per_page: 제공자당 결과 개수

        Returns:
            StockVideoAsset 리스트
        """
        all_assets = []

        for provider_name, provider in self.providers.items():
            try:
                assets = provider.search_videos(keyword, per_page=per_page)
                all_assets.extend(assets)
            except Exception as e:
                print(f"[ERROR] {provider_name} 검색 실패: {e}")

        return all_assets

    def _download_video(self, asset: StockVideoAsset) -> Optional[str]:
        """
        영상 다운로드

        Args:
            asset: StockVideoAsset 객체

        Returns:
            저장된 파일 경로 또는 None
        """
        provider_name = asset.provider
        provider = self.providers.get(provider_name)

        if not provider:
            print(f"[ERROR] 제공자를 찾을 수 없음: {provider_name}")
            return None

        return provider.download_video(asset, output_dir=str(self.video_dir))

    def _generate_tts(self, content_plan: ContentPlan, account_id: Optional[int] = None, tts_settings_override: Optional[Dict[str, Any]] = None) -> Optional[AudioAsset]:
        """
        TTS 음성 생성 (AccountSettings 및 오버라이드 지원)

        Args:
            content_plan: ContentPlan 객체
            account_id: 계정 ID (DB 설정 조회용)
            tts_settings_override: TTS 설정 오버라이드 (프론트엔드 직접 설정용)

        Returns:
            AudioAsset 객체 또는 None
        """
        full_text = " ".join([seg.text for seg in content_plan.segments])

        # 1. DB에서 계정 설정 가져오기
        if account_id:
            settings = self._get_account_tts_settings(account_id)
        else:
            settings = {
                "provider": self.tts_provider,
                "voice_id": "pNInz6obpgDQGcFmaJgB",
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0
            }

        # 2. ✨ 프론트엔드 오버라이드 설정 적용
        if tts_settings_override:
            # provider는 tts_provider로 키 이름이 다름
            if 'provider' in tts_settings_override:
                settings['tts_provider'] = tts_settings_override.pop('provider')
            
            # voiceId는 tts_voice_id로 키 이름이 다름
            if 'voiceId' in tts_settings_override:
                settings['tts_voice_id'] = tts_settings_override.pop('voiceId')
            
            settings.update(tts_settings_override)
            print(f"[AssetManager] TTS 설정을 오버라이드합니다: {settings}")

        # 3. TTS 생성 (설정 반영)
        provider = settings.get("tts_provider", "gtts")
        if provider == "elevenlabs":
            filepath = self._generate_elevenlabs(
                text=full_text,
                voice_id=settings.get("tts_voice_id"),
                stability=settings.get("tts_stability"),
                similarity_boost=settings.get("tts_similarity_boost"),
                style=settings.get("tts_style")
            )
        else:
            filepath = self._generate_gtts(full_text)

        if filepath:
            return AudioAsset(
                text=full_text,
                provider=TTSProvider(provider),
                local_path=filepath
            )

        return None

    def _get_account_tts_settings(self, account_id: int) -> dict:
        """
        AccountSettings에서 TTS 설정 가져오기
        """
        db = SessionLocal()
        try:
            settings = db.query(AccountSettings).filter(
                AccountSettings.account_id == account_id
            ).first()

            if settings:
                return {
                    "tts_provider": settings.tts_provider,
                    "tts_voice_id": settings.tts_voice_id or "pNInz6obpgDQGcFmaJgB",
                    "tts_stability": settings.tts_stability,
                    "tts_similarity_boost": settings.tts_similarity_boost,
                    "tts_style": settings.tts_style
                }
        finally:
            db.close()

        # 기본값 반환
        return {
            "tts_provider": "gtts",
            "tts_voice_id": "pNInz6obpgDQGcFmaJgB",
            "tts_stability": 0.5,
            "tts_similarity_boost": 0.75,
            "tts_style": 0.0
        }


    def _generate_gtts(self, text: str) -> Optional[str]:
        """
        Google TTS (gTTS)로 음성 생성

        Args:
            text: 변환할 텍스트

        Returns:
            저장된 파일 경로 또는 None
        """
        try:
            from gtts import gTTS

            # 파일명 생성 (텍스트 해시)
            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            filename = f"tts_{text_hash}.mp3"
            filepath = self.audio_dir / filename

            # 이미 생성된 경우
            if filepath.exists():
                print(f"[TTS] 이미 생성됨: {filename}")
                return str(filepath)

            # TTS 생성
            tts = gTTS(text=text, lang='ko')
            tts.save(str(filepath))

            print(f"[SUCCESS] TTS 생성 완료: {filepath}")
            return str(filepath)

        except ImportError:
            print("[ERROR] gTTS 패키지가 설치되지 않았습니다. pip install gtts")
            return None
        except Exception as e:
            print(f"[ERROR] TTS 생성 실패: {e}")
            return None

    def _generate_elevenlabs(
        self,
        text: str,
        voice_id: str = "pNInz6obpgDQGcFmaJgB",  # Adam
        stability: float = 0.5,      # ✨ NEW: 0.0 ~ 1.0
        similarity_boost: float = 0.75,  # ✨ NEW: 0.0 ~ 1.0
        style: float = 0.0,          # ✨ NEW: 0.0 ~ 1.0 (과장 정도)
        use_speaker_boost: bool = True  # ✨ NEW: 목소리 강화
    ) -> Optional[str]:
        """
        ElevenLabs TTS 고도화 버전

        Args:
            text: 변환할 텍스트
            voice_id: ElevenLabs Voice ID
            stability: 음성 안정성 (낮을수록 감정 표현 풍부, 높을수록 일관성 유지)
            similarity_boost: 원본 목소리와의 유사도 (높을수록 원본에 가까움)
            style: 스타일 과장 정도 (0.0 = 자연스러움, 1.0 = 과장됨)
            use_speaker_boost: 목소리 강화 (True 권장)

        Returns:
            저장된 파일 경로 또는 None
        """
        try:
            from elevenlabs.client import ElevenLabs
            import os

            # API 키 확인
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                print("[ERROR] ELEVENLABS_API_KEY 환경변수가 설정되지 않았습니다.")
                return self._generate_gtts(text)

            # ✨ 파일명 생성 (설정값 포함 해시)
            # 같은 텍스트라도 파라미터가 다르면 다른 파일로 저장
            settings_str = f"{voice_id}_{stability}_{similarity_boost}_{style}"
            combined_hash = hashlib.md5(
                f"{text}_{settings_str}".encode()
            ).hexdigest()[:10]

            filename = f"tts_elevenlabs_{combined_hash}.mp3"
            filepath = self.audio_dir / filename

            # 이미 생성된 경우 (스마트 캐싱)
            if filepath.exists():
                print(f"[TTS] 캐시에서 로드: {filename}")
                return str(filepath)

            # ElevenLabs 클라이언트 생성
            client = ElevenLabs(api_key=api_key)

            # ✨ 상세 설정으로 TTS 생성
            print(f"[ElevenLabs] 음성 생성 중...")
            print(f"  - Voice: {voice_id}")
            print(f"  - Stability: {stability}")
            print(f"  - Similarity Boost: {similarity_boost}")
            print(f"  - Style: {style}")

            audio_generator = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                # ✨ Voice Settings 추가
                voice_settings={
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            )

            # 오디오 저장
            with open(filepath, 'wb') as f:
                for chunk in audio_generator:
                    if isinstance(chunk, bytes):
                        f.write(chunk)

            print(f"[SUCCESS] ElevenLabs TTS 생성 완료: {filepath}")
            return str(filepath)

        except ImportError:
            print("[ERROR] elevenlabs 패키지가 설치되지 않았습니다.")
            return self._generate_gtts(text)
        except Exception as e:
            print(f"[ERROR] ElevenLabs TTS 생성 실패: {e}")
            return self._generate_gtts(text)

    def _get_cached_video(self, keyword: str) -> Optional[StockVideoAsset]:
        """
        캐시에서 영상 가져오기

        Args:
            keyword: 검색 키워드

        Returns:
            StockVideoAsset 또는 None
        """
        if not self.cache_enabled:
            return None

        cache_key = hashlib.md5(keyword.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                asset = StockVideoAsset(**data)

                # 파일이 실제로 존재하는지 확인
                if asset.local_path and os.path.exists(asset.local_path):
                    return asset

        except Exception as e:
            print(f"[WARNING] 캐시 로드 실패: {e}")

        return None

    def _cache_video(self, keyword: str, asset: StockVideoAsset):
        """
        영상을 캐시에 저장

        Args:
            keyword: 검색 키워드
            asset: StockVideoAsset 객체
        """
        if not self.cache_enabled:
            return

        cache_key = hashlib.md5(keyword.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(asset.model_dump(), f, ensure_ascii=False, indent=2)
            print(f"[Cache] 캐시 저장: {keyword}")
        except Exception as e:
            print(f"[WARNING] 캐시 저장 실패: {e}")

    def clear_cache(self):
        """캐시 디렉토리 비우기"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir()
            print("[Cache] 캐시 삭제 완료")

    def _select_bgm(self, content_plan: ContentPlan) -> Optional[BGMAsset]:
        """
        Phase 2: 콘텐츠에 맞는 BGM 선택

        Args:
            content_plan: ContentPlan 객체

        Returns:
            선택된 BGMAsset 또는 None
        """
        if not self.bgm_manager:
            return None

        try:
            # 주제와 톤에서 분위기 자동 추론
            topic = content_plan.title
            tone = getattr(content_plan, 'tone', '정보성')  # 기본값: 정보성

            mood = self.bgm_manager.auto_select_mood(topic, tone)
            print(f"[BGM] 추론된 분위기: {mood.value} (주제: {topic})")

            # 분위기에 맞는 BGM 선택 (최소 길이: target_duration)
            bgm_asset = self.bgm_manager.get_bgm_by_mood(
                mood=mood,
                min_duration=content_plan.target_duration
            )

            if bgm_asset:
                print(f"[BGM] 선택 완료: {bgm_asset.name}")
            else:
                print(f"[BGM] {mood.value} 분위기의 BGM이 없습니다. 랜덤 선택 시도...")
                # 폴백: 랜덤 BGM 선택
                bgm_asset = self.bgm_manager.get_random_bgm(
                    min_duration=content_plan.target_duration
                )

            return bgm_asset

        except Exception as e:
            print(f"[ERROR] BGM 선택 실패: {e}")
            return None
