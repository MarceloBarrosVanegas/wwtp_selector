import { useState } from 'react'
import { useQuery } from 'react-query'
import { dashboardApi, locationsApi } from '../api/client'
import { parseISO } from 'date-fns'

export default function Gantt() {
  const [filterLocation, setFilterLocation] = useState('All Locations')
  
  const { data: locations } = useQuery('locations', () => locationsApi.getAll().then(r => r.data))
  
  const { data: ganttData, isLoading } = useQuery(
    ['gantt', filterLocation],
    () => dashboardApi.getGantt({ filter_location: filterLocation }).then(r => r.data),
    { enabled: !!locations }
  )

  const formatCurrency = (val: number) => {
    if (!val) return '-'
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
    return `$${val}`
  }

  const months = ganttData?.months || []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cash Flow Gantt</h1>
          <p className="text-gray-500 mt-1">Visual timeline of budgets and expenses by location</p>
        </div>
        
        <select
          value={filterLocation}
          onChange={(e) => setFilterLocation(e.target.value)}
          className="input max-w-xs"
        >
          <option value="All Locations">All Locations</option>
          {locations?.map((loc: any) => (
            <option key={loc.id} value={loc.name}>{loc.name}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="card p-8 text-center text-gray-500">Loading Gantt...</div>
      ) : (
        <>
          {/* INFLOW Section */}
          <div className="card overflow-hidden">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-3 h-3 bg-green-500 rounded mr-2"></span>
              INCOME BY LOCATION (IN)
            </h3>
            
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-primary-900 text-white">
                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
                    <th className="text-right py-2 px-3 font-medium w-24">Initial</th>
                    {months.map((month: string) => (
                      <th key={month} className="text-center py-2 px-2 font-medium text-xs w-16">
                        {month}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {ganttData?.inflow_data?.map((row: any) => (
                    <tr key={row.location_id} className="hover:bg-gray-50">
                      <td className="py-2 px-3 font-medium">{row.location_name}</td>
                      <td className="text-right py-2 px-3 text-green-600">
                        {formatCurrency(row.initial_value)}
                      </td>
                      {months.map((month: string) => {
                        const val = row.months[month]
                        return (
                          <td key={month} className="text-center py-2 px-2">
                            {val ? (
                              <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                                {formatCurrency(val)}
                              </span>
                            ) : (
                              <span className="text-gray-300">-</span>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* CUMULATIVE SUM Section */}
          <div className="card overflow-hidden">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-3 h-3 bg-blue-500 rounded mr-2"></span>
              CUMULATIVE SUM (Running Balance)
            </h3>
            
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-blue-900 text-white">
                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
                    {months.map((month: string) => (
                      <th key={month} className="text-center py-2 px-2 font-medium text-xs w-16">
                        {month}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ganttData?.cumulative_data
                    ?.filter((row: any) => row.row_type === 'cumulative_in')
                    .map((row: any) => (
                    <tr key={row.location_id} className="hover:bg-gray-50 bg-blue-50/30">
                      <td className="py-2 px-3 font-medium text-blue-900">{row.location_name}</td>
                      {months.map((month: string) => (
                        <td key={month} className="text-center py-2 px-2 text-xs">
                          {formatCurrency(row.values[month] || 0)}
                        </td>
                      ))}
                    </tr>
                  ))}
                  
                  {/* General Cumulative */}
                  <tr className="bg-gray-100 font-bold">
                    <td className="py-3 px-3">General Cumulative</td>
                    {months.map((month: string) => {
                      const sum = ganttData?.cumulative_data
                        ?.filter((row: any) => row.row_type === 'cumulative_in')
                        .reduce((acc: number, row: any) => acc + (row.values[month] || 0), 0) || 0
                      return (
                        <td key={month} className="text-center py-3 px-2">
                          {formatCurrency(sum)}
                        </td>
                      )
                    })}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* PROJECTS Section */}
          <div className="card overflow-hidden">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-3 h-3 bg-orange-500 rounded mr-2"></span>
              PROJECTS (OUT)
            </h3>
            
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-orange-900 text-white">
                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
                    <th className="text-left py-2 px-3 font-medium min-w-[200px]">Project</th>
                    <th className="text-center py-2 px-3 font-medium w-20">Status</th>
                    <th className="text-right py-2 px-3 font-medium w-24">Budget</th>
                    {months.slice(0, 12).map((month: string) => (
                      <th key={month} className="text-center py-2 px-1 font-medium text-xs w-12">
                        {month}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {ganttData?.items?.map((item: any) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="py-2 px-3 font-medium">{item.location}</td>
                      <td className="py-2 px-3 max-w-xs truncate" title={item.content}>
                        {item.content}
                      </td>
                      <td className="text-center py-2 px-3">
                        <span className={`inline-flex px-2 py-0.5 text-xs rounded-full ${
                          item.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                          item.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                          item.status === 'At Risk' ? 'bg-red-100 text-red-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="text-right py-2 px-3 font-medium">
                        {formatCurrency(item.amount)}
                      </td>
                      {months.slice(0, 12).map((month: string) => {
                        const itemStart = new Date(item.start)
                        const itemEnd = item.end ? new Date(item.end) : itemStart
                        const monthDate = parseISO(`2026-${month.split('-')[0]}-01`)
                        const isActive = monthDate >= itemStart && monthDate <= itemEnd
                        
                        return (
                          <td key={month} className="text-center py-1 px-1">
                            {isActive && (
                              <div 
                                className="h-6 rounded bg-cyan-200 border border-cyan-300 text-xs flex items-center justify-center"
                                title={`${item.content}: ${formatCurrency(item.amount)}`}
                              >
                                {formatCurrency(item.amount / Math.max(1, Math.ceil((itemEnd.getTime() - itemStart.getTime()) / (1000 * 60 * 60 * 24 * 30))))}
                              </div>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* CUMULATIVE COST */}
          <div className="card overflow-hidden">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-3 h-3 bg-red-500 rounded mr-2"></span>
              CUMULATIVE COST
            </h3>
            
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-red-900 text-white">
                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
                    {months.slice(0, 12).map((month: string) => (
                      <th key={month} className="text-center py-2 px-2 font-medium text-xs w-16">
                        {month}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr className="bg-gray-100 font-bold">
                    <td className="py-3 px-3">Cumulative Cost</td>
                    {months.slice(0, 12).map((month: string) => {
                      const cost = ganttData?.items?.reduce((sum: number, item: any) => {
                        const itemStart = new Date(item.start)
                        const itemEnd = item.end ? new Date(item.end) : itemStart
                        const monthDate = parseISO(`2026-${month.split('-')[0]}-01`)
                        if (monthDate >= itemStart && monthDate <= itemEnd) {
                          return sum + (item.amount / Math.max(1, Math.ceil((itemEnd.getTime() - itemStart.getTime()) / (1000 * 60 * 60 * 24 * 30))))
                        }
                        return sum
                      }, 0) || 0
                      return (
                        <td key={month} className="text-center py-3 px-2">
                          {formatCurrency(cost)}
                        </td>
                      )
                    })}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* NET CASH FLOW */}
          <div className="card overflow-hidden">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-3 h-3 bg-purple-500 rounded mr-2"></span>
              NET CASH FLOW (In - Out)
            </h3>
            
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-purple-900 text-white">
                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
                    {months.slice(0, 12).map((month: string) => (
                      <th key={month} className="text-center py-2 px-2 font-medium text-xs w-16">
                        {month}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ganttData?.net_cash_flow?.map((row: any) => (
                    <tr key={row.location_id} className="hover:bg-gray-50">
                      <td className="py-2 px-3 font-medium">{row.location_name}</td>
                      {months.slice(0, 12).map((month: string) => {
                        const val = row.values[month] || 0
                        return (
                          <td key={month} className={`text-center py-2 px-2 text-xs font-medium ${val < 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {formatCurrency(val)}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
