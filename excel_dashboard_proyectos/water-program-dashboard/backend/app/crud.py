from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from . import models, schemas

def get_location(db: Session, location_id: int):
    return db.query(models.Location).filter(models.Location.id == location_id).first()

def get_location_by_name(db: Session, name: str):
    return db.query(models.Location).filter(models.Location.name == name).first()

def get_locations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Location).offset(skip).limit(limit).all()

def create_location(db: Session, location: schemas.LocationCreate):
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_project(db: Session, project_id: str):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100, location_id: Optional[int] = None):
    query = db.query(models.Project)
    if location_id:
        query = query.filter(models.Project.location_id == location_id)
    return query.offset(skip).limit(limit).all()

def get_projects_list(db: Session) -> List[schemas.ProjectList]:
    projects = db.query(models.Project).all()
    result = []
    for p in projects:
        result.append(schemas.ProjectList(
            id=p.id,
            name=p.name,
            location_id=p.location_id,
            location_name=p.location.name if p.location else "",
            status=p.status,
            progress_pct=p.progress_pct,
            total_budget=p.total_budget,
            start_date=p.start_date,
            planned_end_date=p.planned_end_date,
            alert_level=p.alert_level,
            latitude=p.latitude,
            longitude=p.longitude
        ))
    return result

def create_project(db: Session, project: schemas.ProjectCreate):
    # Calculate derived fields
    duration_days = None
    days_remaining = None
    alert_level = models.AlertLevel.OK
    
    if project.start_date and project.planned_end_date:
        duration_days = (project.planned_end_date - project.start_date).days
        
        if project.status == models.ProjectStatus.CLOSED:
            alert_level = models.AlertLevel.CLOSED
            days_remaining = None
        else:
            days_remaining = (project.planned_end_date - date.today()).days
            
            # Alert thresholds
            urgent_threshold = 7
            attention_threshold = 30
            
            if days_remaining < urgent_threshold:
                alert_level = models.AlertLevel.URGENT
            elif days_remaining < attention_threshold:
                alert_level = models.AlertLevel.ATTENTION
            else:
                alert_level = models.AlertLevel.OK
    
    db_project = models.Project(
        **project.dict(),
        duration_days=duration_days,
        days_remaining=days_remaining,
        alert_level=alert_level
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: str, project_update: schemas.ProjectUpdate):
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    update_data = project_update.dict(exclude_unset=True)
    
    # Recalculate derived fields if dates changed
    start_date = update_data.get('start_date', db_project.start_date)
    end_date = update_data.get('planned_end_date', db_project.planned_end_date)
    status = update_data.get('status', db_project.status)
    
    if start_date and end_date:
        update_data['duration_days'] = (end_date - start_date).days
        
        if status == models.ProjectStatus.CLOSED:
            update_data['alert_level'] = models.AlertLevel.CLOSED
            update_data['days_remaining'] = None
        else:
            days_remaining = (end_date - date.today()).days
            update_data['days_remaining'] = days_remaining
            
            urgent_threshold = 7
            attention_threshold = 30
            
            if days_remaining < urgent_threshold:
                update_data['alert_level'] = models.AlertLevel.URGENT
            elif days_remaining < attention_threshold:
                update_data['alert_level'] = models.AlertLevel.ATTENTION
            else:
                update_data['alert_level'] = models.AlertLevel.OK
    
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db_project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: str):
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

def get_next_project_id(db: Session) -> str:
    last_project = db.query(models.Project).order_by(models.Project.id.desc()).first()
    if not last_project:
        return "P001"
    
    # Extract number from P001
    last_num = int(last_project.id[1:])
    return f"P{last_num + 1:03d}"

def get_kpis(db: Session, year: Optional[int] = None) -> schemas.KPIData:
    if not year:
        year = date.today().year
    
    total = db.query(models.Project).count()
    active = db.query(models.Project).filter(
        models.Project.status != models.ProjectStatus.CLOSED
    ).count()
    closed = db.query(models.Project).filter(
        models.Project.status == models.ProjectStatus.CLOSED
    ).count()
    at_risk = db.query(models.Project).filter(
        models.Project.status == models.ProjectStatus.AT_RISK
    ).count()
    
    avg_progress = db.query(func.avg(models.Project.progress_pct)).scalar() or 0
    
    next_deadline = db.query(models.Project.planned_end_date).filter(
        models.Project.planned_end_date >= date.today(),
        models.Project.status != models.ProjectStatus.CLOSED
    ).order_by(models.Project.planned_end_date).first()
    
    committed = db.query(func.sum(models.Project.total_budget)).scalar() or 0
    
    return schemas.KPIData(
        total_projects=total,
        active_projects=active,
        closed_projects=closed,
        at_risk_projects=at_risk,
        average_progress=round(avg_progress, 2),
        next_deadline=next_deadline[0] if next_deadline else None,
        committed_budget=committed,
        total_budget_used=committed * avg_progress
    )

def get_location_timeline(db: Session, start_year: int, num_years: int = 3):
    locations = get_locations(db)
    result = []
    
    years = list(range(start_year, start_year + num_years))
    
    for loc in locations:
        budgets = {}
        balances = {}
        total = 0
        
        for year in years:
            # Get projects for this location and year
            projects = db.query(models.Project).filter(
                models.Project.location_id == loc.id,
                models.Project.year == year
            ).all()
            
            year_budget = sum(p.total_budget for p in projects)
            budgets[str(year)] = year_budget
            balances[str(year)] = loc.annual_limit - year_budget
            total += year_budget
        
        result.append(schemas.LocationTimeline(
            location_id=loc.id,
            location_name=loc.name,
            budgets=budgets,
            balances=balances,
            total=total
        ))
    
    return result

def get_parameter(db: Session, key: str):
    return db.query(models.Parameter).filter(models.Parameter.key == key).first()

def set_parameter(db: Session, key: str, value: str, description: Optional[str] = None):
    param = get_parameter(db, key)
    if param:
        param.value = value
        if description:
            param.description = description
    else:
        param = models.Parameter(key=key, value=value, description=description)
        db.add(param)
    db.commit()
    return param

def get_parameters(db: Session):
    return db.query(models.Parameter).all()
