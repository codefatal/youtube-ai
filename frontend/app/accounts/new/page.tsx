'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewAccountPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    channel_name: '',
    channel_type: 'INFO',
    upload_schedule: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/accounts/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (data.success) {
        alert(`계정이 생성되었습니다: ${data.data.channel_name}`);
        router.push('/accounts');
      } else {
        throw new Error(data.detail || '계정 생성 실패');
      }
    } catch (error) {
      alert(`오류: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <Link
        href="/accounts"
        className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-6"
      >
        <ArrowLeft size={20} />
        계정 목록으로 돌아가기
      </Link>

      <h1 className="text-3xl font-bold text-white mb-8">
        ➕ 새 계정 추가
      </h1>

      <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-6 space-y-6">
        {/* 채널 이름 */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            채널 이름 *
          </label>
          <input
            type="text"
            required
            value={formData.channel_name}
            onChange={(e) => setFormData({ ...formData, channel_name: e.target.value })}
            placeholder="예: 내 YouTube 채널"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-blue-500 focus:outline-none"
          />
        </div>

        {/* 채널 타입 */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            채널 타입 *
          </label>
          <select
            required
            value={formData.channel_type}
            onChange={(e) => setFormData({ ...formData, channel_type: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-blue-500 focus:outline-none"
          >
            <option value="INFO">정보성</option>
            <option value="HUMOR">유머</option>
            <option value="TREND">트렌드</option>
            <option value="REVIEW">리뷰</option>
            <option value="NEWS">뉴스</option>
            <option value="DAILY">일상</option>
          </select>
          <p className="mt-1 text-xs text-gray-400">
            채널 타입에 따라 AI가 콘텐츠 스타일을 자동으로 조정합니다.
          </p>
        </div>

        {/* 업로드 스케줄 (선택) */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            업로드 스케줄 (선택)
          </label>
          <input
            type="text"
            value={formData.upload_schedule}
            onChange={(e) => setFormData({ ...formData, upload_schedule: e.target.value })}
            placeholder="예: 0 10 * * * (매일 오전 10시)"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-blue-500 focus:outline-none"
          />
          <p className="mt-1 text-xs text-gray-400">
            Cron 형식으로 입력 (비워두면 수동 업로드). 예: "0 10 * * *" = 매일 오전 10시
          </p>
        </div>

        {/* 제출 버튼 */}
        <div className="pt-4 flex gap-3">
          <button
            type="button"
            onClick={() => router.push('/accounts')}
            disabled={loading}
            className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-white font-semibold disabled:opacity-50"
          >
            취소
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-semibold disabled:opacity-50"
          >
            {loading ? '생성 중...' : '계정 생성'}
          </button>
        </div>
      </form>
    </div>
  );
}
