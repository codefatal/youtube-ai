import AccountSidebar from '@/components/AccountSidebar';
import './globals.css';

export const metadata = {
  title: 'YouTube AI v4.0 - Multi-Channel Manager',
  description: '엔터프라이즈급 YouTube 자동화 시스템',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <div className="flex h-screen">
          {/* 사이드바 */}
          <AccountSidebar />

          {/* 메인 콘텐츠 */}
          <main className="flex-1 overflow-y-auto bg-gray-900">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
