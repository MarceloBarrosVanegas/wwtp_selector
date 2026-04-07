# Git Diff - Fase 1: Arquitectura Unificada

**Fecha:** 6 de abril de 2026
**Branch:** master
**Estado:** Cambios staged (listos para commit)

---

## Resumen de Cambios

```
48 files changed, 3384 insertions(+), 0 deletions(-)
```

### Archivos Nuevos (Untracked → Staged)

#### Backend (17 archivos)
```
backend/.env.example
backend/Dockerfile
backend/app/__init__.py
backend/app/crud.py
backend/app/database.py
backend/app/main.py           # CORS configurado para React
backend/app/models.py
backend/app/routers/__init__.py
backend/app/routers/dashboard.py
backend/app/routers/locations.py
backend/app/routers/projects.py
backend/app/schemas.py
backend/app/services/cashflow_calc.py
backend/app/services/gantt_builder.py
backend/import_data.py        # Importador de datos Excel
backend/requirements.txt
```

#### Frontend (21 archivos)
```
frontend/Dockerfile
frontend/index.html
frontend/package-lock.json
frontend/package.json
frontend/postcss.config.js
frontend/src/App.tsx
frontend/src/api/client.ts
frontend/src/components/Layout.tsx
frontend/src/components/Projects/ProjectModal.tsx
frontend/src/index.css
frontend/src/main.tsx
frontend/src/pages/Charts.tsx
frontend/src/pages/Dashboard.tsx
frontend/src/pages/Gantt.tsx
frontend/src/pages/MapView.tsx
frontend/src/pages/Projects.tsx
frontend/tailwind.config.js
frontend/tsconfig.json
frontend/tsconfig.node.json
frontend/vite.config.ts       # Proxy configurado a :8000
```

#### Scripts y Configuración (6 archivos)
```
.gitignore
ARCHITECTURE.md               # Documentación arquitectura
CHANGES-FASE1.md              # Este resumen de cambios
README.md
docker-compose.yml
init-db.py
```

#### Scripts de Inicio (4 archivos)
```
start-dev.bat                 # Inicia backend
start-local.bat               # Script legacy
start-local.sh                # Script legacy
start-react-bg.bat            # Inicia React en background
start-react.bat               # Inicia React (foreground)
```

#### Datos y Frontend Legacy (2 archivos)
```
data_export.json              # Datos exportados del Excel
static/excel-style.html       # Fallback HTML temporal
static/index.html
```

### Archivos Binarios
```
node.exe                      # Node.js descargado (corrupto, no usar)
```

---

## Cambios Clave en Código

### 1. backend/app/main.py
**Cambio principal:** Configuración CORS para React

```python
# CORS middleware - permite conexión desde React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Puerto alternativo
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check dual (para consistencia de rutas)
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
def health_check_api():
    """Endpoint de health bajo /api para consistencia."""
    return {"status": "healthy"}

# Legacy fallback temporal
static_path = os.path.join(os.path.dirname(__file__), "..", "..", "static")
if os.path.exists(static_path):
    app.mount("/legacy", StaticFiles(directory=static_path, html=True), name="legacy")
```

### 2. frontend/vite.config.ts
**Configuración del proxy:**

```typescript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 3. backend/import_data.py
**Importador de datos desde Excel:**

```python
def import_from_json(json_path: str = "../data_export.json"):
    """Importa datos desde el archivo JSON exportado del Excel."""
    # Importa 3 locations y 13 proyectos
    # Crea parámetros del sistema
```

---

## Estado de la Base de Datos

Después de ejecutar `import_data.py`:

```sql
-- Ubicaciones (3)
SELECT * FROM locations;
-- 1, Santa Cruz, #4472C4
-- 2, Cristobal, #4472C4
-- 3, Isabela, #4472C4

-- Proyectos (13)
SELECT COUNT(*) FROM projects;
-- 13

-- Parámetros (8)
SELECT * FROM parameters;
-- active_year = 2026
-- gantt_start = 2026-01-01
-- etc.
```

---

## Verificación de Endpoints

Todos los endpoints han sido verificados:

| Endpoint | Método | Estado | Respuesta |
|----------|--------|--------|-----------|
| /health | GET | ✅ | {"status": "healthy"} |
| /api/health | GET | ✅ | {"status": "healthy"} |
| /api/projects | GET | ✅ | 13 proyectos |
| /api/projects/{id} | GET | ✅ | Proyecto detalle |
| /api/locations | GET | ✅ | 3 ubicaciones |
| /api/dashboard/kpis | GET | ✅ | KPIs calculados |
| /api/dashboard/data | GET | ✅ | Datos dashboard |
| /legacy | GET | ✅ | HTML fallback |

---

## Instrucciones para Revertir

Si es necesario volver al estado anterior:

```bash
cd excel_dashboard_proyectos
git reset HEAD water-program-dashboard/
git checkout water-program-dashboard/
```

---

## Comandos para Commit

```bash
cd excel_dashboard_proyectos
git add water-program-dashboard/
git commit -m "Fase 1: Arquitectura unificada React + FastAPI

- Backend API-only con CORS para React
- Frontend React con Vite y proxy configurado
- Importación de datos desde Excel (13 proyectos, 3 ubicaciones)
- Legacy HTML en /legacy como fallback temporal
- Scripts de inicio automatizados
- Documentación completa de arquitectura"
```

---

## Notas

- No se realizaron cambios en archivos fuera de `water-program-dashboard/`
- El archivo `node.exe` en raíz está corrupto y debe ignorarse/borrarse
- El puerto 3000 estaba ocupado, React usa 3001 (CORS actualizado)
- Todos los tests de conectividad pasaron correctamente
