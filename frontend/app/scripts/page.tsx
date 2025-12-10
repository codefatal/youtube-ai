'use client'

import { useState } from 'react'
import { FileText, Loader2, Copy, Check } from 'lucide-react'

export default function ScriptsPage() {
  const [loading, setLoading] = useState(false)
  const [keywords, setKeywords] = useState('')
  const [format, setFormat] = useState('short')
  const [duration, setDuration] = useState(60)
  const [tone, setTone] = useState('informative')
  const [versions, setVersions] = useState(3)
  const [scripts, setScripts] = useState<string[]>([])
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/scripts/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keywords: keywords.split(',').map(k => k.trim()),
          format,
          duration,
          tone,
          versions
        })
      })
      const data = await response.json()
      setScripts(data.scripts || [])
    } catch (error) {
      console.error('Error:', error)
    }
    setLoading(false)
  }

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">대본 생성</h1>
        <p className="text-gray-600">AI로 자동 대본 생성</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">대본 설정</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              키워드 (쉼표로 구분)
            </label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="예: AI, 기술, 미래"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                영상 형식
              </label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="short">숏폼</option>
                <option value="long">롱폼</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                길이 (초)
              </label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                톤
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="informative">정보 제공</option>
                <option value="entertaining">재미</option>
                <option value="educational">교육적</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                버전 수
              </label>
              <input
                type="number"
                value={versions}
                onChange={(e) => setVersions(parseInt(e.target.value))}
                min={1}
                max={5}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !keywords}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                생성 중...
              </>
            ) : (
              <>
                <FileText className="w-5 h-5 mr-2" />
                대본 생성
              </>
            )}
          </button>
        </div>
      </div>

      {scripts.length > 0 && (
        <div className="space-y-6">
          {scripts.map((script, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">버전 {index + 1}</h3>
                <button
                  onClick={() => copyToClipboard(script, index)}
                  className="flex items-center px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  {copiedIndex === index ? (
                    <>
                      <Check className="w-4 h-4 mr-1 text-green-600" />
                      복사됨
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4 mr-1" />
                      복사
                    </>
                  )}
                </button>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                  {script}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
