'use client'

import { useState, useEffect } from 'react'
import { DollarSign, TrendingUp, Activity } from 'lucide-react'

export default function CostsPage() {
  const [stats, setStats] = useState({
    totalCost: 0,
    thisMonth: 0,
    geminiCalls: 0,
    claudeCalls: 0,
    geminiCost: 0,
    claudeCost: 0
  })

  useEffect(() => {
    // TODO: 실제 API에서 비용 데이터 가져오기
    // 현재는 로컬 스토리지나 백엔드 API에서 사용량 추적 필요
    setStats({
      totalCost: 0,
      thisMonth: 0,
      geminiCalls: 0,
      claudeCalls: 0,
      geminiCost: 0,
      claudeCost: 0
    })
  }, [])

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">비용 관리</h1>
        <p className="text-gray-600">AI API 사용량 및 비용 추적</p>
      </div>

      {/* 비용 요약 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">이번 달 비용</h3>
            <DollarSign className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">${stats.thisMonth.toFixed(2)}</p>
          <p className="text-sm text-gray-600 mt-2">총 누적: ${stats.totalCost.toFixed(2)}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Gemini API</h3>
            <Activity className="w-6 h-6 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.geminiCalls}</p>
          <p className="text-sm text-gray-600 mt-2">호출 / ${stats.geminiCost.toFixed(2)}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Claude API</h3>
            <TrendingUp className="w-6 h-6 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.claudeCalls}</p>
          <p className="text-sm text-gray-600 mt-2">호출 / ${stats.claudeCost.toFixed(2)}</p>
        </div>
      </div>

      {/* 비용 절감 팁 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">비용 절감 팁</h2>
        <ul className="space-y-3">
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            <span className="text-gray-700">
              <strong>Gemini 우선 사용:</strong> Gemini 1.5 Flash는 무료 티어 제공 (분당 15 요청, 일일 1,500 요청)
            </span>
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            <span className="text-gray-700">
              <strong>Auto 모드 활용:</strong> Gemini를 우선 사용하고 실패 시 Claude로 자동 전환
            </span>
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            <span className="text-gray-700">
              <strong>토큰 최적화:</strong> 프롬프트를 간결하게 작성하고 불필요한 요청 줄이기
            </span>
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            <span className="text-gray-700">
              <strong>캐싱 활용:</strong> 반복적인 분석 결과는 로컬에 저장하여 재사용
            </span>
          </li>
        </ul>
      </div>

      {/* API 가격 정보 */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">API 가격 정보</h2>
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Gemini 1.5 Flash</h3>
            <p className="text-sm text-gray-600">무료 티어: 분당 15 요청, 일일 1,500 요청</p>
            <p className="text-sm text-gray-600">유료: 입력 $0.000075/1K 토큰, 출력 $0.0003/1K 토큰</p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Claude Sonnet 4.5</h3>
            <p className="text-sm text-gray-600">입력: $3/1M 토큰, 출력: $15/1M 토큰</p>
          </div>
        </div>
      </div>
    </div>
  )
}
