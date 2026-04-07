# Arquitectura del Proyecto - Water Program Dashboard

## Estado: Fase 1 Completada ✅

**Fecha:** 6 de abril de 2026  
**Versión:** 1.0.0  
**Arquitectura:** React + FastAPI (sin legacy)

---

## Diagrama

```
┌─────────────────────────────────────────┐
│  React Frontend                         │
│  http://localhost:3000 (o 3001)         │
└──────────────┬──────────────────────────┘
               │ Proxy /api/*
               ▼
┌─────────────────────────────────────────┐
│  FastAPI Backend                        │
│  http://localhost:8000                  │
└──────────────┬──────────────────────────┘
               │ SQLAlchemy
               ▼
┌─────────────────────────────────────────┐
│  SQLite (water_program.db)              │
└─────────────────────────────────────────┘
```

---

## URLs

| Servicio | URL |
|----------|-----|
| React Dev | http://localhost:3000 (o 3001) |
| FastAPI | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Endpoints API (Confirmados)

### Health
```
GET /health
GET /api/health
```

### Proyectos
```
GET    /api/projects/              # Lista proyectos
GET    /api/projects/{id}          # Proyecto por ID
POST   /api/projects/              # Crear proyecto
PUT    /api/projects/{id}          # Actualizar proyecto
DELETE /api/projects/{id}          # Eliminar proyecto
GET    /api/projects/next-id/      # Siguiente ID disponible
```

### Ubicaciones
```
GET    /api/locations/             # Lista ubicaciones
GET    /api/locations/{id}         # Ubicación por ID
POST   /api/locations/             # Crear ubicación
PUT    /api/locations/{id}         # Actualizar ubicación
```

### Dashboard
```
GET /api/dashboard/kpis                      # KPIs
GET /api/dashboard/timeline                  # Timeline presupuestos
GET /api/dashboard/data                      # Datos combinados
GET /api/dashboard/gantt                     # Datos Gantt
GET /api/dashboard/map                       # Datos mapa

# Charts
GET /api/dashboard/charts/budget-by-project
GET /api/dashboard/charts/progress-by-project
GET /api/dashboard/charts/status-distribution
GET /api/dashboard/charts/budget-by-location
```

---

## CORS

```python
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]
```

---

## Cómo Iniciar

### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Scripts
```bash
start-dev.bat    # Backend
start-react.bat  # Frontend
```

---

## Verificación

```bash
# Backend
curl http://localhost:8000/
curl http://localhost:8000/api/projects

# Frontend
curl http://localhost:3000

# Build
cd frontend && npm run build
```

---

## Estructura

```
water-program-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   └── routers/
│   │       ├── projects.py
│   │       ├── locations.py
│   │       └── dashboard.py
│   └── import_data.py
├── frontend/
│   ├── src/
│   ├── dist/
│   └── package.json
├── start-dev.bat
├── start-react.bat
└── ARCHITECTURE.md
```

---

## Datos

- 3 ubicaciones: Santa Cruz, Cristobal, Isabela
- 13 proyectos: P001-P013

---

## Estado

- ✅ Backend FastAPI
- ✅ Frontend React
- ✅ Build verificado
- ✅ Sin legacy
