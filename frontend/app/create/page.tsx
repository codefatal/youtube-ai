'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import TTSSettings from '@/components/TTSSettings';
import TemplateSelector from '@/components/TemplateSelector';

export default function CreatePage() {
  const router = useRouter();
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

  // Phase 5: BGM 설정
  const [bgmSettings, setBgmSettings] = useState({
    enabled: true,
    mood: 'auto',
    volume: 0.3,
  });

  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);

  const handleCreate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/videos/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic || null,
          format: 'shorts',
          duration,
          upload: false,
          template: template,  // TemplateSelector에서 선택한 템플릿 사용
          tts_settings: ttsSettings,
          bgm_settings: bgmSettings,  // Phase 5: BGM 설정 전송
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

  // Phase 3: 프리뷰 생성
  const handlePreview = async () => {
    if (!topic.trim()) {
      alert('프리뷰를 생성하려면 주제를 입력해주세요.');
      return;
    }

    setPreviewLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/preview/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          format: 'shorts',
          duration,
          template_name: template,
          low_resolution: true,
          tts_settings: ttsSettings,
        }),
      });

      const data = await res.json();
      if (data.success) {
        // 프리뷰 페이지로 이동
        router.push(`/preview?job_id=${data.job_id}`);
      } else {
        alert(`오류: ${data.detail || '프리뷰 생성 실패'}`);
      }
    } catch (error) {
      console.error('프리뷰 생성 실패:', error);
      alert('프리뷰 생성 중 오류가 발생했습니다.');
    } finally {
      setPreviewLoading(false);
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

          {/* 템플릿 선택 */}
          <TemplateSelector value={template} onChange={setTemplate} />
        </div>

        {/* 오른쪽: TTS 설정 */}
        <div className="space-y-6">
          <TTSSettings settings={ttsSettings} onChange={setTtsSettings} />

          {/* Phase 5: BGM 설정 */}
          <div className="bg-gray-800 rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-semibold text-white mb-4">🎵 BGM 설정</h3>

            {/* BGM 활성화 */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="bgm-enabled"
                checked={bgmSettings.enabled}
                onChange={(e) =>
                  setBgmSettings({ ...bgmSettings, enabled: e.target.checked })
                }
                className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="bgm-enabled" className="text-sm font-medium text-gray-300">
                BGM 사용
              </label>
            </div>

            {bgmSettings.enabled && (
              <>
                {/* 분위기 선택 */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    분위기
                  </label>
                  <select
                    value={bgmSettings.mood}
                    onChange={(e) =>
                      setBgmSettings({ ...bgmSettings, mood: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
                  >
                    <option value="auto">자동 선택 (AI 추론)</option>
                    <option value="HAPPY">행복한 (밝고 즐거운)</option>
                    <option value="SAD">슬픈 (차분하고 감성적인)</option>
                    <option value="ENERGETIC">활기찬 (빠르고 역동적인)</option>
                    <option value="CALM">차분한 (편안하고 여유로운)</option>
                    <option value="TENSE">긴장감 있는 (긴박하고 스릴)</option>
                    <option value="MYSTERIOUS">신비로운 (몽환적이고 신비)</option>
                  </select>
                </div>

                {/* 볼륨 조절 */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    BGM 볼륨: {(bgmSettings.volume * 100).toFixed(0)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={bgmSettings.volume}
                    onChange={(e) =>
                      setBgmSettings({
                        ...bgmSettings,
                        volume: parseFloat(e.target.value),
                      })
                    }
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>0%</span>
                    <span>100%</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 생성 버튼 */}
      <div className="mt-8 flex gap-4">
        {/* 프리뷰 버튼 */}
        <button
          onClick={handlePreview}
          disabled={loading || previewLoading}
          className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-500 rounded-lg text-white font-semibold text-lg disabled:opacity-50 transition"
        >
          {previewLoading ? '프리뷰 생성 중...' : '🎬 프리뷰 먼저 보기'}
        </button>

        {/* 영상 생성 버튼 */}
        <button
          onClick={handleCreate}
          disabled={loading || previewLoading}
          className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-semibold text-lg disabled:opacity-50 transition"
        >
          {loading ? '생성 중...' : '⚡ 바로 생성'}
        </button>
      </div>

      {/* 안내 문구 */}
      <p className="mt-4 text-center text-sm text-gray-400">
        💡 프리뷰를 먼저 확인하고 조정한 후 최종 렌더링하는 것을 권장합니다.
      </p>
    </div>
  );
}
