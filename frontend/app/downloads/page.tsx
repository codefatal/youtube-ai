'use client'

export default function DownloadsPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">다운로드 관리</h1>
      <p className="text-gray-600 mb-6">영상 다운로드 및 관리</p>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <p className="text-blue-900 font-semibold mb-2">이 페이지는 영상 목록에 통합되었습니다</p>
        <p className="text-blue-700 text-sm">
          영상 검색 페이지에서 다운로드하고, 영상 목록 페이지에서 관리하세요.
        </p>
      </div>
    </div>
  )
}
