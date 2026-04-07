from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, models
from ..database import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/", response_model=List[schemas.ProjectList])
def list_projects(db: Session = Depends(get_db)):
    """Lista todos los proyectos con información resumida."""
    return crud.get_projects_list(db)

@router.get("/{project_id}", response_model=schemas.Project)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Obtiene un proyecto por su ID."""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Crea un nuevo proyecto."""
    # Generate ID if not provided
    if not project.id:
        project.id = crud.get_next_project_id(db)
    
    # Check if ID already exists
    existing = crud.get_project(db, project.id)
    if existing:
        raise HTTPException(status_code=400, detail="Project ID already exists")
    
    # Check if location exists
    location = crud.get_location(db, project.location_id)
    if not location:
        raise HTTPException(status_code=400, detail="Location not found")
    
    return crud.create_project(db, project)

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(project_id: str, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    """Actualiza un proyecto existente."""
    updated = crud.update_project(db, project_id, project)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated

@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Elimina un proyecto."""
    success = crud.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

@router.get("/next-id/")
def get_next_id(db: Session = Depends(get_db)):
    """Obtiene el siguiente ID disponible para un proyecto."""
    return {"next_id": crud.get_next_project_id(db)}
