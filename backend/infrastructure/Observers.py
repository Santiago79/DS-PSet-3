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
from domain.factories import get_notification_factory


# ============================================
# NotificationObserver
# ============================================

class NotificationObserver(ObservadorEvento):
    """
    Observador que genera notificaciones cuando ocurren eventos en el sistema.
    Utiliza el Abstract Factory Pattern para crear comandos específicos
    según el tipo de evento (Incident o Task).
    """
    
    def __init__(self, notification_repo):
        """
        Args:
            notification_repo: Repositorio para persistir notificaciones
        """
        self.notification_repo = notification_repo
    
    def on_event(self, evento: Evento) -> None:
        """
        Procesa un evento utilizando la factory correspondiente.
        Obtiene la factory según el tipo de evento y crea el comando apropiado.
        """
        try:
            # Obtener la factory correcta según el tipo de evento
            factory = get_notification_factory(evento)
            
            # Determinar el destinatario según el tipo de evento
            recipient = self._get_recipient(evento)
            
            if recipient:
                # Crear y ejecutar el comando usando la factory
                command = factory.create_command(
                    notification_repo=self.notification_repo,
                    evento=evento,
                    channel="in_app",
                    user_id=recipient,
                )
                command.execute()
        
        except Exception as e:
            # Log del error pero no propagar, para evitar fallos en el evento bus
            logging.error(f"Error procesando evento para notificación: {str(e)}")
    
    def _get_recipient(self, evento: Evento) -> str:
        """
        Determina el usuario destinatario según el tipo de evento.
        
        Args:
            evento: Evento de dominio
        
        Returns:
            str: ID del usuario destinatario, o None si no aplica
        """
        if isinstance(evento, IncidentCreatedEvent):
            # Notificar al creador del incidente
            return evento.incident.created_by
        
        elif isinstance(evento, IncidentAssignedEvent):
            # Notificar al usuario asignado
            return evento.assigned_to
        
        elif isinstance(evento, IncidentStatusChangedEvent):
            # Notificar al usuario asignado si existe
            return evento.incident.assigned_to
        
        elif isinstance(evento, TaskCreatedEvent):
            # Notificar al usuario asignado si existe
            return evento.task.assigned_to
        
        elif isinstance(evento, TaskDoneEvent):
            # Notificar al usuario asignado
            return evento.task.assigned_to
        
        return None


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
