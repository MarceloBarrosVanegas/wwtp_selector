import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Database, 
  CalendarDays, 
  Map as MapIcon, 
  BarChart3,
  Droplets
} from 'lucide-react'
import { clsx } from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: Database },
  { name: 'Gantt / Cash Flow', href: '/gantt', icon: CalendarDays },
  { name: 'Map', href: '/map', icon: MapIcon },
  { name: 'Charts', href: '/charts', icon: BarChart3 },
]

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-galapagos-blue">
        <div className="flex h-16 items-center px-6 border-b border-white/10">
          <Droplets className="h-8 w-8 text-white mr-3" />
          <div>
            <h1 className="text-white font-bold text-lg">Water Program</h1>
            <p className="text-white/60 text-xs">Galapagos Dashboard</p>
          </div>
        </div>
        
        <nav className="mt-6 px-3 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'group flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-white/10 text-white'
                    : 'text-white/70 hover:bg-white/5 hover:text-white'
                )}
              >
                <item.icon
                  className={clsx(
                    'mr-3 h-5 w-5 flex-shrink-0',
                    isActive ? 'text-white' : 'text-white/60 group-hover:text-white'
                  )}
                />
                {item.name}
              </Link>
            )
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/10">
          <p className="text-white/40 text-xs text-center">
            OFC Water Program © 2026
          </p>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
