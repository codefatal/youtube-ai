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
