from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from infrastructure.database import Base

class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Integer, nullable=False) # cite: 66
    email = Column(String, unique=True, index=True, nullable=False) # cite: 67
    hashed_password = Column(String, nullable=False) # cite: 68
    role = Column(String, nullable=False) # ADMIN, SUPERVISOR, OPERATOR [cite: 50-54, 69]

    # Relaciones para trazabilidad (como en el PSet 2)
    incidents_created = relationship("IncidentORM", foreign_keys="[IncidentORM.created_by]", back_populates="creator")
    incidents_assigned = relationship("IncidentORM", foreign_keys="[IncidentORM.assigned_to]", back_populates="assignee")
    tasks_assigned = relationship("TaskORM", back_populates="assignee")

class IncidentORM(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True) # cite: 73
    title = Column(String, nullable=False) # cite: 75
    description = Column(Text, nullable=False) # cite: 76
    severity = Column(String, nullable=False) # cite: 77
    status = Column(String, default="OPEN") # cite: 78, 115
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False) # cite: 79
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True) # cite: 80
    
    created_at = Column(DateTime, default=datetime.utcnow) # cite: 82
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    creator = relationship("UserORM", foreign_keys=[created_by], back_populates="incidents_created")
    assignee = relationship("UserORM", foreign_keys=[assigned_to], back_populates="incidents_assigned")
    tasks = relationship("TaskORM", back_populates="incident", cascade="all, delete-orphan")

class TaskORM(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True) # cite: 84
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False) # cite: 85
    title = Column(String, nullable=False) # cite: 86
    description = Column(Text, nullable=False) # cite: 87
    status = Column(String, default="OPEN") # cite: 88, 148
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True) # cite: 89
    
    created_at = Column(DateTime, default=datetime.utcnow) # cite: 90
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    incident = relationship("IncidentORM", back_populates="tasks")
    assignee = relationship("UserORM", back_populates="tasks_assigned")

class NotificationORM(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True) # cite: 93
    recipient = Column(Integer, ForeignKey("users.id"), nullable=False) # cite: 94
    channel = Column(String, nullable=False) # cite: 95
    message = Column(Text, nullable=False) # cite: 96
    event_type = Column(String, nullable=False) # cite: 97
    status = Column(String, default="PENDING") # cite: 98
    
    created_at = Column(DateTime, default=datetime.utcnow) # cite: 99
    read_at = Column(DateTime, nullable=True)

    # Relación simple con el usuario receptor
    user = relationship("UserORM")