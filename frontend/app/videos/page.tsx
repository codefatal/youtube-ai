'use client'

import { useState, useEffect } from 'react'
import { Video, Upload, Loader2 } from 'lucide-react'

export default function VideosPage() {
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState('')
  const [script, setScript] = useState('')
  const [format, setFormat] = useState('short')
  const [style, setStyle] = useState('short_trendy')
  const [result, setResult] = useState<any>(null)

  // 설정 페이지에서 저장된 기본값 불러오기
  useEffect(() => {
    const savedSettings = localStorage.getItem('appSettings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)
      if (settings.defaultFormat) {
        setFormat(settings.defaultFormat)
        // 형식에 따라 스타일도 자동 변경
        setStyle(settings.defaultFormat === 'short' ? 'short_trendy' : 'long_educational')
      }
    }
  }, [])

  const handleProduce = async () => {
    if (!script.trim()) {
      alert('대본을 입력해주세요')
      return
    }

    setLoading(true)
    setProgress('🎬 영상 제작을 시작합니다...')
    setResult(null)

    try {
      setProgress('🎤 음성을 생성하고 있습니다... (1-2분 소요)')

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/videos/produce`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ script, format, style })
      })

      const data = await response.json()
      console.log('영상 제작 결과:', data)

      if (data.success) {
        setProgress('✅ 영상 제작이 완료되었습니다!')
        setResult(data)
      } else {
        setProgress('')
        alert('영상 제작 실패: ' + (data.detail || '알 수 없는 오류'))
      }
    } catch (error) {
      console.error('Error:', error)
      setProgress('')
      alert('영상 제작 중 오류가 발생했습니다: ' + error)
    }
    setLoading(false)
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">영상 제작</h1>
        <p className="text-gray-600">대본을 영상으로 변환</p>
      </div>

      {/* 무료 TTS 사용 안내 */}
      <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">ℹ️ 무료 TTS 사용</h3>
        <p className="text-sm text-blue-800">
          현재 gTTS (Google Text-to-Speech) 무료 서비스를 사용합니다. 한글과 영어를 자동으로 감지합니다.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">제작 설정</h2>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              대본
            </label>
            <textarea
              value={script}
              onChange={(e) => setScript(e.target.value)}
              placeholder="[00:00] 안녕하세요...&#10;[00:05] 오늘은..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={10}
            />
            <p className="mt-2 text-sm text-gray-500">
              타임스탬프 형식: [00:00] 내용
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                영상 형식
              </label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="short">숏폼 (9:16)</option>
                <option value="long">롱폼 (16:9)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                스타일
              </label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="short_trendy">숏폼 트렌디</option>
                <option value="long_educational">롱폼 교육</option>
                <option value="minimalist">미니멀</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleProduce}
            disabled={loading}
            className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                영상 제작 중...
              </>
            ) : (
              <>
                <Video className="w-5 h-5 mr-2" />
                영상 제작 시작
              </>
            )}
          </button>

          {/* 진행 상황 표시 */}
          {progress && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">{progress}</p>
            </div>
          )}
        </div>
      </div>

      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center text-green-600">
            <Video className="w-5 h-5 mr-2" />
            ✅ 제작 완료!
          </h3>

          <div className="space-y-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800 mb-2">
                영상이 서버에 저장되었습니다. 파일 경로를 확인하세요.
              </p>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-green-700 font-semibold">영상 파일:</p>
                  <p className="text-sm font-mono text-green-900 break-all">{result.video_path}</p>
                </div>
                {result.thumbnail_path && (
                  <div>
                    <p className="text-xs text-green-700 font-semibold">썸네일:</p>
                    <p className="text-sm font-mono text-green-900 break-all">{result.thumbnail_path}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="pt-4 border-t flex gap-3">
              <button
                onClick={() => {
                  // 새 영상 제작
                  setResult(null)
                  setProgress('')
                }}
                className="bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700"
              >
                새 영상 제작
              </button>
              <button
                onClick={() => {
                  // YouTube 업로드 페이지로 이동
                  window.location.href = '/upload'
                }}
                className="bg-red-600 text-white py-2 px-6 rounded-lg hover:bg-red-700 flex items-center"
              >
                <Upload className="w-4 h-4 mr-2" />
                YouTube 업로드
              </button>
            </div>

            <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
              <p className="font-semibold mb-1">💡 파일 다운로드 방법:</p>
              <p>서버의 output 폴더에서 위 경로의 파일을 찾을 수 있습니다.</p>
              <p className="mt-1">예: <code className="bg-gray-200 px-1 rounded">D:\work\code\youtubeAI\output\video_xxxxx.mp4</code></p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
