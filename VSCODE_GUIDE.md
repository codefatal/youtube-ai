# VSCode 사용 가이드 🎯

VSCode에서 버튼 클릭만으로 프로젝트를 실행하는 방법

## 📋 목차

- [초기 설정](#초기-설정)
- [실행 방법](#실행-방법)
- [디버깅](#디버깅)
- [유용한 단축키](#유용한-단축키)
- [추천 확장 프로그램](#추천-확장-프로그램)

## 초기 설정

### 1. VSCode에서 프로젝트 열기

```bash
# 방법 1: 터미널에서
cd D:\work\code\youtubeAI
code .

# 방법 2: VSCode에서 File > Open Folder
```

### 2. Python 인터프리터 선택

1. `Ctrl + Shift + P` 누르기
2. "Python: Select Interpreter" 검색
3. `.\venv\Scripts\python.exe` 선택

### 3. 추천 확장 프로그램 설치

프로젝트를 열면 오른쪽 하단에 "이 작업 영역에 권장되는 확장 프로그램을 설치하시겠습니까?" 알림이 뜹니다.
**"모두 설치"** 클릭!

또는 수동 설치:
1. `Ctrl + Shift + X` (확장 프로그램)
2. 다음 검색 후 설치:
   - Python
   - Pylance
   - ESLint
   - Prettier

## 실행 방법

### 🚀 원클릭 실행

#### 방법 1: Run and Debug 패널 (추천)

1. **왼쪽 사이드바에서 "Run and Debug" 아이콘** 클릭 (또는 `Ctrl + Shift + D`)
2. **실행할 구성 선택:**

   - **🌐 Full Stack (Backend + Frontend)** ⭐ 추천!
     - 백엔드와 프론트엔드를 동시에 실행
     - 웹 UI 사용 가능

   - **🚀 Backend API Server**
     - FastAPI 서버만 실행
     - http://localhost:8000

   - **⌨️ CLI - Full Automation**
     - 전체 자동화 실행 (업로드 제외)

   - **📈 CLI - Trend Analysis**
     - 트렌드 분석만 실행

   - **✍️ CLI - Generate Script**
     - 대본 생성만 실행

   - **🧪 Test AI Service**
     - AI 서비스 테스트

3. **녹색 재생 버튼** 클릭 (또는 `F5`)

#### 방법 2: 상단 메뉴바

1. `Run` > `Start Debugging` (F5)
2. 또는 `Run` > `Run Without Debugging` (Ctrl + F5)

### 📱 실행 결과 확인

**Full Stack 실행 시:**
- 터미널 1: 백엔드 (http://localhost:8000)
- 터미널 2: 프론트엔드 (http://localhost:3000)
- 브라우저에서 http://localhost:3000 자동으로 열림

## 디버깅

### 중단점 (Breakpoint) 설정

1. 코드 줄 번호 왼쪽 클릭 → 빨간 점 표시
2. `F5`로 디버깅 시작
3. 중단점에서 멈추면:
   - 변수 값 확인
   - 스텝 오버 (`F10`)
   - 스텝 인투 (`F11`)
   - 계속 (`F5`)

### 디버그 콘솔 사용

1. 디버깅 중 하단의 "Debug Console" 탭
2. Python 표현식 입력 가능
   ```python
   print(analysis)
   len(scripts)
   ```

## 유용한 단축키

### 실행 관련
- `F5` - 디버깅 시작
- `Ctrl + F5` - 디버깅 없이 실행
- `Shift + F5` - 중지
- `Ctrl + Shift + F5` - 재시작

### 편집 관련
- `Ctrl + Shift + P` - 명령 팔레트
- `Ctrl + P` - 파일 빠르게 열기
- `Ctrl + ,` - 설정
- `Ctrl + `` ` `` - 터미널 토글

### 디버깅 관련
- `F9` - 중단점 토글
- `F10` - 스텝 오버
- `F11` - 스텝 인투
- `Shift + F11` - 스텝 아웃

### 코드 탐색
- `F12` - 정의로 이동
- `Alt + F12` - 정의 미리보기
- `Shift + F12` - 참조 찾기
- `Ctrl + Click` - 정의로 이동

## Tasks (작업)

### 실행 가능한 Tasks

`Ctrl + Shift + P` → "Tasks: Run Task" 검색:

- **Start Frontend Dev Server** - 프론트엔드 개발 서버
- **Install Frontend Dependencies** - npm install
- **Build Frontend** - 프론트엔드 빌드
- **Install Python Dependencies** - pip install
- **Setup Music Folders** - 음악 폴더 생성

## 터미널 사용

### 통합 터미널 열기

1. `` Ctrl + ` `` (백틱)
2. 또는 `View` > `Terminal`

### 여러 터미널 사용

1. 터미널 패널에서 `+` 버튼
2. 또는 `Ctrl + Shift + `` ` ``

### PowerShell vs CMD

`.vscode/settings.json`에서 기본 터미널 변경:
```json
"terminal.integrated.defaultProfile.windows": "PowerShell"
```

## 문제 해결

### "Python 인터프리터를 찾을 수 없음"

1. `Ctrl + Shift + P`
2. "Python: Select Interpreter"
3. `.\venv\Scripts\python.exe` 선택

### "모듈을 찾을 수 없음"

1. 터미널에서 가상환경 활성화:
   ```bash
   .\venv\Scripts\activate
   ```
2. 의존성 재설치:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend npm 오류

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 포트 이미 사용 중

**백엔드 (8000):**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

**프론트엔드 (3000):**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## 고급 기능

### 멀티 루트 워크스페이스

여러 프로젝트를 하나의 VSCode 창에서:

1. `File` > `Add Folder to Workspace`
2. `frontend`, `backend` 폴더 추가

### 코드 스니펫

자주 사용하는 코드 패턴을 스니펫으로:

1. `Ctrl + Shift + P`
2. "Preferences: Configure User Snippets"
3. "python.json" 선택

예시:
```json
{
  "AI Service": {
    "prefix": "aiservice",
    "body": [
      "from local_cli.services.ai_service import get_ai_service",
      "",
      "ai_service = get_ai_service('$1')",
      "response = ai_service.generate_text(",
      "    prompt='$2',",
      "    max_tokens=$3",
      ")"
    ]
  }
}
```

### Git 통합

1. 왼쪽 사이드바 "Source Control" (Ctrl + Shift + G)
2. 변경 사항 확인
3. 커밋 메시지 작성
4. ✓ 버튼 클릭

## 권장 설정

### 자동 저장

`File` > `Auto Save` 활성화

또는 `settings.json`:
```json
"files.autoSave": "afterDelay"
```

### 포맷팅

저장 시 자동 포맷:
```json
"editor.formatOnSave": true
```

### Minimap

코드 오른쪽에 미니맵 표시:
```json
"editor.minimap.enabled": true
```

## 추천 테마

- **Dark+** (기본)
- **Monokai**
- **Dracula**
- **Material Theme**

변경: `Ctrl + K` → `Ctrl + T`

## 추천 워크플로우

### 1. 처음 시작할 때

1. VSCode 열기
2. `Ctrl + Shift + D` (Run and Debug)
3. "🌐 Full Stack" 선택
4. `F5` 실행
5. http://localhost:3000 접속

### 2. 코드 수정 중

1. 왼쪽에서 파일 탐색기로 파일 열기
2. 수정
3. 자동 저장됨
4. 브라우저에서 핫 리로드 확인

### 3. 디버깅 필요 시

1. 의심되는 코드에 중단점 설정 (F9)
2. `F5`로 디버깅 시작
3. 중단점에서 변수 확인
4. `F10`으로 한 줄씩 실행

## 도움말

- VSCode 공식 문서: https://code.visualstudio.com/docs
- Python in VSCode: https://code.visualstudio.com/docs/python/python-tutorial
- 단축키 치트시트: `Ctrl + K` → `Ctrl + R`

## 기타 팁

### Zen Mode

집중 모드: `Ctrl + K` → `Z`

### Split Editor

화면 분할: `Ctrl + \`

### Command Palette

모든 명령어 검색: `Ctrl + Shift + P`

### Quick Open

파일 빠르게 열기: `Ctrl + P`

**예시:**
- `main.py` 입력 → 모든 main.py 파일 표시
- `@함수명` → 현재 파일의 함수로 이동
- `:100` → 100번째 줄로 이동

---

**팁:** 첫 실행 시 "🌐 Full Stack" 구성으로 시작하는 것을 추천합니다!
