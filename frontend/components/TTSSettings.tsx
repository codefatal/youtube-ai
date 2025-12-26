'use client';

import React, { useState } from 'react';

interface TTSSettingsProps {
  settings: {
    provider: string;
    voiceId: string;
    stability: number;
    similarityBoost: number;
    style: number;
  };
  onChange: (settings: any) => void;
}

export default function TTSSettings({ settings, onChange }: TTSSettingsProps) {
  const [previewLoading, setPreviewLoading] = useState(false);

  const handlePreview = async () => {
    setPreviewLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/tts/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: '안녕하세요, 이것은 음성 미리듣기입니다.',
          voice_id: settings.voiceId,
          stability: settings.stability,
          similarity_boost: settings.similarityBoost,
          style: settings.style,
        }),
      });

      const blob = await res.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error('미리듣기 실패:', error);
    } finally {
      setPreviewLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 space-y-4">
      <h3 className="text-lg font-semibold text-white mb-4">🗣️ TTS 설정</h3>

      {/* Provider 선택 */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          TTS 제공자
        </label>
        <select
          value={settings.provider}
          onChange={(e) => onChange({ ...settings, provider: e.target.value })}
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
        >
          <option value="gtts">gTTS (무료)</option>
          <option value="elevenlabs">ElevenLabs (프리미엄)</option>
        </select>
      </div>

      {/* ElevenLabs 설정 */}
      {settings.provider === 'elevenlabs' && (
        <>
          {/* Voice ID */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Voice ID
            </label>
            <select
              value={settings.voiceId}
              onChange={(e) => onChange({ ...settings, voiceId: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            >
              <option value="pNInz6obpgDQGcFmaJgB">Adam (Male)</option>
              <option value="EXAVITQu4vr4xnSDxMaL">Bella (Female)</option>
              <option value="FGY2WhTYpPnrIDTdsKH5">Laura (Female)</option>
            </select>
          </div>

          {/* Stability */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              안정성 (Stability): {settings.stability.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.stability}
              onChange={(e) =>
                onChange({ ...settings, stability: parseFloat(e.target.value) })
              }
              className="w-full"
            />
            <p className="text-xs text-gray-400 mt-1">
              낮음 = 감정 풍부, 높음 = 일관성 유지
            </p>
          </div>

          {/* Similarity Boost */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              유사도 (Similarity Boost): {settings.similarityBoost.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.similarityBoost}
              onChange={(e) =>
                onChange({ ...settings, similarityBoost: parseFloat(e.target.value) })
              }
              className="w-full"
            />
          </div>

          {/* Style */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              스타일 (Style): {settings.style.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.style}
              onChange={(e) =>
                onChange({ ...settings, style: parseFloat(e.target.value) })
              }
              className="w-full"
            />
            <p className="text-xs text-gray-400 mt-1">
              0.0 = 자연스러움, 1.0 = 과장됨
            </p>
          </div>

          {/* 미리듣기 버튼 */}
          <button
            onClick={handlePreview}
            disabled={previewLoading}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium disabled:opacity-50"
          >
            {previewLoading ? '생성 중...' : '🎵 미리듣기'}
          </button>
        </>
      )}
    </div>
  );
}
