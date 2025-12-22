'use client'

import { useState, useEffect } from 'react'
import { Film, Download, Languages, Trash2, Scan, Play } from 'lucide-react'

export default function VideosPage() {
  const [videos, setVideos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const [previewVideo, setPreviewVideo] = useState<string | null>(null)

  useEffect(() => {
    loadVideos()
  }, [filter])

  const loadVideos = async () => {
    setLoading(true)
    try {
      const url = filter === 'all'
        ? `${process.env.NEXT_PUBLIC_API_URL}/api/videos`
        : `${process.env.NEXT_PUBLIC_API_URL}/api/videos?status=${filter}`

      const res = await fetch(url)
      const result = await res.json()
      if (result.success) {
        setVideos(result.data.videos)
      }
    } catch (err) {
      console.error('영상 목록 조회 실패:', err)
    } finally {
      setLoading(false)
    }
  }

  const deleteVideo = async (videoId: string) => {
    if (!confirm('이 영상을 삭제하시겠습니까?')) return

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/videos/${videoId}`, {
        method: 'DELETE'
      })
      const result = await res.json()
      if (result.success) {
        alert('삭제되었습니다')
        loadVideos()
      }
    } catch (err) {
      alert('삭제 실패')
    }
  }

  const processHardcodedSubtitle = async (videoId: string) => {
    if (!confirm('하드코딩된 자막을 추출하고 번역하시겠습니까?\n(OCR 처리로 시간이 걸릴 수 있습니다)')) return

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/hardcoded-subtitle/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: videoId, target_lang: 'ko' })
      })
      const result = await res.json()
      if (result.success) {
        alert(`하드코딩 자막 처리가 시작되었습니다!\nJob ID: ${result.data.job_id}\n\n배치 처리 페이지에서 진행 상황을 확인하세요.`)
        loadVideos()
      } else {
        alert('처리 실패')
      }
    } catch (err: any) {
      alert(`처리 실패: ${err.message || '알 수 없는 오류'}`)
    }
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: { color: 'bg-gray-100 text-gray-700', text: '대기' },
      downloaded: { color: 'bg-blue-100 text-blue-700', text: '다운로드 완료' },
      translated: { color: 'bg-yellow-100 text-yellow-700', text: '번역 완료' },
      processing: { color: 'bg-purple-100 text-purple-700', text: '처리 중' },
      completed: { color: 'bg-green-100 text-green-700', text: '완료' },
      failed: { color: 'bg-red-100 text-red-700', text: '실패' },
    }
    const badge = badges[status as keyof typeof badges] || badges.pending
    return <span className={`px-3 py-1 rounded text-sm font-semibold ${badge.color}`}>{badge.text}</span>
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">영상 목록</h1>
        <p className="text-gray-600">다운로드하고 리믹스한 모든 영상</p>
      </div>

      {/* 필터 */}
      <div className="flex space-x-2 mb-6">
        {['all', 'pending', 'downloaded', 'translated', 'completed', 'failed'].map(status => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg font-medium ${
              filter === status ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {status === 'all' ? '전체' :
             status === 'pending' ? '대기' :
             status === 'downloaded' ? '다운로드' :
             status === 'translated' ? '번역' :
             status === 'completed' ? '완료' : '실패'}
          </button>
        ))}
      </div>

      {/* 영상 목록 */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">로딩 중...</p>
        </div>
      ) : videos.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Film className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">영상이 없습니다</p>
          <p className="text-sm text-gray-500 mt-1">영상 검색 페이지에서 영상을 다운로드하세요</p>
        </div>
      ) : (
        <div className="space-y-4">
          {videos.map((video) => (
            <div key={video.video_id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold">{video.original?.title || 'Unknown Title'}</h3>
                    {getStatusBadge(video.processing?.status || 'pending')}
                  </div>

                  <div className="space-y-1 text-sm text-gray-600 mb-3">
                    <p>📺 채널: {video.original?.channel_name}</p>
                    <p>👁️ 조회수: {(video.original?.views || video.original?.view_count || 0).toLocaleString()}</p>
                    <p>⏱️ 길이: {Math.floor((video.original?.duration || 0) / 60)}분 {(video.original?.duration || 0) % 60}초</p>
                    <p>🔗 <a href={video.original?.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      원본 보기
                    </a></p>
                  </div>

                  {video.translated && (
                    <div className="p-3 bg-blue-50 rounded mb-3">
                      <p className="text-sm font-semibold text-blue-900">번역 제목</p>
                      <p className="text-sm text-blue-700">{video.translated.title}</p>
                    </div>
                  )}

                  <div className="flex items-center space-x-2">
                    {video.files?.remixed_video && (
                      <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
                        ✅ 리믹스 완료
                      </span>
                    )}
                    {video.files?.translated_subtitle && (
                      <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded">
                        ✅ 번역 완료
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex space-x-2 ml-4">
                  {video.files?.remixed_video && (
                    <button
                      onClick={() => setPreviewVideo(video.video_id)}
                      className="p-2 text-green-600 hover:bg-green-50 rounded"
                      title="미리보기"
                    >
                      <Play className="w-5 h-5" />
                    </button>
                  )}
                  <button
                    onClick={() => processHardcodedSubtitle(video.video_id)}
                    className="p-2 text-purple-600 hover:bg-purple-50 rounded"
                    title="하드코딩 자막 추출 및 번역"
                  >
                    <Scan className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => deleteVideo(video.video_id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded"
                    title="삭제"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* 파일 경로 */}
              {video.files && (
                <details className="mt-4">
                  <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-900">
                    파일 정보
                  </summary>
                  <div className="mt-2 p-3 bg-gray-50 rounded text-xs space-y-1">
                    {Object.entries(video.files).map(([key, path]: [string, any]) => (
                      path && <div key={key}><strong>{key}:</strong> {path}</div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 미리보기 모달 */}
      {previewVideo && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
          onClick={() => setPreviewVideo(null)}
        >
          <div
            className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">영상 미리보기</h2>
              <button
                onClick={() => setPreviewVideo(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>
            <div className="aspect-video bg-black rounded">
              <video
                src={`${process.env.NEXT_PUBLIC_API_URL}/api/media/${previewVideo}`}
                controls
                autoPlay
                className="w-full h-full"
                onError={(e) => {
                  console.error('영상 로드 실패:', e)
                  alert('영상을 로드할 수 없습니다.')
                }}
              >
                영상을 재생할 수 없습니다.
              </video>
            </div>
            <div className="mt-4 p-3 bg-gray-50 rounded">
              <p className="text-sm text-gray-600">
                리믹스된 영상이 재생됩니다. 번역된 자막이 포함되어 있습니다.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
