from dataclasses import dataclass
import datetime
from typing import List, Optional

@dataclass
class UserResponseDTO:
    id: str
    name: str
    email: str
    role: str

@dataclass
class LoginRequestDTO:
    email: str
    password: str

@dataclass
class LoginResponseDTO:
    access_token: str
    token_type: str = "bearer"

@dataclass
class TaskResponseDTO:
    """DTO para respuesta de tarea"""
    id: str
    incident_id: str
    title: str
    description: str
    status: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class CreateIncidentDTO:
    """DTO para crear un incidente"""
    title: str
    description: str
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"

@dataclass
class IncidentResponseDTO:
    """DTO para respuesta de incidente"""
    id: str
    title: str
    description: str
    severity: str
    status: str
    created_by: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    tasks: List["TaskResponseDTO"] 


@dataclass
class AssignIncidentDTO:
    """DTO para asignar un incidente"""
    assigned_to: str


@dataclass
class ChangeStatusDTO:
    """DTO para cambiar estado"""
    status: str


@dataclass
class CreateTaskDTO:
    """DTO para crear una tarea"""
    incident_id: str
    title: str
    description: str
    assigned_to: Optional[str] = None


@dataclass
class NotificationResponseDTO:
    """DTO para respuesta de notificación"""
    id: str
    recipient: str
    channel: str
    message: str
    event_type: str
    status: str
    created_at: datetime.datetime
    read_at: Optional[datetime.datetime]


@dataclass
class MarkNotificationReadDTO:
    """DTO para marcar una notificación como leída"""
    notification_id: str





