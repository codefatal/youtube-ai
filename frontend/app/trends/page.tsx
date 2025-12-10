'use client'

import { useState } from 'react'
import { TrendingUp, Play, Loader2 } from 'lucide-react'

export default function TrendsPage() {
  const [loading, setLoading] = useState(false)
  const [region, setRegion] = useState('US')
  const [format, setFormat] = useState('short')
  const [analysis, setAnalysis] = useState<any>(null)

  const handleAnalyze = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/trends/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ region, format })
      })
      const data = await response.json()
      setAnalysis(data)
    } catch (error) {
      console.error('Error:', error)
    }
    setLoading(false)
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">트렌드 분석</h1>
        <p className="text-gray-600">YouTube 트렌딩 비디오 분석</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">분석 설정</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              지역
            </label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="US">미국 (US)</option>
              <option value="KR">한국 (KR)</option>
              <option value="JP">일본 (JP)</option>
              <option value="GB">영국 (GB)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              영상 형식
            </label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="short">숏폼 (Shorts)</option>
              <option value="long">롱폼 (일반 영상)</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              분석 중...
            </>
          ) : (
            <>
              <TrendingUp className="w-5 h-5 mr-2" />
              트렌드 분석 시작
            </>
          )}
        </button>
      </div>

      {analysis && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">주요 키워드</h3>
            <div className="flex flex-wrap gap-2">
              {analysis.keywords?.map((keyword: string, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">트렌딩 주제</h3>
            <ul className="space-y-2">
              {analysis.topics?.map((topic: string, index: number) => (
                <li key={index} className="flex items-center text-gray-700">
                  <TrendingUp className="w-4 h-4 mr-2 text-green-500" />
                  {topic}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">추천 콘텐츠 아이디어</h3>
            <div className="space-y-4">
              {analysis.content_ideas?.map((idea: string, index: number) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-start">
                    <Play className="w-5 h-5 mr-2 mt-0.5 text-blue-500 flex-shrink-0" />
                    <p className="text-gray-700">{idea}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-2">예상 조회수 범위</h3>
            <p className="text-3xl font-bold text-green-600">{analysis.view_range}</p>
          </div>
        </div>
      )}
    </div>
  )
}
