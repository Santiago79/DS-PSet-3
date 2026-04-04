from __future__ import annotations
from typing import Optional, List
from sqlalchemy import String, ForeignKey, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class UserORM(Base):
    __tablename__ = "users"

    # Fix 2 & 4: id como String y usando Mapped/mapped_column
    id: Mapped[str] = mapped_column(String, primary_key=True)
    
    # Fix 1 & 4: name como String y Mapped
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relaciones usando strings para evitar el NameError
    incidents_created: Mapped[List[IncidentORM]] = relationship(
        "IncidentORM", foreign_keys="[IncidentORM.created_by]", back_populates="creator"
    )
    incidents_assigned: Mapped[List[IncidentORM]] = relationship(
        "IncidentORM", foreign_keys="[IncidentORM.assigned_to]", back_populates="assignee"
    )
    tasks_assigned: Mapped[List[TaskORM]] = relationship("TaskORM", back_populates="assignee")

class IncidentORM(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OPEN")
    
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_to: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Fix 3: Relaciones con los foreign_keys corregidos
    creator: Mapped[UserORM] = relationship("UserORM", foreign_keys=[created_by], back_populates="incidents_created")
    assignee: Mapped[Optional[UserORM]] = relationship("UserORM", foreign_keys=[assigned_to], back_populates="incidents_assigned")
    tasks: Mapped[List[TaskORM]] = relationship("TaskORM", back_populates="incident", cascade="all, delete-orphan")

class TaskORM(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OPEN")
    assigned_to: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    incident: Mapped[IncidentORM] = relationship("IncidentORM", back_populates="tasks")
    assignee: Mapped[Optional[UserORM]] = relationship("UserORM", back_populates="tasks_assigned")

class NotificationORM(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    recipient: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped[UserORM] = relationship("UserORM")