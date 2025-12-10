# PowerShell 실행 정책 오류 해결 방법

## 문제

```
npm : 이 시스템에서 스크립트를 실행할 수 없으므로 C:\Program Files\nodejs\npm.ps1 파일을 로드할 수 없습니다.
```

## 해결 방법

### 방법 1: PowerShell 실행 정책 변경 (권장)

**관리자 권한으로 PowerShell 실행:**

1. 시작 메뉴 → "PowerShell" 검색
2. 우클릭 → **"관리자 권한으로 실행"**
3. 다음 명령어 실행:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4. `Y` 입력하고 Enter

5. PowerShell 닫고 VSCode 재시작

### 방법 2: VSCode 터미널을 CMD로 변경

**`.vscode/settings.json` 수정:**

```json
{
  "terminal.integrated.defaultProfile.windows": "Command Prompt"
}
```

또는 VSCode에서:
1. `Ctrl + ,` (설정)
2. "terminal default profile" 검색
3. "Command Prompt" 선택

### 방법 3: Git Bash 사용

1. Git for Windows 설치
2. VSCode 설정에서:

```json
{
  "terminal.integrated.defaultProfile.windows": "Git Bash"
}
```

## 확인

터미널에서 다음 명령어 실행:

```powershell
npm --version
```

정상 출력되면 성공!

## 문제가 계속되면

### 임시 해결책

현재 세션에서만 허용:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 완전 초기화

```powershell
Set-ExecutionPolicy Unrestricted -Scope CurrentUser
```

⚠️ 주의: 보안 위험이 있으므로 신뢰할 수 있는 스크립트만 실행하세요.

## VSCode에서 자동 해결

재시작 후에도 문제가 있다면:

1. VSCode 완전 종료
2. 관리자 권한으로 VSCode 실행
3. 프로젝트 열기
4. 터미널에서 `npm run dev` 실행
