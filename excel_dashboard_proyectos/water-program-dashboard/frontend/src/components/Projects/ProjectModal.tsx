import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { X } from 'lucide-react'
import { projectsApi } from '../../api/client'

interface ProjectModalProps {
  project: any
  locations: any[]
  onClose: () => void
}

const emptyProject = {
  id: '',
  name: '',
  description: '',
  location_id: '',
  owner: '',
  project_type: 'Other',
  status: 'Pending',
  start_date: '',
  planned_end_date: '',
  total_budget: '',
  year: new Date().getFullYear(),
  progress_pct: 0,
  next_action: '',
  notes: '',
  latitude: '',
  longitude: '',
  address: '',
}

export default function ProjectModal({ project, locations, onClose }: ProjectModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState(emptyProject)
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (project) {
      setFormData({
        ...emptyProject,
        ...project,
        start_date: project.start_date ? project.start_date.substring(0, 10) : '',
        planned_end_date: project.planned_end_date ? project.planned_end_date.substring(0, 10) : '',
        location_id: project.location_id?.toString() || '',
      })
    } else {
      // Generate next ID for new project
      projectsApi.getNextId().then(res => {
        setFormData(prev => ({ ...prev, id: res.data.next_id }))
      })
    }
  }, [project])

  const createMutation = useMutation(
    (data: any) => projectsApi.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('projects')
        onClose()
      },
    }
  )

  const updateMutation = useMutation(
    ({ id, data }: { id: string; data: any }) => projectsApi.update(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('projects')
        onClose()
      },
    }
  )

  const validate = () => {
    const newErrors: Record<string, string> = {}
    if (!formData.name) newErrors.name = 'Name is required'
    if (!formData.location_id) newErrors.location_id = 'Location is required'
    if (!formData.start_date) newErrors.start_date = 'Start date is required'
    if (!formData.planned_end_date) newErrors.planned_end_date = 'End date is required'
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    const data = {
      ...formData,
      location_id: parseInt(formData.location_id),
      total_budget: parseFloat(formData.total_budget) || 0,
      progress_pct: typeof formData.progress_pct === 'string' ? parseFloat(formData.progress_pct) || 0 : formData.progress_pct || 0,
      year: typeof formData.year === 'string' ? parseInt(formData.year) || new Date().getFullYear() : formData.year || new Date().getFullYear(),
      latitude: formData.latitude ? parseFloat(formData.latitude) : null,
      longitude: formData.longitude ? parseFloat(formData.longitude) : null,
    }

    if (project) {
      updateMutation.mutate({ id: project.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black/50" onClick={onClose} />
        
        <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-xl font-bold">
              {project ? 'Edit Project' : 'New Project'}
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            <div className="grid grid-cols-2 gap-6">
              {/* Basic Info */}
              <div className="space-y-4">
                <h3 className="font-medium text-gray-900 border-b pb-2">Basic Information</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Project ID</label>
                  <input
                    type="text"
                    name="id"
                    value={formData.id}
                    disabled
                    className="input bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`input ${errors.name ? 'border-red-500' : ''}`}
                  />
                  {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location *</label>
                  <select
                    name="location_id"
                    value={formData.location_id}
                    onChange={handleChange}
                    className={`input ${errors.location_id ? 'border-red-500' : ''}`}
                  >
                    <option value="">Select location</option>
                    {locations.map(loc => (
                      <option key={loc.id} value={loc.id}>{loc.name}</option>
                    ))}
                  </select>
                  {errors.location_id && <p className="text-red-500 text-xs mt-1">{errors.location_id}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Owner</label>
                  <input
                    type="text"
                    name="owner"
                    value={formData.owner}
                    onChange={handleChange}
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select
                    name="project_type"
                    value={formData.project_type}
                    onChange={handleChange}
                    className="input"
                  >
                    <option value="Construction">Construction</option>
                    <option value="Consulting">Consulting</option>
                    <option value="Software">Software</option>
                    <option value="Training">Training</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                    className="input"
                  >
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="At Risk">At Risk</option>
                    <option value="Closed">Closed</option>
                    <option value="Suspended">Suspended</option>
                  </select>
                </div>
              </div>

              {/* Timeline & Budget */}
              <div className="space-y-4">
                <h3 className="font-medium text-gray-900 border-b pb-2">Timeline & Budget</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Start Date *</label>
                    <input
                      type="date"
                      name="start_date"
                      value={formData.start_date}
                      onChange={handleChange}
                      className={`input ${errors.start_date ? 'border-red-500' : ''}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">End Date *</label>
                    <input
                      type="date"
                      name="planned_end_date"
                      value={formData.planned_end_date}
                      onChange={handleChange}
                      className={`input ${errors.planned_end_date ? 'border-red-500' : ''}`}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Total Budget ($)</label>
                    <input
                      type="number"
                      name="total_budget"
                      value={formData.total_budget}
                      onChange={handleChange}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                    <input
                      type="number"
                      name="year"
                      value={formData.year}
                      onChange={handleChange}
                      className="input"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Progress (%)</label>
                  <input
                    type="range"
                    name="progress_pct"
                    min="0"
                    max="1"
                    step="0.01"
                    value={formData.progress_pct}
                    onChange={handleChange}
                    className="w-full"
                  />
                  <p className="text-sm text-gray-500 mt-1">{Math.round((formData.progress_pct || 0) * 100)}%</p>
                </div>

                <h3 className="font-medium text-gray-900 border-b pb-2 mt-6">Geolocation</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
                    <input
                      type="number"
                      step="any"
                      name="latitude"
                      value={formData.latitude}
                      onChange={handleChange}
                      placeholder="-0.9538"
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
                    <input
                      type="number"
                      step="any"
                      name="longitude"
                      value={formData.longitude}
                      onChange={handleChange}
                      placeholder="-90.9656"
                      className="input"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                  <input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    className="input"
                  />
                </div>
              </div>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Next Action</label>
              <textarea
                name="next_action"
                value={formData.next_action}
                onChange={handleChange}
                rows={2}
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={3}
                className="input"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button type="button" onClick={onClose} className="btn-secondary">
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                {project ? 'Update Project' : 'Create Project'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
