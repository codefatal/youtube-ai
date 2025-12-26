# YouTube AI Automation Upgrade Plan

이 문서는 `codefatal/youtube-ai` 레포지토리를 고도화하기 위한 단계별 프롬프트 가이드입니다.
Claude Code 또는 Gemini CLI와 같은 AI 에이전트에게 순서대로 입력하여 개발을 진행하세요.

---

🏗️ Phase 1: 백엔드 구조 개편 및 DB 도입 (기반 공사)

**목표:** 파일 기반(`job_history.json`) 시스템을 RDB(SQLite/SQLAlchemy)로 전환하고, 다중 계정 관리 및 설정 저장 구조를 구현합니다.

현재 프로젝트의 `backend/`, `config/`, `data/` 디렉토리 구조와 `SystemConfig` 클래스를 분석해줘.

분석이 끝나면 다음 요구사항에 맞춰 백엔드 아키텍처를 리팩토링해줘:

1.  **데이터베이스 도입 (SQLAlchemy)**
    * 기존의 `job_history.json` 의존성을 제거하고 **SQLite** 기반의 데이터베이스를 구축해줘.
    * `backend/database.py` 및 `backend/models.py`를 생성하여 ORM 모델을 정의해줘.

2.  **멀티 계정(Multi-Account) 모델링**
    * `Account` 테이블을 생성하여 여러 유튜브 채널 정보를 저장할 수 있게 해줘.
    * **필드 구성**:
        * `id`: PK
        * `channel_name`: 채널명
        * `credentials_path`: `client_secrets.json` 경로 또는 토큰 정보
        * `channel_type`: 채널 성격 (Enum: HUMOR, TREND, INFO, REVIEW 등)
        * `default_prompt_style`: 이 채널이 선호하는 AI 프롬프트 스타일
        * `upload_schedule`: 업로드 스케줄 (Cron 포맷 또는 특정 시간 문자열)
        * `is_active`: 활성화 여부

3.  **설정(Settings) 테이블 분리**
    * 계정별로 다른 TTS 설정이나 영상 스타일을 가질 수 있도록 `AccountSettings` 테이블을 1:1 관계로 연결해줘.

4.  **API 엔드포인트 추가**
    * 계정(Account)을 생성(Create), 조회(Read), 수정(Update), 삭제(Delete)하는 REST API를 `backend/routers/accounts.py`에 구현해줘.

작업 후 `python backend/main.py` 실행 시 DB가 정상적으로 생성되는지 검증 코드를 포함해줘.

🎨 Phase 2: 미디어 엔진 고도화 (템플릿, BGM, 시간 설정)
목표: 쇼츠 템플릿 시스템, 배경음악 관리, 그리고 작동하지 않는 영상 길이 제어 로직을 수정합니다.

`core/` 디렉토리의 `AssetManager`, `Editor`, `Planner` 모듈을 수정하여 미디어 생성 기능을 강화해줘.

1.  **배경음악(BGM) 매니저 구현**
    * `assets/music` 폴더를 기준으로 동작하는 BGM 관리 로직을 추가해줘.
    * 자주 사용하는 무료 음원을 다운로드하는 기능과, DB에 저장된 영상 분위기 태그(슬픔, 신남, 긴장)에 따라 음악을 자동 매칭하는 로직을 `Editor`에 추가해줘.
    * 사용자가 특정 음악을 강제 지정할 수 있는 옵션도 필요해.

2.  **쇼츠 템플릿 시스템 (Shorts Templates)**
    * `templates/shorts/*.json` 형태로 스타일을 정의하는 시스템을 만들어줘.
    * **JSON 정의 내용**: 자막 폰트, 위치(상단/중앙/하단), 색상, 트랜지션 효과, 자막 애니메이션(Pop, Karaoke 등).
    * 기본 템플릿 3종(기본형, 다큐형, 예능형)을 생성해서 `templates/` 폴더에 넣어줘.

3.  **영상 길이(Duration) 로직 수정 (버그 픽스)**
    * 현재 프론트엔드에서 시간을 설정해도 `Planner`가 이를 무시하는 문제를 해결해줘.
    * 사용자가 지정한 시간(예: 58초)을 `Planner`의 프롬프트 컨텍스트에 강력한 제약 조건(Hard Constraint)으로 주입하여, AI가 스크립트 길이를 정확히 조절하도록 수정해줘.

4.  **수동 오버라이드**
    * AI가 검색한 영상 대신, 사용자가 업로드한 특정 로컬 비디오 파일을 배경으로 사용할 수 있도록 파라미터를 처리하는 로직을 추가해줘.

🗣️ Phase 3: ElevenLabs TTS 고도화
목표: 단순한 TTS 생성을 넘어, 상세 설정(안정성 등)과 비용 절감을 위한 캐싱 시스템을 구축합니다.

`providers/tts_provider.py` (또는 관련 파일)를 수정하여 **ElevenLabs API** 기능을 고도화해줘.

1.  **상세 파라미터 제어**
    * 단순 Voice ID 뿐만 아니라 다음 파라미터를 조절할 수 있도록 `SystemConfig`와 연동해줘.
        * `stability`: 목소리 안정성
        * `similarity_boost`: 유사도 증가
        * `style`: 스타일 과장 정도
    * 이 설정값들은 Phase 1에서 만든 DB의 `AccountSettings` 테이블에 저장되어야 해.

2.  **미리듣기(Preview) API**
    * 전체 영상을 생성하기 전에, 특정 텍스트와 설정값으로 짧은 오디오만 생성해서 반환하는 `/api/tts/preview` 엔드포인트를 만들어줘.

3.  **스마트 캐싱 (비용 절감)**
    * 동일한 텍스트와 음성 설정(Voice ID + 파라미터)인 경우, API를 호출하지 않고 저장된 파일을 재사용하도록 해시(Hash) 기반 캐싱 로직을 강화해줘.

🤖 Phase 4: 스케줄링 및 자동화 시스템
목표: 계정별 설정된 스케줄에 따라 백그라운드에서 자동으로 영상을 생성하고 업로드합니다.

백그라운드 작업 관리를 위해 `APScheduler`를 도입하고 자동화 로직을 구현해줘.

1.  **스케줄러 서비스 구현**
    * `backend/scheduler.py`를 생성해줘.
    * 앱 시작 시 DB의 `Account` 테이블을 조회하여, `is_active=True`인 계정들의 `upload_schedule` 정보를 기반으로 작업을 예약(Scheduling)해줘.
    
2.  **작업 실행 로직 (Worker)**
    * 스케줄러가 트리거될 때 실행할 `auto_generate_and_upload(account_id)` 함수를 구현해줘.
    * 이 함수는 해당 계정의 `channel_type`(유머/정보 등)을 기반으로 주제를 선정(트렌드 검색 또는 랜덤)하고, 영상 생성 -> 업로드까지의 파이프라인을 실행해야 해.

3.  **작업 이력 로깅**
    * 자동 실행된 작업의 성공/실패 여부와 로그를 DB의 `JobHistory` 테이블에 기록해줘.

🖥️ Phase 5: 프론트엔드 UI/UX 전면 개편
목표: 위에서 구현한 모든 기능을 제어할 수 있는 현대적인 웹 대시보드를 구축합니다.

`frontend/` 디렉토리의 코드를 수정하여 새로운 기능을 반영한 UI를 개발해줘. (현재 사용 중인 프레임워크 유지)

1.  **사이드바 및 계정 선택**
    * 왼쪽 사이드바에 등록된 유튜브 계정 목록을 표시하고, 계정을 클릭하면 해당 계정의 대시보드(작업 내역, 설정)로 이동하는 구조로 변경해줘.

2.  **영상 생성 페이지 (Create Video)**
    * **TTS 설정**: ElevenLabs 목소리를 선택하고 슬라이더로 안정성(Stability)을 조절하며 '미리듣기' 버튼을 누를 수 있는 패널 추가.
    * **템플릿/BGM 선택**: Phase 2에서 만든 템플릿과 배경음악을 드롭다운으로 선택하는 UI 추가.
    * **시간 설정**: 작동하도록 수정된 시간 설정(30s, 60s, Custom) UI가 백엔드에 올바른 파라미터를 보내도록 연결.

3.  **계정 관리 페이지**
    * 새로운 유튜브 계정을 추가하고, 업로드 스케줄(Cron/Time)을 설정하고, 채널 성격(유머/정보)을 지정하는 폼(Form) 페이지를 만들어줘.

4.  **디자인 폴리싱**
    * 전체적인 테마를 다크 모드 기반의 깔끔한 대시보드 스타일로 CSS/Tailwind를 수정해줘.

🧪 Phase 6: 통합 테스트 및 마무리

지금까지 구현한 기능들의 통합 테스트를 진행하고 싶어.

1.  **API 테스트**: `tests/` 폴더에 새로운 API (계정 관리, TTS 미리듣기)에 대한 테스트 코드를 작성해줘.
2.  **전체 파이프라인 점검**: 더미(Dummy) 계정을 하나 생성해서, 30초짜리 쇼츠를 생성하는 요청을 보냈을 때 DB 기록부터 영상 렌더링까지 에러 없이 진행되는지 확인하는 스크립트를 작성해줘.
3.  **README 업데이트**: 새로 추가된 기능(DB 설정, 멀티 계정, 스케줄링 등)을 포함하여 `README.md`를 최신화해줘.