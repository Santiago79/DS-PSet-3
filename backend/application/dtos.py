from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ============================================
# DTOs de Usuario (Auth)
# ============================================

class UserResponseDTO(BaseModel):
    """DTO para respuesta de usuario autenticado"""
    id: str
    name: str
    email: str
    role: str


class LoginRequestDTO(BaseModel):
    """DTO para solicitud de login"""
    email: str
    password: str


class LoginResponseDTO(BaseModel):
    """DTO para respuesta de login"""
    access_token: str
    token_type: str = "bearer"


# ============================================
# DTOs de Tarea (definido PRIMERO para evitar referencia circular)
# ============================================

class TaskResponseDTO(BaseModel):
    """DTO para respuesta de tarea"""
    id: str
    incident_id: str
    title: str
    description: str
    status: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CreateTaskDTO(BaseModel):
    """DTO para crear una tarea"""
    incident_id: str
    title: str
    description: str
    assigned_to: Optional[str] = None


# ============================================
# DTOs de Incidente
# ============================================

class CreateIncidentDTO(BaseModel):
    """DTO para crear un incidente"""
    title: str
    description: str
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"


class IncidentResponseDTO(BaseModel):
    """DTO para respuesta de incidente"""
    id: str
    title: str
    description: str
    severity: str
    status: str
    created_by: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskResponseDTO] = []  # TaskResponseDTO ya existe


class AssignIncidentDTO(BaseModel):
    """DTO para asignar un incidente"""
    assigned_to: str


class ChangeStatusDTO(BaseModel):
    """DTO para cambiar estado"""
    status: str  # OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED


# ============================================
# DTOs de Notificación
# ============================================

class NotificationResponseDTO(BaseModel):
    """DTO para respuesta de notificación"""
    id: str
    recipient: str
    channel: str
    message: str
    event_type: str
    status: str
    created_at: datetime
    read_at: Optional[datetime] = None


class MarkNotificationReadDTO(BaseModel):
    """DTO para marcar una notificación como leída"""
    notification_id: str