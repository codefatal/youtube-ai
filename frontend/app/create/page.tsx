'use client'

import { useState } from 'react'
import { Sparkles, Video, Clock, Palette, Upload, Wand2 } from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function CreateVideoPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    topic: '',
    format: 'shorts',
    duration: 60,
    style: '정보성',
    upload: false,
    ai_provider: 'gemini',
    tts_provider: 'gtts'
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/videos/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: formData.topic || null,
          format: formData.format,
          duration: formData.duration,
          upload: formData.upload,
          ai_provider: formData.ai_provider,
          tts_provider: formData.tts_provider
        })
      })

      const result = await response.json()

      if (result.success) {
        alert(`영상 생성 시작! Job ID: ${result.data.job_id}`)
        router.push(`/jobs?id=${result.data.job_id}`)
      } else {
        alert(`생성 실패: ${response.statusText}`)
      }
    } catch (error) {
      console.error('영상 생성 실패:', error)
      alert('영상 생성 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <Sparkles className="text-blue-600" />
          새 영상 생성
        </h1>
        <p className="text-gray-600">AI가 독창적인 YouTube 콘텐츠를 자동으로 생성합니다</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* 주제 */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Wand2 size={16} />
            영상 주제
          </label>
          <input
            type="text"
            value={formData.topic}
            onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
            placeholder="비워두면 AI가 트렌딩 주제를 자동 생성합니다"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">예: "Python 프로그래밍 팁", "건강한 아침 루틴"</p>
        </div>

        {/* 포맷 & 길이 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Video size={16} />
              영상 포맷
            </label>
            <select
              value={formData.format}
              onChange={(e) => setFormData({ ...formData, format: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="shorts">Shorts (세로 9:16)</option>
              <option value="landscape">Landscape (가로 16:9)</option>
              <option value="square">Square (정사각형 1:1)</option>
            </select>
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Clock size={16} />
              영상 길이
            </label>
            <select
              value={formData.duration}
              onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={15}>15초 (매우 짧음)</option>
              <option value={30}>30초 (짧음)</option>
              <option value={60}>60초 (Shorts 표준)</option>
              <option value={120}>120초 (긴 Shorts)</option>
              <option value={300}>300초 (일반 영상)</option>
            </select>
          </div>
        </div>

        {/* 스타일 */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Palette size={16} />
            콘텐츠 스타일
          </label>
          <div className="grid grid-cols-3 gap-3">
            {['힐링', '정보성', '유머'].map((style) => (
              <button
                key={style}
                type="button"
                onClick={() => setFormData({ ...formData, style })}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  formData.style === style
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {style}
              </button>
            ))}
          </div>
        </div>

        {/* Provider 설정 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">AI Provider</label>
            <select
              value={formData.ai_provider}
              onChange={(e) => setFormData({ ...formData, ai_provider: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="gemini">Gemini (무료, 빠름)</option>
              <option value="claude">Claude (프리미엄)</option>
              <option value="openai">OpenAI (프리미엄)</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 mb-2 block">TTS Provider</label>
            <select
              value={formData.tts_provider}
              onChange={(e) => setFormData({ ...formData, tts_provider: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="gtts">gTTS (무료, 빠름)</option>
              <option value="elevenlabs">ElevenLabs (프리미엄, 자연스러움)</option>
              <option value="google_cloud">Google Cloud (프리미엄)</option>
            </select>
          </div>
        </div>

        {/* YouTube 업로드 */}
        <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
          <input
            type="checkbox"
            id="upload"
            checked={formData.upload}
            onChange={(e) => setFormData({ ...formData, upload: e.target.checked })}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <label htmlFor="upload" className="flex items-center gap-2 text-sm font-medium text-gray-700 cursor-pointer">
            <Upload size={16} />
            영상 생성 후 YouTube에 자동 업로드
          </label>
        </div>

        {/* 제출 버튼 */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              생성 중...
            </>
          ) : (
            <>
              <Sparkles size={20} />
              영상 생성 시작
            </>
          )}
        </button>

        {loading && (
          <p className="text-sm text-gray-500 text-center">
            AI가 콘텐츠를 생성하고 있습니다. 약 2-5분 소요됩니다...
          </p>
        )}
      </form>
    </div>
  )
}
