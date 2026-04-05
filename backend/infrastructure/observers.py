"""
Implementación de observadores concretos que reaccionan a eventos del sistema.
Los observadores implementan el patrón Observer para orquestar acciones secundarias.
"""

import logging
from datetime import datetime
from domain.interfaces.observador_evento import ObservadorEvento
from domain.events import (
    Evento,
    IncidentCreatedEvent,
    IncidentAssignedEvent,
    IncidentStatusChangedEvent,
    TaskCreatedEvent,
    TaskDoneEvent,
)
from domain.entities import Notification
from domain.enums import NotificationStatus


# ============================================
# NotificationObserver
# ============================================

class NotificationObserver(ObservadorEvento):
    """
    Observador que genera notificaciones cuando ocurren eventos en el sistema.
    Implementa el patrón Command para encapsular el envío de notificaciones.
    """
    
    def __init__(self, notification_repo):
        """
        Args:
            notification_repo: Repositorio para persistir notificaciones
        """
        self.notification_repo = notification_repo
    
    def on_event(self, evento: Evento) -> None:
        """Procesa un evento generando notificaciones apropiadas"""
        
        if isinstance(evento, IncidentCreatedEvent):
            self._handle_incident_created(evento)
        
        elif isinstance(evento, IncidentAssignedEvent):
            self._handle_incident_assigned(evento)
        
        elif isinstance(evento, IncidentStatusChangedEvent):
            self._handle_incident_status_changed(evento)
        
        elif isinstance(evento, TaskCreatedEvent):
            self._handle_task_created(evento)
        
        elif isinstance(evento, TaskDoneEvent):
            self._handle_task_done(evento)
    
    def _handle_incident_created(self, evento: IncidentCreatedEvent) -> None:
        """Genera notificación cuando se crea un incidente"""
        notification = Notification(
            recipient=evento.incident.created_by,
            channel="in_app",
            message=f"Incidente creado: {evento.incident.title}",
            event_type="INCIDENT_CREATED",
            status=NotificationStatus.PENDING
        )
        self.notification_repo.save(notification)
    
    def _handle_incident_assigned(self, evento: IncidentAssignedEvent) -> None:
        """Genera notificación cuando se asigna un incidente"""
        notification = Notification(
            recipient=evento.assigned_to,
            channel="in_app",
            message=f"Se te ha asignado un incidente: {evento.incident.title}",
            event_type="INCIDENT_ASSIGNED",
            status=NotificationStatus.PENDING
        )
        self.notification_repo.save(notification)
    
    def _handle_incident_status_changed(self, evento: IncidentStatusChangedEvent) -> None:
        """Genera notificación cuando cambia el estado de un incidente"""
        if evento.incident.assigned_to:
            notification = Notification(
                recipient=evento.incident.assigned_to,
                channel="in_app",
                message=f"Incidente {evento.incident.title}: {evento.old_status} → {evento.new_status}",
                event_type="INCIDENT_STATUS_CHANGED",
                status=NotificationStatus.PENDING
            )
            self.notification_repo.save(notification)
    
    def _handle_task_created(self, evento: TaskCreatedEvent) -> None:
        """Genera notificación cuando se crea una tarea"""
        if evento.task.assigned_to:
            notification = Notification(
                recipient=evento.task.assigned_to,
                channel="in_app",
                message=f"Nueva tarea asignada: {evento.task.title}",
                event_type="TASK_CREATED",
                status=NotificationStatus.PENDING
            )
            self.notification_repo.save(notification)
    
    def _handle_task_done(self, evento: TaskDoneEvent) -> None:
        """Genera notificación cuando se completa una tarea"""
        # Notificar al creador/supervisor que una tarea fue completada
        notification = Notification(
            recipient=evento.task.assigned_to,
            channel="in_app",
            message=f"Tarea completada: {evento.task.title}",
            event_type="TASK_DONE",
            status=NotificationStatus.PENDING
        )
        self.notification_repo.save(notification)


# ============================================
# LoggingObserver
# ============================================

class LoggingObserver(ObservadorEvento):
    """
    Observador que registra todos los eventos en logs.
    Útil para auditoría y debugging del sistema.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def on_event(self, evento: Evento) -> None:
        """Registra un evento en logs"""
        event_type = tipo_evento = evento.__class__.__name__
        timestamp = evento.occurred_at.isoformat()
        
        log_message = f"[{timestamp}] Event: {event_type}"
        
        # Información específica por tipo de evento
        if isinstance(evento, IncidentCreatedEvent):
            log_message += f" | Incident: {evento.incident.id} | Title: {evento.incident.title}"
        
        elif isinstance(evento, IncidentAssignedEvent):
            log_message += f" | Incident: {evento.incident.id} | Assigned to: {evento.assigned_to}"
        
        elif isinstance(evento, IncidentStatusChangedEvent):
            log_message += f" | Incident: {evento.incident.id} | Status: {evento.old_status} → {evento.new_status}"
        
        elif isinstance(evento, TaskCreatedEvent):
            log_message += f" | Task: {evento.task.id} | Title: {evento.task.title}"
        
        elif isinstance(evento, TaskDoneEvent):
            log_message += f" | Task: {evento.task.id} | Status: DONE"
        
        self.logger.info(log_message)
