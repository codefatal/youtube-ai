'use client';

import React from 'react';

export default function JobMonitor() {
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">
        실시간 작업 모니터링
      </h3>
      <div className="space-y-4">
        <p className="text-gray-400">
          이곳에 현재 진행 중인 작업의 상태가 표시됩니다.
        </p>
        <div className="bg-gray-700 rounded-lg p-4 text-sm">
          <p>
            <span className="font-semibold text-blue-400">Job_12345:</span> 
            <span className="text-gray-300"> 영상 편집 중... (75%)</span>
          </p>
        </div>
      </div>
    </div>
  );
}
