# AI 유튜브 자동 제작 시스템 - 로컬 개발 환경 가이드

> Python 기반 프로젝트를 위한 최적의 IDE, 플러그인, 개발 도구 추천

---

## 🎯 IDE 추천 순위

### 1️⃣ **VS Code (Visual Studio Code)** - 최고 추천 ⭐⭐⭐⭐⭐

**왜 VS Code인가?**
- ✅ **완전 무료** (오픈소스)
- ✅ **가벼움** (500MB 정도, 빠른 실행)
- ✅ **Python 지원 최고** (Pylance, 자동완성, 디버깅)
- ✅ **확장성** (수천 개의 플러그인)
- ✅ **터미널 통합** (CLI 실행 편리)
- ✅ **Git 통합** (버전 관리 쉬움)
- ✅ **리소스 효율적** (RAM 1-2GB)

**다운로드:**
```
https://code.visualstudio.com/
```

**설치 후 설정:**
```bash
# VS Code 실행 후
# 1. Python 설치 확인
python --version

# 2. 가상환경 생성
python -m venv venv

# 3. VS Code에서 Python 인터프리터 선택
# Ctrl+Shift+P (Windows) / Cmd+Shift+P (Mac)
# "Python: Select Interpreter" 검색
# ./venv/Scripts/python.exe (Windows) 또는 ./venv/bin/python (Mac/Linux) 선택
```

---

### 2️⃣ **PyCharm Community Edition** - 대안 ⭐⭐⭐⭐

**장점:**
- Python 전용 IDE (최적화)
- 강력한 디버깅
- 자동 리팩토링
- 데이터베이스 도구 내장

**단점:**
- 무거움 (2GB+ RAM)
- 시작 속도 느림
- 무료 버전은 웹 개발 기능 제한

**추천 대상:**
- 대용량 Python 프로젝트
- 고급 디버깅 필요
- 강력한 PC (RAM 8GB+)

**다운로드:**
```
https://www.jetbrains.com/pycharm/download/
```

---

### 3️⃣ **Cursor** - AI 코딩 도우미 ⭐⭐⭐⭐

**특징:**
- VS Code 기반 + AI 통합
- Claude/GPT와 대화하며 코딩
- 코드 자동 완성 강력
- **유료** ($20/월)

**추천 대상:**
- AI 도움 받으며 개발하고 싶은 경우
- 빠른 프로토타이핑
- 초보자

**다운로드:**
```
https://cursor.sh/
```

---

## 🔌 필수 VS Code 플러그인 (Python 프로젝트용)

### 📦 기본 Python 개발

#### 1. **Python** (Microsoft) ⭐⭐⭐⭐⭐
**설치 ID:** `ms-python.python`

**기능:**
- Python 언어 지원
- IntelliSense (자동완성)
- 린팅 (코드 검사)
- 디버깅
- Jupyter 노트북 지원

**설치:**
```
Ctrl+Shift+X → "Python" 검색 → 설치
```

---

#### 2. **Pylance** (Microsoft) ⭐⭐⭐⭐⭐
**설치 ID:** `ms-python.vscode-pylance`

**기능:**
- 빠른 타입 체킹
- 자동 import 정리
- 코드 탐색 개선
- 함수 시그니처 힌트

**자동으로 Python 플러그인과 함께 설치됨**

---

#### 3. **Python Indent** ⭐⭐⭐⭐
**설치 ID:** `KevinRose.vsc-python-indent`

**기능:**
- Python 들여쓰기 자동 수정
- 코드 블록 자동 정렬

---

#### 4. **autoDocstring** ⭐⭐⭐⭐
**설치 ID:** `njpwerner.autodocstring`

**기능:**
- 함수에 자동으로 독스트링 생성
- 여러 독스트링 형식 지원 (Google, NumPy, Sphinx)

**사용법:**
```python
def generate_script(keywords, duration):
    """
    # 여기서 Ctrl+Shift+2 또는 """+ Enter
    # 자동으로 독스트링 템플릿 생성
    """
    pass
```

---

### 🎨 코드 품질 & 포맷팅

#### 5. **Black Formatter** ⭐⭐⭐⭐⭐
**설치 ID:** `ms-python.black-formatter`

**기능:**
- Python 코드 자동 포맷팅
- PEP 8 스타일 가이드 준수
- 저장 시 자동 포맷팅

**설정 (settings.json):**
```json
{
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

---

#### 6. **Ruff** ⭐⭐⭐⭐⭐
**설치 ID:** `charliermarsh.ruff`

**기능:**
- 초고속 Python 린터 (Flake8, isort 대체)
- 자동 import 정리
- 사용하지 않는 변수 감지

**설정 (settings.json):**
```json
{
    "ruff.lint.args": ["--select=E,F,W"],
    "ruff.organizeImports": true
}
```

---

#### 7. **Error Lens** ⭐⭐⭐⭐
**설치 ID:** `usernamehw.errorlens`

**기능:**
- 에러/경고를 코드 라인 옆에 인라인 표시
- 실시간 피드백
- 가독성 향상

**예시:**
```python
# 에러가 있으면 빨간색으로 라인 옆에 표시
x = 1 / 0  # ⚠️ ZeroDivisionError: division by zero
```

---

### 🐛 디버깅 & 테스트

#### 8. **Python Debugger** (Microsoft) ⭐⭐⭐⭐⭐
**설치 ID:** `ms-python.debugpy`

**기능:**
- 중단점(Breakpoint) 설정
- 변수 감시
- 스택 추적
- 단계별 실행

**자동으로 Python 플러그인과 함께 설치됨**

**사용법:**
```python
# 1. 코드 라인 번호 왼쪽 클릭 → 빨간점 (중단점)
# 2. F5 키 → 디버그 시작
# 3. F10 (Step Over), F11 (Step Into)
```

---

#### 9. **Python Test Explorer** ⭐⭐⭐⭐
**설치 ID:** `LittleFoxTeam.vscode-python-test-adapter`

**기능:**
- 테스트 자동 발견
- 테스트 실행/디버그
- 테스트 결과 시각화

---

### 📁 파일 & 프로젝트 관리

#### 10. **Path Intellisense** ⭐⭐⭐⭐
**설치 ID:** `christian-kohler.path-intellisense`

**기능:**
- 파일 경로 자동완성
- import 문에서 파일 경로 제안

**예시:**
```python
from services.  # ← 여기서 자동완성 목록 표시
```

---

#### 11. **Project Manager** ⭐⭐⭐⭐
**설치 ID:** `alefragnani.project-manager`

**기능:**
- 여러 프로젝트 간 빠른 전환
- 프로젝트 즐겨찾기
- 사이드바에 프로젝트 목록

---

#### 12. **File Utils** ⭐⭐⭐
**설치 ID:** `sleistner.vscode-fileutils`

**기능:**
- 파일 복사/이동/이름변경 단축키
- 파일 생성 템플릿

---

### 🔍 검색 & 탐색

#### 13. **Better Comments** ⭐⭐⭐⭐
**설치 ID:** `aaron-bond.better-comments`

**기능:**
- 주석 색상 구분
- TODO, FIXME, NOTE 하이라이트

**예시:**
```python
# TODO: 여기 나중에 구현
# ! 중요: 여기 주의
# ? 질문: 이게 맞나?
# * 강조 포인트
```

---

#### 14. **Todo Tree** ⭐⭐⭐⭐
**설치 ID:** `Gruntfuggly.todo-tree`

**기능:**
- 프로젝트 전체 TODO 검색
- 사이드바에 TODO 목록 표시
- 클릭하면 해당 코드로 이동

---

#### 15. **Bookmarks** ⭐⭐⭐
**설치 ID:** `alefragnani.Bookmarks`

**기능:**
- 코드 라인에 북마크 설정
- 북마크 간 빠른 이동
- 북마크 목록 관리

---

### 🎨 UI & 테마

#### 16. **Material Icon Theme** ⭐⭐⭐⭐⭐
**설치 ID:** `PKief.material-icon-theme`

**기능:**
- 파일/폴더 아이콘 예쁘게
- 파일 타입 구분 쉬움

---

#### 17. **One Dark Pro** ⭐⭐⭐⭐⭐
**설치 ID:** `zhuangtongfa.Material-theme`

**기능:**
- 눈 편한 다크 테마
- 코드 가독성 향상

**대안:**
- `GitHub Theme` (깃허브 스타일)
- `Dracula Official` (드라큘라 테마)
- `Night Owl` (밤 올빼미)

---

### 🤖 AI 도우미

#### 18. **GitHub Copilot** ⭐⭐⭐⭐⭐
**설치 ID:** `GitHub.copilot`

**기능:**
- AI 코드 자동완성
- 주석으로 코드 생성
- 함수 자동 작성

**비용:**
- 학생/교사: 무료
- 개인: $10/월
- 기업: $19/월

**대안 (무료):**
- **Codeium** (`Codeium.codeium`) - 무료 AI 자동완성
- **Tabnine** (`TabNine.tabnine-vscode`) - 무료 티어

---

#### 19. **Claude Code Helper** (커스텀)
**설치 ID:** `anthropics.claude-dev`

**기능:**
- VS Code에서 Claude와 대화
- 코드 설명 요청
- 리팩토링 제안

---

### 🔧 유틸리티

#### 20. **Thunder Client** ⭐⭐⭐⭐
**설치 ID:** `rangav.vscode-thunder-client`

**기능:**
- REST API 테스트 (Postman 대체)
- VS Code 내에서 HTTP 요청
- YouTube API, Claude API 테스트용

---

#### 21. **SQLite Viewer** ⭐⭐⭐⭐
**설치 ID:** `qwtel.sqlite-viewer`

**기능:**
- SQLite 데이터베이스 뷰어
- 테이블 데이터 조회/편집
- SQL 쿼리 실행

---

#### 22. **YAML** ⭐⭐⭐⭐
**설치 ID:** `redhat.vscode-yaml`

**기능:**
- YAML 문법 하이라이트
- 자동완성
- docker-compose.yml 편집 시 필수

---

#### 23. **DotENV** ⭐⭐⭐⭐
**설치 ID:** `mikestead.dotenv`

**기능:**
- .env 파일 문법 하이라이트
- 환경 변수 구분 쉬움

---

#### 24. **Git Graph** ⭐⭐⭐⭐
**설치 ID:** `mhutchie.git-graph`

**기능:**
- Git 커밋 히스토리 시각화
- 브랜치 관계 그래프
- 커밋 상세 정보

---

#### 25. **Live Server** ⭐⭐⭐
**설치 ID:** `ritwickdey.LiveServer`

**기능:**
- HTML 파일 라이브 프리뷰
- 웹 대시보드 개발 시 유용

---

### 🐳 Docker & 배포

#### 26. **Docker** ⭐⭐⭐⭐
**설치 ID:** `ms-azuretools.vscode-docker`

**기능:**
- Dockerfile 작성 지원
- Docker 컨테이너 관리
- docker-compose.yml 편집

---

#### 27. **Remote - SSH** ⭐⭐⭐⭐
**설치 ID:** `ms-vscode-remote.remote-ssh`

**기능:**
- SSH로 원격 서버 연결
- 원격 서버에서 코드 편집
- VPS에 배포 시 유용

---

### 📊 생산성 도구

#### 28. **Code Spell Checker** ⭐⭐⭐⭐
**설치 ID:** `streetsidesoftware.code-spell-checker`

**기능:**
- 영어 철자 검사
- 변수명 오타 방지
- 주석 철자 검사

---

#### 29. **Bracket Pair Colorizer 2** ⭐⭐⭐⭐
**설치 ID:** `CoenraadS.bracket-pair-colorizer-2`

**기능:**
- 괄호 쌍 색상 구분
- 중첩된 괄호 구분 쉬움

**VS Code 최신 버전에는 기본 내장됨**

---

#### 30. **Indent Rainbow** ⭐⭐⭐
**설치 ID:** `oderwat.indent-rainbow`

**기능:**
- 들여쓰기 레벨 색상 구분
- Python 들여쓰기 구분 쉬움

---

## 📦 추천 플러그인 조합

### 🥇 최소 필수 (5개)
```
1. Python (Microsoft)
2. Pylance (Microsoft)
3. Black Formatter
4. Error Lens
5. Material Icon Theme
```

### 🥈 기본 개발 (10개)
위 5개 + 아래 5개:
```
6. Ruff
7. Path Intellisense
8. Better Comments
9. Todo Tree
10. Thunder Client (API 테스트)
```

### 🥉 완전체 (15개)
위 10개 + 아래 5개:
```
11. GitHub Copilot (또는 Codeium)
12. SQLite Viewer
13. DotENV
14. Git Graph
15. Docker
```

---

## ⚙️ VS Code 최적 설정 (settings.json)

### 설정 파일 열기
```
Ctrl+Shift+P (Windows) / Cmd+Shift+P (Mac)
→ "Preferences: Open Settings (JSON)" 검색
```

### 추천 설정
```json
{
  // ===== 에디터 기본 설정 =====
  "editor.fontSize": 14,
  "editor.fontFamily": "'Fira Code', 'Consolas', 'monospace'",
  "editor.fontLigatures": true,
  "editor.lineHeight": 22,
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "editor.wordWrap": "on",
  "editor.minimap.enabled": true,
  "editor.renderWhitespace": "boundary",
  "editor.rulers": [80, 120],
  
  // ===== 저장 시 자동 작업 =====
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit"
  },
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  
  // ===== Python 설정 =====
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.tabSize": 4
  },
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.inlayHints.functionReturnTypes": true,
  "python.analysis.inlayHints.variableTypes": true,
  
  // ===== 린팅 설정 =====
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "ruff.lint.args": ["--select=E,F,W"],
  "ruff.organizeImports": true,
  
  // ===== 터미널 설정 =====
  "terminal.integrated.fontSize": 13,
  "terminal.integrated.fontFamily": "'Fira Code', 'Consolas'",
  "terminal.integrated.defaultProfile.windows": "Command Prompt",
  
  // ===== Git 설정 =====
  "git.autofetch": true,
  "git.confirmSync": false,
  "git.enableSmartCommit": true,
  
  // ===== 파일 탐색기 설정 =====
  "explorer.confirmDelete": false,
  "explorer.confirmDragAndDrop": false,
  "explorer.compactFolders": false,
  
  // ===== 테마 & UI =====
  "workbench.colorTheme": "One Dark Pro",
  "workbench.iconTheme": "material-icon-theme",
  "workbench.startupEditor": "none",
  
  // ===== 자동완성 설정 =====
  "editor.suggestSelection": "first",
  "editor.quickSuggestions": {
    "strings": true
  },
  "editor.acceptSuggestionOnCommitCharacter": true,
  "editor.snippetSuggestions": "top",
  
  // ===== 브래킷 설정 =====
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": true,
  
  // ===== Error Lens 설정 =====
  "errorLens.enabled": true,
  "errorLens.enabledDiagnosticLevels": ["error", "warning"],
  "errorLens.fontSize": "13",
  
  // ===== 기타 =====
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/venv": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/venv": true,
    "**/__pycache__": true
  }
}
```

---

## 🎯 프로젝트 구조와 VS Code Workspace

### .vscode 폴더 설정

프로젝트 루트에 `.vscode` 폴더 생성:

```
ai-youtube-automation/
├── .vscode/
│   ├── settings.json       # 프로젝트별 설정
│   ├── launch.json         # 디버그 설정
│   ├── tasks.json          # 태스크 설정
│   └── extensions.json     # 추천 플러그인
├── local_cli/
├── ...
```

### .vscode/settings.json (프로젝트별)
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.envFile": "${workspaceFolder}/.env",
  "python.analysis.extraPaths": [
    "${workspaceFolder}/local_cli"
  ]
}
```

### .vscode/launch.json (디버그 설정)
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": true,
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Python: CLI - Full Automation",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/local_cli/main.py",
      "args": ["full-automation", "--ai", "gemini"],
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Python: CLI - Generate Script",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/local_cli/main.py",
      "args": [
        "generate-script",
        "--keywords", "AI,tech",
        "--format", "short",
        "--duration", "60",
        "--ai", "gemini"
      ],
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

### .vscode/tasks.json (태스크 설정)
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Full Automation",
      "type": "shell",
      "command": "${command:python.interpreterPath}",
      "args": [
        "local_cli/main.py",
        "full-automation",
        "--ai",
        "gemini"
      ],
      "problemMatcher": [],
      "group": {
        "kind": "build",
        "isDefault": true
      }
    },
    {
      "label": "Install Dependencies",
      "type": "shell",
      "command": "${command:python.interpreterPath}",
      "args": ["-m", "pip", "install", "-r", "requirements.txt"],
      "problemMatcher": []
    }
  ]
}
```

### .vscode/extensions.json (추천 플러그인)
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "usernamehw.errorlens",
    "christian-kohler.path-intellisense",
    "aaron-bond.better-comments",
    "Gruntfuggly.todo-tree",
    "PKief.material-icon-theme",
    "zhuangtongfa.Material-theme",
    "mikestead.dotenv",
    "rangav.vscode-thunder-client",
    "qwtel.sqlite-viewer"
  ]
}
```

---

## 🚀 빠른 시작 가이드

### 1. VS Code 설치 및 설정 (5분)

```bash
# 1. VS Code 다운로드 및 설치
https://code.visualstudio.com/

# 2. 프로젝트 폴더 열기
code ai-youtube-automation

# 3. 추천 플러그인 설치
# 좌측 하단에 "이 폴더의 추천 확장 설치" 알림 클릭
# 또는 Ctrl+Shift+X → @recommended 검색
```

### 2. Python 환경 설정 (3분)

```bash
# VS Code 터미널에서 (Ctrl+`)
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. VS Code에서 인터프리터 선택
# Ctrl+Shift+P → "Python: Select Interpreter"
# ./venv/Scripts/python.exe 선택
```

### 3. 첫 실행 (2분)

```bash
# .env 파일 생성
cp .env.example .env

# API 키 입력 (VS Code에서 .env 파일 열기)
# Gemini API 키만 필수

# CLI 테스트
python local_cli/main.py test-ai --provider gemini
```

---

## 🔥 유용한 단축키 (VS Code)

### 필수 단축키

| 기능 | Windows/Linux | Mac |
|------|---------------|-----|
| 명령 팔레트 | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| 파일 찾기 | `Ctrl+P` | `Cmd+P` |
| 전체 검색 | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| 터미널 토글 | `Ctrl+`` | `Cmd+`` |
| 사이드바 토글 | `Ctrl+B` | `Cmd+B` |
| 새 파일 | `Ctrl+N` | `Cmd+N` |
| 파일 저장 | `Ctrl+S` | `Cmd+S` |
| 모두 저장 | `Ctrl+K S` | `Cmd+K S` |
| 닫기 | `Ctrl+W` | `Cmd+W` |
| 설정 열기 | `Ctrl+,` | `Cmd+,` |

### 편집 단축키

| 기능 | Windows/Linux | Mac |
|------|---------------|-----|
| 라인 복사 | `Shift+Alt+Down` | `Shift+Option+Down` |
| 라인 이동 | `Alt+Up/Down` | `Option+Up/Down` |
| 라인 삭제 | `Ctrl+Shift+K` | `Cmd+Shift+K` |
| 다중 커서 | `Alt+Click` | `Option+Click` |
| 동일 단어 선택 | `Ctrl+D` | `Cmd+D` |
| 주석 토글 | `Ctrl+/` | `Cmd+/` |
| 블록 주석 | `Shift+Alt+A` | `Shift+Option+A` |
| 포맷팅 | `Shift+Alt+F` | `Shift+Option+F` |
| 자동완성 | `Ctrl+Space` | `Ctrl+Space` |

### 디버깅 단축키

| 기능 | 단축키 |
|------|--------|
| 디버그 시작 | `F5` |
| 중단점 토글 | `F9` |
| Step Over | `F10` |
| Step Into | `F11` |
| Step Out | `Shift+F11` |
| 계속 | `F5` |
| 중지 | `Shift+F5` |

### Python 전용 단축키

| 기능 | Windows/Linux | Mac |
|------|---------------|-----|
| 인터프리터 선택 | `Ctrl+Shift+P` → "Select Interpreter" | 동일 |
| 파일 실행 | `Ctrl+Alt+N` (Code Runner) | `Ctrl+Option+N` |
| 선택 영역 실행 | `Shift+Enter` | `Shift+Enter` |
| Import 정리 | `Shift+Alt+O` | `Shift+Option+O` |

---

## 🎨 테마 추천

### 다크 테마
1. **One Dark Pro** - 가장 인기 ⭐⭐⭐⭐⭐
2. **Dracula Official** - 뱀파이어 스타일
3. **Night Owl** - 밤 작업용
4. **Tokyo Night** - 일본 도쿄 야경 스타일
5. **Monokai Pro** - 클래식

### 라이트 테마
1. **GitHub Theme** - 깃허브 스타일
2. **Solarized Light** - 눈 편함
3. **Material Theme Lighter** - 구글 머터리얼

### 폰트 추천
```bash
# Fira Code (무료, 리가처 지원)
https://github.com/tonsky/FiraCode

# JetBrains Mono (무료, 개발자용)
https://www.jetbrains.com/lp/mono/

# Cascadia Code (무료, Microsoft)
https://github.com/microsoft/cascadia-code
```

---

## 💡 생산성 팁

### 1. 멀티 커서 활용
```python
# Alt+Click으로 여러 라인 동시 편집
variable1 = "test"
variable2 = "test"
variable3 = "test"
# → Alt+Click으로 3줄 동시 선택 → "test" 입력
```

### 2. 스니펫 사용
```python
# "def" 입력 후 Tab → 함수 템플릿
def function_name():
    pass

# "class" 입력 후 Tab → 클래스 템플릿
class ClassName:
    pass

# "if" 입력 후 Tab → if 문 템플릿
if condition:
    pass
```

### 3. 코드 접기
```python
# 함수 옆 화살표 클릭 또는 Ctrl+Shift+[
def long_function():
    # 많은 코드...
    pass  # ← 접힌 상태에서 한 줄로 표시
```

### 4. Zen Mode
```
F11 또는 Ctrl+K Z
→ 전체화면 집중 모드
→ ESC 두 번으로 나가기
```

### 5. 빠른 파일 이동
```
Ctrl+P → 파일명 입력 → Enter
예: "trend" 입력 → trend_analyzer.py 바로 열기
```

---

## 🐛 문제 해결

### Python 인터프리터가 안 보여요
```bash
# 1. Python 설치 확인
python --version

# 2. VS Code 재시작
# 3. Ctrl+Shift+P → "Python: Select Interpreter"
# 4. "Enter interpreter path" → 직접 경로 입력
```

### 가상환경이 활성화 안 돼요 (Windows)
```bash
# PowerShell 실행 정책 변경 (관리자 권한)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 다시 시도
venv\Scripts\activate
```

### 플러그인이 작동 안 해요
```bash
# 1. VS Code 재시작
# 2. 플러그인 재설치
# 3. 개발자 도구 열기 (Ctrl+Shift+I) → 콘솔 확인
```

### 자동완성이 느려요
```json
// settings.json
{
  "python.analysis.memory.keepLibraryAst": true,
  "python.analysis.indexing": true
}
```

---

## 📚 추가 학습 자료

### VS Code 공식 문서
```
https://code.visualstudio.com/docs
```

### Python in VS Code
```
https://code.visualstudio.com/docs/python/python-tutorial
```

### 단축키 치트시트
```
https://code.visualstudio.com/shortcuts/keyboard-shortcuts-windows.pdf
```

### VS Code YouTube 채널
```
https://www.youtube.com/@code
```

---

## 🎯 결론

**최종 추천 조합:**

```
IDE: VS Code
필수 플러그인 (5개):
  1. Python (Microsoft)
  2. Pylance
  3. Black Formatter
  4. Error Lens
  5. Material Icon Theme

추가 추천 (5개):
  6. Ruff
  7. Better Comments
  8. Todo Tree
  9. Thunder Client
  10. SQLite Viewer

테마: One Dark Pro
폰트: Fira Code
```

이 조합으로 **무료**로 최고의 Python 개발 환경을 만들 수 있습니다! 🚀

---

**작성일**: 2025년 12월  
**버전**: 1.0  
**대상**: Python 기반 AI 유튜브 자동 제작 프로젝트
