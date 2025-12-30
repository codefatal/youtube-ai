'use client';

import React, { useState, useEffect, useCallback } from 'react';

interface PreviewJob {
  job_id: string;
  status: string;
  progress: number;
  preview_path?: string;
  segments?: SegmentInfo[];
  metadata?: PreviewMetadata;
  error?: string;
  created_at: string;
  updated_at: string;
}

interface SegmentInfo {
  index: number;
  text: string;
  keyword: string;
  duration: number;
}

interface PreviewMetadata {
  title: string;
  description: string;
  tags: string[];
  duration: number;
  segment_count: number;
  resolution: string;
}

export default function PreviewPage() {
  const [topic, setTopic] = useState('');
  const [duration, setDuration] = useState(60);
  const [template, setTemplate] = useState('basic');
  const [lowResolution, setLowResolution] = useState(true);
  const [loading, setLoading] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<PreviewJob | null>(null);
  const [recentPreviews, setRecentPreviews] = useState<any[]>([]);
  const [selectedSegment, setSelectedSegment] = useState<number | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // 최근 프리뷰 목록 로드
  useEffect(() => {
    loadRecentPreviews();
  }, []);

  const loadRecentPreviews = async () => {
    try {
      const res = await fetch(`${API_URL}/api/preview/list/recent?limit=5`);
      const data = await res.json();
      if (data.success) {
        setRecentPreviews(data.previews);
      }
    } catch (error) {
      console.error('최근 프리뷰 로드 실패:', error);
    }
  };

  // 프리뷰 상태 폴링
  const pollPreviewStatus = useCallback(async (jobId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/preview/${jobId}`);
      const data: PreviewJob = await res.json();
      setPreviewData(data);

      if (data.status === 'generating' || data.status === 'adjusting' || data.status === 'finalizing') {
        // 아직 진행 중이면 계속 폴링
        setTimeout(() => pollPreviewStatus(jobId), 2000);
      } else {
        setLoading(false);
        loadRecentPreviews();
      }
    } catch (error) {
      console.error('상태 조회 실패:', error);
      setLoading(false);
    }
  }, [API_URL]);

  // 프리뷰 생성
  const handleGeneratePreview = async () => {
    if (!topic.trim()) {
      alert('주제를 입력해주세요.');
      return;
    }

    setLoading(true);
    setPreviewData(null);

    try {
      const res = await fetch(`${API_URL}/api/preview/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          format: 'shorts',
          duration,
          template_name: template,
          low_resolution: lowResolution,
        }),
      });

      const data = await res.json();
      if (data.success) {
        setCurrentJobId(data.job_id);
        pollPreviewStatus(data.job_id);
      } else {
        alert(`오류: ${data.detail || '프리뷰 생성 실패'}`);
        setLoading(false);
      }
    } catch (error) {
      console.error('프리뷰 생성 실패:', error);
      setLoading(false);
    }
  };

  // 최종 렌더링
  const handleFinalize = async () => {
    if (!currentJobId) return;

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/preview/finalize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: currentJobId,
          upload: false,
        }),
      });

      const data = await res.json();
      if (data.success) {
        pollPreviewStatus(currentJobId);
      } else {
        alert('최종 렌더링 실패');
        setLoading(false);
      }
    } catch (error) {
      console.error('최종 렌더링 실패:', error);
      setLoading(false);
    }
  };

  // 기존 프리뷰 로드
  const loadPreview = (jobId: string) => {
    setCurrentJobId(jobId);
    pollPreviewStatus(jobId);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400';
      case 'failed': return 'text-red-400';
      case 'generating':
      case 'adjusting':
      case 'finalizing': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return '대기 중';
      case 'generating': return '생성 중';
      case 'completed': return '완료';
      case 'failed': return '실패';
      case 'adjusting': return '조정 중';
      case 'finalizing': return '최종 렌더링 중';
      case 'finalized': return '최종 완료';
      default: return status;
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-8">Preview & Review</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 왼쪽: 프리뷰 생성 */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">프리뷰 생성</h2>

            <div className="space-y-4">
              {/* 주제 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">주제</label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="영상 주제를 입력하세요"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                />
              </div>

              {/* 길이 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  길이: {duration}초
                </label>
                <input
                  type="range"
                  min={15}
                  max={120}
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* 템플릿 */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">템플릿</label>
                <select
                  value={template}
                  onChange={(e) => setTemplate(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                >
                  <option value="basic">Basic</option>
                  <option value="documentary">Documentary</option>
                  <option value="entertainment">Entertainment</option>
                </select>
              </div>

              {/* 저해상도 옵션 */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="lowRes"
                  checked={lowResolution}
                  onChange={(e) => setLowResolution(e.target.checked)}
                  className="mr-2"
                />
                <label htmlFor="lowRes" className="text-sm text-gray-300">
                  저해상도 프리뷰 (빠른 생성)
                </label>
              </div>

              <button
                onClick={handleGeneratePreview}
                disabled={loading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-semibold rounded-lg transition"
              >
                {loading ? '생성 중...' : 'Preview 생성'}
              </button>
            </div>
          </div>

          {/* 최근 프리뷰 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-white mb-4">최근 프리뷰</h2>
            <div className="space-y-2">
              {recentPreviews.map((preview) => (
                <button
                  key={preview.job_id}
                  onClick={() => loadPreview(preview.job_id)}
                  className="w-full text-left p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
                >
                  <div className="text-sm text-white truncate">{preview.topic}</div>
                  <div className="flex justify-between text-xs mt-1">
                    <span className={getStatusColor(preview.status)}>
                      {getStatusText(preview.status)}
                    </span>
                    <span className="text-gray-400">
                      {new Date(preview.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </button>
              ))}
              {recentPreviews.length === 0 && (
                <p className="text-gray-400 text-sm">프리뷰가 없습니다</p>
              )}
            </div>
          </div>
        </div>

        {/* 오른쪽: 프리뷰 뷰어 */}
        <div className="lg:col-span-2">
          {previewData ? (
            <div className="space-y-6">
              {/* 상태 표시 */}
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-gray-400">상태: </span>
                    <span className={getStatusColor(previewData.status)}>
                      {getStatusText(previewData.status)}
                    </span>
                  </div>
                  <div className="text-gray-400">
                    진행률: {previewData.progress}%
                  </div>
                </div>
                {previewData.status === 'generating' && (
                  <div className="mt-2 bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${previewData.progress}%` }}
                    />
                  </div>
                )}
                {previewData.error && (
                  <div className="mt-2 text-red-400 text-sm">{previewData.error}</div>
                )}
              </div>

              {/* 프리뷰 비디오 */}
              {previewData.status === 'completed' && previewData.preview_path && (
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-white mb-4">프리뷰</h3>
                  <div className="bg-black rounded-lg overflow-hidden">
                    <video
                      src={`${API_URL}/api/preview/${currentJobId}/video`}
                      controls
                      className="w-full max-h-[500px]"
                    />
                  </div>
                </div>
              )}

              {/* 메타데이터 */}
              {previewData.metadata && (
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-white mb-4">메타데이터</h3>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-400">제목: </span>
                      <span className="text-white">{previewData.metadata.title}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">해상도: </span>
                      <span className="text-white">{previewData.metadata.resolution}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">세그먼트: </span>
                      <span className="text-white">{previewData.metadata.segment_count}개</span>
                    </div>
                  </div>
                </div>
              )}

              {/* 세그먼트 타임라인 */}
              {previewData.segments && previewData.segments.length > 0 && (
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-white mb-4">세그먼트 타임라인</h3>
                  <div className="flex gap-1 overflow-x-auto pb-2">
                    {previewData.segments.map((seg) => (
                      <button
                        key={seg.index}
                        onClick={() => setSelectedSegment(seg.index)}
                        className={`flex-shrink-0 px-3 py-2 rounded text-sm transition ${
                          selectedSegment === seg.index
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        #{seg.index + 1}
                      </button>
                    ))}
                  </div>

                  {selectedSegment !== null && previewData.segments[selectedSegment] && (
                    <div className="mt-4 p-4 bg-gray-700 rounded-lg">
                      <div className="text-sm space-y-2">
                        <div>
                          <span className="text-gray-400">텍스트: </span>
                          <span className="text-white">{previewData.segments[selectedSegment].text}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">키워드: </span>
                          <span className="text-blue-400">{previewData.segments[selectedSegment].keyword}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">길이: </span>
                          <span className="text-white">{previewData.segments[selectedSegment].duration?.toFixed(1)}초</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 액션 버튼 */}
              {previewData.status === 'completed' && (
                <div className="flex gap-4">
                  <button
                    onClick={handleFinalize}
                    disabled={loading}
                    className="flex-1 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-semibold rounded-lg transition"
                  >
                    최종 렌더링 (1080p)
                  </button>
                  <button
                    onClick={handleGeneratePreview}
                    disabled={loading}
                    className="flex-1 py-3 bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700 text-white font-semibold rounded-lg transition"
                  >
                    다시 생성
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-800 rounded-lg p-12 text-center">
              <div className="text-gray-400 text-lg mb-4">
                프리뷰를 생성하거나 선택해주세요
              </div>
              <p className="text-gray-500 text-sm">
                주제를 입력하고 &apos;Preview 생성&apos; 버튼을 클릭하면<br />
                저해상도 프리뷰를 빠르게 확인할 수 있습니다.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
