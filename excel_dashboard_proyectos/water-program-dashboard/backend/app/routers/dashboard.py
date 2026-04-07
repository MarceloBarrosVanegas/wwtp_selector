from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from .. import schemas, crud
from ..database import get_db
from ..services.gantt_builder import build_gantt_data, get_map_data

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/kpis", response_model=schemas.KPIData)
def get_kpis(year: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """Obtiene los KPIs del dashboard."""
    return crud.get_kpis(db, year)

@router.get("/timeline")
def get_timeline(
    start_year: int = Query(2026),
    num_years: int = Query(3),
    db: Session = Depends(get_db)
):
    """Obtiene la línea de tiempo de presupuestos por ubicación."""
    return crud.get_location_timeline(db, start_year, num_years)

@router.get("/data", response_model=schemas.DashboardData)
def get_dashboard_data(
    year: int = Query(2026),
    num_years: int = Query(3),
    db: Session = Depends(get_db)
):
    """Obtiene todos los datos del dashboard (KPIs + Timeline)."""
    kpis = crud.get_kpis(db, year)
    timeline = crud.get_location_timeline(db, year, num_years)
    
    return schemas.DashboardData(
        kpis=kpis,
        location_timeline=timeline,
        year=year
    )

@router.get("/gantt", response_model=schemas.GanttData)
def get_gantt(
    start_date: Optional[date] = Query(None),
    years: int = Query(3),
    filter_location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtiene los datos para el Gantt de Cash Flow."""
    return build_gantt_data(
        db=db,
        gantt_start=start_date,
        years_count=years,
        filter_location=filter_location
    )

@router.get("/map", response_model=schemas.MapData)
def get_map(db: Session = Depends(get_db)):
    """Obtiene datos de proyectos con coordenadas para el mapa."""
    return get_map_data(db)

@router.get("/charts/budget-by-project")
def get_budget_by_project(db: Session = Depends(get_db)):
    """Datos para gráfico de presupuesto por proyecto."""
    projects = crud.get_projects(db)
    return {
        "labels": [p.name for p in projects],
        "datasets": [{
            "label": "Budget",
            "data": [p.total_budget for p in projects],
            "backgroundColor": "#2E75B6"
        }]
    }

@router.get("/charts/progress-by-project")
def get_progress_by_project(db: Session = Depends(get_db)):
    """Datos para gráfico de progreso por proyecto."""
    projects = crud.get_projects(db)
    return {
        "labels": [p.name for p in projects],
        "datasets": [{
            "label": "Progress %",
            "data": [p.progress_pct * 100 for p in projects],
            "backgroundColor": "#4472C4"
        }]
    }

@router.get("/charts/status-distribution")
def get_status_distribution(db: Session = Depends(get_db)):
    """Datos para gráfico de distribución por estado."""
    from sqlalchemy import func
    from ..models import Project
    
    db_query = db.query(Project.status, func.count(Project.id)).group_by(Project.status).all()
    
    status_colors = {
        "In Progress": "#2E75B6",
        "Pending": "#F79646",
        "At Risk": "#C0504D",
        "Closed": "#5287936",
        "Suspended": "#5592405"
    }
    
    return {
        "labels": [s.value for s, _ in db_query],
        "datasets": [{
            "data": [count for _, count in db_query],
            "backgroundColor": [status_colors.get(s.value, "#999") for s, _ in db_query]
        }]
    }

@router.get("/charts/budget-by-location")
def get_budget_by_location(db: Session = Depends(get_db)):
    """Datos para gráfico de presupuesto por ubicación."""
    from sqlalchemy import func
    from ..models import Project, Location
    
    result = db.query(
        Location.name,
        func.sum(Project.total_budget)
    ).join(Project).group_by(Location.name).all()
    
    colors = ["#2E75B6", "#F79646", "#5287936", "#C0504D", "#5592405", "#9978C4", "#FFC000"]
    
    return {
        "labels": [name for name, _ in result],
        "datasets": [{
            "data": [budget or 0 for _, budget in result],
            "backgroundColor": colors[:len(result)]
        }]
    }
