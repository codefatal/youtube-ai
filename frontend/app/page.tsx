'use client'

import { useState, useEffect } from 'react'
import { Film, CheckCircle, AlertCircle, Activity, Zap } from 'lucide-react'
import StatsCard from '@/components/StatsCard'
import Link from 'next/link'

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_jobs: 0,
    completed_jobs: 0,
    failed_jobs: 0,
    success_rate: 0,
    queue_size: 0
  })
  const [loading, setLoading] = useState(true)
  const [recentJobs, setRecentJobs] = useState<any[]>([])

  useEffect(() => {
    fetchStats()
    fetchRecentJobs()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/stats`)
      const result = await response.json()
      if (result.success && result.data) {
        setStats(result.data)
      }
    } catch (error) {
      console.error('통계 조회 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRecentJobs = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/jobs/recent?limit=5`)
      const result = await response.json()
      if (result.success && result.data) {
        setRecentJobs(result.data.jobs || [])
      }
    } catch (error) {
      console.error('최근 작업 조회 실패:', error)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; color: string }> = {
      completed: { label: '완료', color: 'bg-green-100 text-green-800' },
      failed: { label: '실패', color: 'bg-red-100 text-red-800' },
      planning: { label: '기획 중', color: 'bg-blue-100 text-blue-800' },
      collecting_assets: { label: '에셋 수집 중', color: 'bg-yellow-100 text-yellow-800' },
      editing: { label: '편집 중', color: 'bg-purple-100 text-purple-800' },
      uploading: { label: '업로드 중', color: 'bg-indigo-100 text-indigo-800' }
    }
    const config = statusConfig[status] || { label: status, color: 'bg-gray-100 text-gray-800' }
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>{config.label}</span>
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">대시보드</h1>
        <p className="text-gray-600">YouTube AI v3.0 - AI 기반 독창적 콘텐츠 생성</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <StatsCard title="전체 작업" value={stats.total_jobs} icon={Film} color="blue" />
        <StatsCard title="완료" value={stats.completed_jobs} icon={CheckCircle} color="green" />
        <StatsCard title="실패" value={stats.failed_jobs} icon={AlertCircle} color="red" />
        <StatsCard
          title="성공률"
          value={`${stats.success_rate.toFixed(1)}%`}
          icon={Activity}
          color="purple"
        />
        <StatsCard title="대기 중" value={stats.queue_size} icon={Zap} color="yellow" />
      </div>

      {/* 빠른 액션 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">빠른 작업</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link href="/create" className="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-4xl mr-3">✨</div>
            <div>
              <h3 className="font-semibold">영상 생성</h3>
              <p className="text-sm text-gray-600">AI로 새 영상 만들기</p>
            </div>
          </Link>
          <Link href="/jobs" className="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-4xl mr-3">📋</div>
            <div>
              <h3 className="font-semibold">작업 목록</h3>
              <p className="text-sm text-gray-600">모든 작업 보기</p>
            </div>
          </Link>
          <Link href="/automation" className="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-4xl mr-3">⚡</div>
            <div>
              <h3 className="font-semibold">자동화</h3>
              <p className="text-sm text-gray-600">스케줄링 설정</p>
            </div>
          </Link>
          <Link href="/settings" className="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-4xl mr-3">⚙️</div>
            <div>
              <h3 className="font-semibold">설정</h3>
              <p className="text-sm text-gray-600">시스템 설정</p>
            </div>
          </Link>
        </div>
      </div>

      {/* 최근 작업 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">최근 작업</h2>
          <Link href="/jobs" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            모두 보기 →
          </Link>
        </div>
        {recentJobs.length === 0 ? (
          <p className="text-gray-500 text-center py-8">아직 작업이 없습니다. 새 영상을 생성해보세요!</p>
        ) : (
          <div className="space-y-3">
            {recentJobs.map((job) => (
              <div key={job.job_id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-medium text-gray-900">{job.topic || '제목 없음'}</h3>
                    {getStatusBadge(job.status)}
                  </div>
                  <div className="flex gap-4 text-sm text-gray-500">
                    <span>형식: {job.format || 'N/A'}</span>
                    <span>작성: {job.created_at ? new Date(job.created_at).toLocaleString('ko-KR') : 'N/A'}</span>
                  </div>
                </div>
                <Link
                  href={`/jobs?id=${job.job_id}`}
                  className="ml-4 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  상세보기
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
