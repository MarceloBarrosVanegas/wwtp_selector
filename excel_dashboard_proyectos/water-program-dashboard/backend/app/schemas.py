from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class ProjectStatus(str, Enum):
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"
    AT_RISK = "At Risk"
    CLOSED = "Closed"
    SUSPENDED = "Suspended"

class AlertLevel(str, Enum):
    OK = "OK"
    ATTENTION = "Attention"
    URGENT = "Urgent"
    CLOSED = "Closed"

# Location schemas
class LocationBase(BaseModel):
    name: str
    annual_limit: float = 0
    initial_balance: float = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    color: str = "#4472C4"

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# CashFlow schemas
class CashFlowBase(BaseModel):
    month: date
    amount: float
    is_inflow: bool = False

class CashFlowCreate(CashFlowBase):
    project_id: str
    location_id: Optional[int] = None

class CashFlow(CashFlowBase):
    id: int
    project_id: str
    location_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Project schemas
class ProjectBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    location_id: int
    owner: Optional[str] = None
    project_type: str = "Other"
    status: ProjectStatus = ProjectStatus.PENDING
    
    start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    duration_days: Optional[int] = None
    
    progress_pct: float = 0
    total_budget: float = 0
    annual_budget: float = 0
    year: Optional[int] = None
    
    next_action: Optional[str] = None
    notes: Optional[str] = None
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location_id: Optional[int] = None
    owner: Optional[str] = None
    project_type: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    progress_pct: Optional[float] = None
    total_budget: Optional[float] = None
    annual_budget: Optional[float] = None
    year: Optional[int] = None
    next_action: Optional[str] = None
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None

class Project(ProjectBase):
    days_remaining: Optional[int] = None
    alert_level: AlertLevel = AlertLevel.OK
    created_at: datetime
    updated_at: datetime
    location: Optional[Location] = None
    cash_flows: List[CashFlow] = []
    
    class Config:
        from_attributes = True

class ProjectList(BaseModel):
    id: str
    name: str
    location_id: int
    location_name: str
    status: ProjectStatus
    progress_pct: float
    total_budget: float
    start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    alert_level: AlertLevel
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# Dashboard schemas
class KPIData(BaseModel):
    total_projects: int
    active_projects: int
    closed_projects: int
    at_risk_projects: int
    average_progress: float
    next_deadline: Optional[date] = None
    committed_budget: float
    total_budget_used: float

class LocationBudget(BaseModel):
    location_id: int
    location_name: str
    year: int
    budget: float
    limit: float
    usage_pct: float
    balance: float

class LocationTimeline(BaseModel):
    location_id: int
    location_name: str
    budgets: dict
    balances: dict
    total: float

class DashboardData(BaseModel):
    kpis: KPIData
    location_timeline: List[LocationTimeline]
    year: int

# Gantt schemas
class GanttItem(BaseModel):
    id: str
    group: str
    content: str
    start: date
    end: Optional[date] = None
    type: str
    amount: float
    progress: float
    status: str
    location: str
    style: Optional[str] = None

class CashFlowRow(BaseModel):
    location_id: int
    location_name: str
    initial_value: float
    months: dict

class GanttData(BaseModel):
    items: List[GanttItem]
    locations: List[Location]
    months: List[str]
    inflow_data: List[CashFlowRow]
    cumulative_data: List[dict]
    net_cash_flow: List[dict]

# Map schemas
class MapProject(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    status: str
    progress_pct: float
    budget: float
    location_name: str
    color: str

class MapData(BaseModel):
    projects: List[MapProject]
    locations: List[Location]

# Chart schemas
class ChartData(BaseModel):
    labels: List[str]
    datasets: List[dict]

# Parameter schemas
class ParameterBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class ParameterCreate(ParameterBase):
    pass

class Parameter(ParameterBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True
