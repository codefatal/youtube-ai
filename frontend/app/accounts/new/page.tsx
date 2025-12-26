'use client';

import React from 'react';

export default function NewAccountPage() {
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-8">
        새 계정 추가
      </h1>
      <div className="bg-gray-800 rounded-lg p-6 space-y-6">
        <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
                채널 이름
            </label>
            <input
                type="text"
                placeholder="예: 내 YouTube 채널"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
        </div>
        <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
                채널 타입
            </label>
            <select className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white">
                <option value="info">정보</option>
                <option value="humor">유머</option>
                <option value="trend">트렌드</option>
                <option value="review">리뷰</option>
                <option value="news">뉴스</option>
                <option value="daily">일상</option>
            </select>
        </div>
        <div className="pt-4">
            <button
                className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-semibold text-lg"
            >
                계정 생성 (구현 예정)
            </button>
        </div>
      </div>
    </div>
  );
}
