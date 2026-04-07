from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/api/locations", tags=["locations"])

@router.get("/", response_model=List[schemas.Location])
def list_locations(db: Session = Depends(get_db)):
    """Lista todas las ubicaciones."""
    return crud.get_locations(db)

@router.get("/{location_id}", response_model=schemas.Location)
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Obtiene una ubicación por ID."""
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.post("/", response_model=schemas.Location)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    """Crea una nueva ubicación."""
    # Check if name already exists
    existing = crud.get_location_by_name(db, location.name)
    if existing:
        raise HTTPException(status_code=400, detail="Location name already exists")
    return crud.create_location(db, location)

@router.put("/{location_id}", response_model=schemas.Location)
def update_location(location_id: int, location: schemas.LocationCreate, db: Session = Depends(get_db)):
    """Actualiza una ubicación existente."""
    # Implementation needed in crud.py
    pass
