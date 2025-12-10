# AI 유튜브 자동 제작 시스템 - Claude Code 완전 구현 가이드 (v2.1)

> **프로젝트 목표**: 트렌드 분석부터 유튜브 업로드까지 완전 자동화된 AI 영상 제작 파이프라인 구축

---

## 🎯 사용자 규모별 아키텍처

### 💻 **로컬 전용 (0-1명) - 추천 ⭐**
- **총 비용**: $0-50/월 (Gemini 무료 사용 시 $0!)
- **구조**: 모든 서비스를 로컬 PC에서 실행
- **장점**: 서버 비용 0원, 무제한 영상 제작
- **단점**: PC 켜져 있어야 함, 크로스 디바이스 제한적

### 🏠 **하이브리드 (2-3명) - 최적 ⭐⭐⭐**
- **총 비용**: $0-20/월 (Gemini 사용 시)
- **구조**: 가벼운 서버 + 로컬 영상 제작
- **장점**: 비용 효율 최고, 진척도 공유
- **단점**: 영상 제작은 각자 PC에서

### ☁️ **풀 클라우드 (4명+)**
- **총 비용**: $230-360/월
- **구조**: 모든 서비스 클라우드
- **장점**: 어디서나 접근, 완전 자동화
- **단점**: 비용 부담

---

## 🤖 AI API 비교 및 선택 가이드

### Claude vs Gemini 상세 비교

| 특징 | Claude API | Gemini API |
|------|-----------|------------|
| **무료 티어** | ❌ 없음 | ✅ 있음 (15 RPM) |
| **가격** | $3/1M 입력 토큰 | $0 (무료) ~ $0.35/1M |
| **대본 품질** | ⭐⭐⭐⭐⭐ (최고) | ⭐⭐⭐⭐ (매우 좋음) |
| **트렌드 분석** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **한국어 지원** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **응답 속도** | 빠름 (2-3초) | 매우 빠름 (1-2초) |
| **컨텍스트** | 200K 토큰 | 1M 토큰 (Gemini 1.5) |
| **멀티모달** | 이미지 지원 | 이미지/비디오 지원 |

### 무료 티어 상세 (Gemini)

**Gemini 1.5 Flash (무료)**
- **분당 요청**: 15 RPM
- **일일 요청**: 1,500 RPD
- **비용**: **완전 무료** 🎉
- **용도**: 대본 생성, 트렌드 분석, 메타데이터 생성
- **제한**: 동시 요청 제한

**예상 사용량 (하루 영상 3개 제작)**
- 트렌드 분석: 1회
- 대본 생성: 3회 x 3버전 = 9회
- 메타데이터: 3회
- **총**: 13회/일 → **무료 티어로 충분** ✅

### 권장 사용 전략

**테스트/개발 단계:**
- ✅ **Gemini 1.5 Flash (무료)** 사용
- 완전 무료로 시스템 테스트

**프로덕션 단계:**
- **옵션 1**: Gemini 1.5 Flash 계속 사용 (무료)
  - 영상 수 제한 있음 (하루 50개 정도까지)
- **옵션 2**: Gemini 1.5 Pro ($0.35/1M 토큰)
  - 속도 제한 완화, 더 높은 품질
- **옵션 3**: Claude Sonnet ($3/1M 토큰)
  - 최고 품질, 비용 증가

**하이브리드 전략 (추천):**
```python
# 트렌드 분석: Gemini (무료, 충분한 품질)
# 대본 생성: Claude (중요, 높은 품질)
# 메타데이터: Gemini (무료, 충분)
```

---

## 📦 기술 스택 (하이브리드 구조 기준)

### 로컬 환경 (영상 제작)
- **언어**: Python 3.11+
- **비디오 처리**: FFmpeg, moviepy
- **AI API (선택)**: 
  - **Gemini API** (무료, 테스트용) ⭐⭐⭐
  - **Claude API** (유료, 프로덕션)
- **TTS**: 
  - **무료**: pyttsx3 (오프라인, 품질 낮음)
  - **유료**: ElevenLabs API ($5/월) 또는 Google TTS
- **이미지 생성**: 
  - **무료**: Stable Diffusion 로컬 (VRAM 6GB+)
  - **유료**: Stability AI API, DALL-E
- **음악 라이브러리**: 
  - **무료**: YouTube Audio Library, Free Music Archive
  - **유료**: Epidemic Sound, Artlist

### 최소 서버 (Railway/Fly.io)
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (로컬) 또는 PostgreSQL Free Tier
- **인증**: JWT (OAuth는 선택)
- **비용**: $5-10/월 또는 무료 티어

### Frontend (선택적)
- **옵션 1**: CLI 도구 (가장 저렴)
- **옵션 2**: Next.js + Vercel 무료 (웹 대시보드)

---

## 🏗️ 하이브리드 아키텍처 (2-3명 최적)

```
[로컬 PC #1]                    [로컬 PC #2]
  ↓                               ↓
[Python CLI 도구]            [Python CLI 도구]
  ↓                               ↓
  └─────────[FastAPI 서버 - Railway Free/Fly.io]─────────┘
                ↓
          [SQLite/PostgreSQL]
                ↓
          [Gemini API 무료] ← 대본/분석
          [YouTube API]
```

**데이터 흐름:**
1. 서버: 프로젝트 관리, 진척도 동기화, YouTube OAuth
2. 로컬: 트렌드 분석(Gemini), 대본 생성(Gemini/Claude), 영상 제작, 편집
3. 업로드: 로컬에서 직접 YouTube 업로드

---

## 📋 핵심 기능 요구사항

### 0. AI 서비스 통합 모듈 (신규) ⭐

**기능:**
- Claude와 Gemini API를 통합 인터페이스로 제공
- 환경 변수로 AI 제공자 선택
- 자동 폴백 (Gemini 할당량 초과 시 Claude로)
- 비용 추적 및 로깅

**구현:**
```python
# local_cli/services/ai_service.py
import anthropic
import google.generativeai as genai
from typing import Literal
import os
from datetime import datetime

class AIService:
    """Claude와 Gemini를 통합하는 AI 서비스"""
    
    def __init__(self, provider: Literal['claude', 'gemini', 'auto'] = 'auto'):
        self.provider = provider
        self.usage_log = []
        
        # Claude 초기화
        if os.getenv('ANTHROPIC_API_KEY'):
            self.claude = anthropic.Anthropic(
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        else:
            self.claude = None
        
        # Gemini 초기화
        if os.getenv('GEMINI_API_KEY'):
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.gemini = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini = None
        
        # Auto 모드: Gemini 우선 (무료), 실패 시 Claude
        if provider == 'auto':
            self.primary = 'gemini' if self.gemini else 'claude'
            self.fallback = 'claude' if self.primary == 'gemini' else None
        else:
            self.primary = provider
            self.fallback = None
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> str:
        """텍스트 생성 (Claude/Gemini 자동 선택)"""
        
        try:
            if self.primary == 'gemini':
                return self._generate_with_gemini(
                    prompt, max_tokens, temperature, system_prompt
                )
            elif self.primary == 'claude':
                return self._generate_with_claude(
                    prompt, max_tokens, temperature, system_prompt
                )
        except Exception as e:
            print(f"⚠️ {self.primary} 오류: {e}")
            
            # 폴백 시도
            if self.fallback:
                print(f"🔄 {self.fallback}로 재시도...")
                if self.fallback == 'claude':
                    return self._generate_with_claude(
                        prompt, max_tokens, temperature, system_prompt
                    )
            
            raise
    
    def _generate_with_gemini(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: str
    ) -> str:
        """Gemini로 생성"""
        
        # 시스템 프롬프트를 프롬프트에 포함
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # 생성 설정
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        
        # API 호출
        response = self.gemini.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        # 사용량 로깅
        self._log_usage('gemini', prompt, response.text)
        
        return response.text
    
    def _generate_with_claude(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system_prompt: str
    ) -> str:
        """Claude로 생성"""
        
        if not self.claude:
            raise ValueError("Claude API 키가 설정되지 않았습니다")
        
        # API 호출
        message = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # 사용량 로깅
        self._log_usage('claude', prompt, response_text)
        
        return response_text
    
    def _log_usage(self, provider: str, prompt: str, response: str):
        """API 사용량 로깅"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'prompt_length': len(prompt),
            'response_length': len(response),
        }
        self.usage_log.append(log_entry)
    
    def get_usage_stats(self):
        """사용량 통계 반환"""
        if not self.usage_log:
            return "사용 기록 없음"
        
        claude_count = sum(1 for log in self.usage_log if log['provider'] == 'claude')
        gemini_count = sum(1 for log in self.usage_log if log['provider'] == 'gemini')
        
        total_prompts = sum(log['prompt_length'] for log in self.usage_log)
        total_responses = sum(log['response_length'] for log in self.usage_log)
        
        # 대략적인 토큰 수 계산 (1 토큰 ≈ 4 글자)
        total_tokens = (total_prompts + total_responses) // 4
        
        # 비용 추정
        claude_cost = (claude_count / len(self.usage_log)) * total_tokens * 3 / 1_000_000
        gemini_cost = 0  # 무료
        
        return f"""
📊 AI API 사용 통계:
- Claude 호출: {claude_count}회
- Gemini 호출: {gemini_count}회
- 총 토큰: 약 {total_tokens:,}
- 예상 비용: ${claude_cost:.2f} (Gemini는 무료)
        """


# 전역 AI 서비스 인스턴스
def get_ai_service(provider: str = None) -> AIService:
    """AI 서비스 인스턴스 가져오기"""
    if provider is None:
        provider = os.getenv('AI_PROVIDER', 'auto')
    
    return AIService(provider=provider)
```

**설정 파일 (.env):**
```bash
# AI Provider 선택
# 옵션: 'claude', 'gemini', 'auto' (기본값)
# 'auto'는 Gemini 우선, 실패 시 Claude로 폴백
AI_PROVIDER=auto

# API Keys
ANTHROPIC_API_KEY=sk-ant-...  # 선택 (Claude 사용 시)
GEMINI_API_KEY=AIza...        # 필수 (무료 사용)

# 기타 API
YOUTUBE_API_KEY=AIza...
```

---

### 1. 유튜브 트렌드 분석 모듈 (Gemini 통합)

**기능:**
- YouTube Data API로 트렌딩 영상 수집
- **Gemini 또는 Claude**로 트렌드 키워드 추출
- 숏폼/롱폼 트렌드 분석

**구현:**
```python
# local_cli/services/trend_analyzer.py
from googleapiclient.discovery import build
from .ai_service import get_ai_service

class TrendAnalyzer:
    def __init__(self, ai_provider: str = 'auto'):
        self.youtube = build('youtube', 'v3', 
                           developerKey=os.getenv('YOUTUBE_API_KEY'))
        self.ai_service = get_ai_service(ai_provider)
    
    def fetch_trending_videos(self, region='US', category_id=None, max_results=50):
        """YouTube 트렌딩 비디오 가져오기"""
        request = self.youtube.videos().list(
            part='snippet,statistics',
            chart='mostPopular',
            regionCode=region,
            videoCategoryId=category_id,
            maxResults=max_results
        )
        return request.execute()
    
    def analyze_with_ai(self, video_data, video_format='short'):
        """AI로 트렌드 분석 (Gemini/Claude 자동 선택)"""
        
        # 비디오 데이터를 텍스트로 변환
        video_summaries = []
        for video in video_data.get('items', [])[:20]:  # 상위 20개만
            snippet = video['snippet']
            stats = video['statistics']
            
            summary = f"""
제목: {snippet['title']}
조회수: {stats.get('viewCount', 0)}
좋아요: {stats.get('likeCount', 0)}
댓글: {stats.get('commentCount', 0)}
"""
            video_summaries.append(summary)
        
        videos_text = "\n---\n".join(video_summaries)
        
        prompt = f"""
다음은 YouTube에서 현재 트렌딩 중인 {video_format} 영상들입니다.

{videos_text}

이 데이터를 분석하여 다음을 JSON 형식으로 제공해주세요:
1. 주요 키워드 10개 (배열)
2. 트렌딩 주제 5개 (배열)
3. 추천 콘텐츠 아이디어 3개 (배열)
4. 예상 조회수 범위

JSON 형식 예시:
{{
    "keywords": ["키워드1", "키워드2", ...],
    "topics": ["주제1", "주제2", ...],
    "content_ideas": ["아이디어1", "아이디어2", ...],
    "view_range": "10K-50K"
}}

JSON만 응답해주세요 (추가 설명 없이).
"""
        
        response = self.ai_service.generate_text(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.3  # 분석은 낮은 temperature
        )
        
        # JSON 파싱
        import json
        import re
        
        # JSON 부분만 추출 (```json ... ``` 제거)
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response
        
        try:
            analysis = json.loads(json_str)
            return analysis
        except json.JSONDecodeError:
            # 파싱 실패 시 기본값 반환
            return {
                "keywords": ["트렌드", "인기"],
                "topics": ["일반"],
                "content_ideas": ["트렌드 기반 콘텐츠"],
                "view_range": "알 수 없음"
            }
```

---

### 2. AI 대본 생성 모듈 (Gemini 통합)

**기능:**
- **Gemini 또는 Claude**로 대본 생성
- A/B 테스트용 여러 버전 생성
- 타임스탬프 포함

**구현:**
```python
# local_cli/services/script_generator.py
from .ai_service import get_ai_service
import os

class ScriptGenerator:
    def __init__(self, ai_provider: str = 'auto'):
        self.ai_service = get_ai_service(ai_provider)
    
    def generate_script(
        self,
        trend_keywords: list,
        video_format: str,  # 'short' or 'long'
        duration_seconds: int,
        tone: str = 'informative',
        num_versions: int = 1
    ):
        """대본 생성 (Gemini/Claude 자동 선택)"""
        
        duration_guide = {
            'short': '30-60초 분량, 빠른 템포, 강력한 훅',
            'long': f'{duration_seconds//60}분 분량, 상세한 설명, 단계별 구성'
        }
        
        system_prompt = """당신은 전문 유튜브 대본 작가입니다. 
시청자의 관심을 끌고 유지율을 높이는 대본을 작성합니다."""
        
        prompt = f"""
유튜브 {video_format} 영상 대본을 작성해주세요.

트렌드 키워드: {', '.join(trend_keywords)}
영상 길이: {duration_seconds}초 ({duration_guide[video_format]})
톤: {tone}

요구사항:
1. 첫 3초에 강력한 후킹 포인트 (질문, 놀라운 사실 등)
2. 타임스탬프 포함: [00:00] 형식
3. 시청자 유지율을 고려한 구성
4. 명확한 CTA(Call-to-Action) 포함
5. 자연스러운 말투 (너무 격식적이지 않게)

형식 예시:
[00:00] 여러분, 지금 이 영상을 보시면...
[00:05] 오늘은 {trend_keywords[0]}에 대해...
[00:15] 첫 번째로...

대본을 작성해주세요.
"""
        
        scripts = []
        for i in range(num_versions):
            print(f"📝 대본 버전 {i+1}/{num_versions} 생성 중...")
            
            response = self.ai_service.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7 + (i * 0.1),  # 버전마다 다양성 증가
                system_prompt=system_prompt
            )
            
            scripts.append(response)
        
        return scripts
```

---

### 3. TTS 음성 생성 모듈

**기능:**
- 대본을 자연스러운 음성으로 변환
- 여러 TTS 제공자 지원
- 타임스탬프 기반 분할

**TTS 옵션 비교:**

| 옵션 | 비용 | 품질 | 지연시간 | 추천 |
|------|------|------|----------|------|
| pyttsx3 (로컬) | 무료 | ⭐⭐ | 즉시 | 테스트용 |
| Google TTS | $4/100만자 | ⭐⭐⭐ | 1-2초 | 예산형 ⭐ |
| ElevenLabs | $5/월 (3만자) | ⭐⭐⭐⭐⭐ | 2-5초 | 프리미엄 ⭐⭐⭐ |
| Azure TTS | $4/100만자 | ⭐⭐⭐⭐ | 1-2초 | 기업용 |

**구현:**
```python
# local_cli/services/tts_service.py
import pyttsx3
from google.cloud import texttospeech
from elevenlabs import generate, Voice, VoiceSettings
import azure.cognitiveservices.speech as speechsdk
import os

class TTSService:
    def __init__(self, provider='google'):
        """
        TTS 제공자 초기화
        
        Args:
            provider: 'local', 'google', 'elevenlabs', 'azure'
        """
        self.provider = provider
        
        if provider == 'local':
            self.engine = pyttsx3.init()
        elif provider == 'google':
            self.client = texttospeech.TextToSpeechClient()
        elif provider == 'elevenlabs':
            # ElevenLabs는 API 키만 필요
            self.api_key = os.getenv('ELEVENLABS_API_KEY')
        elif provider == 'azure':
            self.speech_config = speechsdk.SpeechConfig(
                subscription=os.getenv('AZURE_SPEECH_KEY'),
                region=os.getenv('AZURE_REGION')
            )
    
    def generate_speech(
        self,
        script_text: str,
        output_path: str,
        voice_id: str = None,
        speed: float = 1.0,
        pitch: float = 0.0
    ):
        """대본을 음성으로 변환"""
        
        print(f"🎤 {self.provider}로 음성 생성 중...")
        
        if self.provider == 'local':
            return self._generate_local(script_text, output_path, speed)
        elif self.provider == 'google':
            return self._generate_google(script_text, output_path, voice_id, speed, pitch)
        elif self.provider == 'elevenlabs':
            return self._generate_elevenlabs(script_text, output_path, voice_id)
        elif self.provider == 'azure':
            return self._generate_azure(script_text, output_path, voice_id, speed, pitch)
    
    def _generate_local(self, text, output_path, speed):
        """pyttsx3로 로컬 생성 (무료, 품질 낮음)"""
        self.engine.setProperty('rate', 150 * speed)
        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
        return output_path
    
    def _generate_google(self, text, output_path, voice_id, speed, pitch):
        """Google Cloud TTS (추천 - 가성비)"""
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code='ko-KR',  # 또는 'en-US'
            name=voice_id or 'ko-KR-Standard-A',
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speed,
            pitch=pitch
        )
        
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        with open(output_path, 'wb') as out:
            out.write(response.audio_content)
        
        return output_path
    
    def _generate_elevenlabs(self, text, output_path, voice_id):
        """ElevenLabs TTS (최고 품질)"""
        audio = generate(
            text=text,
            voice=Voice(
                voice_id=voice_id or "21m00Tcm4TlvDq8ikWAM",  # Rachel
                settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True
                )
            ),
            model="eleven_multilingual_v2"
        )
        
        with open(output_path, 'wb') as f:
            f.write(audio)
        
        return output_path
    
    def _generate_azure(self, text, output_path, voice_id, speed, pitch):
        """Azure TTS"""
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        
        # SSML로 속도와 피치 조절
        ssml = f"""
        <speak version='1.0' xml:lang='ko-KR'>
            <voice name='{voice_id or "ko-KR-SunHiNeural"}'>
                <prosody rate='{speed}' pitch='{pitch:+.0f}%'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        result = synthesizer.speak_ssml_async(ssml).get()
        return output_path
    
    def generate_with_timestamps(self, script_with_timestamps: str, output_dir: str):
        """타임스탬프 포함 대본을 여러 오디오 파일로 분할"""
        import re
        
        os.makedirs(output_dir, exist_ok=True)
        
        # [00:05] 패턴으로 분할
        segments = re.split(r'\[(\d{2}:\d{2})\]', script_with_timestamps)
        
        audio_files = []
        for i in range(1, len(segments), 2):
            timestamp = segments[i]
            text = segments[i+1].strip()
            
            if text:
                output_path = f"{output_dir}/segment_{i//2}.mp3"
                self.generate_speech(text, output_path)
                audio_files.append({
                    'timestamp': timestamp,
                    'text': text,
                    'audio_path': output_path
                })
        
        return audio_files
```

**음성 병합 및 타이밍 조정:**
```python
# local_cli/services/audio_processor.py
from pydub import AudioSegment
import re

class AudioProcessor:
    def merge_audio_segments(self, segments, output_path):
        """분할된 오디오를 타임스탬프에 맞춰 병합"""
        final_audio = AudioSegment.silent(duration=0)
        
        for i, segment in enumerate(segments):
            audio = AudioSegment.from_file(segment['audio_path'])
            
            # 타임스탬프를 밀리초로 변환
            time_ms = self._timestamp_to_ms(segment['timestamp'])
            
            # 현재 오디오 길이와 목표 시간 차이만큼 무음 추가
            current_length = len(final_audio)
            if time_ms > current_length:
                silence = AudioSegment.silent(duration=time_ms - current_length)
                final_audio += silence
            
            final_audio += audio
        
        final_audio.export(output_path, format='mp3')
        return output_path, len(final_audio) / 1000  # 초 단위 반환
    
    def _timestamp_to_ms(self, timestamp: str):
        """[00:05] -> 5000ms"""
        match = re.match(r'(\d{2}):(\d{2})', timestamp)
        if match:
            minutes, seconds = map(int, match.groups())
            return (minutes * 60 + seconds) * 1000
        return 0
```

---

### 4. 배경음악 추가 모듈

**기능:**
- 무료/유료 음악 라이브러리 통합
- 자동 볼륨 조절
- 음악 페이드 인/아웃

**구현:**
```python
# local_cli/services/music_library.py
import os
import random
from pydub import AudioSegment

class MusicLibrary:
    """무료 음악 라이브러리 관리"""
    
    MUSIC_SOURCES = {
        'youtube_audio_library': {
            'path': './music/youtube_audio_library/',
            'license': 'Free to use',
            'genres': ['ambient', 'electronic', 'cinematic', 'upbeat']
        },
        'free_music_archive': {
            'path': './music/free_music_archive/',
            'license': 'Creative Commons',
            'genres': ['jazz', 'classical', 'indie']
        }
    }
    
    def get_music_for_style(self, style: str, duration_seconds: int):
        """스타일에 맞는 배경음악 선택"""
        genre_mapping = {
            'short_trendy': 'upbeat',
            'long_educational': 'ambient',
            'long_storytelling': 'cinematic'
        }
        
        genre = genre_mapping.get(style, 'ambient')
        
        # 해당 장르의 음악 파일 찾기
        music_files = self._find_music_files(genre)
        
        if not music_files:
            print("⚠️ 음악 파일을 찾을 수 없습니다. 음악 없이 진행합니다.")
            return None
        
        # 랜덤 선택
        selected_music = random.choice(music_files)
        
        # 길이 조정
        return self._adjust_music_length(selected_music, duration_seconds)
    
    def _find_music_files(self, genre: str):
        """장르에 맞는 음악 파일 찾기"""
        music_files = []
        
        for source, info in self.MUSIC_SOURCES.items():
            genre_path = os.path.join(info['path'], genre)
            if os.path.exists(genre_path):
                for file in os.listdir(genre_path):
                    if file.endswith(('.mp3', '.wav')):
                        music_files.append(os.path.join(genre_path, file))
        
        return music_files
    
    def _adjust_music_length(self, music_path: str, target_duration: int):
        """음악 길이를 영상 길이에 맞춤"""
        audio = AudioSegment.from_file(music_path)
        audio_duration = len(audio) / 1000  # 초 단위
        
        target_ms = target_duration * 1000
        
        if audio_duration < target_duration:
            # 음악이 짧으면 반복
            repeats = int(target_duration / audio_duration) + 1
            audio = audio * repeats
        
        # 정확한 길이로 자르기
        audio = audio[:target_ms]
        
        # 마지막 5초 페이드 아웃
        audio = audio.fade_out(5000)
        
        return audio
    
    def mix_voice_and_music(
        self,
        voice_path: str,
        music_audio: AudioSegment,
        output_path: str,
        voice_volume: float = 1.0,
        music_volume: float = 0.2
    ):
        """음성과 배경음악 믹싱"""
        voice = AudioSegment.from_file(voice_path)
        
        # 볼륨 조절 (dB 단위)
        voice = voice + (20 * voice_volume - 20)
        music_audio = music_audio + (20 * music_volume - 20)
        
        # 음악을 음성 길이에 맞춤
        if len(music_audio) < len(voice):
            music_audio = music_audio * (len(voice) // len(music_audio) + 1)
        music_audio = music_audio[:len(voice)]
        
        # 오버레이
        mixed = voice.overlay(music_audio)
        
        mixed.export(output_path, format='mp3')
        return output_path
```

---

### 5. 영상 제작 모듈 (통합)

**구현:**
```python
# local_cli/services/video_producer.py
import moviepy.editor as mp
from moviepy.video.tools.subtitles import SubtitlesClip
import os

class VideoProducer:
    def __init__(self):
        self.tts_service = TTSService(provider=os.getenv('TTS_PROVIDER', 'google'))
        self.music_library = MusicLibrary()
    
    def produce_video(
        self,
        script: dict,
        style_preset: str,
        output_path: str
    ):
        """완전한 영상 제작 파이프라인"""
        
        temp_dir = './temp'
        os.makedirs(temp_dir, exist_ok=True)
        
        # 1. TTS 음성 생성
        print("🎤 음성 생성 중...")
        voice_segments = self.tts_service.generate_with_timestamps(
            script['content'],
            output_dir=f'{temp_dir}/audio'
        )
        
        audio_processor = AudioProcessor()
        voice_path, voice_duration = audio_processor.merge_audio_segments(
            voice_segments,
            f'{temp_dir}/voice_final.mp3'
        )
        
        # 2. 배경음악 추가
        print("🎵 배경음악 추가 중...")
        background_music = self.music_library.get_music_for_style(
            style_preset,
            int(voice_duration)
        )
        
        if background_music:
            final_audio_path = self.music_library.mix_voice_and_music(
                voice_path,
                background_music,
                f'{temp_dir}/audio_with_music.mp3',
                voice_volume=1.0,
                music_volume=0.25
            )
        else:
            final_audio_path = voice_path
        
        # 3. 이미지/영상 클립 생성
        print("🖼️ 이미지 생성 중...")
        visual_clips = self._generate_visual_clips(
            script,
            voice_segments,
            style_preset
        )
        
        # 4. 자막 생성
        print("📝 자막 생성 중...")
        subtitles = self._create_subtitles(voice_segments)
        
        # 5. 최종 합성
        print("🎬 영상 합성 중...")
        final_video = self._compose_video(
            visual_clips,
            final_audio_path,
            subtitles,
            script['video_format']
        )
        
        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            preset='medium'
        )
        
        # 6. 썸네일 생성
        print("📸 썸네일 생성 중...")
        thumbnail_path = output_path.replace('.mp4', '_thumb.jpg')
        final_video.save_frame(thumbnail_path, t=2)
        
        print(f"✅ 영상 생성 완료: {output_path}")
        
        return output_path, thumbnail_path
    
    def _generate_visual_clips(self, script, voice_segments, style_preset):
        """간단한 이미지 슬라이드 (실제로는 AI 이미지 생성)"""
        clips = []
        
        # 임시: 단색 배경 (실제로는 AI 이미지 생성)
        from moviepy.video.VideoClip import ColorClip
        
        for segment in voice_segments:
            # 5초 클립
            clip = ColorClip(size=(1920, 1080), color=(50, 50, 100), duration=5)
            
            # 줌 효과
            clip = clip.resize(lambda t: 1 + 0.05 * t)
            
            clips.append(clip)
        
        return clips
    
    def _create_subtitles(self, voice_segments):
        """자막 데이터 생성"""
        subtitle_data = []
        
        for i, segment in enumerate(voice_segments):
            start_time = self._timestamp_to_seconds(segment['timestamp'])
            end_time = start_time + 5
            
            subtitle_data.append({
                'start': start_time,
                'end': end_time,
                'text': segment['text']
            })
        
        return subtitle_data
    
    def _compose_video(self, visual_clips, audio_path, subtitles, video_format):
        """최종 영상 합성"""
        
        # 비주얼 연결
        video = mp.concatenate_videoclips(visual_clips, method="compose")
        
        # 오디오 추가
        audio = mp.AudioFileClip(audio_path)
        video = video.set_audio(audio)
        
        # 자막 추가
        def make_textclip(txt):
            return mp.TextClip(
                txt,
                font='Arial-Bold',
                fontsize=50 if video_format == 'short' else 40,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(video.w * 0.9, None),
                align='center'
            )
        
        subtitle_clips = []
        for sub in subtitles:
            txt_clip = make_textclip(sub['text'])
            txt_clip = txt_clip.set_start(sub['start']).set_end(sub['end'])
            txt_clip = txt_clip.set_position(('center', 'bottom'))
            subtitle_clips.append(txt_clip)
        
        video = mp.CompositeVideoClip([video] + subtitle_clips)
        
        # 숏폼은 9:16 크롭
        if video_format == 'short':
            video = video.crop(
                x_center=video.w/2,
                y_center=video.h/2,
                width=video.h * 9/16,
                height=video.h
            )
        
        return video
    
    def _timestamp_to_seconds(self, timestamp):
        """[00:05] -> 5.0"""
        import re
        match = re.match(r'(\d{2}):(\d{2})', timestamp)
        if match:
            minutes, seconds = map(int, match.groups())
            return minutes * 60 + seconds
        return 0
```

---

### 6. 유튜브 업로드 모듈 (Gemini로 메타데이터 생성)

**구현:**
```python
# local_cli/services/youtube_uploader.py
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .ai_service import get_ai_service
import pickle
import os
import json
import re

class YouTubeUploader:
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, ai_provider: str = 'auto'):
        self.youtube = self._get_authenticated_service()
        self.ai_service = get_ai_service(ai_provider)
    
    def _get_authenticated_service(self):
        """OAuth 인증"""
        credentials = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)
        
        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                self.SCOPES
            )
            credentials = flow.run_local_server(port=8080)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)
        
        return build('youtube', 'v3', credentials=credentials)
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        category_id: str = '22',
        privacy_status: str = 'public'
    ):
        """비디오 업로드"""
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True
        )
        
        request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        print("📤 업로드 시작...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"업로드 진행: {progress}%")
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"✅ 업로드 완료: {video_url}")
        return video_id, video_url
    
    def generate_metadata(self, script: dict, trend_keywords: list):
        """AI로 자동 메타데이터 생성 (Gemini/Claude)"""
        
        prompt = f"""
다음 영상 대본과 트렌드 키워드를 바탕으로 유튜브 메타데이터를 생성해주세요:

대본 (일부):
{script['content'][:500]}...

키워드: {', '.join(trend_keywords)}

다음 형식의 JSON으로 응답해주세요:
{{
    "title": "클릭을 유도하는 제목 (50자 이내, 이모지 포함 가능)",
    "description": "상세 설명 (500자 이내, 타임스탬프 포함 추천)",
    "tags": ["태그1", "태그2", ...] (10-15개, 관련성 높은 태그)
}}

JSON만 응답해주세요.
"""
        
        response = self.ai_service.generate_text(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        # JSON 파싱
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response
        
        try:
            metadata = json.loads(json_str)
            return metadata
        except json.JSONDecodeError:
            # 파싱 실패 시 기본값
            return {
                "title": f"{trend_keywords[0]} - 필수 시청!",
                "description": f"오늘은 {trend_keywords[0]}에 대해 알아봅니다.",
                "tags": trend_keywords
            }
```

---

### 7. CLI 통합 도구

**메인 CLI:**
```python
# local_cli/main.py
import click
from services.trend_analyzer import TrendAnalyzer
from services.script_generator import ScriptGenerator
from services.video_producer import VideoProducer
from services.youtube_uploader import YouTubeUploader
from services.ai_service import get_ai_service
import os

@click.group()
def cli():
    """AI YouTube Automation CLI"""
    pass

@cli.command()
@click.option('--provider', type=click.Choice(['claude', 'gemini', 'auto']), 
              default='auto', help='AI provider')
def test_ai(provider):
    """AI 서비스 테스트"""
    ai_service = get_ai_service(provider)
    
    print(f"🤖 {provider} 테스트 중...\n")
    
    response = ai_service.generate_text(
        prompt="안녕하세요! 간단한 자기소개를 해주세요.",
        max_tokens=200
    )
    
    print(f"응답:\n{response}\n")
    print(ai_service.get_usage_stats())

@cli.command()
@click.option('--region', default='US', help='YouTube region')
@click.option('--format', type=click.Choice(['short', 'long']), required=True)
@click.option('--ai', type=click.Choice(['claude', 'gemini', 'auto']), 
              default='auto', help='AI provider')
def analyze_trends(region, format, ai):
    """트렌드 분석"""
    analyzer = TrendAnalyzer(ai_provider=ai)
    
    print(f"🔍 {region} 지역의 {format} 트렌드 분석 중...")
    videos = analyzer.fetch_trending_videos(region=region, max_results=50)
    analysis = analyzer.analyze_with_ai(videos, video_format=format)
    
    print("\n✅ 트렌드 분석 완료:")
    print(f"키워드: {', '.join(analysis['keywords'])}")
    print(f"주제: {', '.join(analysis['topics'])}")
    print(f"\n콘텐츠 아이디어:")
    for i, idea in enumerate(analysis['content_ideas'], 1):
        print(f"  {i}. {idea}")

@cli.command()
@click.option('--keywords', required=True, help='Comma-separated keywords')
@click.option('--format', type=click.Choice(['short', 'long']), required=True)
@click.option('--duration', type=int, required=True, help='Duration in seconds')
@click.option('--tone', default='informative', help='Script tone')
@click.option('--versions', type=int, default=3, help='Number of versions')
@click.option('--ai', type=click.Choice(['claude', 'gemini', 'auto']), 
              default='auto', help='AI provider')
def generate_script(keywords, format, duration, tone, versions, ai):
    """대본 생성"""
    generator = ScriptGenerator(ai_provider=ai)
    
    keyword_list = [k.strip() for k in keywords.split(',')]
    
    print(f"✍️ 대본 생성 중... ({format}, {duration}초, {versions}개 버전)")
    scripts = generator.generate_script(
        trend_keywords=keyword_list,
        video_format=format,
        duration_seconds=duration,
        tone=tone,
        num_versions=versions
    )
    
    for i, script in enumerate(scripts, 1):
        print(f"\n{'='*60}")
        print(f"버전 {i}")
        print('='*60)
        print(script)

@cli.command()
@click.option('--script', required=True, help='Script text or file path')
@click.option('--format', type=click.Choice(['short', 'long']), required=True)
@click.option('--style', default='short_trendy', help='Video style')
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
    
    print("🎬 영상 제작 시작...")
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    video_path, thumbnail_path = producer.produce_video(
        script=script_dict,
        style_preset=style,
        output_path=output
    )
    
    print(f"\n✅ 완료!")
    print(f"영상: {video_path}")
    print(f"썸네일: {thumbnail_path}")

@cli.command()
@click.option('--video', required=True, help='Video file path')
@click.option('--keywords', required=True, help='Comma-separated keywords')
@click.option('--ai', type=click.Choice(['claude', 'gemini', 'auto']), 
              default='gemini', help='AI provider for metadata')
def upload(video, keywords, ai):
    """유튜브 업로드"""
    uploader = YouTubeUploader(ai_provider=ai)
    
    keyword_list = [k.strip() for k in keywords.split(',')]
    
    print("📝 메타데이터 생성 중...")
    metadata = uploader.generate_metadata(
        script={'content': ''},
        trend_keywords=keyword_list
    )
    
    print(f"\n제목: {metadata['title']}")
    print(f"설명: {metadata['description'][:100]}...")
    print(f"태그: {', '.join(metadata['tags'])}")
    
    confirm = click.confirm('\n업로드하시겠습니까?')
    if not confirm:
        print("취소됨")
        return
    
    video_id, video_url = uploader.upload_video(
        video_path=video,
        title=metadata['title'],
        description=metadata['description'],
        tags=metadata['tags']
    )
    
    print(f"\n🎉 업로드 완료: {video_url}")

@cli.command()
@click.option('--ai', type=click.Choice(['claude', 'gemini', 'auto']), 
              default='gemini', help='AI provider')
def full_automation(ai):
    """전체 파이프라인 자동 실행"""
    print("🚀 전체 자동화 시작...\n")
    print(f"AI Provider: {ai}\n")
    
    # 1. 트렌드 분석
    print("1️⃣ 트렌드 분석")
    analyzer = TrendAnalyzer(ai_provider=ai)
    videos = analyzer.fetch_trending_videos(region='US', max_results=50)
    analysis = analyzer.analyze_with_ai(videos, video_format='short')
    
    keywords = analysis['keywords'][:3]
    print(f"키워드: {', '.join(keywords)}")
    
    # 2. 대본 생성
    print("\n2️⃣ 대본 생성")
    generator = ScriptGenerator(ai_provider=ai)
    scripts = generator.generate_script(
        trend_keywords=keywords,
        video_format='short',
        duration_seconds=60,
        tone='informative',
        num_versions=1
    )
    
    # 3. 영상 제작
    print("\n3️⃣ 영상 제작")
    producer = VideoProducer()
    
    os.makedirs('./output', exist_ok=True)
    video_path, thumbnail_path = producer.produce_video(
        script={'content': scripts[0], 'video_format': 'short'},
        style_preset='short_trendy',
        output_path='./output/auto_video.mp4'
    )
    
    # 4. 업로드
    print("\n4️⃣ 유튜브 업로드")
    uploader = YouTubeUploader(ai_provider=ai)
    metadata = uploader.generate_metadata(
        {'content': scripts[0]},
        keywords
    )
    
    confirm = click.confirm('업로드하시겠습니까?')
    if confirm:
        video_id, video_url = uploader.upload_video(
            video_path=video_path,
            title=metadata['title'],
            description=metadata['description'],
            tags=metadata['tags']
        )
        
        print(f"\n✅ 전체 프로세스 완료!")
        print(f"영상 URL: {video_url}")
    else:
        print("\n✅ 영상 제작 완료 (업로드 건너뜀)")
        print(f"영상: {video_path}")
    
    # 사용량 통계
    print("\n" + get_ai_service(ai).get_usage_stats())

if __name__ == '__main__':
    cli()
```

---

## 💰 비용 비교 (Gemini 포함)

### 로컬 전용 (2-3명) - Gemini 사용

#### 월간 운영 비용 (영상 30개 기준)

| 항목 | Gemini 옵션 | Claude 옵션 |
|------|-------------|-------------|
| **대본 생성** | 무료 (Gemini Flash) | $15 (Claude Sonnet) |
| **트렌드 분석** | 무료 (Gemini Flash) | $5 (Claude Sonnet) |
| **메타데이터** | 무료 (Gemini Flash) | $3 (Claude Sonnet) |
| **TTS** | Google TTS $2 | Google TTS $2 |
| **이미지** | 로컬 SD 무료 | 로컬 SD 무료 |
| **배경음악** | YouTube 무료 | YouTube 무료 |
| **서버** | Railway Free | Railway Free |
| **합계** | **$2/월** ⭐⭐⭐ | $25/월 |

**Gemini 사용 시 비용: 월 $2 (TTS만!)** 🎉

### 하이브리드 전략 (최적)

| 작업 | AI 선택 | 이유 |
|------|---------|------|
| 트렌드 분석 | Gemini (무료) | 충분한 품질 |
| 대본 생성 | Gemini → Claude | 테스트는 Gemini, 중요 영상은 Claude |
| 메타데이터 | Gemini (무료) | 충분한 품질 |

**예상 비용: $2-10/월**

---

## 🚀 시작 가이드

### 1. 초기 설정

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/ai-youtube-automation.git
cd ai-youtube-automation

# 2. Python 환경
python -m venv venv
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. FFmpeg 설치
# Ubuntu: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

### 2. 환경 변수 설정 (.env)

```bash
# ===== AI Provider 설정 =====
# 옵션: 'claude', 'gemini', 'auto'
AI_PROVIDER=gemini  # 테스트는 Gemini 무료 사용!

# ===== API Keys =====
# Gemini (무료!) - 필수
GEMINI_API_KEY=AIza...

# Claude (선택) - 고품질 필요 시
# ANTHROPIC_API_KEY=sk-ant-...

# YouTube API
YOUTUBE_API_KEY=AIza...

# ===== TTS 설정 =====
TTS_PROVIDER=google  # 옵션: local, google, elevenlabs, azure

# Google TTS (권장)
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json

# ElevenLabs (선택)
# ELEVENLABS_API_KEY=...

# ===== 이미지 생성 =====
USE_LOCAL_SD=true  # 로컬 Stable Diffusion 사용

# Stability AI (선택)
# STABILITY_API_KEY=...
```

### 3. Gemini API 키 발급 (무료!)

```bash
# 1. Google AI Studio 방문
https://makersuite.google.com/app/apikey

# 2. "Create API Key" 클릭
# 3. 프로젝트 선택 또는 생성
# 4. API 키 복사 → .env에 붙여넣기

# 무료 할당량:
# - 분당 15 요청
# - 일일 1,500 요청
# - 월간 무제한 (무료!)
```

### 4. 첫 테스트

```bash
# AI 서비스 테스트
python local_cli/main.py test-ai --provider gemini

# 트렌드 분석
python local_cli/main.py analyze-trends --format short --ai gemini

# 대본 생성
python local_cli/main.py generate-script \
  --keywords "AI,technology" \
  --format short \
  --duration 60 \
  --ai gemini

# 전체 자동화 (Gemini 무료!)
python local_cli/main.py full-automation --ai gemini
```

---

## 📝 requirements.txt

```txt
# ===== 코어 =====
# Gemini (무료!) ⭐
google-generativeai==0.3.2

# Claude (선택)
anthropic==0.40.0

# YouTube
google-api-python-client==2.150.0
google-auth-oauthlib==1.2.1
google-auth-httplib2==0.2.0

# ===== 비디오 처리 =====
moviepy==1.0.3
ffmpeg-python==0.2.0
pydub==0.25.1

# ===== TTS =====
gTTS==2.5.3
google-cloud-texttospeech==2.17.2
elevenlabs==0.2.27
pyttsx3==2.90

# ===== 이미지 생성 =====
stability-sdk==0.8.4
# diffusers==0.27.0  # 로컬 SD 사용 시
# torch==2.1.0

# ===== 유틸리티 =====
click==8.1.7
python-dotenv==1.0.1
pillow==10.4.0
requests==2.32.3

# ===== 데이터베이스 =====
sqlalchemy==2.0.35

# ===== 서버 (선택) =====
fastapi==0.115.5
uvicorn==0.32.1
```

---

## 🎯 Claude Code 실행 프롬프트

위 명세서에 따라 프로젝트를 단계별로 구현해주세요.

**핵심 특징:**
- **Gemini API 무료 지원** (테스트 및 저비용 운영)
- **Claude API 선택적 지원** (고품질 필요 시)
- **자동 폴백** (Gemini 실패 시 Claude로)
- **로컬 중심** (비용 최소화)

**Phase 순서:**

### Phase 1: AI 서비스 통합 (1일) ⭐
1. AIService 클래스 구현 (Gemini + Claude 통합)
2. 환경 변수 설정
3. 자동 폴백 로직
4. 사용량 추적

### Phase 2: 트렌드 분석 + 대본 생성 (1-2일)
5. YouTube Data API 통합
6. Gemini로 트렌드 분석
7. Gemini/Claude로 대본 생성
8. A/B 테스트 버전 생성

### Phase 3: TTS + 배경음악 (2-3일)
9. TTS 다중 제공자 지원
10. 타임스탬프 기반 분할
11. 배경음악 라이브러리
12. 음성+음악 믹싱

### Phase 4: 영상 제작 (3-4일)
13. MoviePy 비디오 합성
14. 자막 오버레이
15. 숏폼/롱폼 크롭
16. 썸네일 생성

### Phase 5: 업로드 (1-2일)
17. YouTube OAuth
18. Gemini로 메타데이터 생성
19. 업로드 로직
20. 진행률 표시

### Phase 6: CLI 통합 (1일)
21. Click CLI 구현
22. 모든 명령어 통합
23. AI Provider 선택 옵션
24. 사용량 통계 표시

### Phase 7: 테스트 & 문서화 (1일)
25. 예제 스크립트
26. README 작성
27. .env.example
28. 문제 해결 가이드

**시작해주세요!**

---

## 💡 Gemini 사용 팁

### 무료 할당량 최대 활용

```python
# 1. 캐싱 활용 (동일한 트렌드 분석 재사용)
# 2. 배치 처리 (대본 여러 개 한 번에)
# 3. 실패 시 재시도 (일시적 오류 대응)
```

### Claude로 업그레이드가 필요한 경우

- 대본 품질이 매우 중요한 프리미엄 채널
- 복잡한 스토리텔링 요구
- 브랜드 톤앤매너가 엄격한 경우

### 하이브리드 전략

```bash
# 일반 영상: Gemini (무료)
python main.py full-automation --ai gemini

# 중요 영상: Claude (유료)
python main.py full-automation --ai claude
```

---

**작성일**: 2025년 12월  
**버전**: 2.1  
**업데이트**: Gemini API 통합 (무료!)  
**라이선스**: MIT
