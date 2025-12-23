# Phase 7 완료 요약: 자동화 및 스케줄링

**완료 날짜**: 2025-12-23
**소요 시간**: 약 1.5시간
**토큰 사용률**: 26%

---

## 📋 목표

Phase 7의 목표는 **콘텐츠 생성 파이프라인의 완전 자동화**입니다:

1. GitHub Actions를 통한 클라우드 자동 실행
2. 로컬 스케줄러를 통한 온프레미스 자동 실행
3. CLI 스크립트를 통한 수동 실행
4. 환경 변수 및 문서 관리 개선

---

## ✅ 완료된 작업

### 1. GitHub Actions 워크플로우 작성 ✅

**파일**: `.github/workflows/auto_create_content.yml`

**주요 기능**:
- **자동 스케줄링**: 매일 오전 9시 (KST, cron: `0 0 * * *`) 자동 실행
- **수동 디스패치**: GitHub UI에서 수동 실행 가능
- **파라미터 입력**:
  - `topic` (주제, 선택)
  - `video_format` (shorts/landscape/square)
  - `duration` (영상 길이, 초)
  - `upload` (YouTube 업로드 여부)
- **환경 변수**: GitHub Secrets 연동 (`GEMINI_API_KEY`, `PEXELS_API_KEY` 등)
- **Python 설정**: Python 3.11, 의존성 자동 설치

**워크플로우 단계**:
```yaml
1. 저장소 체크아웃
2. Python 3.11 설정
3. 의존성 설치 (pip install -r requirements.txt)
4. 자동 실행 스크립트 실행 (scripts/auto_create.py)
5. 아티팩트 업로드 (생성된 영상, 로그)
```

**장점**:
- 서버 리소스 사용 (로컬 PC 절약)
- Git 히스토리에 실행 기록 자동 보관
- 무료 (GitHub Actions 월 2,000분 무료)

---

### 2. 자동 실행 스크립트 작성 ✅

**파일**: `scripts/auto_create.py` (~250줄)

**주요 기능**:
- **CLI 인터페이스**: `argparse` 기반 명령줄 인자 처리
- **AI 주제 생성**: 주제가 없으면 AI가 자동 생성 (트렌드 분석)
- **파라미터**:
  - `--topic`: 영상 주제 (비워두면 AI 자동 생성)
  - `--format`: 영상 포맷 (shorts, landscape, square)
  - `--duration`: 목표 길이 (초, 기본: 60)
  - `--upload` / `--no-upload`: YouTube 업로드 여부
  - `--ai-provider`: AI Provider (gemini, claude, openai)
  - `--tts-provider`: TTS Provider (gtts, elevenlabs, google_cloud)
- **진행 상황 출력**: 실시간 진행률 표시 (0-100%)
- **결과 출력**:
  - 영상 경로
  - 파일 크기
  - YouTube URL (업로드 시)
  - 에러 로그
  - 통계 (총 작업, 완료, 실패, 성공률)
- **종료 코드**: CI/CD 친화적 (0: 성공, 1: 실패, 2: 미완료, 130: 중단)

**사용 예시**:
```bash
# 기본 사용 (AI 자동 주제 생성)
python scripts/auto_create.py --upload

# 주제 지정
python scripts/auto_create.py \
  --topic "강아지 훈련 팁" \
  --format shorts \
  --duration 60 \
  --upload

# 테스트 (업로드 제외)
python scripts/auto_create.py \
  --topic "테스트 주제" \
  --no-upload
```

**특징**:
- Orchestrator를 통한 전체 파이프라인 실행
- 에러 발생 시 상세한 로그 출력
- Ctrl+C 중단 처리 (exit code 130)

---

### 3. 로컬 스케줄러 작성 ✅

**파일**: `scripts/schedule_local.py` (~148줄)

**주요 기능**:
- **스케줄 라이브러리**: Python `schedule` 라이브러리 사용
- **기본 스케줄**: 매일 오전 9시 자동 실행
- **테스트 모드**: `--test` 플래그로 즉시 실행 테스트
- **백그라운드 실행**: 무한 루프로 계속 대기 (1분마다 체크)
- **AI 주제 생성**: Planner를 통해 트렌디한 주제 자동 생성
- **자동 업로드**: 기본적으로 YouTube 업로드 활성화
- **에러 핸들링**: 예외 발생 시 traceback 출력 및 계속 실행

**사용 예시**:
```bash
# 스케줄러 시작 (매일 오전 9시 실행)
python scripts/schedule_local.py

# 테스트 (즉시 실행)
python scripts/schedule_local.py --test
```

**일일 작업 흐름**:
```python
1. ContentOrchestrator 생성
2. Planner로 트렌디한 주제 생성 (count=1, trending=True)
3. 콘텐츠 생성 (Shorts, 60초, 자동 업로드)
4. 결과 출력 (영상 경로, YouTube URL, 에러 로그)
```

**장점**:
- 로컬 PC에서 실행 (서버 불필요)
- cron/Task Scheduler 없이 Python만으로 구현
- 실행 시간 자유 조정 가능

---

### 4. 환경 변수 관리 개선 ✅

**파일**: `.env.example` (갱신)

**개선 사항**:
- **섹션 분리**: AI Provider, Stock Video, TTS, YouTube, Video Settings, Paths
- **상세한 주석**: 각 변수의 용도, 발급 URL, 필수/선택 표시
- **기본값 제공**: 대부분의 설정에 합리적인 기본값 제공
- **새로운 변수 추가**:
  - `GEMINI_MODEL`: Gemini 모델 선택 (기본: gemini-1.5-flash)
  - `AI_PROVIDER`: AI Provider 선택 (gemini, claude, openai)
  - `DEFAULT_FORMAT`: 기본 영상 포맷 (shorts, landscape, square)
  - `DEFAULT_DURATION`: 기본 영상 길이 (초)
  - `AUTO_UPLOAD`: 자동 업로드 여부 (true, false)
  - `DOWNLOAD_DIR`, `OUTPUT_DIR`, `LOG_DIR`, `DATA_DIR`: 디렉토리 경로

**필수 환경 변수**:
```bash
GEMINI_API_KEY          # AI 스크립트 생성
PEXELS_API_KEY          # 스톡 영상 (또는 PIXABAY_API_KEY)
```

**선택 환경 변수**:
```bash
ANTHROPIC_API_KEY       # Claude 사용 시
ELEVENLABS_API_KEY      # 고품질 TTS 사용 시
YOUTUBE_API_KEY         # 트렌드 분석 (업로드는 OAuth 2.0)
```

---

### 5. 의존성 업데이트 ✅

**파일**: `requirements.txt`

**추가된 패키지**:
- `pydantic>=2.0.0`: 데이터 모델 (Phase 1부터 사용하고 있었으나 명시적으로 추가)
- `schedule>=1.2.0`: 로컬 스케줄링

---

### 6. 문서 갱신 ✅

#### QUICK_REFACTOR_GUIDE.md

**업데이트 내용**:
- Phase 7 완료 상태 반영 (100%)
- Phase 8 진행 중으로 표시 (0%)
- 전체 완성도: 87.5% (7/8 Phase 완료)
- 사용 방법 섹션 추가:
  - 자동 콘텐츠 생성 (CLI)
  - 로컬 스케줄러
  - Python 코드 사용
  - GitHub Actions 설정
- 빠른 테스트 명령어 추가
- 현재 세션 통계 업데이트

#### README.md (완전 재작성)

**기존 문제**:
- 리믹스 시스템 (해외 영상 번역) 문서였음
- 새로운 "독창적 콘텐츠 생성" 시스템과 불일치

**새로운 README.md**:
- **핵심 개념**: 기존 vs 현재 비교, 전환 이유 설명
- **비용**: 완전 무료 사용 가능 강조
- **빠른 시작**: 설치, API 키 설정, 테스트
- **사용 방법**: CLI, Python 코드, GitHub Actions
- **시스템 아키텍처**:
  - 전체 파이프라인 다이어그램
  - 핵심 모듈 설명 (Planner, Asset Manager, Editor, Uploader, Orchestrator)
  - 디렉토리 구조
- **현재 상태**: Phase 1-7 완료, Phase 8 진행 중
- **예제 출력물**: Shorts, Landscape 예시
- **고급 설정**: AI Provider, TTS Provider, 영상 포맷, 진행 콜백
- **테스트**: 개별 모듈, 전체 파이프라인
- **상세 문서**: REFACTOR_PLAN.md, Phase 요약 등
- **법적 고려사항**: 100% 합법적 사용, 주의사항
- **기여 방법**, **라이선스** (MIT), **로드맵**, **성능**, **FAQ**

**총 라인 수**: ~560줄 (기존 대비 약 60% 증가)

---

## 📊 생성된 파일 목록

| 파일 | 용도 | 라인 수 |
|------|------|---------|
| `.github/workflows/auto_create_content.yml` | GitHub Actions 워크플로우 | ~80줄 |
| `scripts/auto_create.py` | CLI 자동 실행 스크립트 | ~250줄 |
| `scripts/schedule_local.py` | 로컬 스케줄러 | ~148줄 |
| `.env.example` | 환경 변수 템플릿 (갱신) | ~92줄 |
| `requirements.txt` | 의존성 목록 (갱신) | ~62줄 |
| `QUICK_REFACTOR_GUIDE.md` | 빠른 가이드 (갱신) | ~291줄 |
| `README.md` | 프로젝트 문서 (완전 재작성) | ~563줄 |
| `PHASE7_SUMMARY.md` | Phase 7 요약 (현재 파일) | ~400줄 |

**총**: 8개 파일 생성/갱신 (~1,900줄)

---

## 🎯 달성한 목표

### 1. 완전 자동화 실현 ✅

세 가지 실행 방법 제공:
- **GitHub Actions**: 클라우드 자동 실행 (서버 리소스 사용)
- **로컬 스케줄러**: 온프레미스 자동 실행 (로컬 PC)
- **CLI 스크립트**: 수동 실행 (개발, 테스트)

### 2. 유연한 설정 ✅

- 환경 변수를 통한 설정 관리
- CLI 파라미터를 통한 동적 설정
- 기본값 제공으로 최소 설정으로도 실행 가능

### 3. 사용자 친화성 ✅

- 상세한 문서 (README.md, QUICK_REFACTOR_GUIDE.md)
- 명확한 사용 예시
- 진행 상황 실시간 출력
- 에러 메시지 및 로그

### 4. CI/CD 준비 ✅

- GitHub Actions 통합
- 종료 코드 표준 준수
- 아티팩트 업로드 (영상, 로그)

---

## 🧪 테스트

### 환경 변수 테스트

```bash
# 필수 변수 확인
echo $GEMINI_API_KEY
echo $PEXELS_API_KEY

# .env 파일 확인
cat .env.example
```

### CLI 스크립트 테스트

```bash
# 도움말 확인
python scripts/auto_create.py --help

# 테스트 실행 (업로드 제외)
python scripts/auto_create.py \
  --topic "테스트 주제" \
  --format shorts \
  --duration 60 \
  --no-upload
```

### 로컬 스케줄러 테스트

```bash
# 즉시 실행 테스트
python scripts/schedule_local.py --test
```

### GitHub Actions 테스트

1. GitHub Secrets 설정 확인
2. Actions 페이지에서 "Run workflow" 클릭
3. 파라미터 입력 및 실행
4. 로그 확인 및 아티팩트 다운로드

---

## 🔧 기술적 세부사항

### 1. GitHub Actions 워크플로우

**트리거**:
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # 매일 00:00 UTC = 09:00 KST
  workflow_dispatch:
    inputs:
      topic:
        description: '영상 주제 (비워두면 AI가 자동 생성)'
        required: false
      video_format:
        type: choice
        options: [shorts, landscape, square]
        default: shorts
      duration:
        description: '영상 길이 (초)'
        default: '60'
      upload:
        type: boolean
        description: 'YouTube 업로드'
        default: false
```

**환경 변수 주입**:
```yaml
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
  PIXABAY_API_KEY: ${{ secrets.PIXABAY_API_KEY }}
  YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
```

**아티팩트 업로드**:
```yaml
- name: Upload artifacts
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: video-output
    path: |
      output/
      logs/
```

### 2. CLI 스크립트 (auto_create.py)

**argparse 설정**:
```python
parser.add_argument('--topic', type=str, default='')
parser.add_argument('--format', choices=['shorts', 'landscape', 'square'], default='shorts')
parser.add_argument('--duration', type=int, default=60)
parser.add_argument('--upload', action='store_true', default=False)
parser.add_argument('--no-upload', action='store_false', dest='upload')
parser.add_argument('--ai-provider', choices=['gemini', 'claude', 'openai'], default='gemini')
parser.add_argument('--tts-provider', choices=['gtts', 'elevenlabs', 'google_cloud'], default='gtts')
```

**진행 콜백**:
```python
def progress_callback(message: str, progress: int):
    print(f"[{progress:3d}%] {message}", flush=True)

orchestrator = ContentOrchestrator(
    config=config,
    log_file="logs/orchestrator.log",
    progress_callback=progress_callback
)
```

**종료 코드**:
```python
from core.models import ContentStatus

if job.status == ContentStatus.COMPLETED:
    sys.exit(0)  # 성공
elif job.status == ContentStatus.FAILED:
    sys.exit(1)  # 실패
else:
    sys.exit(2)  # 미완료
```

### 3. 로컬 스케줄러 (schedule_local.py)

**스케줄 설정**:
```python
import schedule

def daily_content_job():
    # ContentOrchestrator로 콘텐츠 생성
    orchestrator = ContentOrchestrator(config=config)
    job = orchestrator.create_content(topic, VideoFormat.SHORTS, 60, upload=True)

# 매일 오전 9시 실행
schedule.every().day.at("09:00").do(daily_content_job)

# 무한 루프
while True:
    schedule.run_pending()
    time.sleep(60)  # 1분마다 체크
```

**테스트 모드**:
```python
if "--test" in sys.argv:
    print("[TEST] 테스트 모드: 즉시 실행합니다...")
    daily_content_job()
    return
```

---

## 📚 사용 시나리오

### 시나리오 1: 개발자 (로컬 테스트)

```bash
# 1. API 키 설정
cp .env.example .env
# .env 파일 편집 (GEMINI_API_KEY, PEXELS_API_KEY 입력)

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 테스트 실행 (업로드 제외)
python scripts/auto_create.py \
  --topic "테스트 주제" \
  --format shorts \
  --no-upload

# 4. 결과 확인
ls output/
```

### 시나리오 2: 크리에이터 (로컬 자동 실행)

```bash
# 1. API 키 설정 (.env)
# 2. 스케줄러 시작
python scripts/schedule_local.py

# 3. 매일 오전 9시 자동 실행
# 4. 생성된 영상 확인 (output/)
# 5. YouTube 자동 업로드 (upload=True)
```

### 시나리오 3: 프로덕션 (GitHub Actions)

```bash
# 1. GitHub Secrets 설정 (GEMINI_API_KEY, PEXELS_API_KEY)
# 2. 워크플로우 파일 커밋 (.github/workflows/auto_create_content.yml)
# 3. 매일 자동 실행 (cron: 00:00 UTC)
# 4. 수동 실행 (Actions → Run workflow)
# 5. 아티팩트 다운로드 (생성된 영상, 로그)
```

### 시나리오 4: 연구자 (Python API)

```python
from core.orchestrator import ContentOrchestrator
from core.models import VideoFormat, SystemConfig

config = SystemConfig()
orchestrator = ContentOrchestrator(config=config)

# 여러 주제로 배치 생성
topics = ["AI 기초", "Python 팁", "건강 루틴"]
for topic in topics:
    job = orchestrator.create_content(topic, VideoFormat.SHORTS, 60, upload=False)
    print(f"완료: {job.output_video_path}")
```

---

## 🚀 다음 단계 (Phase 8)

Phase 7 완료로 **자동화 및 스케줄링** 목표를 100% 달성했습니다. 다음은 **Phase 8: 테스트 및 최적화**입니다:

### Phase 8 계획

1. **통합 테스트 작성**
   - 전체 파이프라인 end-to-end 테스트
   - 에러 케이스 테스트 (API 실패, 네트워크 오류 등)
   - Mock 테스트 (외부 API 의존성 제거)

2. **성능 벤치마크**
   - Shorts (60초) 생성 시간 측정
   - Landscape (300초) 생성 시간 측정
   - 메모리 사용량 프로파일링

3. **에러 케이스 처리 강화**
   - 재시도 로직 개선
   - 폴백 메커니즘 (AI Provider, Stock Video API)
   - 사용자 친화적 에러 메시지

4. **문서화 최종 업데이트**
   - API 문서 (Docstring)
   - 사용자 가이드 (튜토리얼)
   - 트러블슈팅 가이드

---

## 🎉 결론

Phase 7을 통해 YouTube AI 프로젝트는 **완전 자동화 콘텐츠 생성 시스템**으로 진화했습니다:

### 주요 성과

✅ **3가지 실행 방법** 제공 (GitHub Actions, 로컬 스케줄러, CLI)
✅ **유연한 설정 관리** (환경 변수, CLI 파라미터)
✅ **사용자 친화적 문서** (README.md 재작성, QUICK_REFACTOR_GUIDE.md 갱신)
✅ **CI/CD 준비 완료** (종료 코드, 아티팩트 업로드)
✅ **프로덕션 준비** (에러 핸들링, 로깅, 통계)

### 전체 진행률

- **완료**: Phase 1-7 (87.5%)
- **진행 중**: Phase 8 (테스트 및 최적화)
- **예상 완료**: 2025-12-30 (1주일 내)

---

**작성자**: AI Assistant
**날짜**: 2025-12-23
**다음 작업**: Phase 8 시작 (통합 테스트 작성)
