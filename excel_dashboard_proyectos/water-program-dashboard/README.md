# Water Program Galapagos Dashboard

Web application para gestión de proyectos del Water Program en Galápagos. Reemplaza el Excel con una solución web moderna con mapa interactivo, gráficos en tiempo real y cálculo automático de Cash Flow.

## 🚀 Características

### Funcionalidades del Excel migradas:
- ✅ **Project Database**: Tabla completa de proyectos con CRUD
- ✅ **Dashboard**: KPIs y Location Budget Timeline (2026-2028)
- ✅ **Cash Flow Gantt**: Cronograma valorado con IN/OUT/Net
- ✅ **4 Gráficos**: Budget, Progress, Status, Location
- ✅ **Alertas automáticas**: Por días restantes

### Nuevas funcionalidades Web:
- 🗺️ **Mapa interactivo**: Ver proyectos en mapa de Galápagos con coordenadas GPS
- 📊 **Gráficos dinámicos**: Recharts interactivos
- 🔍 **Filtros avanzados**: Por location, status, fechas
- ⚡ **Actualización en tiempo real**: Sin recargar Excel
- 🎨 **UI moderna**: Tailwind CSS responsive
- 🗄️ **Base de datos PostgreSQL**: Persistencia real

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | FastAPI + SQLAlchemy + PostgreSQL |
| **Frontend** | React + TypeScript + Tailwind CSS |
| **Gráficos** | Recharts |
| **Mapas** | React-Leaflet + OpenStreetMap |
| **Estado** | React Query |
| **Deploy** | Docker + Docker Compose |

## 📁 Estructura del Proyecto

```
water-program-dashboard/
├── backend/                 # FastAPI
│   ├── app/
│   │   ├── main.py         # Punto de entrada
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── crud.py         # Operaciones DB
│   │   ├── routers/        # API endpoints
│   │   └── services/       # Lógica de negocio
│   ├── import_data.py      # Importar desde Excel
│   └── requirements.txt
├── frontend/               # React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Dashboard, Projects, Gantt, Map
│   │   ├── api/            # Cliente API
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml      # Orquestación
└── data_export.json        # Datos exportados del Excel
```

## 🚀 Instalación Local

### Opción 1: Docker (Recomendado)

```bash
# 1. Exportar datos del Excel (ya hecho: data_export.json)

# 2. Iniciar servicios
docker-compose up

# 3. Inicializar base de datos (en otra terminal)
docker-compose exec backend python import_data.py

# 4. Abrir en navegador
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Opción 2: Desarrollo Local

**Requisitos:**
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

```bash
# 1. Base de datos
createdb water_program

# 2. Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Inicializar datos
python import_data.py

# Iniciar servidor
uvicorn app.main:app --reload

# 3. Frontend (nueva terminal)
cd frontend
npm install
npm run dev

# 4. Abrir http://localhost:3000
```

## 📊 Uso

### Navegación

| Ruta | Descripción |
|------|-------------|
| `/` | Dashboard con KPIs y Budget Timeline |
| `/projects` | Base de datos de proyectos (CRUD) |
| `/gantt` | Cash Flow Gantt interactivo |
| `/map` | Mapa de Galápagos con proyectos |
| `/charts` | Gráficos y analytics |

### Funcionalidades clave

1. **Agregar Proyecto**: Botón "New Project" en `/projects`
2. **Ver en Mapa**: `/map` muestra proyectos con coordenadas
3. **Filtrar Gantt**: Dropdown en `/gantt` para filtrar por location
4. **Exportar**: Próximamente - exportar a PDF

## 🗺️ Mapa de Galápagos

Los proyectos se muestran en un mapa interactivo con:
- Marcadores por ubicación real (lat/lng)
- Colores por estado del proyecto
- Popups con información detallada
- Filtros por status

Para agregar coordenadas a un proyecto, edítalo y completa los campos Latitude/Longitude.

## 🔧 API Endpoints

Documentación interactiva: `http://localhost:8000/docs`

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/projects/` | Listar proyectos |
| `POST /api/projects/` | Crear proyecto |
| `GET /api/dashboard/data` | Datos del dashboard |
| `GET /api/dashboard/gantt` | Datos del Gantt |
| `GET /api/dashboard/map` | Datos para el mapa |

## 📝 Notas

- La base de datos se inicializa con los 13 proyectos del Excel
- Los cálculos de Cash Flow se hacen automáticamente basados en fechas y presupuestos
- Las alertas se calculan automáticamente según días restantes

## 🚢 Deploy en Render

1. Crear PostgreSQL en Render
2. Crear Web Service para backend (Docker)
3. Crear Static Site para frontend
4. Configurar variables de entorno
5. ¡Listo!

---

**Desarrollado para OFC Water Program Galapagos**
