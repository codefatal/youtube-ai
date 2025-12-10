'use client'

import { useState } from 'react'
import { Upload, Loader2, CheckCircle } from 'lucide-react'

export default function UploadPage() {
  const [loading, setLoading] = useState(false)
  const [videoPath, setVideoPath] = useState('')
  const [keywords, setKeywords] = useState('')
  const [script, setScript] = useState('')
  const [privacy, setPrivacy] = useState('public')
  const [result, setResult] = useState<any>(null)

  const handleUpload = async () => {
    if (!videoPath.trim()) {
      alert('영상 파일 경로를 입력해주세요')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_path: videoPath,
          keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
          script: script || null,
          privacy
        })
      })
      const data = await response.json()
      console.log('업로드 결과:', data)
      if (data.success) {
        setResult(data)
      } else {
        alert('업로드 실패: ' + (data.detail || '알 수 없는 오류'))
      }
    } catch (error) {
      console.error('Error:', error)
      alert('업로드 중 오류가 발생했습니다')
    }
    setLoading(false)
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">YouTube 업로드</h1>
        <p className="text-gray-600">영상을 YouTube에 업로드</p>
      </div>

      {!result ? (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">업로드 설정</h2>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                영상 파일 경로 *
              </label>
              <input
                type="text"
                value={videoPath}
                onChange={(e) => setVideoPath(e.target.value)}
                placeholder="./output/video.mp4"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                키워드 (쉼표로 구분)
              </label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="AI, 기술, 트렌드"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                대본 (선택사항)
              </label>
              <textarea
                value={script}
                onChange={(e) => setScript(e.target.value)}
                placeholder="제목과 설명 자동 생성을 위한 대본"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={5}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                공개 설정
              </label>
              <select
                value={privacy}
                onChange={(e) => setPrivacy(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="public">공개</option>
                <option value="unlisted">일부 공개</option>
                <option value="private">비공개</option>
              </select>
            </div>

            <button
              onClick={handleUpload}
              disabled={loading}
              className="w-full bg-red-600 text-white py-3 px-6 rounded-lg hover:bg-red-700 disabled:bg-gray-400 flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  업로드 중...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5 mr-2" />
                  YouTube 업로드
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center text-green-600">
            <CheckCircle className="w-6 h-6 mr-2" />
            업로드 성공!
          </h3>

          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Video ID</p>
              <p className="text-lg font-mono text-gray-900">{result.video_id}</p>
            </div>

            <div>
              <p className="text-sm text-gray-600">YouTube URL</p>
              <a
                href={result.video_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-lg text-blue-600 hover:underline"
              >
                {result.video_url}
              </a>
            </div>

            {result.metadata && (
              <>
                <div className="pt-4 border-t">
                  <p className="text-sm text-gray-600 mb-2">제목</p>
                  <p className="text-gray-900">{result.metadata.title}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600 mb-2">설명</p>
                  <p className="text-gray-700 text-sm whitespace-pre-wrap">{result.metadata.description}</p>
                </div>

                <div>
                  <p className="text-sm text-gray-600 mb-2">태그</p>
                  <div className="flex flex-wrap gap-2">
                    {result.metadata.tags?.map((tag: string, index: number) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </>
            )}

            <div className="pt-4">
              <button
                onClick={() => {
                  setResult(null)
                  setVideoPath('')
                  setKeywords('')
                  setScript('')
                }}
                className="bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700"
              >
                새 영상 업로드
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
