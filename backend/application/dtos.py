from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# ============================================
# DTOs de Usuario (Auth)
# ============================================

class UserResponseDTO(BaseModel):
    id: str
    name: str
    email: str
    role: str


class LoginRequestDTO(BaseModel):
    email: str = Field(description="Correo electrónico del usuario")
    password: str = Field(min_length=1, description="Contraseña del usuario")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Formato de correo electrónico inválido")
        return v.strip().lower()


class LoginResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ============================================
# DTOs de Tarea 
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
    incident_id: str = Field(min_length=1, description="ID del incidente asociado")
    title: str = Field(min_length=3, max_length=200, description="Título de la tarea")
    description: str = Field(description="Descripción de la tarea")
    assigned_to: Optional[str] = Field(None, description="ID del usuario asignado")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v.strip()


# ============================================
# DTOs de Incidente 
# ============================================

class CreateIncidentDTO(BaseModel):
    """DTO para crear un incidente"""
    title: str = Field(min_length=3, max_length=200, description="Título del incidente")
    description: str = Field(min_length=5, description="Descripción del incidente")
    severity: str = Field(description="Severidad: LOW, MEDIUM, HIGH, CRITICAL")

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        allowed = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if v not in allowed:
            raise ValueError(f"Severidad debe ser uno de: {allowed}")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("La descripción no puede estar vacía")
        return v.strip()


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
    tasks: List[TaskResponseDTO] = [] 


class AssignIncidentDTO(BaseModel):
    """DTO para asignar un incidente"""
    assigned_to: str = Field(min_length=1, description="ID del usuario asignado")


class ChangeStatusDTO(BaseModel):
    """DTO para cambiar estado"""
    status: str = Field(description="Nuevo estado: OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["OPEN", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"]
        if v not in allowed:
            raise ValueError(f"Estado debe ser uno de: {allowed}")
        return v


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
    notification_id: str = Field(min_length=1, description="ID de la notificación a marcar como leída")