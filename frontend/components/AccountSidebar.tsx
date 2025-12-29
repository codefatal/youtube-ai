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
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/accounts/`);
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
          <NavLink href="/jobs" active={pathname.startsWith('/jobs')}>
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
