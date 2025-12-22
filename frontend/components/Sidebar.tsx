'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Home,
  Search,
  Zap,
  Database,
  Settings
} from 'lucide-react'

const navigation = [
  { name: '대시보드', href: '/', icon: Home },
  { name: '영상 검색', href: '/search', icon: Search },
  { name: '배치 처리', href: '/batch', icon: Zap },
  { name: '영상 목록', href: '/videos', icon: Database },
  { name: '설정', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">YouTube Remix</h1>
        <p className="text-sm text-gray-600 mt-1">영상 리믹스 시스템</p>
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
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-xs font-semibold text-blue-900 mb-1">해외 영상 리믹스</p>
          <p className="text-xs text-blue-700">번역 + 자막 자동화</p>
        </div>
      </div>
    </div>
  )
}
