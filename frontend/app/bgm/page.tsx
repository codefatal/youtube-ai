'use client';

import React, { useState, useEffect } from 'react';
import BGMSelector from '@/components/BGMSelector';

interface BGM {
  mood: string;
  name: string;
  filepath: string;
}

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

export default function BGMPage() {
  const [bgmList, setBgmList] = useState<BGM[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const [file, setFile] = useState<File | null>(null);
  const [mood, setMood] = useState('ENERGETIC');
  const [name, setName] = useState('');

  // BGM 선택 상태
  const [selectedBGM, setSelectedBGM] = useState<BGMItem | null>(null);

  const moods = ['HAPPY', 'SAD', 'ENERGETIC', 'CALM', 'TENSE', 'MYSTERIOUS'];

  useEffect(() => {
    fetchBGMList();
  }, []);

  const fetchBGMList = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/bgm/list`);
      const data = await res.json();
      setBgmList(data.bgm_list || []);
    } catch (error) {
      console.error('BGM 목록 가져오기 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file || !name.trim()) {
      alert('파일과 이름을 모두 입력하세요');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mood', mood);
      formData.append('name', name.trim());

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/bgm/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();

      if (data.success) {
        alert('BGM 업로드 성공!');
        setFile(null);
        setName('');
        fetchBGMList();
      } else {
        alert('BGM 업로드 실패');
      }
    } catch (error) {
      console.error('업로드 실패:', error);
      alert('업로드 실패');
    } finally {
      setUploading(false);
    }
  };

  const groupByMood = (bgms: BGM[]) => {
    const grouped: { [key: string]: BGM[] } = {};
    bgms.forEach((bgm) => {
      if (!grouped[bgm.mood]) {
        grouped[bgm.mood] = [];
      }
      grouped[bgm.mood].push(bgm);
    });
    return grouped;
  };

  const groupedBGM = groupByMood(bgmList);

  const handleBGMSelect = (bgm: BGMItem | null) => {
    setSelectedBGM(bgm);
    if (bgm) {
      console.log('Selected BGM:', bgm);
      // 부모 컴포넌트나 상태 관리 스토어에 BGM 정보 전달
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">🎵 BGM 관리</h1>

        {/* BGM 선택 컴포넌트 (NEW) */}
        <div className="mb-8">
          <BGMSelector onSelect={handleBGMSelect} selectedBGM={selectedBGM} />
        </div>

        {/* 업로드 폼 */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">BGM 업로드</h2>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                MP3 파일
              </label>
              <input
                type="file"
                accept=".mp3"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                BGM 이름
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="예: Upbeat_Music"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                분위기 (Mood)
              </label>
              <select
                value={mood}
                onChange={(e) => setMood(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
              >
                {moods.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={uploading || !file || !name.trim()}
              className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? '업로드 중...' : '📤 BGM 업로드'}
            </button>
          </form>
        </div>

        {/* BGM 목록 */}
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">
              BGM 목록 ({bgmList.length}개)
            </h2>
            <button
              onClick={fetchBGMList}
              disabled={loading}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
            >
              {loading ? '로딩 중...' : '새로고침'}
            </button>
          </div>

          {loading ? (
            <p className="text-gray-400">로딩 중...</p>
          ) : bgmList.length === 0 ? (
            <p className="text-gray-400">업로드된 BGM이 없습니다</p>
          ) : (
            <div className="space-y-6">
              {moods.map((moodName) => {
                const bgms = groupedBGM[moodName] || [];
                if (bgms.length === 0) return null;

                return (
                  <div key={moodName}>
                    <h3 className="text-lg font-semibold text-blue-400 mb-2">
                      {moodName} ({bgms.length}개)
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {bgms.map((bgm, index) => (
                        <div
                          key={index}
                          className="bg-gray-700 p-3 rounded-lg"
                        >
                          <p className="font-medium">{bgm.name}</p>
                          <p className="text-xs text-gray-400 mt-1">{bgm.filepath}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* 사용 안내 */}
        <div className="bg-gray-800 rounded-lg p-4 mt-6">
          <h3 className="font-semibold mb-2">📌 사용 방법</h3>
          <ul className="text-sm text-gray-300 space-y-1 list-disc list-inside">
            <li>MP3 파일만 업로드 가능합니다</li>
            <li>분위기(Mood)에 맞는 BGM을 업로드하세요</li>
            <li>영상 생성 시 자동으로 분위기에 맞는 BGM이 선택됩니다</li>
            <li>music/MOOD_NAME/ 폴더에 저장됩니다</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
