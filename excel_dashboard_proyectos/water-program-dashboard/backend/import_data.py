"""
Script para importar datos desde el archivo Excel al PostgreSQL.
"""
import json
import os
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

def parse_date(val):
    """Convierte valor a date si es posible."""
    if not val:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    try:
        return datetime.strptime(str(val), "%Y-%m-%d").date()
    except:
        return None

def parse_float(val):
    """Convierte valor a float."""
    if not val:
        return 0
    try:
        return float(val)
    except:
        return 0

def import_from_json(json_path: str = "../data_export.json"):
    """Importa datos desde el archivo JSON exportado del Excel."""
    db = SessionLocal()
    
    try:
        # Load JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Importando {len(data['locations'])} locations...")
        
        # Create locations
        location_map = {}
        for loc_data in data['locations']:
            location = models.Location(
                name=loc_data['name'],
                annual_limit=parse_float(loc_data.get('annual_limit')),
                initial_balance=parse_float(loc_data.get('initial_balance')),
                color="#4472C4"
            )
            db.add(location)
            db.flush()  # Get ID
            location_map[loc_data['name']] = location.id
            print(f"  Created location: {loc_data['name']} (ID: {location.id})")
        
        db.commit()
        
        print(f"\nImportando {len(data['projects'])} proyectos...")
        
        # Create projects
        for proj_data in data['projects']:
            # Map status
            status_map = {
                'In Progress': models.ProjectStatus.IN_PROGRESS,
                'Pending': models.ProjectStatus.PENDING,
                'At Risk': models.ProjectStatus.AT_RISK,
                'Closed': models.ProjectStatus.CLOSED,
                'Suspended': models.ProjectStatus.SUSPENDED
            }
            
            # Map alert
            alert_map = {
                'OK': models.AlertLevel.OK,
                'Attention': models.AlertLevel.ATTENTION,
                'Urgent': models.AlertLevel.URGENT,
                'Closed': models.AlertLevel.CLOSED
            }
            
            # Get location ID
            loc_name = proj_data.get('Location', '')
            location_id = location_map.get(loc_name, 1)  # Default to first location
            
            # Parse dates
            start_date = parse_date(proj_data.get('Start_Date'))
            end_date = parse_date(proj_data.get('Planned_End_Date'))
            actual_end = parse_date(proj_data.get('Actual_End_Date'))
            
            # Calculate duration
            duration = None
            if start_date and end_date:
                duration = (end_date - start_date).days
            
            # Calculate days remaining and alert
            days_remaining = None
            alert_level = models.AlertLevel.OK
            status = status_map.get(proj_data.get('Status', ''), models.ProjectStatus.PENDING)
            
            if status == models.ProjectStatus.CLOSED:
                alert_level = models.AlertLevel.CLOSED
            elif end_date:
                days_remaining = (end_date - date.today()).days
                if days_remaining < 7:
                    alert_level = models.AlertLevel.URGENT
                elif days_remaining < 30:
                    alert_level = models.AlertLevel.ATTENTION
            
            # Progress
            progress = parse_float(proj_data.get('Progress_Pct', 0))
            if progress > 1:
                progress = progress / 100
            
            project = models.Project(
                id=proj_data.get('ID', 'P001'),
                name=proj_data.get('Project', 'Unnamed'),
                location_id=location_id,
                owner=proj_data.get('Owner'),
                project_type=proj_data.get('Type', 'Other'),
                status=status,
                start_date=start_date,
                planned_end_date=end_date,
                actual_end_date=actual_end,
                duration_days=duration,
                progress_pct=progress,
                total_budget=parse_float(proj_data.get('Total_Budget')),
                year=int(parse_float(proj_data.get('Year', 2026))),
                days_remaining=days_remaining,
                alert_level=alert_level,
                next_action=proj_data.get('Next_Action'),
                notes=proj_data.get('Notes')
            )
            db.add(project)
            print(f"  Created project: {project.id} - {project.name[:50]}")
        
        db.commit()
        
        # Create default parameters
        params = data.get('parameters', {})
        default_params = {
            'active_year': str(params.get('Anio_Activo', 2026)),
            'gantt_start': '2026-01-01',
            'gantt_years': '3',
            'inflow_months': '3,9',
            'inflow_times': '2',
            'annual_limit': str(params.get('Limite_Anual', 2000000)),
            'green_alert_days': str(params.get('Umbral_Verde_Dias', 60)),
            'red_alert_days': str(params.get('Umbral_Rojo_Dias', 20))
        }
        
        print("\nCreando parámetros del sistema...")
        for key, value in default_params.items():
            param = models.Parameter(key=key, value=value)
            db.add(param)
            print(f"  Created parameter: {key} = {value}")
        
        db.commit()
        
        print("\nImportacion completada exitosamente!")
        
    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Create tables first
    print("Creando tablas...")
    models.Base.metadata.create_all(bind=engine)
    
    # Import data
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data_export.json')
    import_from_json(json_path)
