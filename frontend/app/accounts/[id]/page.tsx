'use client';

import { useParams } from 'next/navigation';
import React from 'react';

export default function AccountDetailPage() {
  const params = useParams();
  const { id } = params;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-white mb-8">
        계정 상세 (ID: {id})
      </h1>
      <div className="bg-gray-800 rounded-lg p-6">
        <p className="text-gray-400">
          이 페이지는 계정의 상세 정보, 설정 수정, 스케줄 관리 등을 위한
          페이지입니다.
        </p>
        <p className="text-gray-400 mt-2">
          현재는 기본 구조만 구현되어 있습니다.
        </p>
      </div>
    </div>
  );
}
