'use client';

/**
 * Timeline Editor Page
 * Phase 3: Vrew-style Interactive Timeline Editor
 *
 * Features:
 * - Vertical scroll view (Shorts style)
 * - Segment-by-segment editing
 * - Image regeneration
 * - Text editing with TTS update
 * - Audio preview
 * - Final rendering
 */

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  getProjectDetail,
  updateSegment,
  regenerateSegmentVideo,
  finalizeDraft,
  getTTSAudioUrl,
  getVideoThumbnailUrl,
} from '@/lib/api';
import type { DraftProject, Segment } from '@/lib/types';

export default function TimelineEditorPage() {
  const router = useRouter();
  const params = useParams();
  const draftId = params?.id as string;

  const [project, setProject] = useState<DraftProject | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [rendering, setRendering] = useState(false);

  // 편집 중인 세그먼트 ID (null이면 편집 중이 아님)
  const [editingSegmentIndex, setEditingSegmentIndex] = useState<number | null>(null);
  const [editedText, setEditedText] = useState('');

  // 재생 중인 오디오
  const [playingAudioIndex, setPlayingAudioIndex] = useState<number | null>(null);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);

  // 프로젝트 로드
  useEffect(() => {
    if (!draftId) return;

    const loadProject = async () => {
      try {
        setLoading(true);
        const data = await getProjectDetail(draftId);
        setProject(data);
      } catch (error) {
        console.error('Failed to load project:', error);
        alert('프로젝트를 불러오는데 실패했습니다.');
        router.push('/projects');
      } finally {
        setLoading(false);
      }
    };

    loadProject();
  }, [draftId, router]);

  // 세그먼트 텍스트 수정 시작
  const handleStartEdit = (segment: Segment) => {
    setEditingSegmentIndex(segment.segment_index);
    setEditedText(segment.text);
  };

  // 세그먼트 텍스트 저장
  const handleSaveText = async (segmentIndex: number) => {
    if (!project) return;

    try {
      setSaving(true);
      await updateSegment(draftId, segmentIndex, {
        text: editedText,
      });

      // 로컬 상태 업데이트
      setProject({
        ...project,
        segments: project.segments.map((seg) =>
          seg.segment_index === segmentIndex
            ? { ...seg, text: editedText }
            : seg
        ),
      });

      setEditingSegmentIndex(null);
      alert('텍스트가 저장되었습니다. TTS는 렌더링 시 업데이트됩니다.');
    } catch (error) {
      console.error('Failed to save text:', error);
      alert('텍스트 저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  // 세그먼트 이미지 재생성
  const handleRegenerateImage = async (segmentIndex: number) => {
    if (!project) return;
    if (!confirm('이 세그먼트의 이미지를 다시 검색하시겠습니까?')) return;

    try {
      setSaving(true);
      await regenerateSegmentVideo(draftId, segmentIndex);

      // 프로젝트 새로고침
      const updatedProject = await getProjectDetail(draftId);
      setProject(updatedProject);

      alert('이미지가 재생성되었습니다!');
    } catch (error) {
      console.error('Failed to regenerate image:', error);
      alert('이미지 재생성에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  // TTS 오디오 재생
  const handlePlayAudio = (segment: Segment) => {
    const audioUrl = getTTSAudioUrl(segment.tts_local_path);
    if (!audioUrl) {
      alert('오디오 파일이 없습니다.');
      return;
    }

    // 기존 재생 중지
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
    }

    // 새 오디오 재생
    const audio = new Audio(audioUrl);
    audio.play();
    setPlayingAudioIndex(segment.segment_index);
    setAudioElement(audio);

    audio.onended = () => {
      setPlayingAudioIndex(null);
      setAudioElement(null);
    };
  };

  // TTS 오디오 정지
  const handleStopAudio = () => {
    if (audioElement) {
      audioElement.pause();
      audioElement.currentTime = 0;
    }
    setPlayingAudioIndex(null);
    setAudioElement(null);
  };

  // 최종 렌더링
  const handleFinalize = async () => {
    if (!project) return;
    if (!confirm('최종 렌더링을 시작하시겠습니까? (시간이 소요됩니다)')) return;

    try {
      setRendering(true);
      const result = await finalizeDraft(draftId, {
        upload: false,
        template: 'basic',
        bgm_settings: {
          enabled: true,
          mood: 'auto',
          volume: 0.25,
        },
      });

      alert(`렌더링 완료! Job ID: ${result.data.job_id}`);
      router.push(`/jobs`);
    } catch (error) {
      console.error('Failed to finalize:', error);
      alert('렌더링에 실패했습니다.');
    } finally {
      setRendering(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-white text-xl">프로젝트 로딩 중...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-white text-xl">프로젝트를 찾을 수 없습니다.</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">{project.title}</h1>
            <p className="text-gray-400 text-sm">
              {project.segments.length}개 세그먼트 · {project.target_duration}초
            </p>
          </div>
          <button
            onClick={() => router.push('/projects')}
            className="text-gray-400 hover:text-white"
          >
            ← 목록으로
          </button>
        </div>
      </div>

      {/* Timeline - Vertical Scroll */}
      <div className="max-w-7xl mx-auto p-6 pb-32">
        <div className="space-y-4">
          {project.segments.map((segment) => (
            <div
              key={segment.segment_index}
              className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-all"
            >
              <div className="flex gap-4">
                {/* 좌측: 썸네일/미리보기 */}
                <div className="w-1/3 flex-shrink-0">
                  <div className="aspect-[9/16] bg-gray-700 rounded-lg overflow-hidden relative group">
                    {segment.video_url ? (
                      <img
                        src={getVideoThumbnailUrl(segment.video_url) || ''}
                        alt={`Segment ${segment.segment_index}`}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-500">
                        <svg
                          className="w-16 h-16"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                          />
                        </svg>
                      </div>
                    )}

                    {/* Hover Overlay */}
                    <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <button
                        onClick={() => handleRegenerateImage(segment.segment_index)}
                        disabled={saving}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
                      >
                        🔄 이미지 재생성
                      </button>
                    </div>
                  </div>

                  <div className="mt-2 text-xs text-gray-500">
                    {segment.video_provider && (
                      <div>Provider: {segment.video_provider}</div>
                    )}
                    {segment.duration && (
                      <div>Duration: {segment.duration.toFixed(1)}s</div>
                    )}
                  </div>
                </div>

                {/* 우측: 텍스트 입력창 + 컨트롤 */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-xs text-gray-500">
                      Segment #{segment.segment_index + 1}
                    </span>
                    {editingSegmentIndex === segment.segment_index ? (
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSaveText(segment.segment_index)}
                          disabled={saving}
                          className="text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded disabled:opacity-50"
                        >
                          💾 저장
                        </button>
                        <button
                          onClick={() => setEditingSegmentIndex(null)}
                          className="text-xs bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded"
                        >
                          취소
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleStartEdit(segment)}
                        className="text-xs text-blue-400 hover:text-blue-300"
                      >
                        ✏️ 편집
                      </button>
                    )}
                  </div>

                  {/* 텍스트 영역 */}
                  {editingSegmentIndex === segment.segment_index ? (
                    <textarea
                      value={editedText}
                      onChange={(e) => setEditedText(e.target.value)}
                      className="w-full h-32 bg-gray-700 text-white rounded-lg p-3 border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
                      placeholder="자막 텍스트를 입력하세요..."
                    />
                  ) : (
                    <div className="bg-gray-700 rounded-lg p-3 min-h-[8rem] whitespace-pre-wrap">
                      {segment.text}
                    </div>
                  )}

                  {/* 메타 정보 */}
                  <div className="mt-3 space-y-1 text-xs text-gray-400">
                    <div>
                      <span className="font-semibold">Keyword:</span>{' '}
                      {segment.keyword || 'N/A'}
                    </div>
                    <div>
                      <span className="font-semibold">Visual Query:</span>{' '}
                      {segment.image_search_query || 'N/A'}
                    </div>
                  </div>

                  {/* 오디오 컨트롤 */}
                  <div className="mt-3 flex items-center gap-2">
                    {playingAudioIndex === segment.segment_index ? (
                      <button
                        onClick={handleStopAudio}
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z"
                            clipRule="evenodd"
                          />
                        </svg>
                        정지
                      </button>
                    ) : (
                      <button
                        onClick={() => handlePlayAudio(segment)}
                        disabled={!segment.tts_local_path}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                            clipRule="evenodd"
                          />
                        </svg>
                        TTS 미리듣기
                      </button>
                    )}
                    {segment.tts_duration && (
                      <span className="text-xs text-gray-500">
                        {segment.tts_duration.toFixed(1)}초
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer - Fixed Bottom Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 p-4 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="text-sm text-gray-400">
            총 {project.segments.length}개 세그먼트 ·{' '}
            {project.segments
              .reduce((sum, seg) => sum + (seg.tts_duration || seg.duration || 0), 0)
              .toFixed(1)}
            초
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => alert('전체 미리보기 기능은 추후 구현 예정입니다.')}
              className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium"
            >
              🎬 전체 미리보기
            </button>
            <button
              onClick={handleFinalize}
              disabled={rendering || saving}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-lg font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {rendering ? (
                <span className="flex items-center gap-2">
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
                  렌더링 중...
                </span>
              ) : (
                '✨ 최종 렌더링 (Export)'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
