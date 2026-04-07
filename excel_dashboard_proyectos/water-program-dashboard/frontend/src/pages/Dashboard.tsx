import { useQuery } from 'react-query'
import { dashboardApi } from '../api/client'
import { 
  Building2, 
  Activity, 
  CheckCircle2, 
  AlertTriangle,
  TrendingUp,
  Calendar
} from 'lucide-react'

export default function Dashboard() {
  const { data: dashboardData, isLoading } = useQuery(
    'dashboard',
    () => dashboardApi.getDashboardData(2026, 3).then(r => r.data)
  )

  const formatCurrency = (val: number) => {
    if (!val) return '$0'
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
    return `$${val.toFixed(0)}`
  }

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
  }

  const kpis = dashboardData?.kpis
  const timeline = dashboardData?.location_timeline || []

  // Calculate year totals
  const years = timeline.length > 0 ? Object.keys(timeline[0].budgets) : []
  
  const yearTotals = years.map(year => ({
    year,
    total: timeline.reduce((sum: number, loc: any) => sum + (loc.budgets[year] || 0), 0),
    limit: timeline.reduce((sum: number, _loc: any) => sum + 2000000, 0), // Annual limit
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Water Program Galapagos Dashboard</h1>
          <p className="text-gray-500 mt-1">Program overview and key performance indicators</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Active Year</p>
          <p className="text-2xl font-bold text-primary-600">2026</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Building2 className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-xs text-gray-500">Total Projects</p>
              <p className="text-xl font-bold">{kpis?.total_projects || 0}</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Activity className="h-5 w-5 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-xs text-gray-500">Active</p>
              <p className="text-xl font-bold">{kpis?.active_projects || 0}</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-gray-100 rounded-lg">
              <CheckCircle2 className="h-5 w-5 text-gray-600" />
            </div>
            <div className="ml-3">
              <p className="text-xs text-gray-500">Closed</p>
              <p className="text-xl font-bold">{kpis?.closed_projects || 0}</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <div className="ml-3">
              <p className="text-xs text-gray-500">At Risk</p>
              <p className="text-xl font-bold">{kpis?.at_risk_projects || 0}</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </div>
            <div className="ml-3">
              <p className="text-xs text-gray-500">Avg Progress</p>
              <p className="text-xl font-bold">{Math.round((kpis?.average_progress || 0) * 100)}%</p>
            </div>
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Calendar className="h-5 w-5 text-orange-600" />
            </div>
            <div className="ml-3">
              <p className="text-xs text-gray-500">Next Deadline</p>
              <p className="text-sm font-bold">{formatDate(kpis?.next_deadline)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Budget Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Committed Budget</h3>
          <p className="text-3xl font-bold text-primary-600">
            {formatCurrency(kpis?.committed_budget || 0)}
          </p>
          <p className="text-sm text-gray-500 mt-1">Total across all projects</p>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Budget Used</h3>
          <p className="text-3xl font-bold text-galapagos-accent">
            {formatCurrency(kpis?.total_budget_used || 0)}
          </p>
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-galapagos-accent h-2 rounded-full"
                style={{ width: `${Math.min(100, (kpis?.average_progress || 0) * 100)}%` }}
              />
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Remaining Budget</h3>
          <p className="text-3xl font-bold text-green-600">
            {formatCurrency((kpis?.committed_budget || 0) - (kpis?.total_budget_used || 0))}
          </p>
          <p className="text-sm text-gray-500 mt-1">Available to spend</p>
        </div>
      </div>

      {/* Location Budget Timeline */}
      <div className="card">
        <h2 className="text-lg font-bold text-gray-900 mb-6">Location Budget Timeline</h2>
        
        {isLoading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b-2 border-black">
                  <th className="text-left py-3 px-4 font-semibold">Location</th>
                  {years.map(year => (
                    <th key={year} className="text-center py-3 px-4 font-semibold">{year}</th>
                  ))}
                  <th className="text-center py-3 px-4 font-semibold">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {timeline.map((loc: any) => (
                  <>
                    <tr key={loc.location_id} className="hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{loc.location_name}</td>
                      {years.map(year => (
                        <td key={year} className="text-right py-3 px-4">
                          {formatCurrency(loc.budgets[year] || 0)}
                        </td>
                      ))}
                      <td className="text-right py-3 px-4 font-semibold">
                        {formatCurrency(loc.total)}
                      </td>
                    </tr>
                    <tr key={`${loc.location_id}-balance`} className="bg-gray-50/50 text-sm">
                      <td className="py-2 px-4 text-gray-500 italic">Balance</td>
                      {years.map(year => {
                        const balance = loc.balances[year] || 0
                        return (
                          <td key={year} className={`text-right py-2 px-4 ${balance < 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {formatCurrency(balance)}
                          </td>
                        )
                      })}
                      <td className="text-right py-2 px-4">
                        {formatCurrency(Object.values(loc.balances as Record<string, number>).reduce((a: number, b: number) => a + b, 0))}
                      </td>
                    </tr>
                  </>
                ))}
                
                {/* Totals Row */}
                <tr className="border-t-2 border-gray-300 font-bold bg-gray-50">
                  <td className="py-4 px-4">TOTAL</td>
                  {yearTotals.map(({ year, total }) => (
                    <td key={year} className="text-right py-4 px-4">{formatCurrency(total)}</td>
                  ))}
                  <td className="text-right py-4 px-4">
                    {formatCurrency(yearTotals.reduce((sum, y) => sum + y.total, 0))}
                  </td>
                </tr>

                {/* Balance General */}
                <tr className="bg-blue-50 text-sm">
                  <td className="py-3 px-4 font-medium text-blue-900">Balance General</td>
                  {yearTotals.map(({ year, total, limit }) => {
                    const balance = limit - total
                    return (
                      <td key={year} className={`text-right py-3 px-4 font-medium ${balance < 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatCurrency(balance)}
                      </td>
                    )
                  })}
                  <td className="text-right py-3 px-4">
                    {formatCurrency(yearTotals.reduce((sum, y) => sum + (y.limit - y.total), 0))}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Status Legend */}
      <div className="flex gap-4 text-sm">
        <div className="flex items-center">
          <span className="w-3 h-3 rounded-full bg-green-500 mr-2"></span>
          <span>On Track</span>
        </div>
        <div className="flex items-center">
          <span className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></span>
          <span>Attention</span>
        </div>
        <div className="flex items-center">
          <span className="w-3 h-3 rounded-full bg-red-500 mr-2"></span>
          <span>Over Limit</span>
        </div>
      </div>
    </div>
  )
}
