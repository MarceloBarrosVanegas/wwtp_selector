import { useQuery } from 'react-query'
import { dashboardApi } from '../api/client'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { useState } from 'react'

const COLORS = ['#2E75B6', '#F79646', '#5287936', '#C0504D', '#5592405', '#9978C4', '#FFC000']

const formatCurrency = (val: number) => {
  if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
  if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
  return `$${val}`
}

export default function Charts() {
  const [activeTab, setActiveTab] = useState('budget-project')

  const { data: budgetByProject } = useQuery(
    'chart-budget-project',
    () => dashboardApi.getChartBudgetByProject().then(r => r.data)
  )

  const { data: progressByProject } = useQuery(
    'chart-progress-project',
    () => dashboardApi.getChartProgressByProject().then(r => r.data)
  )

  const { data: statusDistribution } = useQuery(
    'chart-status',
    () => dashboardApi.getChartStatusDistribution().then(r => r.data)
  )

  const { data: budgetByLocation } = useQuery(
    'chart-budget-location',
    () => dashboardApi.getChartBudgetByLocation().then(r => r.data)
  )

  const tabs = [
    { id: 'budget-project', name: 'Budget by Project', icon: '📊' },
    { id: 'progress-project', name: 'Progress by Project', icon: '📈' },
    { id: 'status', name: 'Status Distribution', icon: '🥧' },
    { id: 'budget-location', name: 'Budget by Location', icon: '🗺️' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics & Charts</h1>
          <p className="text-gray-500 mt-1">Visual analysis of project data</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-gray-200">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.name}
          </button>
        ))}
      </div>

      {/* Chart Content */}
      <div className="card">
        {/* Budget by Project */}
        {activeTab === 'budget-project' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Annual Budget by Project</h3>
            <div className="h-[500px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={budgetByProject?.datasets?.[0]?.data?.map((val: number, idx: number) => ({
                    name: budgetByProject.labels[idx]?.length > 20 
                      ? budgetByProject.labels[idx].substring(0, 20) + '...' 
                      : budgetByProject.labels[idx],
                    fullName: budgetByProject.labels[idx],
                    budget: val
                  })) || []}
                  layout="vertical"
                  margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" tickFormatter={formatCurrency} />
                  <YAxis type="category" dataKey="name" width={150} />
                  <Tooltip 
                    formatter={(value: number) => formatCurrency(value)}
                    labelFormatter={(label, payload) => payload?.[0]?.payload?.fullName || label}
                  />
                  <Bar dataKey="budget" fill="#2E75B6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Progress by Project */}
        {activeTab === 'progress-project' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Progress by Project</h3>
            <div className="h-[500px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={progressByProject?.datasets?.[0]?.data?.map((val: number, idx: number) => ({
                    name: progressByProject.labels[idx]?.length > 20 
                      ? progressByProject.labels[idx].substring(0, 20) + '...' 
                      : progressByProject.labels[idx],
                    fullName: progressByProject.labels[idx],
                    progress: val
                  })) || []}
                  layout="vertical"
                  margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                  <YAxis type="category" dataKey="name" width={150} />
                  <Tooltip formatter={(value: number) => `${value.toFixed(0)}%`} />
                  <Bar dataKey="progress" fill="#4472C4" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Status Distribution */}
        {activeTab === 'status' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Projects by Status</h3>
            <div className="grid grid-cols-2 gap-8">
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={statusDistribution?.labels?.map((label: string, idx: number) => ({
                        name: label,
                        value: statusDistribution.datasets[0].data[idx],
                        color: statusDistribution.datasets[0].backgroundColor[idx]
                      })) || []}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {(statusDistribution?.labels || []).map((_: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={statusDistribution.datasets[0].backgroundColor[index]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex items-center">
                <div className="space-y-4">
                  {statusDistribution?.labels?.map((label: string, idx: number) => (
                    <div key={label} className="flex items-center">
                      <span 
                        className="w-4 h-4 rounded mr-3"
                        style={{ backgroundColor: statusDistribution.datasets[0].backgroundColor[idx] }}
                      />
                      <span className="text-gray-700">{label}</span>
                      <span className="ml-auto font-medium text-gray-900">
                        {statusDistribution.datasets[0].data[idx]} projects
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Budget by Location */}
        {activeTab === 'budget-location' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Budget by Location</h3>
            <div className="h-[500px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={budgetByLocation?.labels?.map((label: string, idx: number) => ({
                      name: label,
                      value: budgetByLocation.datasets[0].data[idx]
                    })) || []}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={150}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {(budgetByLocation?.labels || []).map((_: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-6">
              {budgetByLocation?.labels?.map((label: string, idx: number) => (
                <div key={label} className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center mb-2">
                    <span 
                      className="w-3 h-3 rounded-full mr-2"
                      style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                    />
                    <span className="font-medium">{label}</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(budgetByLocation.datasets[0].data[idx])}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
