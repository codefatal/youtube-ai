'use client'

import { useState } from 'react'
import { Search, Download } from 'lucide-react'

export default function SearchPage() {
  const [activeTab, setActiveTab] = useState<'trending' | 'keywords'>('trending')
  const [loading, setLoading] = useState(false)
  const [videos, setVideos] = useState<any[]>([])

  // 트렌딩 검색 설정
  const [region, setRegion] = useState('US')
  const [category, setCategory] = useState('Science & Technology')
  const [duration, setDuration] = useState('short')
  const [minViews, setMinViews] = useState(10000)
  const [trendingOrder, setTrendingOrder] = useState('viewCount')
  const [trendingStartDate, setTrendingStartDate] = useState('')
  const [trendingEndDate, setTrendingEndDate] = useState('')

  // 키워드 검색 설정
  const [keywords, setKeywords] = useState('')
  const [keywordDuration, setKeywordDuration] = useState('any')
  const [keywordMinViews, setKeywordMinViews] = useState(0)
  const [order, setOrder] = useState('viewCount')
  const [keywordStartDate, setKeywordStartDate] = useState('')
  const [keywordEndDate, setKeywordEndDate] = useState('')

  // 날짜를 RFC 3339 형식으로 변환
  const toRFC3339 = (dateStr: string, isEndDate: boolean = false) => {
    if (!dateStr) return undefined
    const date = new Date(dateStr)
    if (isEndDate) {
      // 종료 날짜는 23:59:59로 설정
      date.setHours(23, 59, 59, 999)
    }
    return date.toISOString()
  }

  const searchTrending = async () => {
    setLoading(true)
    try {
      const payload = {
        region,
        category,
        duration,
        min_views: minViews,
        max_results: 10,
        order: trendingOrder,
        published_after: toRFC3339(trendingStartDate, false),
        published_before: toRFC3339(trendingEndDate, true)
      }
      console.log('[FRONTEND] 트렌딩 검색 요청:', payload)

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/search/trending`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const result = await res.json()
      if (result.success) setVideos(result.data.videos)
    } catch (err) {
      console.error(err)
      alert('검색 실패')
    } finally {
      setLoading(false)
    }
  }

  const searchKeywords = async () => {
    setLoading(true)
    try {
      const payload = {
        keywords,
        region,
        order,
        duration: keywordDuration,
        min_views: keywordMinViews,
        max_results: 10,
        published_after: toRFC3339(keywordStartDate, false),
        published_before: toRFC3339(keywordEndDate, true)
      }
      console.log('[FRONTEND] 키워드 검색 요청:', payload)

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/search/keywords`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const result = await res.json()
      if (result.success) setVideos(result.data.videos)
    } catch (err) {
      console.error(err)
      alert('검색 실패')
    } finally {
      setLoading(false)
    }
  }

  const downloadVideo = async (url: string) => {
    if (!confirm('이 영상을 다운로드하시겠습니까?')) return

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/download`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      })
      const result = await res.json()
      if (result.success) {
        alert('다운로드 완료!')
      } else {
        alert('다운로드 실패')
      }
    } catch (err) {
      alert('다운로드 실패')
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">영상 검색</h1>

      {/* 탭 */}
      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => setActiveTab('trending')}
          className={`px-6 py-3 rounded-lg font-semibold ${
            activeTab === 'trending' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
          }`}
        >
          🔥 트렌딩
        </button>
        <button
          onClick={() => setActiveTab('keywords')}
          className={`px-6 py-3 rounded-lg font-semibold ${
            activeTab === 'keywords' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
          }`}
        >
          🔍 키워드
        </button>
      </div>

      {/* 검색 폼 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        {activeTab === 'trending' ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">지역</label>
                <select value={region} onChange={(e) => setRegion(e.target.value)} className="w-full border rounded px-3 py-2">
                  <option value="US">미국</option>
                  <option value="KR">한국</option>
                  <option value="JP">일본</option>
                  <option value="GB">영국</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">카테고리</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)} className="w-full border rounded px-3 py-2">
                  <option value="Science & Technology">과학/기술</option>
                  <option value="Education">교육</option>
                  <option value="Entertainment">엔터테인먼트</option>
                  <option value="Music">음악</option>
                  <option value="Gaming">게임</option>
                  <option value="Sports">스포츠</option>
                  <option value="News & Politics">뉴스/정치</option>
                  <option value="Howto & Style">생활/노하우</option>
                  <option value="Film & Animation">영화/애니메이션</option>
                  <option value="Comedy">코미디</option>
                  <option value="People & Blogs">사람/블로그</option>
                  <option value="Autos & Vehicles">자동차</option>
                  <option value="Pets & Animals">동물</option>
                  <option value="Travel & Events">여행/이벤트</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">영상 길이</label>
                <select value={duration} onChange={(e) => setDuration(e.target.value)} className="w-full border rounded px-3 py-2">
                  <option value="short">숏폼 (4분 이하)</option>
                  <option value="medium">중간 (4-20분)</option>
                  <option value="long">롱폼 (20분 이상)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">정렬</label>
                <select value={trendingOrder} onChange={(e) => setTrendingOrder(e.target.value)} className="w-full border rounded px-3 py-2">
                  <option value="viewCount">조회수</option>
                  <option value="date">최신 날짜</option>
                  <option value="rating">평점</option>
                  <option value="relevance">관련성</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">최소 조회수</label>
                <input type="number" value={minViews} onChange={(e) => setMinViews(Number(e.target.value))} className="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">시작 날짜 (선택)</label>
                <input type="date" value={trendingStartDate} onChange={(e) => setTrendingStartDate(e.target.value)} className="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">종료 날짜 (선택)</label>
                <input type="date" value={trendingEndDate} onChange={(e) => setTrendingEndDate(e.target.value)} className="w-full border rounded px-3 py-2" />
              </div>
            </div>
            <button onClick={searchTrending} disabled={loading} className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50">
              {loading ? '검색 중...' : '트렌딩 영상 검색'}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">검색 키워드</label>
              <input type="text" value={keywords} onChange={(e) => setKeywords(e.target.value)} placeholder="예: AI technology" className="w-full border rounded px-3 py-2" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">지역</label>
                <select value={region} onChange={(e) => setRegion(e.target.value)} className="w-full border rounded px-3 py-2">
                  <option value="US">미국</option>
                  <option value="KR">한국</option>
                  <option value="JP">일본</option>
                  <option value="GB">영국</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">정렬</label>
                <select value={order} onChange={(e) => setOrder(e.target.value)} className="w-full border rounded px-3 py-2">
                  <option value="viewCount">조회수</option>
                  <option value="relevance">관련성</option>
                  <option value="date">최신 날짜</option>
                  <option value="rating">평점</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">영상 길이</label>
                <select value={keywordDuration} onChange={(e) => setKeywordDuration(e.target.value)} className="w-full border rounded px-3 py-2">
                  <option value="any">전체</option>
                  <option value="short">숏폼 (4분 이하)</option>
                  <option value="medium">중간 (4-20분)</option>
                  <option value="long">롱폼 (20분 이상)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">최소 조회수</label>
                <input type="number" value={keywordMinViews} onChange={(e) => setKeywordMinViews(Number(e.target.value))} className="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">시작 날짜 (선택)</label>
                <input type="date" value={keywordStartDate} onChange={(e) => setKeywordStartDate(e.target.value)} className="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">종료 날짜 (선택)</label>
                <input type="date" value={keywordEndDate} onChange={(e) => setKeywordEndDate(e.target.value)} className="w-full border rounded px-3 py-2" />
              </div>
            </div>
            <button onClick={searchKeywords} disabled={loading || !keywords} className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50">
              {loading ? '검색 중...' : '키워드 검색'}
            </button>
          </div>
        )}
      </div>

      {/* 검색 결과 */}
      {videos.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">{videos.length}개 영상 발견</h2>
          {videos.map((video) => (
            <div key={video.video_id} className="bg-white rounded-lg shadow p-4 flex items-start space-x-4">
              <img src={video.thumbnail} alt={video.title} className="w-48 h-27 object-cover rounded" />
              <div className="flex-1">
                <h3 className="font-semibold text-lg mb-2">{video.title}</h3>
                <p className="text-sm text-gray-600 mb-2">채널: {video.channel_name}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>👁️ {video.view_count.toLocaleString()} 조회</span>
                  <span>⏱️ {Math.floor(video.duration / 60)}분 {video.duration % 60}초</span>
                  <span>{video.caption === 'true' ? '✅ 자막' : '❌ 자막 없음'}</span>
                </div>
                <div className="mt-3 flex space-x-2">
                  <button onClick={() => downloadVideo(video.url)} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    <Download className="w-4 h-4 mr-2" />
                    다운로드
                  </button>
                  <a href={video.url} target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                    YouTube에서 보기
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
