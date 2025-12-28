'use client';

import React, { useState, useEffect } from 'react';

interface Voice {
  voice_id: string;
  name: string;
  language: string;
  description: string;
}

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
  const [voices, setVoices] = useState<Voice[]>([]);
  const [voicesLoading, setVoicesLoading] = useState(false);

  // Phase 4: Voice 목록 가져오기
  useEffect(() => {
    if (settings.provider === 'elevenlabs') {
      fetchVoices();
    }
  }, [settings.provider]);

  const fetchVoices = async () => {
    setVoicesLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/tts/voices`);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      const data = await res.json();
      console.log('Voices loaded:', data.voices?.length || 0);
      setVoices(data.voices || []);
    } catch (error) {
      console.error('Voice 목록 가져오기 실패:', error);
      // 에러 발생 시에도 기본 목록 유지
      setVoices([]);
    } finally {
      setVoicesLoading(false);
    }
  };

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
          <option value="typecast">Typecast (한국어 전문)</option>
        </select>
      </div>

      {/* ElevenLabs 설정 */}
      {settings.provider === 'elevenlabs' && (
        <>
          {/* Phase 4: Voice ID 동적 선택 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              음성 선택 {voicesLoading && <span className="text-xs text-blue-400">(로딩 중...)</span>}
            </label>
            <select
              value={settings.voiceId}
              onChange={(e) => onChange({ ...settings, voiceId: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
              disabled={voicesLoading}
            >
              {voices.length === 0 ? (
                <option value="pNInz6obpgDQGcFmaJgB">Adam (남성) - 기본값 (목록 로딩 실패)</option>
              ) : (
                voices.map((voice) => (
                  <option key={voice.voice_id} value={voice.voice_id}>
                    {voice.name} - {voice.description}
                  </option>
                ))
              )}
            </select>
            {voices.length > 0 ? (
              <p className="text-xs text-gray-400 mt-1">
                ⭐ = 한국어 지원 | 총 {voices.length}개 음성 사용 가능
              </p>
            ) : !voicesLoading ? (
              <p className="text-xs text-yellow-400 mt-1">
                ⚠️ 음성 목록을 불러올 수 없습니다. 백엔드 서버를 확인하세요.
              </p>
            ) : null}
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

      {/* Phase 5: Typecast 설정 (v1 API) */}
      {settings.provider === 'typecast' && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              목소리 선택
            </label>
            <select
              value={settings.voiceId || 'tc_5c3c52ca5827e00008dd7f3a'}
              onChange={(e) => onChange({ ...settings, voiceId: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
            >
              <option value="tc_5c3c52ca5827e00008dd7f3a">Sujin (여성, 밝은)</option>
              <option value="tc_5c3c52caea9791000747155e">Younghee (여성, 부드러운)</option>
              <option value="tc_5c789c337ad86500073a02cd">GeumHee (여성, 전문적인)</option>
              <option value="tc_5c3c52ca5827e00008dd7f38">Minsang (남성, 차분한)</option>
              <option value="tc_5c789c32dabcfa0008b0a38e">Jeongseob (남성, 활기찬)</option>
              <option value="tc_5c3c52ca5827e00008dd7f36">Jinhyuk (남성, 깊은)</option>
              <option value="tc_64b8fa1ef1ff6f997055188e">Geunyeong (여성, 최신)</option>
              <option value="tc_64b8fa40ef03762a5fc0e51d">Geunhyeok (남성, 최신)</option>
            </select>
            <p className="text-xs text-gray-400 mt-1">
              Typecast v1 API (한국어 전문 음성)
            </p>
          </div>
        </>
      )}
    </div>
  );
}
