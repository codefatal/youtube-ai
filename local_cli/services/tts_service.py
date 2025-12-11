"""
TTS Service - 텍스트를 음성으로 변환하는 서비스
"""
import os
import re
from typing import Optional, List, Dict


class TTSService:
    """TTS (Text-To-Speech) 서비스"""

    def __init__(self, provider: str = 'gtts'):
        """
        TTS 제공자 초기화

        Args:
            provider: 'local', 'gtts', 'google', 'elevenlabs', 'azure'
        """
        self.provider = provider

        if provider == 'local':
            self._init_local()
        elif provider == 'gtts':
            self._init_gtts()
        elif provider == 'google':
            self._init_google()
        elif provider == 'elevenlabs':
            self._init_elevenlabs()
        elif provider == 'azure':
            self._init_azure()
        else:
            raise ValueError(f"지원하지 않는 TTS provider: {provider}")

    def _init_local(self):
        """pyttsx3 로컬 TTS 초기화"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
        except ImportError:
            raise ImportError("pyttsx3가 설치되지 않았습니다. pip install pyttsx3")

    def _init_gtts(self):
        """gTTS (Google Text-to-Speech) 무료 초기화"""
        try:
            from gtts import gTTS
            self.gtts_class = gTTS
        except ImportError:
            raise ImportError("gTTS가 설치되지 않았습니다. pip install gTTS")

    def _init_google(self):
        """Google Cloud TTS 초기화"""
        try:
            from google.cloud import texttospeech
            self.client = texttospeech.TextToSpeechClient()
            self.texttospeech = texttospeech
        except ImportError:
            raise ImportError("google-cloud-texttospeech가 설치되지 않았습니다. pip install google-cloud-texttospeech")

    def _init_elevenlabs(self):
        """ElevenLabs TTS 초기화"""
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY가 설정되지 않았습니다")

        try:
            from elevenlabs import generate, Voice, VoiceSettings
            self.elevenlabs_generate = generate
            self.elevenlabs_voice = Voice
            self.elevenlabs_settings = VoiceSettings
        except ImportError:
            raise ImportError("elevenlabs가 설치되지 않았습니다. pip install elevenlabs")

    def _init_azure(self):
        """Azure TTS 초기화"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            self.speech_config = speechsdk.SpeechConfig(
                subscription=os.getenv('AZURE_SPEECH_KEY'),
                region=os.getenv('AZURE_REGION')
            )
            self.speechsdk = speechsdk
        except ImportError:
            raise ImportError("azure-cognitiveservices-speech가 설치되지 않았습니다. pip install azure-cognitiveservices-speech")

    def generate_speech(
        self,
        script_text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 0.0
    ) -> str:
        """대본을 음성으로 변환"""

        print(f"🎤 {self.provider}로 음성 생성 중...")

        if self.provider == 'local':
            return self._generate_local(script_text, output_path, speed)
        elif self.provider == 'gtts':
            return self._generate_gtts(script_text, output_path, speed)
        elif self.provider == 'google':
            return self._generate_google(script_text, output_path, voice_id, speed, pitch)
        elif self.provider == 'elevenlabs':
            return self._generate_elevenlabs(script_text, output_path, voice_id)
        elif self.provider == 'azure':
            return self._generate_azure(script_text, output_path, voice_id, speed, pitch)

    def _generate_local(self, text: str, output_path: str, speed: float) -> str:
        """pyttsx3로 로컬 생성 (무료, 품질 낮음)"""
        self.engine.setProperty('rate', 150 * speed)
        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
        print(f"✅ 음성 생성 완료: {output_path}")
        return output_path

    def _generate_gtts(self, text: str, output_path: str, speed: float) -> str:
        """gTTS로 생성 (무료, 좋은 품질)"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 한글 감지
        lang = 'ko' if any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in text) else 'en'

        tts = self.gtts_class(text=text, lang=lang, slow=(speed < 0.9))
        tts.save(output_path)
        print(f"✅ 음성 생성 완료: {output_path}")
        return output_path

    def _generate_google(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str],
        speed: float,
        pitch: float
    ) -> str:
        """Google Cloud TTS (추천 - 가성비)"""
        synthesis_input = self.texttospeech.SynthesisInput(text=text)

        voice = self.texttospeech.VoiceSelectionParams(
            language_code='ko-KR',  # 또는 'en-US'
            name=voice_id or 'ko-KR-Standard-A',
            ssml_gender=self.texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = self.texttospeech.AudioConfig(
            audio_encoding=self.texttospeech.AudioEncoding.MP3,
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

        print(f"✅ 음성 생성 완료: {output_path}")
        return output_path

    def _generate_elevenlabs(self, text: str, output_path: str, voice_id: Optional[str]) -> str:
        """ElevenLabs TTS (최고 품질)"""
        audio = self.elevenlabs_generate(
            text=text,
            voice=self.elevenlabs_voice(
                voice_id=voice_id or "21m00Tcm4TlvDq8ikWAM",  # Rachel
                settings=self.elevenlabs_settings(
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

        print(f"✅ 음성 생성 완료: {output_path}")
        return output_path

    def _generate_azure(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str],
        speed: float,
        pitch: float
    ) -> str:
        """Azure TTS"""
        audio_config = self.speechsdk.audio.AudioOutputConfig(filename=output_path)

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

        synthesizer = self.speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )

        result = synthesizer.speak_ssml_async(ssml).get()
        print(f"✅ 음성 생성 완료: {output_path}")
        return output_path

    def generate_with_timestamps(
        self,
        script_with_timestamps: str,
        output_dir: str
    ) -> List[Dict]:
        """타임스탬프 포함 대본을 여러 오디오 파일로 분할"""

        print(f"🎤 타임스탬프 기반 음성 생성 중...")

        os.makedirs(output_dir, exist_ok=True)

        # [00:05] 패턴으로 분할
        segments = re.split(r'\[(\d{2}:\d{2})\]', script_with_timestamps)

        audio_files = []
        for i in range(1, len(segments), 2):
            timestamp = segments[i]
            text = segments[i+1].strip() if i+1 < len(segments) else ""

            if text:
                output_path = os.path.join(output_dir, f"segment_{i//2}.mp3")
                self.generate_speech(text, output_path)

                # 오디오 길이 측정
                duration = self._get_audio_duration(output_path)

                audio_files.append({
                    'timestamp': timestamp,
                    'text': text,
                    'audio_path': output_path,
                    'duration': duration
                })

        print(f"✅ {len(audio_files)}개 세그먼트 생성 완료")
        return audio_files

    def _get_audio_duration(self, audio_path: str) -> float:
        """오디오 길이 가져오기 (FFprobe 또는 MoviePy 사용)"""

        # 방법 1: FFprobe 사용 (가장 빠름)
        try:
            import subprocess
            import os

            # imageio-ffmpeg에서 ffprobe 경로 가져오기
            try:
                from imageio_ffmpeg import get_ffmpeg_exe
                ffmpeg_path = get_ffmpeg_exe()
                # Windows: ffmpeg.exe → ffprobe.exe
                # Linux/Mac: ffmpeg → ffprobe
                ffmpeg_dir = os.path.dirname(ffmpeg_path)
                ffmpeg_name = os.path.basename(ffmpeg_path)
                ffprobe_name = ffmpeg_name.replace('ffmpeg', 'ffprobe')
                ffprobe_path = os.path.join(ffmpeg_dir, ffprobe_name)

                # ffprobe가 실제로 존재하는지 확인
                if not os.path.exists(ffprobe_path):
                    raise FileNotFoundError(f"ffprobe를 찾을 수 없습니다: {ffprobe_path}")
            except Exception as e:
                # 시스템 PATH에서 ffprobe 찾기
                ffprobe_path = 'ffprobe'

            cmd = [
                ffprobe_path,
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
            print(f"✅ 오디오 길이 측정 성공 (ffprobe): {duration:.2f}초")
            return duration
        except Exception as e:
            print(f"⚠️ FFprobe 실패: {e}")

        # 방법 2: MoviePy 사용 (fallback)
        try:
            from moviepy import AudioFileClip
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            print(f"✅ 오디오 길이 측정 성공 (MoviePy): {duration:.2f}초")
            return duration
        except Exception as e:
            print(f"⚠️ MoviePy 실패: {e}")

        # 방법 3: 기본값 사용
        print(f"⚠️ 모든 방법 실패, 기본값 5초 사용")
        return 5.0
