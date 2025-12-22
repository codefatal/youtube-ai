'use client'

import { useState, useEffect } from 'react'
import { Zap, CheckCircle, XCircle } from 'lucide-react'

export default function BatchPage() {
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<any>(null)
  const [allJobs, setAllJobs] = useState<any[]>([])

  // 설정
  const [region, setRegion] = useState('US')
  const [category, setCategory] = useState('Science & Technology')
  const [maxVideos, setMaxVideos] = useState(3)
  const [duration, setDuration] = useState('short')
  const [minViews, setMinViews] = useState(10000)
  const [targetLang, setTargetLang] = useState('ko')
  const [order, setOrder] = useState('viewCount')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  // 날짜를 RFC 3339 형식으로 변환
  const toRFC3339 = (dateStr: string, isEndDate: boolean = false) => {
    if (!dateStr) return undefined
    const date = new Date(dateStr)
    if (isEndDate) {
      date.setHours(23, 59, 59, 999)
    }
    return date.toISOString()
  }

  useEffect(() => {
    loadAllJobs()
  }, [])

  useEffect(() => {
    if (jobId) {
      const interval = setInterval(checkJobStatus, 3000)
      return () => clearInterval(interval)
    }
  }, [jobId])

  useEffect(() => {
    // 작업 목록을 주기적으로 새로고침
    const interval = setInterval(loadAllJobs, 5000)
    return () => clearInterval(interval)
  }, [])

  const startBatch = async () => {
    if (!confirm(`${maxVideos}개 영상을 자동 리믹스하시겠습니까?`)) return

    setLoading(true)
    try {
      const payload = {
        region,
        category,
        max_videos: maxVideos,
        duration,
        min_views: minViews,
        target_lang: targetLang,
        order,
        published_after: toRFC3339(startDate, false),
        published_before: toRFC3339(endDate, true)
      }
      console.log('[BATCH] 배치 시작 요청:', payload)

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/batch/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
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

  const loadAllJobs = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/batch/jobs`)
      const result = await res.json()
      if (result.success) {
        setAllJobs(result.data.jobs)
      }
    } catch (err) {
      console.error('작업 목록 조회 실패:', err)
    }
  }

  const getJobType = (jobId: string) => {
    if (jobId.startsWith('hardcoded_')) return '하드코딩 자막'
    if (jobId.startsWith('batch_')) return '배치 리믹스'
    return '알 수 없음'
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      processing: { color: 'bg-yellow-100 text-yellow-700', text: '처리 중' },
      running: { color: 'bg-blue-100 text-blue-700', text: '실행 중' },
      completed: { color: 'bg-green-100 text-green-700', text: '완료' },
      failed: { color: 'bg-red-100 text-red-700', text: '실패' },
    }
    const badge = badges[status as keyof typeof badges] || { color: 'bg-gray-100 text-gray-700', text: status }
    return <span className={`px-3 py-1 rounded text-sm font-semibold ${badge.color}`}>{badge.text}</span>
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
              <option value="Music">음악</option>
              <option value="Gaming">게임</option>
              <option value="Sports">스포츠</option>
              <option value="News & Politics">뉴스/정치</option>
              <option value="Howto & Style">생활/노하우</option>
              <option value="Film & Animation">영화/애니메이션</option>
              <option value="Comedy">코미디</option>
              <option value="People & Blogs">사람/블로그</option>
              <option value="Autos & Vehicles">자동차</option>
              <option value="Pets & Animals">동물</option>
              <option value="Travel & Events">여행/이벤트</option>
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
            <label className="block text-sm font-medium mb-2">정렬</label>
            <select value={order} onChange={(e) => setOrder(e.target.value)} className="w-full border rounded px-3 py-2">
              <option value="viewCount">조회수</option>
              <option value="date">최신 날짜</option>
              <option value="rating">평점</option>
              <option value="relevance">관련성</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">번역 언어</label>
            <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)} className="w-full border rounded px-3 py-2">
              <option value="ko">한국어</option>
              <option value="ja">일본어</option>
              <option value="zh">중국어</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">시작 날짜 (선택)</label>
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">종료 날짜 (선택)</label>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full border rounded px-3 py-2" />
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

      {/* 모든 작업 목록 */}
      {allJobs.length > 0 && (
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">전체 작업 목록</h2>
          <div className="space-y-3">
            {allJobs.map((job) => (
              <div key={job.job_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-medium text-gray-700">{getJobType(job.job_id)}</span>
                    {getStatusBadge(job.status)}
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date((job.started_at || 0) * 1000).toLocaleString('ko-KR')}
                  </span>
                </div>

                <div className="text-xs text-gray-600 mb-2">
                  <code className="bg-gray-100 px-2 py-1 rounded">{job.job_id}</code>
                </div>

                {job.video_id && (
                  <div className="text-sm text-gray-600 mb-2">
                    영상 ID: <code className="bg-gray-100 px-2 py-1 rounded text-xs">{job.video_id}</code>
                  </div>
                )}

                {job.result && (
                  <div className="mt-2 p-3 bg-gray-50 rounded text-xs">
                    {job.result.searched !== undefined && (
                      <div className="grid grid-cols-3 gap-2">
                        <div>검색: {job.result.searched}개</div>
                        <div>다운로드: {job.result.downloaded}개</div>
                        <div>번역: {job.result.translated}개</div>
                        <div>리믹스: {job.result.remixed}개</div>
                        <div className="text-red-600">실패: {job.result.failed}개</div>
                        <div className="text-gray-500">스킵: {job.result.skipped}개</div>
                      </div>
                    )}
                    {job.result.success !== undefined && (
                      <div className="text-sm">
                        {job.result.success ? '✅ 처리 완료' : '❌ 처리 실패'}
                        {job.result.output_video && (
                          <div className="mt-1 text-xs text-gray-600">
                            출력: {job.result.output_video}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {job.error && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                    오류: {job.error}
                  </div>
                )}
              </div>
            ))}
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
