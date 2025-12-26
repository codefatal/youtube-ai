'use client';

import React from 'react';

interface TemplateSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function TemplateSelector({ value, onChange }: TemplateSelectorProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <label className="block text-sm font-medium text-gray-300 mb-2">
        영상 템플릿
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
      >
        <option value="basic">기본형</option>
        <option value="documentary">다큐형</option>
        <option value="entertainment">예능형</option>
      </select>
    </div>
  );
}
