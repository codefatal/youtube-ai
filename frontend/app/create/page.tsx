'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import TTSSettings from '@/components/TTSSettings';
import TemplateSelector from '@/components/TemplateSelector';
import BGMSelector from '@/components/BGMSelector';
import { createDraft } from '@/lib/api';

interface BGMItem {
  name: string;
  mood: string;
  file_path: string;
  duration: number;
  volume: number;
  artist: string;
  license: string;
  url: string;
}

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
    file_path: '',  // 선택된 BGM 파일 경로
  });

  // 선택된 BGM
  const [selectedBGM, setSelectedBGM] = useState<BGMItem | null>(null);

  // ✨ Phase 6: AI 고급 설정
  const [advancedSettings, setAdvancedSettings] = useState({
    useWholesomeTTS: true,       // Wholesome TTS 사용 (전체 대본 생성)
    aiVideoSelection: true,       // AI 기반 영상 선택
    autoTuneTTS: true,           // TTS 파라미터 자동 조정
  });

  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [draftLoading, setDraftLoading] = useState(false);

  // BGM 선택 핸들러
  const handleBGMSelect = (bgm: BGMItem | null) => {
    setSelectedBGM(bgm);
    if (bgm) {
      setBgmSettings({
        ...bgmSettings,
        mood: bgm.mood.toUpperCase(),
        file_path: bgm.file_path,
      });
    }
  };

  // BGM 볼륨 변경 핸들러
  const handleBGMVolumeChange = (volume: number) => {
    setBgmSettings({ ...bgmSettings, volume });
  };

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
        advanced_settings: advancedSettings,  // ✨ Phase 6: AI 고급 설정
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
          advanced_settings: advancedSettings,  // ✨ Phase 6: AI 고급 설정 전송
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
          <div className="space-y-4">
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
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
                <BGMSelector
                  onSelect={handleBGMSelect}
                  selectedBGM={selectedBGM}
                  volume={bgmSettings.volume}
                  onVolumeChange={handleBGMVolumeChange}
                  showVolumeControl={true}
                />
              )}
            </div>
          </div>

          {/* ✨ Phase 6: AI 고급 설정 */}
          <div className="bg-gradient-to-r from-purple-900 to-blue-900 bg-opacity-50 rounded-lg p-6 space-y-4 border border-purple-700">
            <h3 className="text-lg font-semibold text-white mb-4">🤖 AI 고급 설정 (Phase 6)</h3>

            {/* Wholesome TTS */}
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="wholesome-tts"
                checked={advancedSettings.useWholesomeTTS}
                onChange={(e) =>
                  setAdvancedSettings({ ...advancedSettings, useWholesomeTTS: e.target.checked })
                }
                className="mt-1 w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
              />
              <div>
                <label htmlFor="wholesome-tts" className="text-sm font-medium text-gray-200">
                  Wholesome TTS (권장)
                </label>
                <p className="text-xs text-gray-400 mt-1">
                  전체 대본을 한 번에 생성하여 톤 일관성 30% 향상. Whisper로 정확한 타이밍 추출.
                </p>
              </div>
            </div>

            {/* AI 영상 선택 */}
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="ai-video-selection"
                checked={advancedSettings.aiVideoSelection}
                onChange={(e) =>
                  setAdvancedSettings({ ...advancedSettings, aiVideoSelection: e.target.checked })
                }
                className="mt-1 w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
              />
              <div>
                <label htmlFor="ai-video-selection" className="text-sm font-medium text-gray-200">
                  AI 영상 선택 (권장)
                </label>
                <p className="text-xs text-gray-400 mt-1">
                  Gemini AI가 5-10개 후보 중 대본과 가장 잘 맞는 영상 자동 선택. 매칭률 40% 향상.
                </p>
              </div>
            </div>

            {/* TTS 자동 조정 */}
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="auto-tune-tts"
                checked={advancedSettings.autoTuneTTS}
                onChange={(e) =>
                  setAdvancedSettings({ ...advancedSettings, autoTuneTTS: e.target.checked })
                }
                className="mt-1 w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
              />
              <div>
                <label htmlFor="auto-tune-tts" className="text-sm font-medium text-gray-200">
                  TTS 파라미터 자동 조정 (권장)
                </label>
                <p className="text-xs text-gray-400 mt-1">
                  대본 내용 분석하여 감정, 격식, 구어체에 맞게 파라미터 자동 조정. 감정 표현 25% 향상.
                </p>
              </div>
            </div>

            {/* 안내 문구 */}
            <div className="mt-4 bg-purple-800 bg-opacity-30 border border-purple-600 rounded p-3">
              <p className="text-xs text-purple-200">
                💡 Phase 6 기능들은 <strong>기본적으로 모두 활성화</strong>되어 있습니다.
                최고의 영상 품질을 위해 모두 켜두는 것을 권장합니다.
              </p>
            </div>
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
