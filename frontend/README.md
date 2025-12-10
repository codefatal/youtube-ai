# YouTube AI - Web UI

Next.js 14 + TypeScript + Tailwind CSS로 구현된 웹 인터페이스

## 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Data Fetching**: SWR

## 설치

```bash
npm install
```

## 실행

```bash
# 개발 모드
npm run dev

# 프로덕션 빌드
npm run build
npm start
```

## 환경 변수

`.env.local` 파일을 생성하고 다음 설정:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 프로젝트 구조

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx           # 대시보드 (/)
│   ├── trends/            # 트렌드 분석
│   ├── scripts/           # 대본 생성
│   ├── videos/            # 영상 제작
│   ├── upload/            # 업로드
│   ├── automation/        # 전체 자동화
│   ├── costs/             # 비용 관리
│   ├── settings/          # 설정
│   ├── layout.tsx         # 루트 레이아웃
│   └── globals.css        # 전역 스타일
├── components/            # 재사용 컴포넌트
│   ├── Sidebar.tsx        # 사이드바
│   └── StatsCard.tsx      # 통계 카드
├── public/                # 정적 파일
└── package.json
```

## 주요 페이지

- `/` - 대시보드
- `/trends` - 트렌드 분석
- `/scripts` - 대본 생성
- `/automation` - 전체 자동화
- `/settings` - 설정

## 개발 가이드

### 새 페이지 추가

```bash
# app/ 디렉토리에 새 폴더 생성
mkdir app/new-page

# page.tsx 파일 생성
# app/new-page/page.tsx
```

### API 호출

```typescript
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/api/endpoint`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }
)
```

## 배포

### Vercel (권장)

```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
vercel
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

CMD ["npm", "start"]
```

## 문제 해결

### 백엔드 연결 안됨

백엔드 서버가 http://localhost:8000에서 실행 중인지 확인

### CORS 오류

backend/main.py의 CORS 설정 확인

## 라이선스

MIT
