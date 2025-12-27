'use client';

import { useState, useEffect } from 'react';
import { Calendar, Play, Trash2, RefreshCw, Clock } from 'lucide-react';

export default function AutomationPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobs();
    fetchAccounts();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/scheduler/jobs');
      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (error) {
      console.error('스케줄 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/accounts/');
      const data = await response.json();
      if (data.success) {
        setAccounts(data.data || []);
      }
    } catch (error) {
      console.error('계정 조회 실패:', error);
    }
  };

  const handleReloadSchedules = async () => {
    try {
      await fetch('http://localhost:8000/api/scheduler/reload', {
        method: 'POST',
      });
      alert('스케줄이 다시 로드되었습니다.');
      fetchJobs();
    } catch (error) {
      alert('스케줄 로드 실패: ' + error);
    }
  };

  const handleTriggerJob = async (accountId: number) => {
    try {
      await fetch(`http://localhost:8000/api/scheduler/trigger/${accountId}`, {
        method: 'POST',
      });
      alert(`계정 ID ${accountId}의 작업이 즉시 실행됩니다.`);
    } catch (error) {
      alert('작업 실행 실패: ' + error);
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!confirm('이 스케줄을 삭제하시겠습니까?')) return;

    try {
      await fetch(`http://localhost:8000/api/scheduler/jobs/${jobId}`, {
        method: 'DELETE',
      });
      alert('스케줄이 삭제되었습니다.');
      fetchJobs();
    } catch (error) {
      alert('삭제 실패: ' + error);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-2">
          <Calendar />
          스케줄 관리
        </h1>
        <p className="text-gray-400">
          계정별 자동 생성 스케줄 관리 및 즉시 실행
        </p>
      </div>

      {/* 상단 액션 버튼 */}
      <div className="mb-6 flex gap-3">
        <button
          onClick={handleReloadSchedules}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <RefreshCw size={18} />
          스케줄 다시 로드
        </button>
      </div>

      {/* 스케줄 목록 */}
      <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">
            등록된 스케줄 ({jobs.length}개)
          </h2>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-400">로딩 중...</div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            등록된 스케줄이 없습니다.
            <p className="text-sm mt-2">
              계정 관리에서 upload_schedule을 설정하세요.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-700">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="p-6 hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Clock className="text-blue-400" size={20} />
                      <h3 className="font-semibold text-white">{job.name}</h3>
                      {job.next_run_time && (
                        <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800">
                          다음 실행:{' '}
                          {new Date(job.next_run_time).toLocaleString('ko-KR')}
                        </span>
                      )}
                    </div>

                    <div className="text-sm text-gray-400 space-y-1">
                      <p>Job ID: {job.id}</p>
                      {job.trigger && (
                        <p>
                          Trigger: {job.trigger.type}
                          {job.trigger.cron && ` (${job.trigger.cron})`}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDeleteJob(job.id)}
                      className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
                    >
                      <Trash2 size={16} />
                      삭제
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 계정별 즉시 실행 */}
      <div className="mt-8 bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">즉시 실행</h2>
          <p className="text-sm text-gray-400 mt-1">
            스케줄을 기다리지 않고 즉시 영상을 생성합니다.
          </p>
        </div>

        <div className="p-6">
          {accounts.length === 0 ? (
            <p className="text-gray-400">등록된 계정이 없습니다.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {accounts.map((account) => (
                <div
                  key={account.id}
                  className="p-4 bg-gray-700 rounded-lg flex items-center justify-between"
                >
                  <div>
                    <h3 className="font-semibold text-white">
                      {account.channel_name}
                    </h3>
                    <p className="text-sm text-gray-400">
                      채널 타입: {account.channel_type}
                    </p>
                  </div>
                  <button
                    onClick={() => handleTriggerJob(account.id)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                  >
                    <Play size={16} />
                    즉시 실행
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 도움말 */}
      <div className="mt-8 bg-blue-900 border border-blue-700 rounded-lg p-6">
        <h3 className="font-semibold text-blue-200 mb-2">💡 스케줄 설정 방법</h3>
        <ul className="text-sm text-blue-300 space-y-1">
          <li>• 계정 관리 페이지에서 upload_schedule을 Cron 형식으로 설정하세요</li>
          <li>• 예: "0 10 * * *" = 매일 오전 10시</li>
          <li>• 예: "0 */6 * * *" = 6시간마다</li>
          <li>• 설정 후 "스케줄 다시 로드" 버튼을 클릭하세요</li>
        </ul>
      </div>
    </div>
  );
}
