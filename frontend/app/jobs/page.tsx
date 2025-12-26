'use client';

import { useState, useEffect } from 'react';
import { Clipboard, CheckCircle, XCircle, Clock, Play, ChevronDown, ChevronUp } from 'lucide-react';

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);

  // Phase 6: 페이징 상태
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const limit = 10;

  useEffect(() => {
    fetchJobs(currentPage);
  }, [currentPage]);

  const fetchJobs = async (page: number) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/jobs/recent?page=${page}&limit=${limit}`
      );
      const result = await response.json();

      if (result.success) {
        setJobs(result.data.jobs || []);
        setTotalPages(result.data.total_pages || 1);
        setTotal(result.data.total || 0);
      }
    } catch (error) {
      console.error('작업 목록 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // Phase 6: 아코디언 토글
  const toggleJobDetail = (jobId: string) => {
    setExpandedJobId(expandedJobId === jobId ? null : jobId);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-600" size={20} />;
      case 'failed':
        return <XCircle className="text-red-600" size={20} />;
      default:
        return <Clock className="text-yellow-600" size={20} />;
    }
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      completed: '완료',
      failed: '실패',
      planning: '기획 중',
      collecting_assets: '에셋 수집 중',
      editing: '편집 중',
      uploading: '업로드 중',
    };
    return statusMap[status] || status;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-2">
          <Clipboard />
          작업 목록
        </h1>
        <p className="text-gray-400">
          전체 {total}개 작업 (페이지 {currentPage} / {totalPages})
        </p>
      </div>

      {/* Phase 6: 아코디언 형식 작업 목록 */}
      <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-400">로딩 중...</div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-gray-400">아직 작업이 없습니다.</div>
        ) : (
          <div className="divide-y divide-gray-700">
            {jobs.map((job) => (
              <div key={job.job_id} className="transition-all">
                {/* 작업 헤더 (클릭 가능) */}
                <div
                  onClick={() => toggleJobDetail(job.job_id)}
                  className={`p-6 hover:bg-gray-700 cursor-pointer transition-colors ${
                    expandedJobId === job.job_id ? 'bg-gray-700' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        {getStatusIcon(job.status)}
                        <h3 className="font-semibold text-white">
                          {job.topic || '제목 없음'}
                        </h3>
                        <span
                          className={`text-xs px-2 py-1 rounded font-medium ${getStatusColor(
                            job.status
                          )}`}
                        >
                          {getStatusText(job.status)}
                        </span>
                      </div>
                      <div className="flex gap-4 text-sm text-gray-400">
                        <span>형식: {job.format || 'N/A'}</span>
                        <span>
                          생성:{' '}
                          {job.created_at
                            ? new Date(job.created_at).toLocaleString('ko-KR')
                            : 'N/A'}
                        </span>
                        {job.completed_at && (
                          <span>
                            완료: {new Date(job.completed_at).toLocaleString('ko-KR')}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="ml-4 text-blue-400">
                      {expandedJobId === job.job_id ? (
                        <ChevronUp size={20} />
                      ) : (
                        <ChevronDown size={20} />
                      )}
                    </div>
                  </div>
                </div>

                {/* Phase 6: 아코디언 상세 정보 (바로 아래 펼쳐짐) */}
                {expandedJobId === job.job_id && (
                  <div className="px-6 pb-6 bg-gray-750 border-t border-gray-700">
                    <div className="space-y-3 pt-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-400">작업 ID</p>
                          <p className="font-mono text-sm text-white">{job.job_id}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-400">상태</p>
                          <p className="font-semibold text-white">
                            {getStatusText(job.status)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-400">주제</p>
                          <p className="text-white">{job.topic || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-400">포맷</p>
                          <p className="text-white">{job.format || 'N/A'}</p>
                        </div>
                      </div>

                      {job.output_video_path && (
                        <div>
                          <p className="text-sm text-gray-400 mb-1">영상 파일</p>
                          <p className="font-mono text-sm bg-gray-700 p-2 rounded break-all text-white">
                            {job.output_video_path}
                          </p>
                        </div>
                      )}

                      {job.youtube_url && (
                        <div>
                          <p className="text-sm text-gray-400 mb-1">YouTube URL</p>
                          <a
                            href={job.youtube_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 flex items-center gap-2"
                          >
                            <Play size={16} />
                            {job.youtube_url}
                          </a>
                        </div>
                      )}

                      {job.error_log && (
                        <div>
                          <p className="text-sm text-gray-400 mb-1">에러 로그</p>
                          <pre className="bg-red-900 text-red-200 p-3 rounded text-xs overflow-x-auto">
                            {job.error_log}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Phase 6: 페이징 컨트롤 */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <button
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 bg-gray-800 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700"
          >
            이전
          </button>

          <div className="flex gap-1">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`px-3 py-2 rounded-lg ${
                  currentPage === page
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                {page}
              </button>
            ))}
          </div>

          <button
            onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 bg-gray-800 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700"
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}
