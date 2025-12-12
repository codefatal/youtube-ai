'use client'

import { useState, useEffect } from 'react'
import { Zap, CheckCircle, XCircle } from 'lucide-react'

export default function BatchPage() {
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<any>(null)

  // 설정
  const [region, setRegion] = useState('US')
  const [category, setCategory] = useState('Science & Technology')
  const [maxVideos, setMaxVideos] = useState(3)
  const [duration, setDuration] = useState('short')
  const [minViews, setMinViews] = useState(10000)
  const [targetLang, setTargetLang] = useState('ko')

  useEffect(() => {
    if (jobId) {
      const interval = setInterval(checkJobStatus, 3000)
      return () => clearInterval(interval)
    }
  }, [jobId])

  const startBatch = async () => {
    if (!confirm(`${maxVideos}개 영상을 자동 리믹스하시겠습니까?`)) return

    setLoading(true)
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/batch/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          region,
          category,
          max_videos: maxVideos,
          duration,
          min_views: minViews,
          target_lang: targetLang
        })
      })
      const result = await res.json()
      if (result.success) {
        setJobId(result.data.job_id)
        alert('배치 작업이 시작되었습니다!')
      }
    } catch (err) {
      alert('배치 시작 실패')
    } finally {
      setLoading(false)
    }
  }

  const checkJobStatus = async () => {
    if (!jobId) return

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/batch/status/${jobId}`)
      const result = await res.json()
      if (result.success) {
        setJobStatus(result.data)
      }
    } catch (err) {
      console.error('상태 조회 실패:', err)
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">배치 자동 처리</h1>
      <p className="text-gray-600 mb-6">트렌딩 검색부터 리믹스까지 한번에 처리</p>

      {/* 설정 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">설정</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">지역</label>
            <select value={region} onChange={(e) => setRegion(e.target.value)} className="w-full border rounded px-3 py-2">
              <option value="US">미국</option>
              <option value="KR">한국</option>
              <option value="JP">일본</option>
              <option value="GB">영국</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">카테고리</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)} className="w-full border rounded px-3 py-2">
              <option value="Science & Technology">과학/기술</option>
              <option value="Education">교육</option>
              <option value="Entertainment">엔터테인먼트</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">최대 영상 수</label>
            <input type="number" value={maxVideos} onChange={(e) => setMaxVideos(Number(e.target.value))} min={1} max={10} className="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">영상 길이</label>
            <select value={duration} onChange={(e) => setDuration(e.target.value)} className="w-full border rounded px-3 py-2">
              <option value="short">숏폼 (4분 이하)</option>
              <option value="medium">중간 (4-20분)</option>
              <option value="long">롱폼 (20분 이상)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">최소 조회수</label>
            <input type="number" value={minViews} onChange={(e) => setMinViews(Number(e.target.value))} className="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">번역 언어</label>
            <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)} className="w-full border rounded px-3 py-2">
              <option value="ko">한국어</option>
              <option value="ja">일본어</option>
              <option value="zh">중국어</option>
            </select>
          </div>
        </div>

        <button
          onClick={startBatch}
          disabled={loading || !!jobId}
          className="mt-6 w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
        >
          <Zap className="w-5 h-5 mr-2" />
          {loading ? '시작 중...' : jobId ? '작업 진행 중...' : '배치 처리 시작'}
        </button>
      </div>

      {/* 작업 상태 */}
      {jobStatus && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">작업 상태</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span className="font-medium">Job ID</span>
              <span className="text-sm text-gray-600">{jobId}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span className="font-medium">상태</span>
              <span className={`px-3 py-1 rounded text-sm font-semibold ${
                jobStatus.status === 'completed' ? 'bg-green-100 text-green-700' :
                jobStatus.status === 'failed' ? 'bg-red-100 text-red-700' :
                'bg-yellow-100 text-yellow-700'
              }`}>
                {jobStatus.status === 'completed' ? '완료' :
                 jobStatus.status === 'failed' ? '실패' :
                 jobStatus.status === 'running' ? '실행 중' : '대기 중'}
              </span>
            </div>

            {jobStatus.result && (
              <div className="mt-4 p-4 bg-blue-50 rounded">
                <h3 className="font-semibold mb-2">결과</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>검색: {jobStatus.result.searched}개</div>
                  <div>다운로드: {jobStatus.result.downloaded}개</div>
                  <div>번역: {jobStatus.result.translated}개</div>
                  <div>리믹스: {jobStatus.result.remixed}개</div>
                  <div className="text-red-600">실패: {jobStatus.result.failed}개</div>
                  <div className="text-gray-600">스킵: {jobStatus.result.skipped}개</div>
                </div>
              </div>
            )}

            {jobStatus.error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded">
                <p className="text-sm text-red-700">오류: {jobStatus.error}</p>
              </div>
            )}

            {jobStatus.status === 'completed' && (
              <button
                onClick={() => { setJobId(null); setJobStatus(null); }}
                className="w-full mt-4 bg-green-600 text-white py-2 rounded font-semibold hover:bg-green-700"
              >
                새 작업 시작
              </button>
            )}
          </div>
        </div>
      )}

      {/* 안내 */}
      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>참고:</strong> 배치 작업은 백그라운드에서 실행됩니다. 영상 개수에 따라 수십 분이 소요될 수 있습니다.
        </p>
      </div>
    </div>
  )
}
