"""
Servicio para calcular el Cash Flow y distribuir presupuestos mensualmente.
Reproduce la lógica del VBA de Excel.
"""
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from .. import models, crud

def distribute_project_budget(
    project: models.Project,
    gantt_start: date,
    months_count: int
) -> List[Dict]:
    """
    Distribuye el presupuesto de un proyecto en meses basado en sus fechas.
    Similar a la lógica del VBA BuildCashFlowGantt.
    """
    if not project.start_date or not project.planned_end_date or not project.total_budget:
        return []
    
    cashflows = []
    
    # Calculate months active in the Gantt period
    start_month = max(project.start_date, gantt_start)
    end_month = min(project.planned_end_date, gantt_start + relativedelta(months=months_count))
    
    if start_month >= end_month:
        return []
    
    # Total duration of project in months
    total_months = max(1, (project.planned_end_date - project.start_date).days // 30)
    
    # Monthly budget
    monthly_budget = project.total_budget / total_months
    
    # Generate entries for each month
    current = start_month
    while current <= end_month:
        cashflows.append({
            'month': current,
            'amount': monthly_budget,
            'project_id': project.id,
            'location_id': project.location_id
        })
        current += relativedelta(months=1)
    
    return cashflows

def calculate_location_inflows(
    db: Session,
    gantt_start: date,
    months_count: int,
    inflow_months: List[int] = [1, 8],  # Default: January and August
    inflow_times: int = 2
) -> Dict:
    """
    Calcula los ingresos (IN) por location según los parámetros.
    Los inflows entran en meses específicos (ej: mes 1 y 8 de cada año).
    """
    locations = crud.get_locations(db)
    inflow_data = {}
    
    for loc in locations:
        monthly_data = {}
        annual_limit = loc.annual_limit
        
        if annual_limit > 0 and inflow_times > 0:
            monthly_value = annual_limit / inflow_times
            
            # Distribute across months
            for year_offset in range(0, months_count, 12):
                for month_num in inflow_months:
                    actual_month = year_offset + month_num
                    if actual_month <= months_count:
                        month_date = gantt_start + relativedelta(months=actual_month-1)
                        monthly_data[month_date.isoformat()] = monthly_value
        
        inflow_data[loc.id] = {
            'location_name': loc.name,
            'initial_value': loc.initial_balance,
            'monthly_values': monthly_data,
            'total': sum(monthly_data.values()) + loc.initial_balance
        }
    
    return inflow_data

def calculate_cumulative_sum(
    inflow_data: Dict,
    projects_data: Dict,
    gantt_start: date,
    months_count: int
) -> Dict:
    """
    Calcula la suma acumulativa (Cumulative Sum) por location.
    """
    cumulative = {}
    
    for loc_id, loc_data in inflow_data.items():
        running_total = loc_data['initial_value']
        monthly_cumulative = {}
        
        for i in range(months_count):
            month_date = gantt_start + relativedelta(months=i)
            month_key = month_date.isoformat()
            
            # Add inflow for this month
            inflow = loc_data['monthly_values'].get(month_key, 0)
            running_total += inflow
            
            # Subtract projects expenses for this location and month
            project_expense = projects_data.get(loc_id, {}).get(month_key, 0)
            
            monthly_cumulative[month_key] = running_total
        
        cumulative[loc_id] = {
            'location_name': loc_data['location_name'],
            'values': monthly_cumulative,
            'final_balance': running_total
        }
    
    return cumulative

def calculate_net_cash_flow(
    cumulative_in: Dict,
    cumulative_cost: Dict
) -> Dict:
    """
    Calcula el Net Cash Flow (In - Out).
    """
    net_flow = {}
    
    all_locations = set(cumulative_in.keys()) | set(cumulative_cost.keys())
    
    for loc_id in all_locations:
        in_values = cumulative_in.get(loc_id, {}).get('values', {})
        cost_values = cumulative_cost.get(loc_id, {}).get('values', {})
        
        net_values = {}
        all_months = set(in_values.keys()) | set(cost_values.keys())
        
        for month in sorted(all_months):
            net_values[month] = in_values.get(month, 0) - cost_values.get(month, 0)
        
        net_flow[loc_id] = {
            'location_name': cumulative_in.get(loc_id, {}).get('location_name', ''),
            'values': net_values
        }
    
    return net_flow
