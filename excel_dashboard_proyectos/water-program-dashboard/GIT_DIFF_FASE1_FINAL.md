diff --git a/excel_dashboard_proyectos/water-program-dashboard/ARCHITECTURE.md b/excel_dashboard_proyectos/water-program-dashboard/ARCHITECTURE.md
new file mode 100644
index 0000000..beb22a7
--- /dev/null
+++ b/excel_dashboard_proyectos/water-program-dashboard/ARCHITECTURE.md
@@ -0,0 +1,315 @@
+# Arquitectura del Proyecto - Water Program Dashboard
+
+## Estado Actual: Fase 1 Completada ✅
+
+**Fecha:** 6 de abril de 2026
+**Versión:** 1.0.0
+**Estado:** React + FastAPI funcionando con datos reales (13 proyectos, 3 ubicaciones)
+
+---
+
+## Arquitectura Unificada
+
+```
+┌─────────────────────────────────────────────────────────────┐
+│                         CLIENTE                              │
+│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
+│  │  React Frontend     │    │  Legacy HTML (fallback)     │ │
+│  │  http://localhost:  │    │  http://localhost:8000/     │ │
+│  │         3001        │    │         legacy              │ │
+│  └──────────┬──────────┘    └─────────────────────────────┘ │
+│             │                                                │
+│             │  Proxy /api/*                                  │
+│             │  CORS habilitado                               │
+│             ▼                                                │
+│  ┌──────────────────────────────────────────────────────┐   │
+│  │           FastAPI Backend (API-only)                 │   │
+│  │           http://localhost:8000                      │   │
+│  │                                                      │   │
+│  │  Endpoints:                                          │   │
+│  │  ├── /api/projects/*    (CRUD proyectos)            │   │
+│  │  ├── /api/locations/*   (CRUD ubicaciones)          │   │
+│  │  ├── /api/dashboard/*   (KPIs, timeline, datos)     │   │
+│  │  ├── /api/health        (health check)              │   │
+│  │  ├── /health            (health check alternativo)  │   │
+│  │  └── /legacy/*          (fallback HTML temporal)    │   │
+│  │                                                      │   │
+│  └────────────────────────┬─────────────────────────────┘   │
+│                           │                                  │
+│                           │  SQLAlchemy                      │
+│                           ▼                                  │
+│  ┌──────────────────────────────────────────────────────┐   │
+│  │           SQLite Database                            │   │
+│  │           water_program.db                           │   │
+│  │                                                      │   │
+│  │  Tablas:                                             │   │
+│  │  ├── projects         (13 proyectos activos)        │   │
+│  │  ├── locations        (3 ubicaciones)               │   │
+│  │  ├── cash_flows       (flujos de caja)              │   │
+│  │  └── parameters       (configuración sistema)       │   │
+│  └──────────────────────────────────────────────────────┘   │
+└─────────────────────────────────────────────────────────────┘
+```
+
+---
+
+## Puertos y URLs
+
+### Desarrollo
+
+| Servicio | URL | Propósito |
+|----------|-----|-----------|
+| React Dev | http://localhost:3001 | Frontend principal (puerto 3000 ocupado) |
+| FastAPI | http://localhost:8000 | API Backend |
+| API Docs | http://localhost:8000/docs | Swagger UI |
+| Legacy | http://localhost:8000/legacy | Fallback HTML temporal |
+
+### Endpoints API Confirmados
+
+```bash
+# Health checks
+GET http://localhost:8000/health
+GET http://localhost:8000/api/health
+
+# Proyectos (13 proyectos importados)
+GET    http://localhost:8000/api/projects
+GET    http://localhost:8000/api/projects/{id}
+POST   http://localhost:8000/api/projects
+PUT    http://localhost:8000/api/projects/{id}
+DELETE http://localhost:8000/api/projects/{id}
+
+# Ubicaciones (3 ubicaciones: Santa Cruz, Cristobal, Isabela)
+GET    http://localhost:8000/api/locations
+GET    http://localhost:8000/api/locations/{id}
+POST   http://localhost:8000/api/locations
+
+# Dashboard
+GET http://localhost:8000/api/dashboard/kpis
+GET http://localhost:8000/api/dashboard/data?year=2026
+GET http://localhost:8000/api/dashboard/timeline
+GET http://localhost:8000/api/dashboard/cashflow?project_id={id}
+GET http://localhost:8000/api/dashboard/map-data
+```
+
+---
+
+## CORS Configurado
+
+```python
+allow_origins=[
+    "http://localhost:3000",
+    "http://127.0.0.1:3000",
+    "http://localhost:3001",  # Puerto actual de React
+    "http://127.0.0.1:3001",
+    "http://localhost:8000",
+    "http://127.0.0.1:8000"
+]
+```
+
+---
+
+## Cómo Iniciar el Proyecto
+
+### Requisitos
+- Python 3.13+ con uv/pip
+- Node.js 24.x (instalado en `C:\Program Files\nodejs`)
+
+### Paso 1: Backend
+
+```bash
+# Desde water-program-dashboard/
+start-dev.bat
+```
+
+O manualmente:
+```bash
+cd backend
+uvicorn app.main:app --reload --port 8000
+```
+
+### Paso 2: Frontend
+
+```bash
+# Desde water-program-dashboard/
+start-react-bg.bat
+```
+
+O manualmente:
+```bash
+# En nueva terminal
+cd frontend
+npm install  # solo primera vez
+npm run dev
+```
+
+**Nota:** Si el puerto 3000 está ocupado, React usará 3001 automáticamente.
+
+### Paso 3: Importar Datos (si la base está vacía)
+
+```bash
+cd backend
+python import_data.py
+```
+
+Esto importa:
+- 3 ubicaciones: Santa Cruz, Cristobal, Isabela
+- 13 proyectos del Water Program
+- Parámetros del sistema
+
+---
+
+## Verificación de Funcionamiento
+
+### Backend
+```bash
+curl http://localhost:8000/health
+# {"status": "healthy"}
+
+curl http://localhost:8000/api/projects | head
+# [{"id":"P001","name":"WWTP Isabela DBA",...}]
+```
+
+### Frontend
+1. Abrir http://localhost:3001 en navegador
+2. Verificar que carga sin errores
+3. Probar navegación entre páginas
+
+### Proxy React → API
+```bash
+# Desde React (puerto 3001), probar proxy:
+curl http://localhost:3001/api/health
+# {"status": "healthy"}
+```
+
+---
+
+## Estructura de Archivos
+
+```
+water-program-dashboard/
+├── backend/
+│   ├── app/
+│   │   ├── main.py           # Entry point FastAPI
+│   │   ├── models.py         # SQLAlchemy models
+│   │   ├── schemas.py        # Pydantic schemas
+│   │   ├── crud.py           # Operaciones DB
+│   │   ├── database.py       # Conexión SQLite
+│   │   ├── routers/
+│   │   │   ├── projects.py   # /api/projects
+│   │   │   ├── locations.py  # /api/locations
+│   │   │   └── dashboard.py  # /api/dashboard
+│   │   └── services/
+│   │       └── gantt_builder.py
+│   ├── import_data.py        # Importa datos Excel→DB
+│   └── water_program.db      # SQLite database
+├── frontend/
+│   ├── src/
+│   │   ├── components/       # Componentes React
+│   │   ├── pages/            # Páginas (Home, Projects, etc.)
+│   │   ├── services/
+│   │   │   └── api.ts        # Cliente API (Axios)
+│   │   └── App.tsx           # Router principal
+│   ├── index.html
+│   ├── package.json
+│   └── vite.config.ts        # Proxy config
+├── static/
+│   └── excel-style.html      # Legacy fallback
+├── start-dev.bat             # Script inicio backend
+├── start-react-bg.bat        # Script inicio React (bg)
+├── data_export.json          # Datos exportados Excel
+└── ARCHITECTURE.md           # Este archivo
+```
+
+---
+
+## Datos Importados
+
+### Ubicaciones (3)
+| ID | Nombre | Presupuesto Anual |
+|----|--------|-------------------|
+| 1 | Santa Cruz | $2,000,000 |
+| 2 | Cristobal | $2,000,000 |
+| 3 | Isabela | $2,000,000 |
+
+### Proyectos (13)
+| ID | Nombre | Ubicación | Estado |
+|----|--------|-----------|--------|
+| P001 | WWTP Isabela DBA | Isabela | In Progress |
+| P002 | WWTP + Outafall San Cristobal Consultancy | Cristobal | In Progress |
+| P003 | WWTP + Outafall San Cristobal Construction | Cristobal | In Progress |
+| P004 | WTP Pozo Profundo Santa Cruz | Santa Cruz | Pending |
+| P005 | La Grieta - La Camiseta | Santa Cruz | Pending |
+| P006 | WTP Pozo Profundo Construction | Santa Cruz | Pending |
+| P007 | La Grieta - La Camiseta Construccion | Santa Cruz | Pending |
+| P008 | Water and WasteWater Master Plan Consultancy | Santa Cruz | Pending |
+| P009 | Non-Revenue Water | Santa Cruz | Pending |
+| P010 | ISP baseline | Santa Cruz | Pending |
+| P011 | ISP training | Santa Cruz | Pending |
+| P012 | OFC Water Consultant | Santa Cruz | Pending |
+| P013 | Political Liaison for OFC and GAD | Santa Cruz | Pending |
+
+---
+
+## Próximos Pasos (Fase 2)
+
+### Prioridad Alta
+1. **Corregir cálculo Cash Flow Gantt**
+   - Implementar distribución mensual exacta (IN/OUT/Net)
+   - Validar contra fórmulas Excel originales
+
+2. **Filtros dinámicos en Gantt**
+   - Ocultar/mostrar filas por ubicación
+   - Filtros por estado, año, etc.
+
+### Prioridad Media
+3. **Componentes React faltantes**
+   - Completar páginas de proyectos
+   - Implementar gráficos de dashboard
+   - Formularios de edición
+
+4. **Parámetros editables**
+   - Migrar fórmulas de hoja Parameters
+   - UI para modificar configuración
+
+### Limpieza
+5. Eliminar `/legacy` cuando React esté 100% funcional
+6. Borrar `node.exe` corrupto de raíz
+
+---
+
+## Troubleshooting
+
+### Puerto 3000 ocupado
+React automáticamente usa 3001. CORS ya está configurado para ambos.
+
+### Error "No such file or directory: package.json"
+Node.js no está en PATH. Usar ruta completa:
+```bash
+"C:\Program Files\nodejs\npm.cmd" install
+```
+
+### Base de datos vacía
+Ejecutar importación:
+```bash
+cd backend && python import_data.py
+```
+
+### CORS errors
+Verificar que el backend está corriendo en puerto 8000 y CORS incluye el puerto de React.
+
+---
+
+## Historial de Cambios
+
+### Fase 1 (Completada)
+- ✅ Unificación de arquitectura React + FastAPI
+- ✅ CORS configurado para puertos 3000/3001
+- ✅ Proxy Vite funcionando
+- ✅ Datos importados (13 proyectos, 3 ubicaciones)
+- ✅ Endpoints API verificados
+- ✅ Documentación actualizada
+
+### Fase 2 (Pendiente)
+- Migrar lógica VBA (Cash Flow, filtros, etc.)
+- Completar componentes React
+- Implementar fórmulas de Parameters
diff --git a/excel_dashboard_proyectos/water-program-dashboard/backend/app/main.py b/excel_dashboard_proyectos/water-program-dashboard/backend/app/main.py
new file mode 100644
index 0000000..b378f05
--- /dev/null
+++ b/excel_dashboard_proyectos/water-program-dashboard/backend/app/main.py
@@ -0,0 +1,77 @@
+from fastapi import FastAPI
+from fastapi.middleware.cors import CORSMiddleware
+from fastapi.staticfiles import StaticFiles
+from fastapi.responses import FileResponse, RedirectResponse
+from contextlib import asynccontextmanager
+import os
+
+from .database import engine
+from . import models
+from .routers import projects, locations, dashboard
+
+# Create tables on startup
+@asynccontextmanager
+async def lifespan(app: FastAPI):
+    models.Base.metadata.create_all(bind=engine)
+    yield
+
+app = FastAPI(
+    title="Water Program Galapagos API",
+    description="API para gestión de proyectos del Water Program",
+    version="1.0.0",
+    lifespan=lifespan
+)
+
+# CORS middleware - permite conexión desde React dev server (puerto 3000)
+# y desde el HTML legacy (puerto 8000/app)
+app.add_middleware(
+    CORSMiddleware,
+    allow_origins=[
+        "http://localhost:3000",
+        "http://127.0.0.1:3000",
+        "http://localhost:3001",  # Puerto alternativo si 3000 está ocupado
+        "http://127.0.0.1:3001",
+        "http://localhost:8000",
+        "http://127.0.0.1:8000"
+    ],
+    allow_credentials=True,
+    allow_methods=["*"],
+    allow_headers=["*"],
+)
+
+# Include routers
+app.include_router(projects.router)
+app.include_router(locations.router)
+app.include_router(dashboard.router)
+
+@app.get("/")
+def root():
+    """
+    Endpoint raíz - Información de la API.
+    
+    NOTA: El frontend oficial es React (corre en localhost:3000).
+    Para desarrollo sin Node.js, usar /legacy como fallback temporal.
+    """
+    return {
+        "message": "Water Program Galapagos API",
+        "version": "1.0.0",
+        "docs": "/docs",
+        "frontend_react": "http://localhost:3000",
+        "legacy_fallback": "/legacy",
+        "status": "API running. Install Node.js to run React frontend."
+    }
+
+@app.get("/health")
+def health_check():
+    return {"status": "healthy"}
+
+@app.get("/api/health")
+def health_check_api():
+    """Endpoint de health bajo /api para consistencia."""
+    return {"status": "healthy"}
+
+# Legacy: Servir HTML estático como fallback temporal durante transición
+# TODO: Eliminar cuando React esté completamente funcional
+static_path = os.path.join(os.path.dirname(__file__), "..", "..", "static")
+if os.path.exists(static_path):
+    app.mount("/legacy", StaticFiles(directory=static_path, html=True), name="legacy")
diff --git a/excel_dashboard_proyectos/water-program-dashboard/frontend/src/components/Projects/ProjectModal.tsx b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/components/Projects/ProjectModal.tsx
new file mode 100644
index 0000000..16055ad
--- /dev/null
+++ b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/components/Projects/ProjectModal.tsx
@@ -0,0 +1,362 @@
+import { useState, useEffect } from 'react'
+import { useMutation, useQueryClient } from 'react-query'
+import { X } from 'lucide-react'
+import { projectsApi } from '../../api/client'
+
+interface ProjectModalProps {
+  project: any
+  locations: any[]
+  onClose: () => void
+}
+
+const emptyProject = {
+  id: '',
+  name: '',
+  description: '',
+  location_id: '',
+  owner: '',
+  project_type: 'Other',
+  status: 'Pending',
+  start_date: '',
+  planned_end_date: '',
+  total_budget: '',
+  year: new Date().getFullYear(),
+  progress_pct: 0,
+  next_action: '',
+  notes: '',
+  latitude: '',
+  longitude: '',
+  address: '',
+}
+
+export default function ProjectModal({ project, locations, onClose }: ProjectModalProps) {
+  const queryClient = useQueryClient()
+  const [formData, setFormData] = useState(emptyProject)
+  const [errors, setErrors] = useState<Record<string, string>>({})
+
+  useEffect(() => {
+    if (project) {
+      setFormData({
+        ...emptyProject,
+        ...project,
+        start_date: project.start_date ? project.start_date.substring(0, 10) : '',
+        planned_end_date: project.planned_end_date ? project.planned_end_date.substring(0, 10) : '',
+        location_id: project.location_id?.toString() || '',
+      })
+    } else {
+      // Generate next ID for new project
+      projectsApi.getNextId().then(res => {
+        setFormData(prev => ({ ...prev, id: res.data.next_id }))
+      })
+    }
+  }, [project])
+
+  const createMutation = useMutation(
+    (data: any) => projectsApi.create(data),
+    {
+      onSuccess: () => {
+        queryClient.invalidateQueries('projects')
+        onClose()
+      },
+    }
+  )
+
+  const updateMutation = useMutation(
+    ({ id, data }: { id: string; data: any }) => projectsApi.update(id, data),
+    {
+      onSuccess: () => {
+        queryClient.invalidateQueries('projects')
+        onClose()
+      },
+    }
+  )
+
+  const validate = () => {
+    const newErrors: Record<string, string> = {}
+    if (!formData.name) newErrors.name = 'Name is required'
+    if (!formData.location_id) newErrors.location_id = 'Location is required'
+    if (!formData.start_date) newErrors.start_date = 'Start date is required'
+    if (!formData.planned_end_date) newErrors.planned_end_date = 'End date is required'
+    
+    setErrors(newErrors)
+    return Object.keys(newErrors).length === 0
+  }
+
+  const handleSubmit = (e: React.FormEvent) => {
+    e.preventDefault()
+    if (!validate()) return
+
+    const data = {
+      ...formData,
+      location_id: parseInt(formData.location_id),
+      total_budget: parseFloat(formData.total_budget) || 0,
+      progress_pct: parseFloat(formData.progress_pct) || 0,
+      year: parseInt(formData.year) || new Date().getFullYear(),
+      latitude: formData.latitude ? parseFloat(formData.latitude) : null,
+      longitude: formData.longitude ? parseFloat(formData.longitude) : null,
+    }
+
+    if (project) {
+      updateMutation.mutate({ id: project.id, data })
+    } else {
+      createMutation.mutate(data)
+    }
+  }
+
+  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
+    const { name, value } = e.target
+    setFormData(prev => ({ ...prev, [name]: value }))
+    if (errors[name]) {
+      setErrors(prev => ({ ...prev, [name]: '' }))
+    }
+  }
+
+  return (
+    <div className="fixed inset-0 z-50 overflow-y-auto">
+      <div className="flex items-center justify-center min-h-screen px-4">
+        <div className="fixed inset-0 bg-black/50" onClick={onClose} />
+        
+        <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
+          <div className="flex items-center justify-between p-6 border-b">
+            <h2 className="text-xl font-bold">
+              {project ? 'Edit Project' : 'New Project'}
+            </h2>
+            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
+              <X className="h-6 w-6" />
+            </button>
+          </div>
+
+          <form onSubmit={handleSubmit} className="p-6 space-y-6">
+            <div className="grid grid-cols-2 gap-6">
+              {/* Basic Info */}
+              <div className="space-y-4">
+                <h3 className="font-medium text-gray-900 border-b pb-2">Basic Information</h3>
+                
+                <div>
+                  <label className="block text-sm font-medium text-gray-700 mb-1">Project ID</label>
+                  <input
+                    type="text"
+                    name="id"
+                    value={formData.id}
+                    disabled
+                    className="input bg-gray-50"
+                  />
+                </div>
+
+                <div>
+                  <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
+                  <input
+                    type="text"
+                    name="name"
+                    value={formData.name}
+                    onChange={handleChange}
+                    className={`input ${errors.name ? 'border-red-500' : ''}`}
+                  />
+                  {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
+                </div>
+
+                <div>
+                  <label className="block text-sm font-medium text-gray-700 mb-1">Location *</label>
+                  <select
+                    name="location_id"
+                    value={formData.location_id}
+                    onChange={handleChange}
+                    className={`input ${errors.location_id ? 'border-red-500' : ''}`}
+                  >
+                    <option value="">Select location</option>
+                    {locations.map(loc => (
+                      <option key={loc.id} value={loc.id}>{loc.name}</option>
+                    ))}
+                  </select>
+                  {errors.location_id && <p className="text-red-500 text-xs mt-1">{errors.location_id}</p>}
+                </div>
+
+                <div>
+                  <label className="block text-sm font-medium text-gray-700 mb-1">Owner</label>
+                  <input
+                    type="text"
+                    name="owner"
+                    value={formData.owner}
+                    onChange={handleChange}
+                    className="input"
+                  />
+                </div>
+
+                <div>
+                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
+                  <select
+                    name="project_type"
+                    value={formData.project_type}
+                    onChange={handleChange}
+                    className="input"
+                  >
+                    <option value="Construction">Construction</option>
+                    <option value="Consulting">Consulting</option>
+                    <option value="Software">Software</option>
+                    <option value="Training">Training</option>
+                    <option value="Other">Other</option>
+                  </select>
+                </div>
+
+                <div>
+                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
+                  <select
+                    name="status"
+                    value={formData.status}
+                    onChange={handleChange}
+                    className="input"
+                  >
+                    <option value="Pending">Pending</option>
+                    <option value="In Progress">In Progress</option>
+                    <option value="At Risk">At Risk</option>
+                    <option value="Closed">Closed</option>
+                    <option value="Suspended">Suspended</option>
+                  </select>
+                </div>
+              </div>
+
+              {/* Timeline & Budget */}
+              <div className="space-y-4">
+                <h3 className="font-medium text-gray-900 border-b pb-2">Timeline & Budget</h3>
+                
+                <div className="grid grid-cols-2 gap-4">
+                  <div>
+                    <label className="block text-sm font-medium text-gray-700 mb-1">Start Date *</label>
+                    <input
+                      type="date"
+                      name="start_date"
+                      value={formData.start_date}
+                      onChange={handleChange}
+                      className={`input ${errors.start_date ? 'border-red-500' : ''}`}
+                    />
+                  </div>
+                  <div>
+                    <label className="block text-sm font-medium text-gray-700 mb-1">End Date *</label>
+                    <input
+                      type="date"
+                      name="planned_end_date"
+                      value={formData.planned_end_date}
+                      onChange={handleChange}
+                      className={`input ${errors.planned_end_date ? 'border-red-500' : ''}`}
+                    />
+                  </div>
+                </div>
+
+                <div className="grid grid-cols-2 gap-4">
+                  <div>
+                    <label className="block text-sm font-medium text-gray-700 mb-1">Total Budget ($)</label>
+                    <input
+                      type="number"
+                      name="total_budget"
+                      value={formData.total_budget}
+                      onChange={handleChange}
+                      className="input"
+                    />
+                  </div>
+                  <div>
+                    <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
+                    <input
+                      type="number"
+                      name="year"
+                      value={formData.year}
+                      onChange={handleChange}
+                      className="input"
+                    />
+                  </div>
+                </div>
+
+                <div>
+                  <label className="block text-sm font-medium text-gray-700 mb-1">Progress (%)</label>
+                  <input
+                    type="range"
+                    name="progress_pct"
+                    min="0"
+                    max="1"
+                    step="0.01"
+                    value={formData.progress_pct}
+                    onChange={handleChange}
+                    className="w-full"
+                  />
+                  <p className="text-sm text-gray-500 mt-1">{Math.round((formData.progress_pct || 0) * 100)}%</p>
+                </div>
+
+                <h3 className="font-medium text-gray-900 border-b pb-2 mt-6">Geolocation</h3>
+                
+                <div className="grid grid-cols-2 gap-4">
+                  <div>
+                    <label className="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
+                    <input
+                      type="number"
+                      step="any"
+                      name="latitude"
+                      value={formData.latitude}
+                      onChange={handleChange}
+                      placeholder="-0.9538"
+                      className="input"
+                    />
+                  </div>
+                  <div>
+                    <label className="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
+                    <input
+                      type="number"
+                      step="any"
+                      name="longitude"
+                      value={formData.longitude}
+                      onChange={handleChange}
+                      placeholder="-90.9656"
+                      className="input"
+                    />
+                  </div>
+                </div>
+
+                <div>
+                  <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
+                  <input
+                    type="text"
+                    name="address"
+                    value={formData.address}
+                    onChange={handleChange}
+                    className="input"
+                  />
+                </div>
+              </div>
+            </div>
+
+            {/* Notes */}
+            <div>
+              <label className="block text-sm font-medium text-gray-700 mb-1">Next Action</label>
+              <textarea
+                name="next_action"
+                value={formData.next_action}
+                onChange={handleChange}
+                rows={2}
+                className="input"
+              />
+            </div>
+
+            <div>
+              <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
+              <textarea
+                name="notes"
+                value={formData.notes}
+                onChange={handleChange}
+                rows={3}
+                className="input"
+              />
+            </div>
+
+            {/* Actions */}
+            <div className="flex justify-end space-x-3 pt-4 border-t">
+              <button type="button" onClick={onClose} className="btn-secondary">
+                Cancel
+              </button>
+              <button type="submit" className="btn-primary">
+                {project ? 'Update Project' : 'Create Project'}
+              </button>
+            </div>
+          </form>
+        </div>
+      </div>
+    </div>
+  )
+}
diff --git a/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/Charts.tsx b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/Charts.tsx
new file mode 100644
index 0000000..030943b
--- /dev/null
+++ b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/Charts.tsx
@@ -0,0 +1,246 @@
+import { useQuery } from 'react-query'
+import { dashboardApi } from '../api/client'
+import {
+  BarChart,
+  Bar,
+  XAxis,
+  YAxis,
+  CartesianGrid,
+  Tooltip,
+  Legend,
+  ResponsiveContainer,
+  PieChart,
+  Pie,
+  Cell,
+  LineChart,
+  Line,
+} from 'recharts'
+import { useState } from 'react'
+
+const COLORS = ['#2E75B6', '#F79646', '#5287936', '#C0504D', '#5592405', '#9978C4', '#FFC000']
+
+const formatCurrency = (val: number) => {
+  if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
+  if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
+  return `$${val}`
+}
+
+export default function Charts() {
+  const [activeTab, setActiveTab] = useState('budget-project')
+
+  const { data: budgetByProject } = useQuery(
+    'chart-budget-project',
+    () => dashboardApi.getChartBudgetByProject().then(r => r.data)
+  )
+
+  const { data: progressByProject } = useQuery(
+    'chart-progress-project',
+    () => dashboardApi.getChartProgressByProject().then(r => r.data)
+  )
+
+  const { data: statusDistribution } = useQuery(
+    'chart-status',
+    () => dashboardApi.getChartStatusDistribution().then(r => r.data)
+  )
+
+  const { data: budgetByLocation } = useQuery(
+    'chart-budget-location',
+    () => dashboardApi.getChartBudgetByLocation().then(r => r.data)
+  )
+
+  const tabs = [
+    { id: 'budget-project', name: 'Budget by Project', icon: '📊' },
+    { id: 'progress-project', name: 'Progress by Project', icon: '📈' },
+    { id: 'status', name: 'Status Distribution', icon: '🥧' },
+    { id: 'budget-location', name: 'Budget by Location', icon: '🗺️' },
+  ]
+
+  return (
+    <div className="space-y-6">
+      <div className="flex justify-between items-center">
+        <div>
+          <h1 className="text-2xl font-bold text-gray-900">Analytics & Charts</h1>
+          <p className="text-gray-500 mt-1">Visual analysis of project data</p>
+        </div>
+      </div>
+
+      {/* Tabs */}
+      <div className="flex space-x-2 border-b border-gray-200">
+        {tabs.map(tab => (
+          <button
+            key={tab.id}
+            onClick={() => setActiveTab(tab.id)}
+            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
+              activeTab === tab.id
+                ? 'border-primary-500 text-primary-600'
+                : 'border-transparent text-gray-500 hover:text-gray-700'
+            }`}
+          >
+            <span className="mr-2">{tab.icon}</span>
+            {tab.name}
+          </button>
+        ))}
+      </div>
+
+      {/* Chart Content */}
+      <div className="card">
+        {/* Budget by Project */}
+        {activeTab === 'budget-project' && (
+          <div>
+            <h3 className="text-lg font-semibold text-gray-900 mb-6">Annual Budget by Project</h3>
+            <div className="h-[500px]">
+              <ResponsiveContainer width="100%" height="100%">
+                <BarChart
+                  data={budgetByProject?.datasets?.[0]?.data?.map((val: number, idx: number) => ({
+                    name: budgetByProject.labels[idx]?.length > 20 
+                      ? budgetByProject.labels[idx].substring(0, 20) + '...' 
+                      : budgetByProject.labels[idx],
+                    fullName: budgetByProject.labels[idx],
+                    budget: val
+                  })) || []}
+                  layout="vertical"
+                  margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
+                >
+                  <CartesianGrid strokeDasharray="3 3" />
+                  <XAxis type="number" tickFormatter={formatCurrency} />
+                  <YAxis type="category" dataKey="name" width={150} />
+                  <Tooltip 
+                    formatter={(value: number) => formatCurrency(value)}
+                    labelFormatter={(label, payload) => payload?.[0]?.payload?.fullName || label}
+                  />
+                  <Bar dataKey="budget" fill="#2E75B6" />
+                </BarChart>
+              </ResponsiveContainer>
+            </div>
+          </div>
+        )}
+
+        {/* Progress by Project */}
+        {activeTab === 'progress-project' && (
+          <div>
+            <h3 className="text-lg font-semibold text-gray-900 mb-6">Progress by Project</h3>
+            <div className="h-[500px]">
+              <ResponsiveContainer width="100%" height="100%">
+                <BarChart
+                  data={progressByProject?.datasets?.[0]?.data?.map((val: number, idx: number) => ({
+                    name: progressByProject.labels[idx]?.length > 20 
+                      ? progressByProject.labels[idx].substring(0, 20) + '...' 
+                      : progressByProject.labels[idx],
+                    fullName: progressByProject.labels[idx],
+                    progress: val
+                  })) || []}
+                  layout="vertical"
+                  margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
+                >
+                  <CartesianGrid strokeDasharray="3 3" />
+                  <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
+                  <YAxis type="category" dataKey="name" width={150} />
+                  <Tooltip formatter={(value: number) => `${value.toFixed(0)}%`} />
+                  <Bar dataKey="progress" fill="#4472C4" />
+                </BarChart>
+              </ResponsiveContainer>
+            </div>
+          </div>
+        )}
+
+        {/* Status Distribution */}
+        {activeTab === 'status' && (
+          <div>
+            <h3 className="text-lg font-semibold text-gray-900 mb-6">Projects by Status</h3>
+            <div className="grid grid-cols-2 gap-8">
+              <div className="h-[400px]">
+                <ResponsiveContainer width="100%" height="100%">
+                  <PieChart>
+                    <Pie
+                      data={statusDistribution?.labels?.map((label: string, idx: number) => ({
+                        name: label,
+                        value: statusDistribution.datasets[0].data[idx],
+                        color: statusDistribution.datasets[0].backgroundColor[idx]
+                      })) || []}
+                      cx="50%"
+                      cy="50%"
+                      labelLine={false}
+                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
+                      outerRadius={120}
+                      fill="#8884d8"
+                      dataKey="value"
+                    >
+                      {(statusDistribution?.labels || []).map((_: any, index: number) => (
+                        <Cell key={`cell-${index}`} fill={statusDistribution.datasets[0].backgroundColor[index]} />
+                      ))}
+                    </Pie>
+                    <Tooltip />
+                  </PieChart>
+                </ResponsiveContainer>
+              </div>
+              <div className="flex items-center">
+                <div className="space-y-4">
+                  {statusDistribution?.labels?.map((label: string, idx: number) => (
+                    <div key={label} className="flex items-center">
+                      <span 
+                        className="w-4 h-4 rounded mr-3"
+                        style={{ backgroundColor: statusDistribution.datasets[0].backgroundColor[idx] }}
+                      />
+                      <span className="text-gray-700">{label}</span>
+                      <span className="ml-auto font-medium text-gray-900">
+                        {statusDistribution.datasets[0].data[idx]} projects
+                      </span>
+                    </div>
+                  ))}
+                </div>
+              </div>
+            </div>
+          </div>
+        )}
+
+        {/* Budget by Location */}
+        {activeTab === 'budget-location' && (
+          <div>
+            <h3 className="text-lg font-semibold text-gray-900 mb-6">Budget by Location</h3>
+            <div className="h-[500px]">
+              <ResponsiveContainer width="100%" height="100%">
+                <PieChart>
+                  <Pie
+                    data={budgetByLocation?.labels?.map((label: string, idx: number) => ({
+                      name: label,
+                      value: budgetByLocation.datasets[0].data[idx]
+                    })) || []}
+                    cx="50%"
+                    cy="50%"
+                    innerRadius={60}
+                    outerRadius={150}
+                    paddingAngle={5}
+                    dataKey="value"
+                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
+                  >
+                    {(budgetByLocation?.labels || []).map((_: any, index: number) => (
+                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
+                    ))}
+                  </Pie>
+                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
+                  <Legend />
+                </PieChart>
+              </ResponsiveContainer>
+            </div>
+            <div className="grid grid-cols-3 gap-4 mt-6">
+              {budgetByLocation?.labels?.map((label: string, idx: number) => (
+                <div key={label} className="bg-gray-50 p-4 rounded-lg">
+                  <div className="flex items-center mb-2">
+                    <span 
+                      className="w-3 h-3 rounded-full mr-2"
+                      style={{ backgroundColor: COLORS[idx % COLORS.length] }}
+                    />
+                    <span className="font-medium">{label}</span>
+                  </div>
+                  <p className="text-2xl font-bold text-gray-900">
+                    {formatCurrency(budgetByLocation.datasets[0].data[idx])}
+                  </p>
+                </div>
+              ))}
+            </div>
+          </div>
+        )}
+      </div>
+    </div>
+  )
+}
diff --git a/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/Dashboard.tsx b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/Dashboard.tsx
new file mode 100644
index 0000000..9926cb6
--- /dev/null
+++ b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/Dashboard.tsx
@@ -0,0 +1,275 @@
+import { useQuery } from 'react-query'
+import { dashboardApi } from '../api/client'
+import { 
+  Building2, 
+  Activity, 
+  CheckCircle2, 
+  AlertTriangle,
+  TrendingUp,
+  Calendar
+} from 'lucide-react'
+
+const statusColors: Record<string, string> = {
+  'OK': 'bg-green-100 text-green-800 border-green-200',
+  'Attention': 'bg-yellow-100 text-yellow-800 border-yellow-200',
+  'Urgent': 'bg-red-100 text-red-800 border-red-200',
+}
+
+export default function Dashboard() {
+  const { data: dashboardData, isLoading } = useQuery(
+    'dashboard',
+    () => dashboardApi.getDashboardData(2026, 3).then(r => r.data)
+  )
+
+  const { data: chartData } = useQuery(
+    'chart-status',
+    () => dashboardApi.getChartStatusDistribution().then(r => r.data)
+  )
+
+  const formatCurrency = (val: number) => {
+    if (!val) return '$0'
+    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
+    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
+    return `$${val.toFixed(0)}`
+  }
+
+  const formatDate = (dateStr: string) => {
+    if (!dateStr) return '-'
+    const date = new Date(dateStr)
+    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
+  }
+
+  const kpis = dashboardData?.kpis
+  const timeline = dashboardData?.location_timeline || []
+
+  // Calculate year totals
+  const years = timeline.length > 0 ? Object.keys(timeline[0].budgets) : []
+  
+  const yearTotals = years.map(year => ({
+    year,
+    total: timeline.reduce((sum, loc) => sum + (loc.budgets[year] || 0), 0),
+    limit: timeline.reduce((sum, loc) => sum + 2000000, 0), // Annual limit
+  }))
+
+  return (
+    <div className="space-y-6">
+      {/* Header */}
+      <div className="flex justify-between items-center">
+        <div>
+          <h1 className="text-2xl font-bold text-gray-900">Water Program Galapagos Dashboard</h1>
+          <p className="text-gray-500 mt-1">Program overview and key performance indicators</p>
+        </div>
+        <div className="text-right">
+          <p className="text-sm text-gray-500">Active Year</p>
+          <p className="text-2xl font-bold text-primary-600">2026</p>
+        </div>
+      </div>
+
+      {/* KPI Cards */}
+      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
+        <div className="card p-4">
+          <div className="flex items-center">
+            <div className="p-2 bg-blue-100 rounded-lg">
+              <Building2 className="h-5 w-5 text-blue-600" />
+            </div>
+            <div className="ml-3">
+              <p className="text-xs text-gray-500">Total Projects</p>
+              <p className="text-xl font-bold">{kpis?.total_projects || 0}</p>
+            </div>
+          </div>
+        </div>
+
+        <div className="card p-4">
+          <div className="flex items-center">
+            <div className="p-2 bg-green-100 rounded-lg">
+              <Activity className="h-5 w-5 text-green-600" />
+            </div>
+            <div className="ml-3">
+              <p className="text-xs text-gray-500">Active</p>
+              <p className="text-xl font-bold">{kpis?.active_projects || 0}</p>
+            </div>
+          </div>
+        </div>
+
+        <div className="card p-4">
+          <div className="flex items-center">
+            <div className="p-2 bg-gray-100 rounded-lg">
+              <CheckCircle2 className="h-5 w-5 text-gray-600" />
+            </div>
+            <div className="ml-3">
+              <p className="text-xs text-gray-500">Closed</p>
+              <p className="text-xl font-bold">{kpis?.closed_projects || 0}</p>
+            </div>
+          </div>
+        </div>
+
+        <div className="card p-4">
+          <div className="flex items-center">
+            <div className="p-2 bg-red-100 rounded-lg">
+              <AlertTriangle className="h-5 w-5 text-red-600" />
+            </div>
+            <div className="ml-3">
+              <p className="text-xs text-gray-500">At Risk</p>
+              <p className="text-xl font-bold">{kpis?.at_risk_projects || 0}</p>
+            </div>
+          </div>
+        </div>
+
+        <div className="card p-4">
+          <div className="flex items-center">
+            <div className="p-2 bg-purple-100 rounded-lg">
+              <TrendingUp className="h-5 w-5 text-purple-600" />
+            </div>
+            <div className="ml-3">
+              <p className="text-xs text-gray-500">Avg Progress</p>
+              <p className="text-xl font-bold">{Math.round((kpis?.average_progress || 0) * 100)}%</p>
+            </div>
+          </div>
+        </div>
+
+        <div className="card p-4">
+          <div className="flex items-center">
+            <div className="p-2 bg-orange-100 rounded-lg">
+              <Calendar className="h-5 w-5 text-orange-600" />
+            </div>
+            <div className="ml-3">
+              <p className="text-xs text-gray-500">Next Deadline</p>
+              <p className="text-sm font-bold">{formatDate(kpis?.next_deadline)}</p>
+            </div>
+          </div>
+        </div>
+      </div>
+
+      {/* Budget Summary */}
+      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
+        <div className="card">
+          <h3 className="font-semibold text-gray-900 mb-4">Committed Budget</h3>
+          <p className="text-3xl font-bold text-primary-600">
+            {formatCurrency(kpis?.committed_budget || 0)}
+          </p>
+          <p className="text-sm text-gray-500 mt-1">Total across all projects</p>
+        </div>
+
+        <div className="card">
+          <h3 className="font-semibold text-gray-900 mb-4">Budget Used</h3>
+          <p className="text-3xl font-bold text-galapagos-accent">
+            {formatCurrency(kpis?.total_budget_used || 0)}
+          </p>
+          <div className="mt-2">
+            <div className="w-full bg-gray-200 rounded-full h-2">
+              <div
+                className="bg-galapagos-accent h-2 rounded-full"
+                style={{ width: `${Math.min(100, (kpis?.average_progress || 0) * 100)}%` }}
+              />
+            </div>
+          </div>
+        </div>
+
+        <div className="card">
+          <h3 className="font-semibold text-gray-900 mb-4">Remaining Budget</h3>
+          <p className="text-3xl font-bold text-green-600">
+            {formatCurrency((kpis?.committed_budget || 0) - (kpis?.total_budget_used || 0))}
+          </p>
+          <p className="text-sm text-gray-500 mt-1">Available to spend</p>
+        </div>
+      </div>
+
+      {/* Location Budget Timeline */}
+      <div className="card">
+        <h2 className="text-lg font-bold text-gray-900 mb-6">Location Budget Timeline</h2>
+        
+        {isLoading ? (
+          <div className="text-center py-8 text-gray-500">Loading...</div>
+        ) : (
+          <div className="overflow-x-auto">
+            <table className="min-w-full">
+              <thead>
+                <tr className="border-b-2 border-black">
+                  <th className="text-left py-3 px-4 font-semibold">Location</th>
+                  {years.map(year => (
+                    <th key={year} className="text-center py-3 px-4 font-semibold">{year}</th>
+                  ))}
+                  <th className="text-center py-3 px-4 font-semibold">Total</th>
+                </tr>
+              </thead>
+              <tbody className="divide-y divide-gray-200">
+                {timeline.map((loc: any) => (
+                  <>
+                    <tr key={loc.location_id} className="hover:bg-gray-50">
+                      <td className="py-3 px-4 font-medium">{loc.location_name}</td>
+                      {years.map(year => (
+                        <td key={year} className="text-right py-3 px-4">
+                          {formatCurrency(loc.budgets[year] || 0)}
+                        </td>
+                      ))}
+                      <td className="text-right py-3 px-4 font-semibold">
+                        {formatCurrency(loc.total)}
+                      </td>
+                    </tr>
+                    <tr key={`${loc.location_id}-balance`} className="bg-gray-50/50 text-sm">
+                      <td className="py-2 px-4 text-gray-500 italic">Balance</td>
+                      {years.map(year => {
+                        const balance = loc.balances[year] || 0
+                        return (
+                          <td key={year} className={`text-right py-2 px-4 ${balance < 0 ? 'text-red-600' : 'text-green-600'}`}>
+                            {formatCurrency(balance)}
+                          </td>
+                        )
+                      })}
+                      <td className="text-right py-2 px-4">
+                        {formatCurrency(Object.values(loc.balances).reduce((a: number, b: number) => a + b, 0))}
+                      </td>
+                    </tr>
+                  </>
+                ))}
+                
+                {/* Totals Row */}
+                <tr className="border-t-2 border-gray-300 font-bold bg-gray-50">
+                  <td className="py-4 px-4">TOTAL</td>
+                  {yearTotals.map(({ year, total }) => (
+                    <td key={year} className="text-right py-4 px-4">{formatCurrency(total)}</td>
+                  ))}
+                  <td className="text-right py-4 px-4">
+                    {formatCurrency(yearTotals.reduce((sum, y) => sum + y.total, 0))}
+                  </td>
+                </tr>
+
+                {/* Balance General */}
+                <tr className="bg-blue-50 text-sm">
+                  <td className="py-3 px-4 font-medium text-blue-900">Balance General</td>
+                  {yearTotals.map(({ year, total, limit }) => {
+                    const balance = limit - total
+                    return (
+                      <td key={year} className={`text-right py-3 px-4 font-medium ${balance < 0 ? 'text-red-600' : 'text-green-600'}`}>
+                        {formatCurrency(balance)}
+                      </td>
+                    )
+                  })}
+                  <td className="text-right py-3 px-4">
+                    {formatCurrency(yearTotals.reduce((sum, y) => sum + (y.limit - y.total), 0))}
+                  </td>
+                </tr>
+              </tbody>
+            </table>
+          </div>
+        )}
+      </div>
+
+      {/* Status Legend */}
+      <div className="flex gap-4 text-sm">
+        <div className="flex items-center">
+          <span className="w-3 h-3 rounded-full bg-green-500 mr-2"></span>
+          <span>On Track</span>
+        </div>
+        <div className="flex items-center">
+          <span className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></span>
+          <span>Attention</span>
+        </div>
+        <div className="flex items-center">
+          <span className="w-3 h-3 rounded-full bg-red-500 mr-2"></span>
+          <span>Over Limit</span>
+        </div>
+      </div>
+    </div>
+  )
+}
diff --git a/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/Gantt.tsx b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/Gantt.tsx
new file mode 100644
index 0000000..1c705d2
--- /dev/null
+++ b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/Gantt.tsx
@@ -0,0 +1,303 @@
+import { useState } from 'react'
+import { useQuery } from 'react-query'
+import { dashboardApi, locationsApi } from '../api/client'
+import { format, addMonths, parseISO } from 'date-fns'
+
+export default function Gantt() {
+  const [filterLocation, setFilterLocation] = useState('All Locations')
+  
+  const { data: locations } = useQuery('locations', () => locationsApi.getAll().then(r => r.data))
+  
+  const { data: ganttData, isLoading } = useQuery(
+    ['gantt', filterLocation],
+    () => dashboardApi.getGantt({ filter_location: filterLocation }).then(r => r.data),
+    { enabled: !!locations }
+  )
+
+  const formatCurrency = (val: number) => {
+    if (!val) return '-'
+    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
+    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
+    return `$${val}`
+  }
+
+  const months = ganttData?.months || []
+
+  return (
+    <div className="space-y-6">
+      <div className="flex justify-between items-center">
+        <div>
+          <h1 className="text-2xl font-bold text-gray-900">Cash Flow Gantt</h1>
+          <p className="text-gray-500 mt-1">Visual timeline of budgets and expenses by location</p>
+        </div>
+        
+        <select
+          value={filterLocation}
+          onChange={(e) => setFilterLocation(e.target.value)}
+          className="input max-w-xs"
+        >
+          <option value="All Locations">All Locations</option>
+          {locations?.map((loc: any) => (
+            <option key={loc.id} value={loc.name}>{loc.name}</option>
+          ))}
+        </select>
+      </div>
+
+      {isLoading ? (
+        <div className="card p-8 text-center text-gray-500">Loading Gantt...</div>
+      ) : (
+        <>
+          {/* INFLOW Section */}
+          <div className="card overflow-hidden">
+            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
+              <span className="w-3 h-3 bg-green-500 rounded mr-2"></span>
+              INCOME BY LOCATION (IN)
+            </h3>
+            
+            <div className="overflow-x-auto">
+              <table className="min-w-full text-sm">
+                <thead>
+                  <tr className="bg-primary-900 text-white">
+                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
+                    <th className="text-right py-2 px-3 font-medium w-24">Initial</th>
+                    {months.map((month: string) => (
+                      <th key={month} className="text-center py-2 px-2 font-medium text-xs w-16">
+                        {month}
+                      </th>
+                    ))}
+                  </tr>
+                </thead>
+                <tbody className="divide-y divide-gray-200">
+                  {ganttData?.inflow_data?.map((row: any) => (
+                    <tr key={row.location_id} className="hover:bg-gray-50">
+                      <td className="py-2 px-3 font-medium">{row.location_name}</td>
+                      <td className="text-right py-2 px-3 text-green-600">
+                        {formatCurrency(row.initial_value)}
+                      </td>
+                      {months.map((month: string) => {
+                        const val = row.months[month]
+                        return (
+                          <td key={month} className="text-center py-2 px-2">
+                            {val ? (
+                              <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
+                                {formatCurrency(val)}
+                              </span>
+                            ) : (
+                              <span className="text-gray-300">-</span>
+                            )}
+                          </td>
+                        )
+                      })}
+                    </tr>
+                  ))}
+                </tbody>
+              </table>
+            </div>
+          </div>
+
+          {/* CUMULATIVE SUM Section */}
+          <div className="card overflow-hidden">
+            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
+              <span className="w-3 h-3 bg-blue-500 rounded mr-2"></span>
+              CUMULATIVE SUM (Running Balance)
+            </h3>
+            
+            <div className="overflow-x-auto">
+              <table className="min-w-full text-sm">
+                <thead>
+                  <tr className="bg-blue-900 text-white">
+                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
+                    {months.map((month: string) => (
+                      <th key={month} className="text-center py-2 px-2 font-medium text-xs w-16">
+                        {month}
+                      </th>
+                    ))}
+                  </tr>
+                </thead>
+                <tbody>
+                  {ganttData?.cumulative_data
+                    ?.filter((row: any) => row.row_type === 'cumulative_in')
+                    .map((row: any) => (
+                    <tr key={row.location_id} className="hover:bg-gray-50 bg-blue-50/30">
+                      <td className="py-2 px-3 font-medium text-blue-900">{row.location_name}</td>
+                      {months.map((month: string) => (
+                        <td key={month} className="text-center py-2 px-2 text-xs">
+                          {formatCurrency(row.values[month] || 0)}
+                        </td>
+                      ))}
+                    </tr>
+                  ))}
+                  
+                  {/* General Cumulative */}
+                  <tr className="bg-gray-100 font-bold">
+                    <td className="py-3 px-3">General Cumulative</td>
+                    {months.map((month: string, idx: number) => {
+                      const sum = ganttData?.cumulative_data
+                        ?.filter((row: any) => row.row_type === 'cumulative_in')
+                        .reduce((acc: number, row: any) => acc + (row.values[month] || 0), 0) || 0
+                      return (
+                        <td key={month} className="text-center py-3 px-2">
+                          {formatCurrency(sum)}
+                        </td>
+                      )
+                    })}
+                  </tr>
+                </tbody>
+              </table>
+            </div>
+          </div>
+
+          {/* PROJECTS Section */}
+          <div className="card overflow-hidden">
+            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
+              <span className="w-3 h-3 bg-orange-500 rounded mr-2"></span>
+              PROJECTS (OUT)
+            </h3>
+            
+            <div className="overflow-x-auto">
+              <table className="min-w-full text-sm">
+                <thead>
+                  <tr className="bg-orange-900 text-white">
+                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
+                    <th className="text-left py-2 px-3 font-medium min-w-[200px]">Project</th>
+                    <th className="text-center py-2 px-3 font-medium w-20">Status</th>
+                    <th className="text-right py-2 px-3 font-medium w-24">Budget</th>
+                    {months.slice(0, 12).map((month: string) => (
+                      <th key={month} className="text-center py-2 px-1 font-medium text-xs w-12">
+                        {month}
+                      </th>
+                    ))}
+                  </tr>
+                </thead>
+                <tbody className="divide-y divide-gray-200">
+                  {ganttData?.items?.map((item: any) => (
+                    <tr key={item.id} className="hover:bg-gray-50">
+                      <td className="py-2 px-3 font-medium">{item.location}</td>
+                      <td className="py-2 px-3 max-w-xs truncate" title={item.content}>
+                        {item.content}
+                      </td>
+                      <td className="text-center py-2 px-3">
+                        <span className={`inline-flex px-2 py-0.5 text-xs rounded-full ${
+                          item.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
+                          item.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
+                          item.status === 'At Risk' ? 'bg-red-100 text-red-800' :
+                          'bg-green-100 text-green-800'
+                        }`}>
+                          {item.status}
+                        </span>
+                      </td>
+                      <td className="text-right py-2 px-3 font-medium">
+                        {formatCurrency(item.amount)}
+                      </td>
+                      {months.slice(0, 12).map((month: string) => {
+                        const itemStart = new Date(item.start)
+                        const itemEnd = item.end ? new Date(item.end) : itemStart
+                        const monthDate = parseISO(`2026-${month.split('-')[0]}-01`)
+                        const isActive = monthDate >= itemStart && monthDate <= itemEnd
+                        
+                        return (
+                          <td key={month} className="text-center py-1 px-1">
+                            {isActive && (
+                              <div 
+                                className="h-6 rounded bg-cyan-200 border border-cyan-300 text-xs flex items-center justify-center"
+                                title={`${item.content}: ${formatCurrency(item.amount)}`}
+                              >
+                                {formatCurrency(item.amount / Math.max(1, Math.ceil((itemEnd - itemStart) / (1000 * 60 * 60 * 24 * 30))))}
+                              </div>
+                            )}
+                          </td>
+                        )
+                      })}
+                    </tr>
+                  ))}
+                </tbody>
+              </table>
+            </div>
+          </div>
+
+          {/* CUMULATIVE COST */}
+          <div className="card overflow-hidden">
+            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
+              <span className="w-3 h-3 bg-red-500 rounded mr-2"></span>
+              CUMULATIVE COST
+            </h3>
+            
+            <div className="overflow-x-auto">
+              <table className="min-w-full text-sm">
+                <thead>
+                  <tr className="bg-red-900 text-white">
+                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
+                    {months.slice(0, 12).map((month: string) => (
+                      <th key={month} className="text-center py-2 px-2 font-medium text-xs w-16">
+                        {month}
+                      </th>
+                    ))}
+                  </tr>
+                </thead>
+                <tbody>
+                  <tr className="bg-gray-100 font-bold">
+                    <td className="py-3 px-3">Cumulative Cost</td>
+                    {months.slice(0, 12).map((month: string) => {
+                      const cost = ganttData?.items?.reduce((sum: number, item: any) => {
+                        const itemStart = new Date(item.start)
+                        const itemEnd = item.end ? new Date(item.end) : itemStart
+                        const monthDate = parseISO(`2026-${month.split('-')[0]}-01`)
+                        if (monthDate >= itemStart && monthDate <= itemEnd) {
+                          return sum + (item.amount / Math.max(1, Math.ceil((itemEnd - itemStart) / (1000 * 60 * 60 * 24 * 30))))
+                        }
+                        return sum
+                      }, 0) || 0
+                      return (
+                        <td key={month} className="text-center py-3 px-2">
+                          {formatCurrency(cost)}
+                        </td>
+                      )
+                    })}
+                  </tr>
+                </tbody>
+              </table>
+            </div>
+          </div>
+
+          {/* NET CASH FLOW */}
+          <div className="card overflow-hidden">
+            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
+              <span className="w-3 h-3 bg-purple-500 rounded mr-2"></span>
+              NET CASH FLOW (In - Out)
+            </h3>
+            
+            <div className="overflow-x-auto">
+              <table className="min-w-full text-sm">
+                <thead>
+                  <tr className="bg-purple-900 text-white">
+                    <th className="text-left py-2 px-3 font-medium w-32">Location</th>
+                    {months.slice(0, 12).map((month: string) => (
+                      <th key={month} className="text-center py-2 px-2 font-medium text-xs w-16">
+                        {month}
+                      </th>
+                    ))}
+                  </tr>
+                </thead>
+                <tbody>
+                  {ganttData?.net_cash_flow?.map((row: any) => (
+                    <tr key={row.location_id} className="hover:bg-gray-50">
+                      <td className="py-2 px-3 font-medium">{row.location_name}</td>
+                      {months.slice(0, 12).map((month: string) => {
+                        const val = row.values[month] || 0
+                        return (
+                          <td key={month} className={`text-center py-2 px-2 text-xs font-medium ${val < 0 ? 'text-red-600' : 'text-green-600'}`}>
+                            {formatCurrency(val)}
+                          </td>
+                        )
+                      })}
+                    </tr>
+                  ))}
+                </tbody>
+              </table>
+            </div>
+          </div>
+        </>
+      )}
+    </div>
+  )
+}
diff --git a/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/MapView.tsx b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/MapView.tsx
new file mode 100644
index 0000000..2600de2
--- /dev/null
+++ b/excel_dashboard_proyectos/water-program-dashboard/frontend/src/pages/MapView.tsx
@@ -0,0 +1,260 @@
+import { useState } from 'react'
+import { useQuery } from 'react-query'
+import { dashboardApi, projectsApi } from '../api/client'
+import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
+import { Icon, LatLngBounds } from 'leaflet'
+import { MapPin, Navigation, Layers } from 'lucide-react'
+
+// Custom marker icons
+const createCustomIcon = (color: string) => new Icon({
+  iconUrl: `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='${encodeURIComponent(color)}' stroke='white' stroke-width='2'%3E%3Cpath d='M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z'/%3E%3Ccircle cx='12' cy='10' r='3' fill='white'/%3E%3C/svg%3E`,
+  iconSize: [32, 32],
+  iconAnchor: [16, 32],
+  popupAnchor: [0, -32]
+})
+
+// Fit bounds component
+function FitBounds({ projects }: { projects: any[] }) {
+  const map = useMap()
+  
+  if (projects.length > 0) {
+    const bounds = new LatLngBounds(
+      projects.map(p => [p.latitude, p.longitude])
+    )
+    map.fitBounds(bounds, { padding: [50, 50] })
+  }
+  
+  return null
+}
+
+const statusColors: Record<string, string> = {
+  'In Progress': '#2E75B6',
+  'Pending': '#F79646',
+  'At Risk': '#C0504D',
+  'Closed': '#70AD47',
+  'Suspended': '#A5A5A5',
+}
+
+export default function MapView() {
+  const [selectedStatus, setSelectedStatus] = useState<string>('')
+  const [mapType, setMapType] = useState<'street' | 'satellite'>('street')
+  
+  const { data: mapData, isLoading } = useQuery(
+    'map-data',
+    () => dashboardApi.getMap().then(r => r.data)
+  )
+
+  const { data: allProjects } = useQuery(
+    'projects-for-map',
+    () => projectsApi.getAll().then(r => r.data)
+  )
+
+  const filteredProjects = mapData?.projects?.filter((p: any) => {
+    if (selectedStatus && p.status !== selectedStatus) return false
+    return true
+  }) || []
+
+  const formatCurrency = (val: number) => {
+    if (!val) return '$0'
+    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
+    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
+    return `$${val}`
+  }
+
+  // Center of Galapagos
+  const defaultCenter = [-0.6, -90.3]
+  const defaultZoom = 8
+
+  return (
+    <div className="h-[calc(100vh-4rem)] -m-8 flex">
+      {/* Sidebar */}
+      <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
+        <div className="p-4 border-b border-gray-200">
+          <h2 className="text-lg font-bold text-gray-900 flex items-center">
+            <MapPin className="h-5 w-5 mr-2 text-primary-600" />
+            Project Map
+          </h2>
+          <p className="text-sm text-gray-500 mt-1">
+            {filteredProjects.length} projects with coordinates
+          </p>
+        </div>
+
+        {/* Filters */}
+        <div className="p-4 border-b border-gray-200">
+          <label className="block text-sm font-medium text-gray-700 mb-2">
+            Filter by Status
+          </label>
+          <select
+            value={selectedStatus}
+            onChange={(e) => setSelectedStatus(e.target.value)}
+            className="input"
+          >
+            <option value="">All Statuses</option>
+            <option value="In Progress">In Progress</option>
+            <option value="Pending">Pending</option>
+            <option value="At Risk">At Risk</option>
+            <option value="Closed">Closed</option>
+          </select>
+        </div>
+
+        {/* Stats */}
+        <div className="p-4 border-b border-gray-200">
+          <h3 className="text-sm font-medium text-gray-700 mb-3">Summary by Location</h3>
+          <div className="space-y-2">
+            {mapData?.locations?.map((loc: any) => {
+              const locProjects = filteredProjects.filter((p: any) => p.location_name === loc.name)
+              const totalBudget = locProjects.reduce((sum: number, p: any) => sum + p.budget, 0)
+              
+              return (
+                <div key={loc.id} className="flex items-center justify-between text-sm">
+                  <div className="flex items-center">
+                    <span 
+                      className="w-3 h-3 rounded-full mr-2" 
+                      style={{ backgroundColor: loc.color }}
+                    />
+                    <span>{loc.name}</span>
+                  </div>
+                  <div className="text-gray-500">
+                    {locProjects.length} proj · {formatCurrency(totalBudget)}
+                  </div>
+                </div>
+              )
+            })}
+          </div>
+        </div>
+
+        {/* Project List */}
+        <div className="p-4">
+          <h3 className="text-sm font-medium text-gray-700 mb-3">Projects</h3>
+          <div className="space-y-3">
+            {filteredProjects.map((project: any) => (
+              <div 
+                key={project.id} 
+                className="p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors cursor-pointer"
+              >
+                <div className="flex items-start justify-between">
+                  <div>
+                    <p className="font-medium text-sm text-gray-900">{project.name}</p>
+                    <p className="text-xs text-gray-500 mt-1">{project.location_name}</p>
+                  </div>
+                  <span 
+                    className="w-2 h-2 rounded-full mt-1"
+                    style={{ backgroundColor: statusColors[project.status] || '#999' }}
+                  />
+                </div>
+                <div className="mt-2 flex items-center justify-between text-xs">
+                  <span className={`px-2 py-0.5 rounded-full ${
+                    project.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
+                    project.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
+                    project.status === 'At Risk' ? 'bg-red-100 text-red-800' :
+                    'bg-green-100 text-green-800'
+                  }`}>
+                    {project.status}
+                  </span>
+                  <span className="text-gray-600">{formatCurrency(project.budget)}</span>
+                </div>
+                <div className="mt-2">
+                  <div className="w-full bg-gray-200 rounded-full h-1.5">
+                    <div
+                      className="bg-primary-500 h-1.5 rounded-full"
+                      style={{ width: `${project.progress_pct * 100}%` }}
+                    />
+                  </div>
+                  <p className="text-xs text-gray-500 mt-1">
+                    {Math.round(project.progress_pct * 100)}% complete
+                  </p>
+                </div>
+              </div>
+            ))}
+          </div>
+        </div>
+      </div>
+
+      {/* Map */}
+      <div className="flex-1 relative">
+        {/* Map Controls */}
+        <div className="absolute top-4 right-4 z-[1000] flex space-x-2">
+          <button
+            onClick={() => setMapType(mapType === 'street' ? 'satellite' : 'street')}
+            className="bg-white p-2 rounded-lg shadow-md hover:bg-gray-50 flex items-center text-sm"
+          >
+            <Layers className="h-4 w-4 mr-2" />
+            {mapType === 'street' ? 'Satellite' : 'Street'}
+          </button>
+        </div>
+
+        {isLoading ? (
+          <div className="h-full flex items-center justify-center bg-gray-100">
+            <div className="text-gray-500">Loading map...</div>
+          </div>
+        ) : (
+          <MapContainer
+            center={defaultCenter}
+            zoom={defaultZoom}
+            style={{ height: '100%', width: '100%' }}
+          >
+            <TileLayer
+              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
+              url={mapType === 'street' 
+                ? 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
+                : 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
+              }
+            />
+            
+            {filteredProjects.map((project: any) => (
+              <Marker
+                key={project.id}
+                position={[project.latitude, project.longitude]}
+                icon={createCustomIcon(statusColors[project.status] || '#4472C4')}
+              >
+                <Popup>
+                  <div className="p-2 min-w-[250px]">
+                    <h3 className="font-bold text-gray-900 mb-1">{project.name}</h3>
+                    <p className="text-sm text-gray-600 mb-2">{project.location_name}</p>
+                    
+                    <div className="space-y-1 text-sm">
+                      <div className="flex justify-between">
+                        <span className="text-gray-500">Status:</span>
+                        <span className={`px-2 py-0.5 rounded text-xs ${
+                          project.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
+                          project.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
+                          project.status === 'At Risk' ? 'bg-red-100 text-red-800' :
+                          'bg-green-100 text-green-800'
+                        }`}>
+                          {project.status}
+                        </span>
+                      </div>
+                      <div className="flex justify-between">
+                        <span className="text-gray-500">Budget:</span>
+                        <span className="font-medium">{formatCurrency(project.budget)}</span>
+                      </div>
+                      <div className="flex justify-between">
+                        <span className="text-gray-500">Progress:</span>
+                        <span className="font-medium">{Math.round(project.progress_pct * 100)}%</span>
+                      </div>
+                    </div>
+                    
+                    <div className="mt-3">
+                      <div className="w-full bg-gray-200 rounded-full h-2">
+                        <div
+                          className="bg-primary-500 h-2 rounded-full"
+                          style={{ width: `${project.progress_pct * 100}%` }}
+                        />
+                      </div>
+                    </div>
+                    
+                    <div className="mt-2 text-xs text-gray-400">
+                      Lat: {project.latitude.toFixed(4)}, Lng: {project.longitude.toFixed(4)}
+                    </div>
+                  </div>
+                </Popup>
+              </Marker>
+            ))}
+            
+            <FitBounds projects={filteredProjects} />
+          </MapContainer>
+        )}
+      </div>
+    </div>
+  )
+}
diff --git a/excel_dashboard_proyectos/water-program-dashboard/start-dev.bat b/excel_dashboard_proyectos/water-program-dashboard/start-dev.bat
new file mode 100644
index 0000000..875cf72
--- /dev/null
+++ b/excel_dashboard_proyectos/water-program-dashboard/start-dev.bat
@@ -0,0 +1,50 @@
+@echo off
+chcp 65001 >nul
+echo ============================================
+echo Water Program Dashboard - Development Mode
+echo ============================================
+echo.
+
+echo [1/2] Iniciando Backend (FastAPI)...
+echo         URL: http://localhost:8000
+echo         Docs: http://localhost:8000/docs
+echo         Legacy: http://localhost:8000/legacy
+echo.
+
+cd backend
+start "Backend API" cmd /k "uvicorn app.main:app --reload --port 8000"
+cd ..
+
+echo.
+echo [2/2] Verificando Node.js...
+node --version >nul 2>&1
+if errorlevel 1 (
+    echo.
+    echo ⚠️  NODE.JS NO ESTÁ INSTALADO
+    echo.
+    echo Para usar React (frontend oficial):
+    echo 1. Descarga Node.js desde https://nodejs.org
+    echo 2. Instala la versión LTS
+    echo 3. Cierra y abre una nueva terminal
+    echo 4. Ejecuta: cd frontend ^&^& npm install ^&^& npm run dev
+    echo.
+    echo Mientras tanto, usa el fallback temporal:
+    echo 🌐 http://localhost:8000/legacy
+    echo.
+) else (
+    echo ✅ Node.js encontrado
+    echo.
+    echo Para iniciar React (en otra terminal):
+    echo    cd frontend
+    echo    npm install
+    echo    npm run dev
+    echo.
+    echo O ejecuta: start-react.bat
+    echo.
+)
+
+echo ============================================
+echo Backend corriendo en http://localhost:8000
+echo ============================================
+echo.
+pause
diff --git a/excel_dashboard_proyectos/water-program-dashboard/start-react.bat b/excel_dashboard_proyectos/water-program-dashboard/start-react.bat
new file mode 100644
index 0000000..b7833b8
--- /dev/null
+++ b/excel_dashboard_proyectos/water-program-dashboard/start-react.bat
@@ -0,0 +1,41 @@
+@echo off
+chcp 65001 >nul
+echo ============================================
+echo React Frontend - Development Mode
+echo ============================================
+echo.
+
+node --version >nul 2>&1
+if errorlevel 1 (
+    echo ❌ ERROR: Node.js no está instalado
+    echo.
+    echo Por favor instala Node.js desde:
+    echo https://nodejs.org
+    echo.
+    echo Luego vuelve a ejecutar este script.
+    pause
+    exit /b 1
+)
+
+echo ✅ Node.js detectado
+echo.
+
+cd frontend
+
+echo 📦 Instalando dependencias (si es necesario)...
+call npm install
+if errorlevel 1 (
+    echo ❌ Error instalando dependencias
+    pause
+    exit /b 1
+)
+
+echo.
+echo 🚀 Iniciando React dev server...
+echo    URL: http://localhost:3000
+echo    API Proxy: http://localhost:8000/api
+echo.
+echo Presiona Ctrl+C para detener
+echo.
+
+npm run dev
