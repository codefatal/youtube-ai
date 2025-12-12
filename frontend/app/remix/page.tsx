'use client'

export default function RemixPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">리믹스</h1>
      <p className="text-gray-600 mb-6">영상 + 번역 자막 합성</p>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <p className="text-blue-900 font-semibold mb-2">자동 리믹스 시스템</p>
        <p className="text-blue-700 text-sm mb-4">
          리믹스는 배치 처리 페이지에서 자동으로 실행됩니다.
        </p>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• 영상 검색 → 자동 다운로드</li>
          <li>• 자막 자동 번역</li>
          <li>• 영상 + 자막 자동 합성</li>
          <li>• 메타데이터 자동 저장</li>
        </ul>
      </div>
    </div>
  )
}
