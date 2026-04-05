from dataclasses import dataclass, field
import datetime
from typing import Optional
from backend.domain.exceptions import InvalidStateTransitionError, ValidationError
from backend.domain.states import IncidentState
from domain.enums import IncidentStatus, Role, Severity, TaskStatus, NotificationStatus
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
    Usa State Pattern para manejar su ciclo de vida.
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
    _state: Optional[IncidentState] = field(default=None, init=False, repr=False)

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

    @property
    def state(self) -> IncidentState:
        """
        Retorna el objeto State actual (lazy loading).
        El estado se crea según el valor de _status.
        """
        if self._state is None:
            from domain.states import create_state_from_status
            self._state = create_state_from_status(self._status, self)
        return self._state

    def assign_to(self, user_id: str) -> None:
        """
        Asigna el incidente a un usuario.
        Delega en el estado actual la lógica de asignación.
        """
        self.state.assign(self, user_id)
        self.updated_at = datetime.utcnow()

    def start_progress(self) -> None:
        """Marca el incidente como en progreso"""
        self.state.start_progress(self)
        self.updated_at = datetime.utcnow()

    def resolve(self) -> None:
        """Resuelve el incidente"""
        self.state.resolve(self)
        self.updated_at = datetime.utcnow()

    def close(self) -> None:
        """Cierra el incidente"""
        self.state.close(self)
        self.updated_at = datetime.utcnow()

    def reopen(self) -> None:
        """Reabre el incidente"""
        self.state.reopen(self)
        self.updated_at = datetime.utcnow()

    def _transition_to(self, new_status: IncidentStatus) -> None:
        """
        Método interno llamado por los estados para cambiar el estado.
        No debe ser llamado directamente desde fuera.
        """
        self._status = new_status
        self._state = None  # Forzar recarga del nuevo estado
        self.updated_at = datetime.utcnow()

@dataclass
class Task:
    """Entidad Task - Tareas asociadas a un incidente
    Usa State Pattern para manejar su ciclo de vida 
    """
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

@dataclass
class Notification:
    """
    Entidad Notification - Maneja las alertas del sistema.
    Parte del Issue #10.
    """
    recipient: str  # user_id
    channel: str    # email, in_app, sms
    message: str
    event_type: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: NotificationStatus = field(default=NotificationStatus.PENDING)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    read_at: Optional[datetime.datetime] = field(default=None)

    def __post_init__(self) -> None:
        if not self.recipient:
            raise ValidationError("El destinatario es requerido")
        if not self.message or len(self.message.strip()) < 1:
            raise ValidationError("El contenido de la notificación no puede estar vacío")
        if not self.channel:
            raise ValidationError("El canal de notificación es requerido")

    def mark_as_read(self) -> None:
        """Registra la lectura de la notificación"""
        self.read_at = datetime.datetime.now(datetime.timezone.utc)
        self.status = NotificationStatus.READ