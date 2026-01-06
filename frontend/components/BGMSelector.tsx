'use client'

import { useState, useEffect, useRef } from 'react'
import { Play, Pause, Check, Music } from 'lucide-react'

interface BGMItem {
  name: string
  mood: string
  file_path: string
  duration: number
  volume: number
  artist: string
  license: string
  url: string
}

interface BGMCatalog {
  version: string
  source: string
  license: string
  total_count: number
  moods: string[]
  bgm_list: BGMItem[]
}

interface BGMSelectorProps {
  onSelect: (bgm: BGMItem | null) => void
  selectedBGM?: BGMItem | null
  volume?: number
  onVolumeChange?: (volume: number) => void
  showVolumeControl?: boolean
}

export default function BGMSelector({
  onSelect,
  selectedBGM,
  volume = 0.3,
  onVolumeChange,
  showVolumeControl = true
}: BGMSelectorProps) {
  const [catalog, setCatalog] = useState<BGMCatalog | null>(null)
  const [selectedMood, setSelectedMood] = useState<string>('all')
  const [playingBGM, setPlayingBGM] = useState<string | null>(null)
  const [currentVolume, setCurrentVolume] = useState(volume)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // BGM catalog 로드
  useEffect(() => {
    fetch('/assets/bgm/bgm_catalog.json')
      .then(res => res.json())
      .then(data => setCatalog(data))
      .catch(err => console.error('Failed to load BGM catalog:', err))
  }, [])

  // 볼륨 변경 핸들러
  const handleVolumeChange = (newVolume: number) => {
    setCurrentVolume(newVolume)
    if (audioRef.current) {
      audioRef.current.volume = newVolume
    }
    if (onVolumeChange) {
      onVolumeChange(newVolume)
    }
  }

  // 오디오 재생/일시정지
  const togglePlay = (bgm: BGMItem) => {
    const audioPath = `/assets/bgm/${bgm.file_path}`

    if (playingBGM === bgm.file_path) {
      // 현재 재생 중인 BGM을 클릭하면 일시정지
      audioRef.current?.pause()
      setPlayingBGM(null)
    } else {
      // 다른 BGM 재생
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.src = audioPath
        audioRef.current.volume = currentVolume
        audioRef.current.play()
        setPlayingBGM(bgm.file_path)
      }
    }
  }

  // 오디오 종료 시 상태 초기화
  useEffect(() => {
    const audio = audioRef.current
    if (audio) {
      const handleEnded = () => setPlayingBGM(null)
      audio.addEventListener('ended', handleEnded)
      return () => audio.removeEventListener('ended', handleEnded)
    }
  }, [])

  if (!catalog) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-500">Loading BGM catalog...</p>
      </div>
    )
  }

  // 필터링된 BGM 리스트
  const filteredBGM = selectedMood === 'all'
    ? catalog.bgm_list
    : catalog.bgm_list.filter(bgm => bgm.mood === selectedMood)

  const moodColors: Record<string, string> = {
    happy: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    sad: 'bg-blue-100 text-blue-700 border-blue-300',
    energetic: 'bg-red-100 text-red-700 border-red-300',
    calm: 'bg-green-100 text-green-700 border-green-300',
    tense: 'bg-purple-100 text-purple-700 border-purple-300',
    mysterious: 'bg-gray-100 text-gray-700 border-gray-300',
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-2 mb-4">
        <Music className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold">BGM Selection</h3>
      </div>

      {/* 라이선스 정보 */}
      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
        <p className="text-blue-800">
          <strong>Source:</strong> {catalog.source}
        </p>
        <p className="text-blue-700 mt-1">
          <strong>License:</strong> {catalog.license}
        </p>
      </div>

      {/* 분위기 필터 탭 */}
      <div className="flex flex-wrap gap-2 mb-4">
        <button
          onClick={() => setSelectedMood('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedMood === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All ({catalog.total_count})
        </button>
        {catalog.moods.map(mood => {
          const count = catalog.bgm_list.filter(bgm => bgm.mood === mood).length
          return (
            <button
              key={mood}
              onClick={() => setSelectedMood(mood)}
              className={`px-4 py-2 rounded-lg font-medium capitalize transition-colors ${
                selectedMood === mood
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {mood} ({count})
            </button>
          )
        })}
      </div>

      {/* BGM 리스트 */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredBGM.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            No BGM found for this mood.
          </p>
        ) : (
          filteredBGM.map((bgm, index) => {
            const isPlaying = playingBGM === bgm.file_path
            const isSelected = selectedBGM?.file_path === bgm.file_path

            return (
              <div
                key={index}
                className={`p-4 border rounded-lg transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  {/* BGM 정보 */}
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{bgm.name}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`px-2 py-1 text-xs rounded border capitalize ${
                          moodColors[bgm.mood] || 'bg-gray-100 text-gray-700 border-gray-300'
                        }`}
                      >
                        {bgm.mood}
                      </span>
                      <span className="text-sm text-gray-600">
                        by {bgm.artist}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Source:{' '}
                      <a
                        href={bgm.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {bgm.artist}
                      </a>
                    </p>
                  </div>

                  {/* 컨트롤 버튼 */}
                  <div className="flex items-center gap-2">
                    {/* 미리듣기 버튼 */}
                    <button
                      onClick={() => togglePlay(bgm)}
                      className={`p-2 rounded-lg transition-colors ${
                        isPlaying
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                      title={isPlaying ? 'Pause' : 'Play'}
                    >
                      {isPlaying ? (
                        <Pause className="w-4 h-4" />
                      ) : (
                        <Play className="w-4 h-4" />
                      )}
                    </button>

                    {/* 선택 버튼 */}
                    <button
                      onClick={() => onSelect(isSelected ? null : bgm)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        isSelected
                          ? 'bg-green-600 text-white hover:bg-green-700'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      {isSelected ? (
                        <span className="flex items-center gap-1">
                          <Check className="w-4 h-4" />
                          Selected
                        </span>
                      ) : (
                        'Select'
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* 숨겨진 오디오 플레이어 */}
      <audio ref={audioRef} className="hidden" />

      {/* 볼륨 조절 */}
      {showVolumeControl && (
        <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium text-gray-700 min-w-[80px]">
              Volume:
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={currentVolume}
              onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <span className="text-sm font-medium text-gray-700 min-w-[50px] text-right">
              {Math.round(currentVolume * 100)}%
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Adjust the volume and click play to preview
          </p>
        </div>
      )}

      {/* 선택된 BGM 표시 */}
      {selectedBGM && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
          <p className="text-sm text-green-800">
            <strong>Selected BGM:</strong> {selectedBGM.name} ({selectedBGM.mood})
          </p>
        </div>
      )}
    </div>
  )
}
