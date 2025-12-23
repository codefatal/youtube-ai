'use client'

import { useState, useEffect } from 'react'
import { Clipboard, CheckCircle, XCircle, Clock, Play } from 'lucide-react'
import { useSearchParams } from 'next/navigation'

export default function JobsPage() {
  const searchParams = useSearchParams()
  const jobId = searchParams.get('id')

  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedJob, setSelectedJob] = useState<any>(null)

  useEffect(() => {
    fetchJobs()
    if (jobId) {
      fetchJobStatus(jobId)
    }
  }, [jobId])

  const fetchJobs = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/jobs/recent?limit=20`)
      const result = await response.json()
      if (result.success) {
        setJobs(result.data.jobs || [])
      }
    } catch (error) {
      console.error('작업 목록 조회 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchJobStatus = async (id: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/jobs/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: id })
      })
      const result = await response.json()
      if (result.success) {
        setSelectedJob(result.data)
      }
    } catch (error) {
      console.error('작업 상태 조회 실패:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-600" size={20} />
      case 'failed':
        return <XCircle className="text-red-600" size={20} />
      default:
        return <Clock className="text-yellow-600" size={20} />
    }
  }

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      completed: '완료',
      failed: '실패',
      planning: '기획 중',
      collecting_assets: '에셋 수집 중',
      editing: '편집 중',
      uploading: '업로드 중'
    }
    return statusMap[status] || status
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <Clipboard />
          작업 목록
        </h1>
        <p className="text-gray-600">모든 영상 생성 작업을 확인하세요</p>
      </div>

      {/* 작업 목록 */}
      <div className="bg-white rounded-lg shadow-md">
        {loading ? (
          <div className="p-8 text-center text-gray-500">로딩 중...</div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-gray-500">아직 작업이 없습니다.</div>
        ) : (
          <div className="divide-y divide-gray-200">
            {jobs.map((job) => (
              <div
                key={job.job_id}
                onClick={() => fetchJobStatus(job.job_id)}
                className={`p-6 hover:bg-gray-50 cursor-pointer transition-colors ${
                  selectedJob?.job_id === job.job_id ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusIcon(job.status)}
                      <h3 className="font-semibold text-gray-900">{job.topic || '제목 없음'}</h3>
                      <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {getStatusText(job.status)}
                      </span>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600">
                      <span>형식: {job.format || 'N/A'}</span>
                      <span>생성: {job.created_at ? new Date(job.created_at).toLocaleString('ko-KR') : 'N/A'}</span>
                      {job.completed_at && (
                        <span>완료: {new Date(job.completed_at).toLocaleString('ko-KR')}</span>
                      )}
                    </div>
                  </div>
                  <button className="ml-4 text-blue-600 hover:text-blue-700 font-medium text-sm">
                    상세보기 →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 선택된 작업 상세 정보 */}
      {selectedJob && (
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            {getStatusIcon(selectedJob.status)}
            작업 상세 정보
          </h2>

          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">작업 ID</p>
                <p className="font-mono text-sm">{selectedJob.job_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">상태</p>
                <p className="font-semibold">{getStatusText(selectedJob.status)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">주제</p>
                <p>{selectedJob.topic || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">포맷</p>
                <p>{selectedJob.format || 'N/A'}</p>
              </div>
            </div>

            {selectedJob.output_video_path && (
              <div>
                <p className="text-sm text-gray-500 mb-1">영상 파일</p>
                <p className="font-mono text-sm bg-gray-50 p-2 rounded break-all">
                  {selectedJob.output_video_path}
                </p>
              </div>
            )}

            {selectedJob.youtube_url && (
              <div>
                <p className="text-sm text-gray-500 mb-1">YouTube URL</p>
                <a
                  href={selectedJob.youtube_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-700 flex items-center gap-2"
                >
                  <Play size={16} />
                  {selectedJob.youtube_url}
                </a>
              </div>
            )}

            {selectedJob.error_log && (
              <div>
                <p className="text-sm text-gray-500 mb-1">에러 로그</p>
                <pre className="bg-red-50 text-red-800 p-3 rounded text-xs overflow-x-auto">
                  {selectedJob.error_log}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
