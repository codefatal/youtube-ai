'use client'

import { useState, useEffect } from 'react'
import { Film, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import StatsCard from '@/components/StatsCard'
import Link from 'next/link'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalVideos: 0,
    completed: 0,
    processing: 0,
    failed: 0,
    totalViews: 0,
    totalDuration: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/stats`)
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

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">대시보드</h1>
        <p className="text-gray-600">YouTube 리믹스 시스템</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard title="전체 영상" value={stats.totalVideos} icon={Film} color="blue" />
        <StatsCard title="완료" value={stats.completed} icon={CheckCircle} color="green" />
        <StatsCard title="처리 중" value={stats.processing} icon={Clock} color="yellow" />
        <StatsCard title="실패" value={stats.failed} icon={AlertCircle} color="red" />
      </div>

      {/* 빠른 액션 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">빠른 작업</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link href="/search" className="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-4xl mr-3">🔍</div>
            <div><h3 className="font-semibold">영상 검색</h3><p className="text-sm text-gray-600">트렌딩 영상 찾기</p></div>
          </Link>
          <Link href="/batch" className="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-4xl mr-3">⚡</div>
            <div><h3 className="font-semibold">배치 처리</h3><p className="text-sm text-gray-600">자동 리믹스</p></div>
          </Link>
          <Link href="/downloads" className="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-4xl mr-3">📥</div>
            <div><h3 className="font-semibold">다운로드</h3><p className="text-sm text-gray-600">영상 관리</p></div>
          </Link>
          <Link href="/videos" className="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-4xl mr-3">🎬</div>
            <div><h3 className="font-semibold">영상 목록</h3><p className="text-sm text-gray-600">모든 영상 보기</p></div>
          </Link>
        </div>
      </div>
    </div>
  )
}
