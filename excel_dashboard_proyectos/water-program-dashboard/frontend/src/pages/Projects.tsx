import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Plus, Edit2, Trash2, MapPin } from 'lucide-react'
import { projectsApi, locationsApi } from '../api/client'
import ProjectModal from '../components/Projects/ProjectModal'

const statusColors: Record<string, string> = {
  'In Progress': 'bg-blue-100 text-blue-800',
  'Pending': 'bg-yellow-100 text-yellow-800',
  'At Risk': 'bg-red-100 text-red-800',
  'Closed': 'bg-green-100 text-green-800',
  'Suspended': 'bg-gray-100 text-gray-800',
}

const alertColors: Record<string, string> = {
  'OK': 'bg-green-100 text-green-800',
  'Attention': 'bg-yellow-100 text-yellow-800',
  'Urgent': 'bg-red-100 text-red-800',
  'Closed': 'bg-gray-100 text-gray-800',
}

export default function Projects() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingProject, setEditingProject] = useState<any>(null)
  const [filterLocation, setFilterLocation] = useState('')
  const [filterStatus, setFilterStatus] = useState('')

  const { data: projects, isLoading: projectsLoading } = useQuery(
    'projects',
    () => projectsApi.getAll().then(r => r.data)
  )

  const { data: locations } = useQuery(
    'locations',
    () => locationsApi.getAll().then(r => r.data)
  )

  const deleteMutation = useMutation(
    (id: string) => projectsApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('projects')
      },
    }
  )

  const handleEdit = (project: any) => {
    setEditingProject(project)
    setIsModalOpen(true)
  }

  const handleCreate = () => {
    setEditingProject(null)
    setIsModalOpen(true)
  }

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this project?')) {
      deleteMutation.mutate(id)
    }
  }

  const filteredProjects = projects?.filter((p: any) => {
    if (filterLocation && p.location_name !== filterLocation) return false
    if (filterStatus && p.status !== filterStatus) return false
    return true
  })

  const formatCurrency = (val: number) => {
    if (!val) return '-'
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
    return `$${val}`
  }

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-GB')
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Project Database</h1>
          <p className="text-gray-500 mt-1">Manage all projects for the Water Program</p>
        </div>
        <button onClick={handleCreate} className="btn-primary flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </button>
      </div>

      {/* Filters */}
      <div className="card mb-6 flex gap-4">
        <select
          value={filterLocation}
          onChange={(e) => setFilterLocation(e.target.value)}
          className="input max-w-xs"
        >
          <option value="">All Locations</option>
          {locations?.map((loc: any) => (
            <option key={loc.id} value={loc.name}>{loc.name}</option>
          ))}
        </select>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="input max-w-xs"
        >
          <option value="">All Statuses</option>
          <option value="In Progress">In Progress</option>
          <option value="Pending">Pending</option>
          <option value="At Risk">At Risk</option>
          <option value="Closed">Closed</option>
        </select>

        {(filterLocation || filterStatus) && (
          <button
            onClick={() => { setFilterLocation(''); setFilterStatus('') }}
            className="text-primary-600 hover:text-primary-700 text-sm"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Projects Table */}
      <div className="card overflow-hidden">
        {projectsLoading ? (
          <div className="p-8 text-center text-gray-500">Loading projects...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="table-header">ID</th>
                  <th className="table-header">Project Name</th>
                  <th className="table-header">Location</th>
                  <th className="table-header">Status</th>
                  <th className="table-header">Progress</th>
                  <th className="table-header">Budget</th>
                  <th className="table-header">Start</th>
                  <th className="table-header">End</th>
                  <th className="table-header">Alert</th>
                  <th className="table-header">Map</th>
                  <th className="table-header">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredProjects?.map((project: any) => (
                  <tr key={project.id} className="hover:bg-gray-50">
                    <td className="table-cell font-medium">{project.id}</td>
                    <td className="table-cell max-w-xs truncate" title={project.name}>
                      {project.name}
                    </td>
                    <td className="table-cell">{project.location_name}</td>
                    <td className="table-cell">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusColors[project.status] || 'bg-gray-100'}`}>
                        {project.status}
                      </span>
                    </td>
                    <td className="table-cell">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className="bg-primary-500 h-2 rounded-full"
                            style={{ width: `${(project.progress_pct || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs">{Math.round((project.progress_pct || 0) * 100)}%</span>
                      </div>
                    </td>
                    <td className="table-cell">{formatCurrency(project.total_budget)}</td>
                    <td className="table-cell">{formatDate(project.start_date)}</td>
                    <td className="table-cell">{formatDate(project.planned_end_date)}</td>
                    <td className="table-cell">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${alertColors[project.alert_level] || 'bg-gray-100'}`}>
                        {project.alert_level}
                      </span>
                    </td>
                    <td className="table-cell">
                      {project.latitude && project.longitude ? (
                        <span className="text-green-600">
                          <MapPin className="h-4 w-4" />
                        </span>
                      ) : (
                        <span className="text-gray-300">-</span>
                      )}
                    </td>
                    <td className="table-cell">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEdit(project)}
                          className="text-primary-600 hover:text-primary-800"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(project.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredProjects?.length === 0 && (
              <div className="p-8 text-center text-gray-500">
                No projects found matching the filters.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 mt-6">
        <div className="card">
          <p className="text-sm text-gray-500">Total Projects</p>
          <p className="text-2xl font-bold text-gray-900">{filteredProjects?.length || 0}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Total Budget</p>
          <p className="text-2xl font-bold text-primary-600">
            {formatCurrency(filteredProjects?.reduce((sum: number, p: any) => sum + (p.total_budget || 0), 0) || 0)}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Active Projects</p>
          <p className="text-2xl font-bold text-green-600">
            {filteredProjects?.filter((p: any) => p.status !== 'Closed').length || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">At Risk</p>
          <p className="text-2xl font-bold text-red-600">
            {filteredProjects?.filter((p: any) => p.alert_level === 'Urgent').length || 0}
          </p>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <ProjectModal
          project={editingProject}
          locations={locations || []}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </div>
  )
}
