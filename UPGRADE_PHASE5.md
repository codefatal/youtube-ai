# Phase 5: 프론트엔드 UI/UX 전면 개편

**작업 기간**: 1.5주 (2026-01-24 ~ 2026-01-30)
**담당 모듈**: `frontend/`
**우선순위**: ⭐⭐⭐⭐ (높음)
**난이도**: 🔥🔥 (중)
**의존성**: Phase 1, 2, 3 완료 필수

---

## 📋 개요

Phase 1~4에서 구축한 모든 백엔드 기능(멀티 계정, BGM, TTS 설정, 스케줄링)을 제어할 수 있는 현대적인 웹 대시보드를 구축합니다. 다크 모드, 계정 선택 사이드바, 상세 설정 페이지 등을 포함합니다.

### 목표
- ✅ 계정 선택 사이드바 (멀티 계정 관리)
- ✅ 영상 생성 페이지 개선 (TTS, 템플릿, BGM 설정)
- ✅ 계정 관리 페이지 (CRUD, 스케줄 설정)
- ✅ 작업 이력 모니터링
- ✅ 다크 모드 디자인
- ✅ 모바일 반응형

---

## 🗂️ 디렉토리 구조

```
youtube-ai/frontend/
├── app/
│   ├── layout.tsx           # 🔧 MODIFY - 사이드바 추가
│   ├── page.tsx             # 🔧 MODIFY - 대시보드 개선
│   ├── accounts/
│   │   ├── page.tsx         # ✨ NEW - 계정 목록
│   │   ├── [id]/
│   │   │   └── page.tsx     # ✨ NEW - 계정 상세
│   │   └── new/
│   │       └── page.tsx     # ✨ NEW - 계정 생성
│   ├── create/
│   │   └── page.tsx         # 🔧 MODIFY - 영상 생성 개선
│   └── history/
│       └── page.tsx         # ✨ NEW - 작업 이력
├── components/
│   ├── AccountSidebar.tsx   # ✨ NEW - 계정 사이드바
│   ├── TTSSettings.tsx      # ✨ NEW - TTS 설정 컴포넌트
│   ├── TemplateSelector.tsx # ✨ NEW - 템플릿 선택
│   ├── ScheduleEditor.tsx   # ✨ NEW - 스케줄 편집기
│   └── JobMonitor.tsx       # ✨ NEW - 작업 모니터링
└── styles/
    └── globals.css          # 🔧 MODIFY - 다크 모드 추가
```

---

## 🎨 디자인 시스템

### 컬러 팔레트 (다크 모드)

```css
/* frontend/styles/globals.css */

:root {
  /* 다크 모드 기본 컬러 */
  --bg-primary: #0f172a;      /* 주 배경 */
  --bg-secondary: #1e293b;    /* 카드 배경 */
  --bg-tertiary: #334155;     /* 호버 배경 */

  --text-primary: #f1f5f9;    /* 주 텍스트 */
  --text-secondary: #94a3b8;  /* 보조 텍스트 */

  --accent-primary: #3b82f6;  /* 블루 (주요 액션) */
  --accent-success: #10b981;  /* 그린 (성공) */
  --accent-warning: #f59e0b;  /* 오렌지 (경고) */
  --accent-error: #ef4444;    /* 레드 (에러) */

  --border-color: #475569;    /* 보더 */
  --shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}

/* 스크롤바 스타일 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--border-color);
}
```

---

## 🏗️ 구현 단계

### Step 1: 계정 사이드바 (`components/AccountSidebar.tsx`)

```typescript
'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface Account {
  id: number;
  channel_name: string;
  channel_type: string;
  is_active: boolean;
}

export default function AccountSidebar() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const pathname = usePathname();

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/accounts/');
      const data = await res.json();
      setAccounts(data);
    } catch (error) {
      console.error('계정 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="w-64 h-screen bg-gray-800 border-r border-gray-700 flex flex-col">
      {/* 로고 */}
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-2xl font-bold text-blue-400">YouTube AI v4.0</h1>
        <p className="text-sm text-gray-400 mt-1">Multi-Channel Manager</p>
      </div>

      {/* 네비게이션 */}
      <nav className="flex-1 overflow-y-auto p-4">
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-gray-400 uppercase mb-3">
            일반
          </h3>
          <NavLink href="/" active={pathname === '/'}>
            📊 대시보드
          </NavLink>
          <NavLink href="/create" active={pathname === '/create'}>
            ✨ 영상 생성
          </NavLink>
          <NavLink href="/history" active={pathname === '/history'}>
            📜 작업 이력
          </NavLink>
        </div>

        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold text-gray-400 uppercase">
              계정 ({accounts.length})
            </h3>
            <Link
              href="/accounts/new"
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              + 추가
            </Link>
          </div>

          {loading ? (
            <div className="text-gray-500 text-sm">로딩 중...</div>
          ) : (
            accounts.map((account) => (
              <Link
                key={account.id}
                href={`/accounts/${account.id}`}
                className={`
                  block px-3 py-2 rounded-lg mb-1 text-sm
                  ${pathname === `/accounts/${account.id}`
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <span className="truncate">{account.channel_name}</span>
                  {account.is_active && (
                    <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                  )}
                </div>
                <span className="text-xs text-gray-400">{account.channel_type}</span>
              </Link>
            ))
          )}
        </div>
      </nav>

      {/* 설정 */}
      <div className="p-4 border-t border-gray-700">
        <Link
          href="/accounts"
          className="block px-3 py-2 rounded-lg text-sm text-gray-300 hover:bg-gray-700"
        >
          ⚙️ 계정 관리
        </Link>
      </div>
    </aside>
  );
}

// NavLink 컴포넌트
function NavLink({ href, active, children }: { href: string; active: boolean; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className={`
        block px-3 py-2 rounded-lg mb-1 text-sm
        ${active ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-700'}
      `}
    >
      {children}
    </Link>
  );
}
```

---

### Step 2: 레이아웃 수정 (`app/layout.tsx`)

```typescript
import AccountSidebar from '@/components/AccountSidebar';
import '@/styles/globals.css';

export const metadata = {
  title: 'YouTube AI v4.0 - Multi-Channel Manager',
  description: '엔터프라이즈급 YouTube 자동화 시스템',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <div className="flex h-screen">
          {/* 사이드바 */}
          <AccountSidebar />

          {/* 메인 콘텐츠 */}
          <main className="flex-1 overflow-y-auto bg-gray-900">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
```

---

### Step 3: TTS 설정 컴포넌트 (`components/TTSSettings.tsx`)

```typescript
'use client';

import React, { useState } from 'react';

interface TTSSettingsProps {
  settings: {
    provider: string;
    voiceId: string;
    stability: number;
    similarityBoost: number;
    style: number;
  };
  onChange: (settings: any) => void;
}

export default function TTSSettings({ settings, onChange }: TTSSettingsProps) {
  const [previewLoading, setPreviewLoading] = useState(false);

  const handlePreview = async () => {
    setPreviewLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/tts/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: '안녕하세요, 이것은 음성 미리듣기입니다.',
          voice_id: settings.voiceId,
          stability: settings.stability,
          similarity_boost: settings.similarityBoost,
          style: settings.style,
        }),
      });

      const blob = await res.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error('미리듣기 실패:', error);
    } finally {
      setPreviewLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 space-y-4">
      <h3 className="text-lg font-semibold text-white mb-4">🗣️ TTS 설정</h3>

      {/* Provider 선택 */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          TTS 제공자
        </label>
        <select
          value={settings.provider}
          onChange={(e) => onChange({ ...settings, provider: e.target.value })}
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
        >
          <option value="gtts">gTTS (무료)</option>
          <option value="elevenlabs">ElevenLabs (프리미엄)</option>
        </select>
      </div>

      {/* ElevenLabs 설정 */}
      {settings.provider === 'elevenlabs' && (
        <>
          {/* Voice ID */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Voice ID
            </label>
            <select
              value={settings.voiceId}
              onChange={(e) => onChange({ ...settings, voiceId: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            >
              <option value="pNInz6obpgDQGcFmaJgB">Adam (Male)</option>
              <option value="EXAVITQu4vr4xnSDxMaL">Bella (Female)</option>
              <option value="FGY2WhTYpPnrIDTdsKH5">Laura (Female)</option>
            </select>
          </div>

          {/* Stability */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              안정성 (Stability): {settings.stability.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.stability}
              onChange={(e) =>
                onChange({ ...settings, stability: parseFloat(e.target.value) })
              }
              className="w-full"
            />
            <p className="text-xs text-gray-400 mt-1">
              낮음 = 감정 풍부, 높음 = 일관성 유지
            </p>
          </div>

          {/* Similarity Boost */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              유사도 (Similarity Boost): {settings.similarityBoost.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.similarityBoost}
              onChange={(e) =>
                onChange({ ...settings, similarityBoost: parseFloat(e.target.value) })
              }
              className="w-full"
            />
          </div>

          {/* Style */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              스타일 (Style): {settings.style.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.style}
              onChange={(e) =>
                onChange({ ...settings, style: parseFloat(e.target.value) })
              }
              className="w-full"
            />
            <p className="text-xs text-gray-400 mt-1">
              0.0 = 자연스러움, 1.0 = 과장됨
            </p>
          </div>

          {/* 미리듣기 버튼 */}
          <button
            onClick={handlePreview}
            disabled={previewLoading}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium disabled:opacity-50"
          >
            {previewLoading ? '생성 중...' : '🎵 미리듣기'}
          </button>
        </>
      )}
    </div>
  );
}
```

---

### Step 4: 영상 생성 페이지 개선 (`app/create/page.tsx`)

```typescript
'use client';

import React, { useState } from 'react';
import TTSSettings from '@/components/TTSSettings';

export default function CreatePage() {
  const [topic, setTopic] = useState('');
  const [duration, setDuration] = useState(60);
  const [template, setTemplate] = useState('basic');
  const [ttsSettings, setTtsSettings] = useState({
    provider: 'gtts',
    voiceId: 'pNInz6obpgDQGcFmaJgB',
    stability: 0.5,
    similarityBoost: 0.75,
    style: 0.0,
  });
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/videos/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic || null,
          format: 'shorts',
          duration,
          upload: false,
          template,
          tts_settings: ttsSettings,
        }),
      });

      const data = await res.json();
      alert(`영상 생성 시작! Job ID: ${data.job_id}`);
    } catch (error) {
      console.error('영상 생성 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-8">✨ 영상 생성</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 왼쪽: 기본 설정 */}
        <div className="space-y-6">
          {/* 주제 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              주제 (비워두면 AI가 자동 생성)
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="예: Python 프로그래밍 팁"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>

          {/* 길이 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              영상 길이: {duration}초
            </label>
            <input
              type="range"
              min="30"
              max="180"
              step="10"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>30초</span>
              <span>180초</span>
            </div>
          </div>

          {/* 템플릿 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              템플릿
            </label>
            <select
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            >
              <option value="basic">기본형</option>
              <option value="documentary">다큐형</option>
              <option value="entertainment">예능형</option>
            </select>
          </div>
        </div>

        {/* 오른쪽: TTS 설정 */}
        <div>
          <TTSSettings settings={ttsSettings} onChange={setTtsSettings} />
        </div>
      </div>

      {/* 생성 버튼 */}
      <button
        onClick={handleCreate}
        disabled={loading}
        className="mt-8 w-full px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-semibold text-lg disabled:opacity-50"
      >
        {loading ? '생성 중...' : '🎬 영상 생성 시작'}
      </button>
    </div>
  );
}
```

---

### Step 5: 계정 관리 페이지 (`app/accounts/page.tsx`)

```typescript
'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

interface Account {
  id: number;
  channel_name: string;
  channel_type: string;
  upload_schedule: string | null;
  is_active: boolean;
  created_at: string;
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/accounts/');
      const data = await res.json();
      setAccounts(data);
    } catch (error) {
      console.error('계정 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await fetch(`http://localhost:8000/api/accounts/${id}`, {
        method: 'DELETE',
      });
      fetchAccounts();
    } catch (error) {
      console.error('삭제 실패:', error);
    }
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">⚙️ 계정 관리</h1>
        <Link
          href="/accounts/new"
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium"
        >
          + 새 계정 추가
        </Link>
      </div>

      {loading ? (
        <div className="text-gray-400">로딩 중...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {accounts.map((account) => (
            <div key={account.id} className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-white">
                    {account.channel_name}
                  </h3>
                  <p className="text-sm text-gray-400">{account.channel_type}</p>
                </div>
                {account.is_active && (
                  <span className="px-2 py-1 bg-green-600 rounded text-xs text-white">
                    활성
                  </span>
                )}
              </div>

              {account.upload_schedule && (
                <p className="text-sm text-gray-300 mb-4">
                  📅 스케줄: {account.upload_schedule}
                </p>
              )}

              <div className="flex gap-2">
                <Link
                  href={`/accounts/${account.id}`}
                  className="flex-1 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-center text-sm text-white"
                >
                  상세
                </Link>
                <button
                  onClick={() => handleDelete(account.id)}
                  className="px-3 py-2 bg-red-600 hover:bg-red-500 rounded text-sm text-white"
                >
                  삭제
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## ✅ 테스트 체크리스트

### 1. UI 렌더링 테스트

```bash
# 프론트엔드 서버 시작
cd frontend
npm run dev

# 브라우저에서 확인:
# - http://localhost:3000/ (대시보드)
# - http://localhost:3000/create (영상 생성)
# - http://localhost:3000/accounts (계정 관리)
```

### 2. 사이드바 테스트

- [ ] 계정 목록이 정상적으로 로드됨
- [ ] 계정 클릭 시 페이지 이동
- [ ] 활성 계정에 초록색 점 표시
- [ ] 스크롤 동작 확인

### 3. TTS 설정 테스트

- [ ] 슬라이더 조작 시 값 변경
- [ ] 미리듣기 버튼 클릭 시 음성 재생
- [ ] ElevenLabs/gTTS 전환 시 UI 변경

### 4. 반응형 테스트

```bash
# 다양한 화면 크기에서 테스트
- 데스크톱 (1920x1080)
- 태블릿 (768x1024)
- 모바일 (375x667)
```

---

## 📊 성공 기준

- [x] 계정 선택 UI 작동 (사이드바에서 계정 전환)
- [x] 다크 모드 적용 (모든 페이지)
- [x] 모바일 반응형 지원 (375px 이상)
- [x] TTS 미리듣기 1초 이내 응답
- [x] 모든 API 연동 작동

---

## 🚀 커밋 전략

```bash
# Step 1-2
git add frontend/components/AccountSidebar.tsx frontend/app/layout.tsx frontend/styles/globals.css
git commit -m "Phase 5: Add account sidebar and dark mode layout"

# Step 3-4
git add frontend/components/TTSSettings.tsx frontend/app/create/page.tsx
git commit -m "Phase 5: Improve video creation page with TTS settings"

# Step 5
git add frontend/app/accounts/
git commit -m "Phase 5: Add account management pages"

# 나머지 컴포넌트
git add frontend/components/
git commit -m "Phase 5: Add remaining components (TemplateSelector, ScheduleEditor, JobMonitor)"
```

---

## ⚠️ 주의사항

1. **API URL 설정**
   - 프로덕션: 환경변수로 백엔드 URL 설정
   - 개발: `http://localhost:8000`

2. **CORS 설정**
   - FastAPI `main.py`에 CORS 미들웨어 추가 필요

3. **타입 안전성**
   - TypeScript 인터페이스 정의 권장

---

## 📚 다음 단계

Phase 5 완료 후:
- **Phase 6**: 통합 테스트, README 업데이트, 배포 준비

**Phase 6로 이동**: [UPGRADE_PHASE6.md](./UPGRADE_PHASE6.md)

---

**작성일**: 2025-12-26
**버전**: 1.0
**상태**: Ready for Implementation
