from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class ProjectStatus(str, enum.Enum):
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"
    AT_RISK = "At Risk"
    CLOSED = "Closed"
    SUSPENDED = "Suspended"

class ProjectType(str, enum.Enum):
    CONSTRUCTION = "Construction"
    CONSULTING = "Consulting"
    SOFTWARE = "Software"
    TRAINING = "Training"
    OTHER = "Other"

class AlertLevel(str, enum.Enum):
    OK = "OK"
    ATTENTION = "Attention"
    URGENT = "Urgent"
    CLOSED = "Closed"

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    annual_limit = Column(Float, default=0)
    initial_balance = Column(Float, default=0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    color = Column(String(7), default="#4472C4")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="location")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(20), primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    owner = Column(String(100), nullable=True)
    project_type = Column(String(50), default="Other")
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PENDING)
    
    start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    duration_days = Column(Integer, nullable=True)
    
    progress_pct = Column(Float, default=0)
    total_budget = Column(Float, default=0)
    annual_budget = Column(Float, default=0)
    year = Column(Integer, nullable=True)
    
    days_remaining = Column(Integer, nullable=True)
    alert_level = Column(Enum(AlertLevel), default=AlertLevel.OK)
    
    next_action = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Geolocation
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    location = relationship("Location", back_populates="projects")
    cash_flows = relationship("CashFlow", back_populates="project", cascade="all, delete-orphan")

class CashFlow(Base):
    __tablename__ = "cash_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(20), ForeignKey("projects.id"), nullable=False)
    month = Column(Date, nullable=False)
    amount = Column(Float, default=0)
    is_inflow = Column(Boolean, default=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    
    project = relationship("Project", back_populates="cash_flows")

class Parameter(Base):
    __tablename__ = "parameters"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(500), nullable=True)
    description = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    user_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
