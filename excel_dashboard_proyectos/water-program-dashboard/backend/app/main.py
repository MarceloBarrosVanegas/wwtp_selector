from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine
from . import models
from .routers import projects, locations, dashboard

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Water Program Galapagos API",
    description="API para gestión de proyectos del Water Program",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - permite conexión desde React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Puerto alternativo si 3000 está ocupado
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router)
app.include_router(locations.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    """
    Water Program Galapagos API
    
    Frontend: React (http://localhost:3000 o http://localhost:3001)
    """
    return {
        "message": "Water Program Galapagos API",
        "version": "1.0.0",
        "docs": "/docs",
        "frontend": "http://localhost:3000 (o 3001 si está ocupado)",
        "status": "API running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
def health_check_api():
    """Endpoint de health bajo /api para consistencia."""
    return {"status": "healthy"}
