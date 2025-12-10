'use client'

import { useState } from 'react'
import { PlayCircle, TrendingUp, FileText, Video, Upload, Settings } from 'lucide-react'
import StatsCard from '@/components/StatsCard'

export default function Dashboard() {
  const [stats] = useState({
    totalVideos: 24,
    videosThisMonth: 8,
    totalViews: 125430,
    aiCost: 12.50,
  })

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">대시보드</h1>
        <p className="text-gray-600">AI 유튜브 자동화 시스템</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="총 영상"
          value={stats.totalVideos}
          icon={Video}
          color="blue"
        />
        <StatsCard
          title="이번 달 영상"
          value={stats.videosThisMonth}
          icon={PlayCircle}
          color="green"
        />
        <StatsCard
          title="총 조회수"
          value={stats.totalViews.toLocaleString()}
          icon={TrendingUp}
          color="purple"
        />
        <StatsCard
          title="AI 비용 (월)"
          value={`$${stats.aiCost.toFixed(2)}`}
          icon={Settings}
          color="orange"
        />
      </div>

      {/* 빠른 액션 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">빠른 액션</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <QuickActionButton
            href="/trends"
            icon={TrendingUp}
            title="트렌드 분석"
            description="YouTube 트렌드 분석 시작"
          />
          <QuickActionButton
            href="/scripts"
            icon={FileText}
            title="대본 생성"
            description="AI로 대본 생성하기"
          />
          <QuickActionButton
            href="/automation"
            icon={PlayCircle}
            title="전체 자동화"
            description="원클릭 영상 제작"
          />
        </div>
      </div>
    </div>
  )
}

function QuickActionButton({
  href,
  icon: Icon,
  title,
  description
}: {
  href: string
  icon: any
  title: string
  description: string
}) {
  return (
    <a
      href={href}
      className="flex items-start p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
    >
      <div className="p-2 bg-blue-100 rounded-lg mr-4">
        <Icon className="w-6 h-6 text-blue-600" />
      </div>
      <div>
        <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </a>
  )
}
