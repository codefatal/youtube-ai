'use client'

import { useState, useEffect } from 'react'
import { Settings, Save } from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    aiProvider: 'auto',
    geminiModel: 'gemini-1.5-flash',
    defaultRegion: 'KR',
    defaultFormat: 'short',
    defaultTone: 'informative',
    ttsLanguage: 'ko',
    ttsSpeed: 1.2,
    ttsPitch: 0
  })

  const [isTestingVoice, setIsTestingVoice] = useState(false)

  // 저장된 설정 불러오기
  useEffect(() => {
    const savedSettings = localStorage.getItem('appSettings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
    }
  }, [])

  const handleSave = () => {
    localStorage.setItem('appSettings', JSON.stringify(settings))
    // 다른 탭/페이지에도 변경 알림
    window.dispatchEvent(new Event('storage'))
    alert('설정이 저장되었습니다')
  }

  const handleTestVoice = async () => {
    setIsTestingVoice(true)
    try {
      const response = await fetch('http://localhost:8000/api/tts/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: '안녕하세요. TTS 테스트 음성입니다.',
          language: settings.ttsLanguage,
          speed: settings.ttsSpeed,
          pitch: settings.ttsPitch
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const audio = new Audio(URL.createObjectURL(blob))
        audio.play()
      } else {
        alert('테스트 음성 생성 실패')
      }
    } catch (error) {
      alert('서버 연결 실패: ' + error)
    } finally {
      setIsTestingVoice(false)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">설정</h1>
        <p className="text-gray-600">애플리케이션 설정 관리</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-6 flex items-center">
          <Settings className="w-5 h-5 mr-2" />
          AI 설정
        </h2>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI 프로바이더
            </label>
            <select
              value={settings.aiProvider}
              onChange={(e) => setSettings({...settings, aiProvider: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="auto">Auto (Gemini 우선, 실패 시 Claude)</option>
              <option value="gemini">Gemini 전용</option>
              <option value="claude">Claude 전용</option>
            </select>
            <p className="mt-2 text-sm text-gray-500">
              Auto 모드를 권장합니다. Gemini 무료 티어를 최대한 활용합니다.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gemini 모델
            </label>
            <select
              value={settings.geminiModel}
              onChange={(e) => setSettings({...settings, geminiModel: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="gemini-1.5-flash">Gemini 1.5 Flash (빠르고 안정적)</option>
              <option value="gemini-2.5-flash">Gemini 2.5 Flash (최신)</option>
              <option value="gemini-2.5-pro">Gemini 2.5 Pro (고급, 유료)</option>
            </select>
          </div>

          <div className="pt-6 border-t">
            <h3 className="text-lg font-semibold mb-4">기본 설정</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  기본 지역
                </label>
                <select
                  value={settings.defaultRegion}
                  onChange={(e) => setSettings({...settings, defaultRegion: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="KR">한국 (KR)</option>
                  <option value="US">미국 (US)</option>
                  <option value="JP">일본 (JP)</option>
                  <option value="GB">영국 (GB)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  기본 영상 형식
                </label>
                <select
                  value={settings.defaultFormat}
                  onChange={(e) => setSettings({...settings, defaultFormat: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="short">숏폼 (Shorts)</option>
                  <option value="long">롱폼 (일반 영상)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  기본 대본 톤
                </label>
                <select
                  value={settings.defaultTone}
                  onChange={(e) => setSettings({...settings, defaultTone: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="informative">정보 전달형</option>
                  <option value="entertaining">오락형</option>
                  <option value="educational">교육형</option>
                </select>
              </div>
            </div>
          </div>

          {/* TTS 설정 */}
          <div className="pt-6 border-t">
            <h3 className="text-lg font-semibold mb-4">TTS (음성 합성) 설정</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  TTS 언어
                </label>
                <select
                  value={settings.ttsLanguage}
                  onChange={(e) => setSettings({...settings, ttsLanguage: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="ko">한국어 (Korean)</option>
                  <option value="en">영어 (English)</option>
                  <option value="ja">일본어 (Japanese)</option>
                  <option value="zh-CN">중국어 간체 (Chinese Simplified)</option>
                  <option value="es">스페인어 (Spanish)</option>
                  <option value="fr">프랑스어 (French)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  속도 조절: {settings.ttsSpeed}x
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  value={settings.ttsSpeed}
                  onChange={(e) => setSettings({...settings, ttsSpeed: parseFloat(e.target.value)})}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>느림 (0.5x)</span>
                  <span>보통 (1.0x)</span>
                  <span>빠름 (2.0x)</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  피치 조절: {settings.ttsPitch > 0 ? '+' : ''}{settings.ttsPitch}
                </label>
                <input
                  type="range"
                  min="-5"
                  max="5"
                  step="1"
                  value={settings.ttsPitch}
                  onChange={(e) => setSettings({...settings, ttsPitch: parseInt(e.target.value)})}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>낮음 (-5)</span>
                  <span>보통 (0)</span>
                  <span>높음 (+5)</span>
                </div>
              </div>

              <div>
                <button
                  onClick={handleTestVoice}
                  disabled={isTestingVoice}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {isTestingVoice ? '테스트 중...' : '🎤 테스트 음성 재생'}
                </button>
                <p className="mt-2 text-xs text-gray-500">
                  현재 설정으로 "안녕하세요. TTS 테스트 음성입니다."를 재생합니다.
                </p>
              </div>
            </div>
          </div>

          <div className="pt-6">
            <button
              onClick={handleSave}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 flex items-center justify-center"
            >
              <Save className="w-5 h-5 mr-2" />
              설정 저장
            </button>
          </div>
        </div>
      </div>

      {/* API 키 관리 안내 */}
      <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-yellow-900 mb-2">API 키 관리</h3>
        <p className="text-yellow-800 text-sm mb-4">
          API 키는 서버의 <code className="bg-yellow-100 px-2 py-1 rounded">.env</code> 파일에서 관리됩니다.
        </p>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• <strong>GEMINI_API_KEY</strong>: Gemini API 키</li>
          <li>• <strong>ANTHROPIC_API_KEY</strong>: Claude API 키</li>
          <li>• <strong>YOUTUBE_API_KEY</strong>: YouTube Data API 키</li>
        </ul>
      </div>
    </div>
  )
}
