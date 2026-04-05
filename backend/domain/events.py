"""
Definición de eventos del dominio para el patrón Observer.
Los eventos se publican cuando ocurren cambios importantes en el negocio.
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Evento(ABC):
    """Clase base abstracta para todos los eventos del dominio"""
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# ============================================
# Eventos de Incidente
# ============================================

@dataclass
class IncidentCreatedEvent(Evento):
    """Evento: Un incidente fue creado"""
    incident: Any  # Incident entity


@dataclass
class IncidentAssignedEvent(Evento):
    """Evento: Un incidente fue asignado a un usuario"""
    incident: Any  # Incident entity
    assigned_to: str  # user_id


@dataclass
class IncidentStatusChangedEvent(Evento):
    """Evento: El estado de un incidente cambió"""
    incident: Any  # Incident entity
    old_status: str
    new_status: str


# ============================================
# Eventos de Tarea
# ============================================

@dataclass
class TaskCreatedEvent(Evento):
    """Evento: Una tarea fue creada"""
    task: Any  # Task entity


@dataclass
class TaskDoneEvent(Evento):
    """Evento: Una tarea fue completada"""
    task: Any  # Task entity
