'use client';

import React from 'react';

export default function ScheduleEditor() {
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">
        자동 업로드 스케줄
      </h3>
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Cron 표현식
        </label>
        <input
          type="text"
          placeholder="예: 0 9 * * *"
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white font-mono"
        />
        <p className="text-xs text-gray-400 mt-2">
          매일 오전 9시에 업로드하려면 "0 9 * * *"를 입력하세요.
        </p>
      </div>
      <div className="pt-4">
        <button className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium">
          스케줄 저장 (구현 예정)
        </button>
      </div>
    </div>
  );
}
