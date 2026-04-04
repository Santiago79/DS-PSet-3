from dataclasses import dataclass, field
import datetime
from typing import Optional
from backend.domain.exceptions import InvalidStateTransitionError, ValidationError
from domain.enums import IncidentStatus, Role, Severity, TaskStatus
from uuid import uuid4

@dataclass
class User:
    name: str
    email: str
    hashed_password: str
    role: Role
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError("El nombre del cliente debe tener al menos 2 caracteres")
        if "@" not in self.email:
            raise ValidationError("El formato del email es inválido")


@dataclass
class Incident:
    """
    Entidad Incident - Corazón del sistema OpsCenter.
    """
    title: str
    description: str
    severity: Severity
    created_by: str
    id: str = field(default_factory=lambda: str(uuid4()))
    _status: IncidentStatus = field(default=IncidentStatus.OPEN)
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("El título debe tener al menos 3 caracteres")
        if not self.description or len(self.description.strip()) < 5:
            raise ValidationError("La descripción debe tener al menos 5 caracteres")
        if not isinstance(self.severity, Severity):
            raise ValidationError(f"Severidad inválida: {self.severity}")
        if not self.created_by:
            raise ValidationError("El creador del incidente es requerido")

    @property
    def status(self) -> IncidentStatus:
        """Retorna el estado actual del incidente"""
        return self._status

    def assign_to(self, user_id: str) -> None:
        """
        Asigna el incidente a un usuario.
        Solo se puede asignar si el incidente está OPEN.
        """
        if self._status != IncidentStatus.OPEN:
            raise InvalidStateTransitionError(
                f"No se puede asignar un incidente en estado {self._status.value}"
            )
        self.assigned_to = user_id
        self._status = IncidentStatus.ASSIGNED
        self.updated_at = datetime.utcnow()

    def change_status(self, new_status: IncidentStatus) -> None:
        """
        Cambia el estado del incidente validando las transiciones permitidas.
        """
        # Definir transiciones válidas
        allowed_transitions = {
            IncidentStatus.OPEN: [IncidentStatus.ASSIGNED],
            IncidentStatus.ASSIGNED: [IncidentStatus.IN_PROGRESS, IncidentStatus.OPEN],
            IncidentStatus.IN_PROGRESS: [IncidentStatus.RESOLVED, IncidentStatus.ASSIGNED],
            IncidentStatus.RESOLVED: [IncidentStatus.CLOSED, IncidentStatus.OPEN],
            IncidentStatus.CLOSED: [],  # Estado final, no se puede cambiar
        }
        
        if new_status == self._status:
            return  # No hay cambio
        
        if new_status not in allowed_transitions.get(self._status, []):
            raise InvalidStateTransitionError(
                f"Transición inválida: {self._status.value} -> {new_status.value}"
            )
        
        self._status = new_status
        self.updated_at = datetime.utcnow()


@dataclass
class Task:
    """Entidad Task - Tareas asociadas a un incidente"""
    incident_id: str
    title: str
    description: str
    id: str = field(default_factory=lambda: str(uuid4()))
    _status: TaskStatus = field(default=TaskStatus.OPEN)
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError("El título de la tarea debe tener al menos 3 caracteres")
        if not self.incident_id:
            raise ValidationError("La tarea debe estar asociada a un incidente")

    @property
    def status(self) -> TaskStatus:
        return self._status

    def assign_to(self, user_id: str) -> None:
        """Asigna la tarea a un usuario"""
        self.assigned_to = user_id
        self.updated_at = datetime.utcnow()

    def mark_in_progress(self) -> None:
        """Marca la tarea como en progreso"""
        if self._status != TaskStatus.OPEN:
            raise InvalidStateTransitionError(
                f"No se puede iniciar una tarea en estado {self._status.value}"
            )
        self._status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def mark_done(self) -> None:
        """Marca la tarea como completada"""
        if self._status == TaskStatus.DONE:
            return
        if self._status not in [TaskStatus.OPEN, TaskStatus.IN_PROGRESS]:
            raise InvalidStateTransitionError(
                f"No se puede completar una tarea en estado {self._status.value}"
            )
        self._status = TaskStatus.DONE
        self.updated_at = datetime.utcnow()