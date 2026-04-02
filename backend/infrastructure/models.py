from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from infrastructure.database import Base

class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False) # ADMIN, SUPERVISOR, OPERATOR

    incidents_created = relationship("IncidentORM", foreign_keys="[IncidentORM.created_by]", back_populates="creator")
    incidents_assigned = relationship("IncidentORM", foreign_keys="[IncidentORM.assigned_to]", back_populates="assignee")
    tasks_assigned = relationship("TaskORM", back_populates="assignee")

class IncidentORM(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, default="OPEN")
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("UserORM", foreign_keys=[created_by], back_populates="incidents_created")
    assignee = relationship("UserORM", foreign_keys=[assigned_to], back_populates="incidents_assigned")
    tasks = relationship("TaskORM", back_populates="incident", cascade="all, delete-orphan")

class TaskORM(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="OPEN")
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    incident = relationship("IncidentORM", back_populates="tasks")
    assignee = relationship("UserORM", back_populates="tasks_assigned")

class NotificationORM(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    event_type = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    user = relationship("UserORM")