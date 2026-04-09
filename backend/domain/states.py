"""
State Pattern para el ciclo de vida de un Incidente.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from domain.enums import IncidentStatus
from domain.exceptions import InvalidStateTransitionError

if TYPE_CHECKING:
    from domain.entities import Incident


# ============================================
# Clase abstracta del State
# ============================================

class IncidentState(ABC):
    """
    Clase abstracta que define las acciones que pueden realizarse
    sobre un incidente dependiendo de su estado actual.
    """
    
    @abstractmethod
    def assign(self, incident: Incident, user_id: str) -> None:
        """Asignar el incidente a un usuario"""
        pass
    
    @abstractmethod
    def start_progress(self, incident: Incident) -> None:
        """Iniciar el progreso del incidente"""
        pass
    
    @abstractmethod
    def resolve(self, incident: Incident) -> None:
        """Resolver el incidente"""
        pass
    
    @abstractmethod
    def close(self, incident: Incident) -> None:
        """Cerrar el incidente"""
        pass
    
    @abstractmethod
    def reopen(self, incident: Incident) -> None:
        """Reabrir el incidente"""
        pass


# ============================================
# Estados concretos
# ============================================

class OpenState(IncidentState):
    """
    Estado: OPEN (Abierto)
    Se puede asignar, pero no se puede iniciar progreso, resolver ni cerrar.
    """
    
    def assign(self, incident: Incident, user_id: str) -> None:
        incident.assigned_to = user_id
        incident._transition_to(IncidentStatus.ASSIGNED)

    def start_progress(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede iniciar progreso: el incidente no está asignado"
        )

#    def start_progress(self, incident: Incident) -> None:
#       incident._transition_to(IncidentStatus.IN_PROGRESS)
    
    def resolve(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede resolver: el incidente no está asignado"
        )
    
    def close(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede cerrar: el incidente no está resuelto"
        )
    
    def reopen(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede reabrir: el incidente ya está abierto"
        )


class AssignedState(IncidentState):
    """
    Estado: ASSIGNED (Asignado)
    Se puede iniciar progreso o reabrir (volver a OPEN).
    """
    
    def assign(self, incident: Incident, user_id: str) -> None:
        # Reasignar es válido, se queda en ASSIGNED
        incident.assigned_to = user_id
    
    def start_progress(self, incident: Incident) -> None:
        incident._transition_to(IncidentStatus.IN_PROGRESS)
    
    def resolve(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede resolver: el incidente no está en progreso"
        )
    
    def close(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede cerrar: el incidente no está resuelto"
        )
    
    def reopen(self, incident: Incident) -> None:
        incident.assigned_to = None
        incident._transition_to(IncidentStatus.OPEN)


class InProgressState(IncidentState):
    """
    Estado: IN_PROGRESS (En progreso)
    Se puede resolver o volver a asignado.
    """
    
    def assign(self, incident: Incident, user_id: str) -> None:
        # Volver a asignar (cambiar de responsable)
        incident.assigned_to = user_id
        incident._transition_to(IncidentStatus.ASSIGNED)
    
    def start_progress(self, incident: Incident) -> None:
        # Ya está en progreso, no hacer nada
        pass
    
    def resolve(self, incident: Incident) -> None:
        incident._transition_to(IncidentStatus.RESOLVED)
    
    def close(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede cerrar: el incidente no está resuelto"
        )
    
    def reopen(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede reabrir: el incidente no está cerrado"
        )


class ResolvedState(IncidentState):
    """
    Estado: RESOLVED (Resuelto)
    Se puede cerrar o reabrir.
    """
    
    def assign(self, incident: Incident, user_id: str) -> None:
        raise InvalidStateTransitionError(
            "No se puede asignar: el incidente está resuelto"
        )
    
    def start_progress(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede iniciar progreso: el incidente está resuelto"
        )
    
    def resolve(self, incident: Incident) -> None:
        # Ya está resuelto, no hacer nada
        pass
    
    def close(self, incident: Incident) -> None:
        incident._transition_to(IncidentStatus.CLOSED)
    
    def reopen(self, incident: Incident) -> None:
        incident.assigned_to = None
        incident._transition_to(IncidentStatus.OPEN)


class ClosedState(IncidentState):
    """
    Estado: CLOSED (Cerrado)
    Estado final. Solo se puede reabrir.
    """
    
    def assign(self, incident: Incident, user_id: str) -> None:
        raise InvalidStateTransitionError(
            "No se puede asignar: el incidente está cerrado"
        )
    
    def start_progress(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede iniciar progreso: el incidente está cerrado"
        )
    
    def resolve(self, incident: Incident) -> None:
        raise InvalidStateTransitionError(
            "No se puede resolver: el incidente está cerrado"
        )
    
    def close(self, incident: Incident) -> None:
        # Ya está cerrado, no hacer nada
        pass
    
    def reopen(self, incident: Incident) -> None:
        incident.assigned_to = None
        incident._transition_to(IncidentStatus.OPEN)


# ============================================
# Factory para crear el estado según el enum
# ============================================

def create_state_from_status(status: IncidentStatus, incident: Incident) -> IncidentState:
    """
    Fábrica que retorna la instancia del estado correcto según el enum.
    Esto permite hacer lazy loading del estado.
    """
    states = {
        IncidentStatus.OPEN: OpenState,
        IncidentStatus.ASSIGNED: AssignedState,
        IncidentStatus.IN_PROGRESS: InProgressState,
        IncidentStatus.RESOLVED: ResolvedState,
        IncidentStatus.CLOSED: ClosedState,
    }
    
    state_class = states.get(status)
    if state_class is None:
        raise ValueError(f"Estado desconocido: {status}")
    
    return state_class()
