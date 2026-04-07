import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export default api

// Projects API
export const projectsApi = {
  getAll: () => api.get('/projects/'),
  getById: (id: string) => api.get(`/projects/${id}`),
  create: (data: any) => api.post('/projects/', data),
  update: (id: string, data: any) => api.put(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
  getNextId: () => api.get('/projects/next-id/'),
}

// Locations API
export const locationsApi = {
  getAll: () => api.get('/locations/'),
  getById: (id: number) => api.get(`/locations/${id}`),
  create: (data: any) => api.post('/locations/', data),
}

// Dashboard API
export const dashboardApi = {
  getKPIs: (year?: number) => api.get('/dashboard/kpis', { params: { year } }),
  getTimeline: (start_year: number, num_years: number) => 
    api.get('/dashboard/timeline', { params: { start_year, num_years } }),
  getDashboardData: (year: number, num_years: number) => 
    api.get('/dashboard/data', { params: { year, num_years } }),
  getGantt: (params?: any) => api.get('/dashboard/gantt', { params }),
  getMap: () => api.get('/dashboard/map'),
  getChartBudgetByProject: () => api.get('/dashboard/charts/budget-by-project'),
  getChartProgressByProject: () => api.get('/dashboard/charts/progress-by-project'),
  getChartStatusDistribution: () => api.get('/dashboard/charts/status-distribution'),
  getChartBudgetByLocation: () => api.get('/dashboard/charts/budget-by-location'),
}
