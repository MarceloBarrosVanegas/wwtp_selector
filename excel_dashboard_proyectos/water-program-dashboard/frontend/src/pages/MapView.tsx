import { useState } from 'react'
import { useQuery } from 'react-query'
import { dashboardApi } from '../api/client'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import { Icon, LatLngBounds } from 'leaflet'
import { MapPin, Layers } from 'lucide-react'

// Custom marker icons
const createCustomIcon = (color: string) => new Icon({
  iconUrl: `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='${encodeURIComponent(color)}' stroke='white' stroke-width='2'%3E%3Cpath d='M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z'/%3E%3Ccircle cx='12' cy='10' r='3' fill='white'/%3E%3C/svg%3E`,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
})

// Fit bounds component
function FitBounds({ projects }: { projects: any[] }) {
  const map = useMap()
  
  if (projects.length > 0) {
    const bounds = new LatLngBounds(
      projects.map(p => [p.latitude, p.longitude])
    )
    map.fitBounds(bounds, { padding: [50, 50] })
  }
  
  return null
}

const statusColors: Record<string, string> = {
  'In Progress': '#2E75B6',
  'Pending': '#F79646',
  'At Risk': '#C0504D',
  'Closed': '#70AD47',
  'Suspended': '#A5A5A5',
}

export default function MapView() {
  const [selectedStatus, setSelectedStatus] = useState<string>('')
  const [mapType, setMapType] = useState<'street' | 'satellite'>('street')
  
  const { data: mapData, isLoading } = useQuery(
    'map-data',
    () => dashboardApi.getMap().then(r => r.data)
  )

  const filteredProjects = mapData?.projects?.filter((p: any) => {
    if (selectedStatus && p.status !== selectedStatus) return false
    return true
  }) || []

  const formatCurrency = (val: number) => {
    if (!val) return '$0'
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
    return `$${val}`
  }

  // Center of Galapagos
  const defaultCenter: [number, number] = [-0.6, -90.3]
  const defaultZoom = 8

  return (
    <div className="h-[calc(100vh-4rem)] -m-8 flex">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 flex items-center">
            <MapPin className="h-5 w-5 mr-2 text-primary-600" />
            Project Map
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            {filteredProjects.length} projects with coordinates
          </p>
        </div>

        {/* Filters */}
        <div className="p-4 border-b border-gray-200">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filter by Status
          </label>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="input"
          >
            <option value="">All Statuses</option>
            <option value="In Progress">In Progress</option>
            <option value="Pending">Pending</option>
            <option value="At Risk">At Risk</option>
            <option value="Closed">Closed</option>
          </select>
        </div>

        {/* Stats */}
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Summary by Location</h3>
          <div className="space-y-2">
            {mapData?.locations?.map((loc: any) => {
              const locProjects = filteredProjects.filter((p: any) => p.location_name === loc.name)
              const totalBudget = locProjects.reduce((sum: number, p: any) => sum + p.budget, 0)
              
              return (
                <div key={loc.id} className="flex items-center justify-between text-sm">
                  <div className="flex items-center">
                    <span 
                      className="w-3 h-3 rounded-full mr-2" 
                      style={{ backgroundColor: loc.color }}
                    />
                    <span>{loc.name}</span>
                  </div>
                  <div className="text-gray-500">
                    {locProjects.length} proj · {formatCurrency(totalBudget)}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Project List */}
        <div className="p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Projects</h3>
          <div className="space-y-3">
            {filteredProjects.map((project: any) => (
              <div 
                key={project.id} 
                className="p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-sm text-gray-900">{project.name}</p>
                    <p className="text-xs text-gray-500 mt-1">{project.location_name}</p>
                  </div>
                  <span 
                    className="w-2 h-2 rounded-full mt-1"
                    style={{ backgroundColor: statusColors[project.status] || '#999' }}
                  />
                </div>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className={`px-2 py-0.5 rounded-full ${
                    project.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                    project.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                    project.status === 'At Risk' ? 'bg-red-100 text-red-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {project.status}
                  </span>
                  <span className="text-gray-600">{formatCurrency(project.budget)}</span>
                </div>
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className="bg-primary-500 h-1.5 rounded-full"
                      style={{ width: `${project.progress_pct * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {Math.round(project.progress_pct * 100)}% complete
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 relative">
        {/* Map Controls */}
        <div className="absolute top-4 right-4 z-[1000] flex space-x-2">
          <button
            onClick={() => setMapType(mapType === 'street' ? 'satellite' : 'street')}
            className="bg-white p-2 rounded-lg shadow-md hover:bg-gray-50 flex items-center text-sm"
          >
            <Layers className="h-4 w-4 mr-2" />
            {mapType === 'street' ? 'Satellite' : 'Street'}
          </button>
        </div>

        {isLoading ? (
          <div className="h-full flex items-center justify-center bg-gray-100">
            <div className="text-gray-500">Loading map...</div>
          </div>
        ) : (
          <MapContainer
            center={defaultCenter}
            zoom={defaultZoom}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url={mapType === 'street' 
                ? 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
                : 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
              }
            />
            
            {filteredProjects.map((project: any) => (
              <Marker
                key={project.id}
                position={[project.latitude, project.longitude]}
                icon={createCustomIcon(statusColors[project.status] || '#4472C4')}
              >
                <Popup>
                  <div className="p-2 min-w-[250px]">
                    <h3 className="font-bold text-gray-900 mb-1">{project.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{project.location_name}</p>
                    
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Status:</span>
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          project.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                          project.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                          project.status === 'At Risk' ? 'bg-red-100 text-red-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {project.status}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Budget:</span>
                        <span className="font-medium">{formatCurrency(project.budget)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Progress:</span>
                        <span className="font-medium">{Math.round(project.progress_pct * 100)}%</span>
                      </div>
                    </div>
                    
                    <div className="mt-3">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-500 h-2 rounded-full"
                          style={{ width: `${project.progress_pct * 100}%` }}
                        />
                      </div>
                    </div>
                    
                    <div className="mt-2 text-xs text-gray-400">
                      Lat: {project.latitude.toFixed(4)}, Lng: {project.longitude.toFixed(4)}
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
            
            <FitBounds projects={filteredProjects} />
          </MapContainer>
        )}
      </div>
    </div>
  )
}
