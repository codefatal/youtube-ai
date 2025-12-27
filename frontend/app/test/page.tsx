'use client';

import React, { useState } from 'react';

export default function TestPage() {
  const [duration, setDuration] = useState(10);
  const [title, setTitle] = useState('테스트 영상');
  const [subtitles, setSubtitles] = useState(['테스트 자막 1', '테스트 자막 2', '테스트 자막 3']);
  const [newSubtitle, setNewSubtitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const addSubtitle = () => {
    if (newSubtitle.trim()) {
      setSubtitles([...subtitles, newSubtitle.trim()]);
      setNewSubtitle('');
    }
  };

  const removeSubtitle = (index: number) => {
    setSubtitles(subtitles.filter((_, i) => i !== index));
  };

  const createTestVideo = async () => {
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/test/video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          duration,
          title,
          subtitles,
        }),
      });

      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error('테스트 영상 생성 실패:', error);
      setResult({ success: false, error: String(error) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">🧪 영상 테스트 페이지</h1>

        <div className="bg-gray-800 rounded-lg p-6 space-y-6">
          {/* 영상 길이 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              영상 길이 (초)
            </label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              min={5}
              max={60}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
            <p className="text-xs text-gray-400 mt-1">5초 ~ 60초</p>
          </div>

          {/* 제목 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              영상 제목
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            />
          </div>

          {/* 자막 리스트 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              자막 리스트 ({subtitles.length}개)
            </label>
            <div className="space-y-2 mb-3">
              {subtitles.map((subtitle, index) => (
                <div key={index} className="flex items-center gap-2">
                  <span className="text-sm text-gray-400 w-8">{index + 1}.</span>
                  <input
                    type="text"
                    value={subtitle}
                    onChange={(e) => {
                      const newSubs = [...subtitles];
                      newSubs[index] = e.target.value;
                      setSubtitles(newSubs);
                    }}
                    className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
                  />
                  <button
                    onClick={() => removeSubtitle(index)}
                    className="px-3 py-2 bg-red-600 hover:bg-red-500 rounded-lg text-sm"
                  >
                    삭제
                  </button>
                </div>
              ))}
            </div>

            {/* 자막 추가 */}
            <div className="flex gap-2">
              <input
                type="text"
                value={newSubtitle}
                onChange={(e) => setNewSubtitle(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addSubtitle()}
                placeholder="새 자막 입력 (Enter로 추가)"
                className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
              />
              <button
                onClick={addSubtitle}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm"
              >
                추가
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2">
              자막 1개당 약 {(duration / subtitles.length).toFixed(1)}초
            </p>
          </div>

          {/* 생성 버튼 */}
          <button
            onClick={createTestVideo}
            disabled={loading || subtitles.length === 0}
            className="w-full px-6 py-3 bg-green-600 hover:bg-green-500 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '생성 중...' : '🎬 테스트 영상 생성'}
          </button>

          {/* 결과 표시 */}
          {result && (
            <div className={`p-4 rounded-lg ${result.success ? 'bg-green-900/30 border border-green-600' : 'bg-red-900/30 border border-red-600'}`}>
              <h3 className="font-semibold mb-2">
                {result.success ? '✅ 생성 완료' : '❌ 생성 실패'}
              </h3>
              {result.success ? (
                <div className="text-sm space-y-1">
                  <p><strong>파일 경로:</strong> {result.video_path}</p>
                  <p><strong>영상 길이:</strong> {result.duration}초</p>
                  <p><strong>자막 개수:</strong> {result.subtitles.length}개</p>
                </div>
              ) : (
                <p className="text-sm text-red-400">{result.error}</p>
              )}
            </div>
          )}

          {/* 사용 안내 */}
          <div className="bg-gray-700/50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">📌 사용 방법</h3>
            <ul className="text-sm text-gray-300 space-y-1 list-disc list-inside">
              <li>원하는 영상 길이를 설정하세요 (5~60초)</li>
              <li>제목을 입력하세요</li>
              <li>자막을 추가/수정/삭제하세요</li>
              <li>생성 버튼을 클릭하면 자막이 포함된 테스트 영상이 생성됩니다</li>
              <li>생성된 영상은 output 폴더에 저장됩니다</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
