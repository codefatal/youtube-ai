'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import TTSSettings from '@/components/TTSSettings';
import TemplateSelector from '@/components/TemplateSelector';
import { createDraft } from '@/lib/api';

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
  const [draftLoading, setDraftLoading] = useState(false);

  // Phase 3: Draft 모드로 생성 (편집 가능한 초안)
  const handleCreateDraft = async () => {
    setDraftLoading(true);
    try {
      const draft = await createDraft({
        topic: topic || null,
        format: 'shorts',
        duration,
        style: '정보성',
        collect_assets: true,  // 에셋도 미리 수집
      });

      // 편집 페이지로 리다이렉트
      router.push(`/projects/${draft.draft_id}/edit`);
    } catch (error) {
      console.error('Draft 생성 실패:', error);
      alert('Draft 생성에 실패했습니다.');
    } finally {
      setDraftLoading(false);
    }
  };

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
      <div className="mt-8 space-y-4">
        {/* Phase 3: Draft 모드 버튼 (권장) */}
        <button
          onClick={handleCreateDraft}
          disabled={loading || previewLoading || draftLoading}
          className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 rounded-lg text-white font-bold text-xl disabled:opacity-50 transition shadow-lg"
        >
          {draftLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="animate-spin h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Draft 생성 중...
            </span>
          ) : (
            '✨ 편집 모드로 생성 (권장)'
          )}
        </button>

        <div className="grid grid-cols-2 gap-4">
          {/* 프리뷰 버튼 */}
          <button
            onClick={handlePreview}
            disabled={loading || previewLoading || draftLoading}
            className="px-6 py-3 bg-gray-600 hover:bg-gray-500 rounded-lg text-white font-semibold text-lg disabled:opacity-50 transition"
          >
            {previewLoading ? '프리뷰 생성 중...' : '🎬 프리뷰'}
          </button>

          {/* 영상 생성 버튼 */}
          <button
            onClick={handleCreate}
            disabled={loading || previewLoading || draftLoading}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-semibold text-lg disabled:opacity-50 transition"
          >
            {loading ? '생성 중...' : '⚡ 바로 생성'}
          </button>
        </div>
      </div>

      {/* 안내 문구 */}
      <div className="mt-4 bg-purple-900 bg-opacity-30 border border-purple-700 rounded-lg p-4">
        <p className="text-sm text-purple-200">
          💡 <strong>편집 모드</strong>를 사용하면:
        </p>
        <ul className="mt-2 space-y-1 text-sm text-purple-300 list-disc list-inside">
          <li>스크립트와 이미지를 먼저 확인하고 수정할 수 있습니다</li>
          <li>세그먼트별로 이미지 재생성 및 텍스트 편집이 가능합니다</li>
          <li>최종 확인 후 렌더링하여 시간을 절약할 수 있습니다</li>
        </ul>
      </div>
    </div>
  );
}
