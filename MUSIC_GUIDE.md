# 무료 배경음악 다운로드 가이드

영상 제작에 사용할 수 있는 **저작권 걱정 없는** 무료 음악을 다운로드하는 방법입니다.

## 📁 음악 폴더 구조

```
music/
├── youtube_audio_library/
│   ├── ambient/          # 차분한 배경음악
│   ├── electronic/       # 전자음악
│   ├── cinematic/        # 영화 같은 웅장한 음악
│   └── upbeat/           # 활기찬 음악
└── free_music_archive/
    ├── jazz/             # 재즈
    ├── classical/        # 클래식
    └── indie/            # 인디 음악
```

## 🎵 추천 무료 음악 사이트

### 1. **YouTube Audio Library** (최고 추천!) ⭐⭐⭐⭐⭐

**장점:**
- ✅ 100% 무료
- ✅ 저작권 걱정 없음 (YouTube에서 공식 제공)
- ✅ 상업적 사용 가능
- ✅ 고품질 MP3 파일
- ✅ 장르별 분류

**다운로드 방법:**
1. [YouTube Audio Library](https://studio.youtube.com/channel/UC/music) 접속
2. YouTube Studio 로그인 필요
3. 좌측 메뉴 → "오디오 라이브러리" 클릭
4. 장르별로 필터링 후 다운로드

**추천 장르:**
- **Ambient** → `music/youtube_audio_library/ambient/`
- **Electronic** → `music/youtube_audio_library/electronic/`
- **Cinematic** → `music/youtube_audio_library/cinematic/`
- **Pop** → `music/youtube_audio_library/upbeat/`

---

### 2. **Pixabay Music** ⭐⭐⭐⭐⭐

**장점:**
- ✅ 완전 무료
- ✅ 저작권 표시 불필요
- ✅ 상업적 사용 가능
- ✅ 회원가입 없이 다운로드 가능

**다운로드 방법:**
1. [Pixabay Music](https://pixabay.com/music/) 접속
2. 검색창에 원하는 분위기 입력 (예: "calm", "energetic")
3. 다운로드 버튼 클릭

**추천 키워드:**
- "calm background" → ambient
- "corporate" → professional
- "upbeat" → upbeat
- "epic" → cinematic

---

### 3. **Free Music Archive** ⭐⭐⭐⭐

**장점:**
- ✅ 다양한 장르
- ✅ Creative Commons 라이선스
- ✅ 고품질 음원

**주의사항:**
- ⚠️ 라이선스 확인 필요 (일부는 저작권 표시 요구)
- ✅ "CC0" 라이선스 음악 선택 권장

**다운로드 방법:**
1. [Free Music Archive](https://freemusicarchive.org/) 접속
2. "Genres" → 원하는 장르 선택
3. "License" → "CC0 (Public Domain)" 필터링
4. 다운로드

**추천 장르:**
- Jazz → `music/free_music_archive/jazz/`
- Classical → `music/free_music_archive/classical/`
- Indie → `music/free_music_archive/indie/`

---

### 4. **Incompetech** (Kevin MacLeod) ⭐⭐⭐⭐

**장점:**
- ✅ 방대한 라이브러리
- ✅ 유튜버들이 많이 사용
- ✅ 무료 사용 가능 (저작권 표시 필요)

**다운로드 방법:**
1. [Incompetech](https://incompetech.com/music/royalty-free/) 접속
2. "Browse" → 장르 선택
3. 다운로드 (MP3 형식)

**크레딧 표시:**
```
Music: [곡명] by Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 3.0
```

---

### 5. **Bensound** ⭐⭐⭐⭐

**장점:**
- ✅ 고품질 음악
- ✅ 깔끔한 인터페이스
- ✅ 상업적 사용 가능 (크레딧 표시 시)

**다운로드 방법:**
1. [Bensound](https://www.bensound.com/) 접속
2. "Royalty Free Music" 클릭
3. 원하는 곡 다운로드

**크레딧 표시:**
```
Music: www.bensound.com
```

---

## 📥 빠른 시작 가이드

### 1단계: 음악 다운로드

가장 빠른 방법:
1. **Pixabay Music** 접속 (회원가입 불필요)
2. 다음 키워드로 검색:
   - "calm background music" (3-5곡)
   - "upbeat background music" (3-5곡)
   - "cinematic" (2-3곡)
3. MP3 파일 다운로드

### 2단계: 파일 배치

다운로드한 음악을 적절한 폴더에 복사:

```bash
# Windows
copy calm*.mp3 music\youtube_audio_library\ambient\
copy upbeat*.mp3 music\youtube_audio_library\upbeat\
copy cinematic*.mp3 music\youtube_audio_library\cinematic\

# Linux/Mac
cp calm*.mp3 music/youtube_audio_library/ambient/
cp upbeat*.mp3 music/youtube_audio_library/upbeat/
cp cinematic*.mp3 music/youtube_audio_library/cinematic/
```

### 3단계: 확인

음악이 제대로 추가되었는지 확인:

```bash
python local_cli/main.py list-music
```

---

## 🎼 스타일별 추천 음악

### Short Trendy (숏폼)
- 장르: **Upbeat, Electronic**
- 분위기: 활기차고 트렌디한
- 길이: 30-60초

### Long Educational (교육)
- 장르: **Ambient, Classical**
- 분위기: 차분하고 집중할 수 있는
- 길이: 5-15분

### Long Storytelling (스토리텔링)
- 장르: **Cinematic, Ambient**
- 분위기: 감동적이고 몰입감 있는
- 길이: 10-20분

---

## ⚖️ 저작권 안전 가이드

### ✅ 안전한 사용
1. **YouTube Audio Library** - 100% 안전
2. **Pixabay** - 100% 안전
3. **CC0 (Public Domain)** 라이선스 - 100% 안전

### ⚠️ 주의 필요
1. **Creative Commons BY** - 크레딧 표시 필요
2. **Creative Commons BY-SA** - 크레딧 + 동일 라이선스
3. **Creative Commons BY-NC** - 비상업적 사용만 가능 (수익화 X)

### ❌ 사용 금지
1. "All Rights Reserved" 표시 음악
2. 라이선스 정보가 없는 음악
3. 무단 배포된 음악

---

## 🚀 CLI 명령어

### 음악 폴더 구조 생성
```bash
python local_cli/main.py setup-music
```

### 사용 가능한 음악 목록 확인
```bash
python local_cli/main.py list-music
```

---

## 💡 팁

### 1. 파일명 규칙
음악 파일 이름을 알아보기 쉽게:
```
calm-piano-01.mp3
upbeat-guitar-02.mp3
cinematic-epic-03.mp3
```

### 2. 길이 확인
영상 길이보다 긴 음악을 선택하세요.
- 30초 영상 → 1분 이상 음악
- 5분 영상 → 6-7분 음악

### 3. 볼륨 조절
배경음악은 음성보다 낮게 (약 20-30%):
```python
# video_producer.py에서 자동 조절됨
voice_volume=1.0
music_volume=0.25
```

### 4. 장르 믹스
다양한 장르를 준비하면 영상에 맞춰 선택 가능:
- 차분한 영상: ambient, classical
- 활기찬 영상: upbeat, electronic
- 감동적인 영상: cinematic

---

## 📚 추가 자료

- [YouTube Copyright Basics](https://support.google.com/youtube/answer/2797466)
- [Creative Commons 라이선스 이해하기](https://creativecommons.org/licenses/)
- [무료 음악 사용 가이드](https://www.youtube.com/audiolibrary/music)

---

**작성일**: 2025년 12월
**업데이트**: 최신 무료 음악 사이트 반영
**라이선스**: 이 문서는 자유롭게 사용 가능합니다
