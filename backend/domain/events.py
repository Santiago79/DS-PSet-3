"""
Definición de eventos del dominio para el patrón Observer.
Los eventos se publican cuando ocurren cambios importantes en el negocio.
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entities import Incident, Task  # ¡Infiltrado 'backend.' eliminado!


@dataclass(kw_only=True)
class Evento(ABC):
    """Clase base abstracta para todos los eventos del dominio"""
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# ============================================
# Eventos de Incidente
# ============================================

@dataclass(kw_only=True)
class IncidentCreatedEvent(Evento):
    """Evento: Un incidente fue creado"""
    incident: "Incident"


@dataclass(kw_only=True)
class IncidentAssignedEvent(Evento):
    """Evento: Un incidente fue asignado a un usuario"""
    incident: "Incident"
    assigned_to: str  # user_id


@dataclass(kw_only=True)
class IncidentStatusChangedEvent(Evento):
    """Evento: El estado de un incidente cambió"""
    incident: "Incident"
    old_status: str
    new_status: str


# ============================================
# Eventos de Tarea
# ============================================

@dataclass(kw_only=True)
class TaskCreatedEvent(Evento):
    """Evento: Una tarea fue creada"""
    task: "Task"


@dataclass(kw_only=True)
class TaskDoneEvent(Evento):
    """Evento: Una tarea fue completada"""
    task: "Task"