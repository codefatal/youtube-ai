'use client'

import { useState } from 'react'
import { PlayCircle, Loader2, CheckCircle, XCircle } from 'lucide-react'

type StepStatus = 'pending' | 'running' | 'completed' | 'error'

interface Step {
  name: string
  status: StepStatus
  message?: string
}

export default function AutomationPage() {
  const [running, setRunning] = useState(false)
  const [steps, setSteps] = useState<Step[]>([
    { name: '트렌드 분석', status: 'pending' },
    { name: '대본 생성', status: 'pending' },
    { name: '영상 제작', status: 'pending' },
    { name: 'YouTube 업로드', status: 'pending' },
  ])

  const handleStart = async () => {
    setRunning(true)

    try {
      // 각 단계별로 API 호출
      for (let i = 0; i < steps.length; i++) {
        setSteps(prev => prev.map((step, idx) =>
          idx === i ? { ...step, status: 'running' } : step
        ))

        await new Promise(resolve => setTimeout(resolve, 2000)) // 시뮬레이션

        setSteps(prev => prev.map((step, idx) =>
          idx === i ? { ...step, status: 'completed', message: '완료' } : step
        ))
      }
    } catch (error) {
      console.error('Error:', error)
    }

    setRunning(false)
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">전체 자동화</h1>
        <p className="text-gray-600">원클릭으로 영상 제작 및 업로드</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">자동화 프로세스</h2>

        <div className="space-y-4 mb-6">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border-2 ${
                step.status === 'running' ? 'border-blue-500 bg-blue-50' :
                step.status === 'completed' ? 'border-green-500 bg-green-50' :
                step.status === 'error' ? 'border-red-500 bg-red-50' :
                'border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  {step.status === 'running' && (
                    <Loader2 className="w-5 h-5 mr-3 text-blue-600 animate-spin" />
                  )}
                  {step.status === 'completed' && (
                    <CheckCircle className="w-5 h-5 mr-3 text-green-600" />
                  )}
                  {step.status === 'error' && (
                    <XCircle className="w-5 h-5 mr-3 text-red-600" />
                  )}
                  {step.status === 'pending' && (
                    <div className="w-5 h-5 mr-3 rounded-full border-2 border-gray-300" />
                  )}

                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {index + 1}. {step.name}
                    </h3>
                    {step.message && (
                      <p className="text-sm text-gray-600">{step.message}</p>
                    )}
                  </div>
                </div>

                <span className={`text-xs font-medium px-2 py-1 rounded ${
                  step.status === 'running' ? 'bg-blue-100 text-blue-700' :
                  step.status === 'completed' ? 'bg-green-100 text-green-700' :
                  step.status === 'error' ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {step.status === 'pending' ? '대기 중' :
                   step.status === 'running' ? '진행 중' :
                   step.status === 'completed' ? '완료' :
                   '오류'}
                </span>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={handleStart}
          disabled={running}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center"
        >
          {running ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              실행 중...
            </>
          ) : (
            <>
              <PlayCircle className="w-5 h-5 mr-2" />
              자동화 시작
            </>
          )}
        </button>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">💡 참고사항</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• 전체 프로세스는 약 10-15분 소요됩니다</li>
          <li>• Gemini 무료 API를 사용하면 비용이 발생하지 않습니다</li>
          <li>• 진행 중 페이지를 닫지 마세요</li>
        </ul>
      </div>
    </div>
  )
}
