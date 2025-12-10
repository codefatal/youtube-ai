'use client'

import { useState } from 'react'
import { Settings, Save } from 'lucide-react'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    aiProvider: 'auto',
    geminiModel: 'gemini-1.5-flash',
    defaultRegion: 'KR',
    defaultFormat: 'short',
    defaultTone: 'informative'
  })

  const handleSave = () => {
    // TODO: 설정을 로컬 스토리지나 백엔드에 저장
    localStorage.setItem('appSettings', JSON.stringify(settings))
    alert('설정이 저장되었습니다')
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
