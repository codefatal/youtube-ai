'use client';

import { useParams, useRouter } from 'next/navigation';
import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save, Trash2 } from 'lucide-react';
import Link from 'next/link';

interface AccountSettings {
  tts_provider: string;
  tts_voice_id: string | null;
  tts_stability: number;
  tts_similarity_boost: number;
  tts_style: number;
  default_format: string;
  default_duration: number;
  bgm_enabled: boolean;
  bgm_volume: number;
}

interface JobHistory {
  id: number;
  job_id: string;
  topic: string;
  status: string;
  format: string;
  duration: number;
  output_video_path: string | null;
  youtube_url: string | null;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
}

interface Account {
  id: number;
  channel_name: string;
  channel_type: string;
  upload_schedule: string | null;
  is_active: boolean;
  created_at: string;
  settings: AccountSettings | null;
  jobs: JobHistory[];
}

export default function AccountDetailPage() {
  const params = useParams();
  const router = useRouter();
  const accountId = params.id as string;

  const [account, setAccount] = useState<Account | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // 편집 가능한 필드
  const [uploadSchedule, setUploadSchedule] = useState('');
  const [settings, setSettings] = useState<AccountSettings>({
    tts_provider: 'gtts',
    tts_voice_id: null,
    tts_stability: 0.5,
    tts_similarity_boost: 0.75,
    tts_style: 0.0,
    default_format: 'shorts',
    default_duration: 60,
    bgm_enabled: false,
    bgm_volume: 0.3,
  });

  useEffect(() => {
    fetchAccount();
  }, [accountId]);

  const fetchAccount = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/accounts/${accountId}`
      );

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setAccount(data);
      setUploadSchedule(data.upload_schedule || '');

      if (data.settings) {
        setSettings(data.settings);
      }
    } catch (error) {
      console.error('계정 로드 실패:', error);
      alert('계정을 찾을 수 없습니다.');
      router.push('/accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      // 1. Update account (upload_schedule)
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/accounts/${accountId}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ upload_schedule: uploadSchedule || null }),
        }
      );

      // 2. Update settings
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/accounts/${accountId}/settings`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(settings),
        }
      );

      alert('설정이 저장되었습니다.');
      fetchAccount(); // Refresh
    } catch (error) {
      alert(`저장 실패: ${error}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`'${account?.channel_name}' 계정을 삭제하시겠습니까?`)) return;

    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/accounts/${accountId}`,
        { method: 'DELETE' }
      );
      alert('계정이 삭제되었습니다.');
      router.push('/accounts');
    } catch (error) {
      alert(`삭제 실패: ${error}`);
    }
  };

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <div className="text-gray-400">로딩 중...</div>
      </div>
    );
  }

  if (!account) {
    return null;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* 헤더 */}
      <div className="mb-8">
        <Link
          href="/accounts"
          className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-4"
        >
          <ArrowLeft size={20} />
          계정 목록으로 돌아가기
        </Link>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              {account.channel_name}
            </h1>
            <div className="flex items-center gap-4 text-sm text-gray-400">
              <span>채널 타입: {account.channel_type}</span>
              <span>•</span>
              <span>생성일: {new Date(account.created_at).toLocaleDateString('ko-KR')}</span>
              <span>•</span>
              <span className={account.is_active ? 'text-green-400' : 'text-red-400'}>
                {account.is_active ? '활성' : '비활성'}
              </span>
            </div>
          </div>

          <button
            onClick={handleDelete}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg flex items-center gap-2"
          >
            <Trash2 size={16} />
            계정 삭제
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 왼쪽: 설정 */}
        <div className="space-y-6">
          {/* 스케줄 설정 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">📅 업로드 스케줄</h2>
            <input
              type="text"
              value={uploadSchedule}
              onChange={(e) => setUploadSchedule(e.target.value)}
              placeholder="예: 0 10 * * * (매일 오전 10시)"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-blue-500 focus:outline-none"
            />
            <p className="mt-2 text-xs text-gray-400">
              Cron 형식으로 입력 (비워두면 수동 업로드)
            </p>
          </div>

          {/* TTS 설정 */}
          <div className="bg-gray-800 rounded-lg p-6 space-y-4">
            <h2 className="text-xl font-semibold text-white mb-4">🗣️ TTS 설정</h2>

            {/* TTS Provider */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                TTS 제공자
              </label>
              <select
                value={settings.tts_provider}
                onChange={(e) => setSettings({ ...settings, tts_provider: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
              >
                <option value="gtts">gTTS (무료)</option>
                <option value="elevenlabs">ElevenLabs (프리미엄)</option>
                <option value="typecast">Typecast (한국어 전문)</option>
              </select>
            </div>

            {/* ElevenLabs 설정 */}
            {settings.tts_provider === 'elevenlabs' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Voice ID
                  </label>
                  <input
                    type="text"
                    value={settings.tts_voice_id || 'pNInz6obpgDQGcFmaJgB'}
                    onChange={(e) =>
                      setSettings({ ...settings, tts_voice_id: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Stability: {settings.tts_stability.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={settings.tts_stability}
                    onChange={(e) =>
                      setSettings({ ...settings, tts_stability: parseFloat(e.target.value) })
                    }
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Similarity Boost: {settings.tts_similarity_boost.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={settings.tts_similarity_boost}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        tts_similarity_boost: parseFloat(e.target.value),
                      })
                    }
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Style: {settings.tts_style.toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={settings.tts_style}
                    onChange={(e) =>
                      setSettings({ ...settings, tts_style: parseFloat(e.target.value) })
                    }
                    className="w-full"
                  />
                </div>
              </>
            )}
          </div>

          {/* BGM 설정 */}
          <div className="bg-gray-800 rounded-lg p-6 space-y-4">
            <h2 className="text-xl font-semibold text-white mb-4">🎵 BGM 설정</h2>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="bgm-enabled"
                checked={settings.bgm_enabled}
                onChange={(e) =>
                  setSettings({ ...settings, bgm_enabled: e.target.checked })
                }
                className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded"
              />
              <label htmlFor="bgm-enabled" className="text-sm font-medium text-gray-300">
                BGM 사용
              </label>
            </div>

            {settings.bgm_enabled && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  BGM 볼륨: {(settings.bgm_volume * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={settings.bgm_volume}
                  onChange={(e) =>
                    setSettings({ ...settings, bgm_volume: parseFloat(e.target.value) })
                  }
                  className="w-full"
                />
              </div>
            )}
          </div>

          {/* 기본 영상 설정 */}
          <div className="bg-gray-800 rounded-lg p-6 space-y-4">
            <h2 className="text-xl font-semibold text-white mb-4">🎬 기본 영상 설정</h2>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                기본 포맷
              </label>
              <select
                value={settings.default_format}
                onChange={(e) => setSettings({ ...settings, default_format: e.target.value })}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
              >
                <option value="shorts">Shorts (1080x1920)</option>
                <option value="landscape">Landscape (1920x1080)</option>
                <option value="square">Square (1080x1080)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                기본 길이: {settings.default_duration}초
              </label>
              <input
                type="range"
                min="30"
                max="180"
                step="10"
                value={settings.default_duration}
                onChange={(e) =>
                  setSettings({ ...settings, default_duration: parseInt(e.target.value) })
                }
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>30초</span>
                <span>180초</span>
              </div>
            </div>
          </div>

          {/* 저장 버튼 */}
          <button
            onClick={handleSaveSettings}
            disabled={saving}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Save size={20} />
            {saving ? '저장 중...' : '설정 저장'}
          </button>
        </div>

        {/* 오른쪽: 작업 이력 */}
        <div>
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              📜 작업 이력 ({account.jobs.length}개)
            </h2>

            {account.jobs.length === 0 ? (
              <p className="text-gray-400 text-sm">아직 작업 이력이 없습니다.</p>
            ) : (
              <div className="space-y-3 max-h-[800px] overflow-y-auto">
                {account.jobs.map((job) => (
                  <div
                    key={job.id}
                    className="p-4 bg-gray-700 rounded-lg hover:bg-gray-650 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h3 className="font-semibold text-white text-sm">{job.topic}</h3>
                        <p className="text-xs text-gray-400 mt-1">
                          Job ID: {job.job_id}
                        </p>
                      </div>
                      <StatusBadge status={job.status} />
                    </div>

                    <div className="text-xs text-gray-400 space-y-1">
                      <p>
                        포맷: {job.format} | 길이: {job.duration}초
                      </p>
                      <p>시작: {new Date(job.started_at).toLocaleString('ko-KR')}</p>
                      {job.completed_at && (
                        <p>완료: {new Date(job.completed_at).toLocaleString('ko-KR')}</p>
                      )}
                    </div>

                    {job.youtube_url && (
                      <a
                        href={job.youtube_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-2 inline-block text-xs text-blue-400 hover:text-blue-300"
                      >
                        🎥 YouTube에서 보기
                      </a>
                    )}

                    {job.error_message && (
                      <p className="mt-2 text-xs text-red-400">
                        오류: {job.error_message}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    COMPLETED: 'bg-green-100 text-green-800',
    FAILED: 'bg-red-100 text-red-800',
    PLANNING: 'bg-blue-100 text-blue-800',
    COLLECTING_ASSETS: 'bg-yellow-100 text-yellow-800',
    EDITING: 'bg-purple-100 text-purple-800',
    UPLOADING: 'bg-indigo-100 text-indigo-800',
  };

  const labels: Record<string, string> = {
    COMPLETED: '완료',
    FAILED: '실패',
    PLANNING: '기획 중',
    COLLECTING_ASSETS: '에셋 수집 중',
    EDITING: '편집 중',
    UPLOADING: '업로드 중',
  };

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {labels[status] || status}
    </span>
  );
}
