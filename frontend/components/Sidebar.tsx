'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Home,
  Sparkles,
  Clipboard,
  Zap,
  Settings,
  Video
} from 'lucide-react'

const navigation = [
  { name: '대시보드', href: '/', icon: Home },
  { name: '영상 생성', href: '/create', icon: Sparkles },
  { name: '작업 목록', href: '/jobs', icon: Clipboard },
  { name: '자동화', href: '/automation', icon: Zap },
  { name: '영상 관리', href: '/videos', icon: Video },
  { name: '설정', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">YouTube AI v3.0</h1>
        <p className="text-sm text-gray-600 mt-1">AI 콘텐츠 생성</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                ${isActive
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-700 hover:bg-gray-50'
                }
              `}
            >
              <Icon className="w-5 h-5 mr-3" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4">
          <p className="text-xs font-semibold text-gray-900 mb-1">✨ AI 기반 독창적 콘텐츠</p>
          <p className="text-xs text-gray-700">Planner → Assets → Editor → Upload</p>
        </div>
      </div>
    </div>
  )
}
