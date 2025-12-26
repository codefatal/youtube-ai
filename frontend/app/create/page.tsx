'use client';

import React, { useState } from 'react';
import TTSSettings from '@/components/TTSSettings';

export default function CreatePage() {
  const [topic, setTopic] = useState('');
  const [duration, setDuration] = useState(60);
  const [template, setTemplate] = useState('basic');
  const [ttsSettings, setTtsSettings] = useState({
    provider: 'gtts',
    voiceId: 'pNInz6obpgDQGcFmaJgB',
    stability: 0.5,
    similarityBoost: 0.75,
    style: 0.0,
  });
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/videos/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic || null,
          format: 'shorts',
          duration,
          upload: false,
          template,
          tts_settings: ttsSettings,
        }),
      });

      const data = await res.json();
      if (data.success) {
        alert(`영상 생성 시작! Job ID: ${data.data.job_id}`);
      } else {
        alert(`오류: ${data.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('영상 생성 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-8">✨ 영상 생성</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 왼쪽: 기본 설정 */}
        <div className="space-y-6">
          {/* 주제 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              주제 (비워두면 AI가 자동 생성)
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="예: Python 프로그래밍 팁"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>

          {/* 길이 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              영상 길이: {duration}초
            </label>
            <input
              type="range"
              min="30"
              max="180"
              step="10"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>30초</span>
              <span>180초</span>
            </div>
          </div>

          {/* 템플릿 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              템플릿
            </label>
            <select
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            >
              <option value="basic">기본형</option>
              <option value="documentary">다큐형</option>
              <option value="entertainment">예능형</option>
            </select>
          </div>
        </div>

        {/* 오른쪽: TTS 설정 */}
        <div>
          <TTSSettings settings={ttsSettings} onChange={setTtsSettings} />
        </div>
      </div>

      {/* 생성 버튼 */}
      <button
        onClick={handleCreate}
        disabled={loading}
        className="mt-8 w-full px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-semibold text-lg disabled:opacity-50"
      >
        {loading ? '생성 중...' : '🎬 영상 생성 시작'}
      </button>
    </div>
  );
}
