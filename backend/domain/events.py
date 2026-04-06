"""
Definición de eventos del dominio para el patrón Observer.
Los eventos se publican cuando ocurren cambios importantes en el negocio.
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.domain.entities import Incident, Task


@dataclass(kw_only=True)
class Evento(ABC):
    """Clase base abstracta para todos los eventos del dominio"""
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ============================================
# Eventos de Incidente
# ============================================

@dataclass
class IncidentCreatedEvent(Evento):
    """Evento: Un incidente fue creado"""
    incident: "Incident"


@dataclass
class IncidentAssignedEvent(Evento):
    """Evento: Un incidente fue asignado a un usuario"""
    incident: "Incident"
    assigned_to: str  # user_id


@dataclass
class IncidentStatusChangedEvent(Evento):
    """Evento: El estado de un incidente cambió"""
    incident: "Incident"
    old_status: str
    new_status: str


# ============================================
# Eventos de Tarea
# ============================================

@dataclass
class TaskCreatedEvent(Evento):
    """Evento: Una tarea fue creada"""
    task: "Task"


@dataclass
class TaskDoneEvent(Evento):
    """Evento: Una tarea fue completada"""
    task: "Task"
