"""
Servicio para construir los datos del Gantt (Cronograma Valorado).
"""
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from .. import models, crud, schemas
from .cashflow_calc import distribute_project_budget, calculate_location_inflows

def build_gantt_data(
    db: Session,
    gantt_start: Optional[date] = None,
    years_count: int = 3,
    inflow_months: List[int] = [3, 9],
    inflow_times: int = 2,
    filter_location: Optional[str] = None
) -> schemas.GanttData:
    """
    Construye todos los datos necesarios para el Gantt de Cash Flow.
    """
    if not gantt_start:
        gantt_start = date(2026, 1, 1)
    
    months_count = years_count * 12
    
    # Generate month labels
    months = []
    for i in range(months_count):
        month_date = gantt_start + relativedelta(months=i)
        months.append(month_date.strftime("%b-%y"))
    
    locations = crud.get_locations(db)
    location_map = {loc.id: loc for loc in locations}
    
    # Filter locations if specified
    if filter_location and filter_location != "All Locations":
        filtered_locations = [loc for loc in locations if loc.name == filter_location]
        if filtered_locations:
            locations = filtered_locations
    
    # === INFLOW DATA (Income by Location) ===
    inflow_data = []
    for loc in locations:
        monthly_value = loc.annual_limit / inflow_times if loc.annual_limit and inflow_times else 0
        months_dict = {}
        
        for year_offset in range(0, months_count, 12):
            for month_num in inflow_months:
                actual_month = year_offset + month_num
                if actual_month <= months_count:
                    month_key = months[actual_month - 1]
                    months_dict[month_key] = monthly_value
        
        inflow_data.append(schemas.CashFlowRow(
            location_id=loc.id,
            location_name=loc.name,
            initial_value=loc.initial_balance or 0,
            months=months_dict
        ))
    
    # === PROJECTS (OUTFLOW) ===
    projects = db.query(models.Project).all()
    gantt_items = []
    
    for proj in projects:
        # Skip if location filter is active
        if filter_location and filter_location != "All Locations":
            if proj.location and proj.location.name != filter_location:
                continue
        
        if proj.start_date and proj.planned_end_date:
            # Calculate bar color based on status
            color_map = {
                models.ProjectStatus.IN_PROGRESS: "#C0E6F5",
                models.ProjectStatus.PENDING: "#FFE699",
                models.ProjectStatus.AT_RISK: "#F4B084",
                models.ProjectStatus.CLOSED: "#C6E0B4",
                models.ProjectStatus.SUSPENDED: "#D9D9D9"
            }
            
            item = schemas.GanttItem(
                id=proj.id,
                group="projects",
                content=proj.name,
                start=proj.start_date,
                end=proj.planned_end_date,
                type="range",
                amount=proj.total_budget or 0,
                progress=proj.progress_pct or 0,
                status=proj.status.value,
                location=proj.location.name if proj.location else "",
                style=f"background-color: {color_map.get(proj.status, '#C0E6F5')}"
            )
            gantt_items.append(item)
    
    # === CUMULATIVE SUM (IN) ===
    cumulative_in = []
    for loc in locations:
        values = {}
        running = loc.initial_balance or 0
        
        for i, month_label in enumerate(months):
            # Add inflow if this month has one
            month_num = (i % 12) + 1
            if month_num in inflow_months:
                running += (loc.annual_limit or 0) / inflow_times
            
            values[month_label] = running
        
        cumulative_in.append({
            "location_id": loc.id,
            "location_name": loc.name,
            "values": values,
            "row_type": "cumulative_in"
        })
    
    # === CUMULATIVE COST (OUT) ===
    cumulative_cost = []
    for loc in locations:
        values = {}
        running = 0
        
        for i, month_label in enumerate(months):
            # Sum project expenses for this location and month
            month_start = gantt_start + relativedelta(months=i)
            month_end = month_start + relativedelta(months=1)
            
            monthly_cost = 0
            for proj in projects:
                if proj.location_id == loc.id and proj.start_date and proj.planned_end_date:
                    if proj.start_date <= month_start < proj.planned_end_date:
                        # Simple monthly distribution
                        proj_months = max(1, (proj.planned_end_date - proj.start_date).days // 30)
                        monthly_cost += (proj.total_budget or 0) / proj_months
            
            running += monthly_cost
            values[month_label] = running
        
        cumulative_cost.append({
            "location_id": loc.id,
            "location_name": loc.name,
            "values": values,
            "row_type": "cumulative_cost"
        })
    
    # === NET CASH FLOW ===
    net_cash_flow = []
    for loc in locations:
        in_values = next((c["values"] for c in cumulative_in if c["location_id"] == loc.id), {})
        cost_values = next((c["values"] for c in cumulative_cost if c["location_id"] == loc.id), {})
        
        values = {}
        for month_label in months:
            values[month_label] = in_values.get(month_label, 0) - cost_values.get(month_label, 0)
        
        net_cash_flow.append({
            "location_id": loc.id,
            "location_name": loc.name,
            "values": values,
            "row_type": "net_cash_flow"
        })
    
    return schemas.GanttData(
        items=gantt_items,
        locations=locations,
        months=months,
        inflow_data=inflow_data,
        cumulative_data=cumulative_in + cumulative_cost,
        net_cash_flow=net_cash_flow
    )

def get_map_data(db: Session) -> schemas.MapData:
    """
    Obtiene datos de proyectos con coordenadas para el mapa.
    """
    projects = db.query(models.Project).all()
    locations = crud.get_locations(db)
    
    # Color por location
    location_colors = {
        "Santa Cruz": "#4472C4",
        "Cristobal": "#ED7D31",
        "Isabela": "#A5A5A5",
        "Floreana": "#FFC000",
        "Baltra": "#5B9BD5",
    }
    
    map_projects = []
    for proj in projects:
        if proj.latitude and proj.longitude:
            map_projects.append(schemas.MapProject(
                id=proj.id,
                name=proj.name,
                latitude=proj.latitude,
                longitude=proj.longitude,
                status=proj.status.value,
                progress_pct=proj.progress_pct or 0,
                budget=proj.total_budget or 0,
                location_name=proj.location.name if proj.location else "",
                color=location_colors.get(proj.location.name if proj.location else "", "#4472C4")
            ))
    
    return schemas.MapData(
        projects=map_projects,
        locations=locations
    )
