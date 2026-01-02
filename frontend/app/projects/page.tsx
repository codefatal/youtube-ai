'use client';

/**
 * Projects List Page
 * Phase 3: List all draft projects
 */

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { listDrafts, deleteDraft } from '@/lib/api';
import type { DraftProject } from '@/lib/types';

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<DraftProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  // 프로젝트 목록 로드
  useEffect(() => {
    loadProjects();
  }, [filter]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await listDrafts(
        0,
        20,
        undefined,
        filter === 'all' ? undefined : filter
      );
      setProjects(data);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  // 프로젝트 삭제
  const handleDelete = async (draftId: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
      await deleteDraft(draftId);
      await loadProjects();
      alert('프로젝트가 삭제되었습니다.');
    } catch (error) {
      console.error('Failed to delete project:', error);
      alert('프로젝트 삭제에 실패했습니다.');
    }
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      editing: { label: '편집 중', color: 'bg-yellow-600' },
      assets_ready: { label: '에셋 준비 완료', color: 'bg-green-600' },
      converting: { label: '렌더링 중', color: 'bg-blue-600' },
      finalized: { label: '완료', color: 'bg-gray-600' },
    };

    const badge = badges[status as keyof typeof badges] || {
      label: status,
      color: 'bg-gray-600',
    };

    return (
      <span
        className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${badge.color}`}
      >
        {badge.label}
      </span>
    );
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">📁 프로젝트 목록</h1>
        <button
          onClick={() => router.push('/create')}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
        >
          ➕ 새 프로젝트
        </button>
      </div>

      {/* 필터 */}
      <div className="mb-6 flex gap-2">
        {['all', 'editing', 'assets_ready', 'converting', 'finalized'].map(
          (status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {status === 'all'
                ? '전체'
                : status === 'editing'
                ? '편집 중'
                : status === 'assets_ready'
                ? '준비 완료'
                : status === 'converting'
                ? '렌더링 중'
                : '완료'}
            </button>
          )
        )}
      </div>

      {/* 프로젝트 리스트 */}
      {loading ? (
        <div className="text-center text-white py-12">로딩 중...</div>
      ) : projects.length === 0 ? (
        <div className="text-center text-gray-400 py-12">
          프로젝트가 없습니다. 새 프로젝트를 생성해보세요!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.draft_id}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-all cursor-pointer"
              onClick={() => router.push(`/projects/${project.draft_id}/edit`)}
            >
              {/* 헤더 */}
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-bold text-white line-clamp-2">
                  {project.title}
                </h3>
                {getStatusBadge(project.status)}
              </div>

              {/* 메타 정보 */}
              <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                {project.description || project.topic}
              </p>

              <div className="space-y-2 text-xs text-gray-500">
                <div className="flex items-center gap-2">
                  <span>🎬 {project.segments.length}개 세그먼트</span>
                  <span>·</span>
                  <span>⏱️ {project.target_duration}초</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>📅 {new Date(project.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              {/* 액션 버튼 */}
              <div className="mt-4 flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    router.push(`/projects/${project.draft_id}/edit`);
                  }}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                >
                  ✏️ 편집
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(project.draft_id);
                  }}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
