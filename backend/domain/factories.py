"""
Factory Pattern para la creación centralizada de Incidentes y Tareas.
Centraliza validaciones de negocio y asegura que las entidades se creen en estado válido.

Además implementa Abstract Factory Pattern para crear familias de objetos
de notificación según el tipo de evento (Incident o Task).
"""

from abc import ABC, abstractmethod
from uuid import uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from domain.entities import Incident, Task, Notification
from domain.enums import Severity, IncidentStatus, TaskStatus, NotificationStatus, NotificationChannel
from domain.exceptions import ValidationError
from domain.events import (
    Evento,
    IncidentCreatedEvent,
    IncidentAssignedEvent,
    IncidentStatusChangedEvent,
    TaskCreatedEvent,
    TaskDoneEvent,
)

if TYPE_CHECKING:
    from domain.commands import NotificationCommand
    from domain.templates import NotificationMessageBuilder
    from domain.repositories import NotificationRepository


class IncidentFactory:
    """Factory para crear incidentes de manera centralizada."""
    
    @staticmethod
    def create(
        title: str,
        description: str,
        severity: Severity,
        created_by: str
    ) -> Incident:
        """
        Crea un nuevo incidente con validaciones.
        
        Args:
            title: Título del incidente (no vacío, mínimo 3 caracteres)
            description: Descripción del incidente (no vacía, mínimo 5 caracteres)
            severity: Severidad del incidente (debe ser valor válido de Severity)
            created_by: ID del usuario que crea el incidente
        
        Returns:
            Incident: Nueva instancia de incidente con estado OPEN y UUID generado
            
        Raises:
            ValidationError: Si alguna validación falla
        """
        # Validaciones de negocio
        if not title or not title.strip():
            raise ValidationError("El título del incidente es requerido")
        
        if len(title.strip()) < 3:
            raise ValidationError("El título debe tener al menos 3 caracteres")
        
        if not description or not description.strip():
            raise ValidationError("La descripción del incidente es requerida")
        
        if len(description.strip()) < 5:
            raise ValidationError("La descripción debe tener al menos 5 caracteres")
        
        if not isinstance(severity, Severity):
            raise ValidationError(f"Severidad inválida: {severity}")
        
        if not created_by:
            raise ValidationError("El creador del incidente es requerido")
        
        # Crear instancia
        return Incident(
            id=str(uuid4()),
            title=title.strip(),
            description=description.strip(),
            severity=severity,
            created_by=created_by,
            assigned_to=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            _status=IncidentStatus.OPEN
        )


class TaskFactory:
    """Factory para crear tareas de manera centralizada."""
    
    @staticmethod
    def create(
        incident_id: str,
        title: str,
        description: str,
        assigned_to: Optional[str] = None
    ) -> Task:
        """
        Crea una nueva tarea asociada a un incidente.
        
        Args:
            incident_id: ID del incidente al que pertenece la tarea
            title: Título de la tarea (no vacío, mínimo 3 caracteres)
            description: Descripción de la tarea
            assigned_to: ID del usuario asignado (opcional)
        
        Returns:
            Task: Nueva instancia de tarea con estado OPEN y UUID generado
            
        Raises:
            ValidationError: Si alguna validación falla
        """
        # Validaciones de negocio
        if not incident_id:
            raise ValidationError("El ID del incidente es requerido")
        
        if not title or not title.strip():
            raise ValidationError("El título de la tarea es requerido")
        
        if len(title.strip()) < 3:
            raise ValidationError("El título de la tarea debe tener al menos 3 caracteres")
        
        # Crear instancia
        return Task(
            id=str(uuid4()),
            incident_id=incident_id,
            title=title.strip(),
            description=description.strip() if description else "",
            assigned_to=assigned_to,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            _status=TaskStatus.OPEN
        )


# ============================================
# Abstract Factory Pattern para Notificaciones
# ============================================

class NotificationFactory(ABC):
    """
    Clase abstracta que implementa el patrón Abstract Factory.
    Define la interfaz para crear familias de objetos de notificación
    (comandos y message builders) según el tipo de evento.
    """
    
    @abstractmethod
    def create_command(
        self,
        notification_repo: "NotificationRepository",
        evento: Evento,
        **kwargs,
    ) -> "NotificationCommand":
        """
        Crea un comando de notificación específico para este tipo de evento.
        
        Args:
            notification_repo: Repositorio para persistir notificaciones
            evento: Evento de dominio que genera la notificación
            **kwargs: Parámetros específicos (recipient, user_id, etc.)
        
        Returns:
            NotificationCommand: Comando creado
        """
        pass
    
    @abstractmethod
    def create_message_builder(self) -> "NotificationMessageBuilder":
        """
        Crea un message builder específico para este tipo de evento.
        
        Returns:
            NotificationMessageBuilder: Builder para construir el mensaje
        """
        pass


class IncidentNotificationFactory(NotificationFactory):
    """
    Factory concreta para crear objetos de notificación relacionados con Incidentes.
    Crea comandos y message builders específicos para eventos de Incident.
    """
    
    def create_command(
        self,
        notification_repo: "NotificationRepository",
        evento: Evento,
        **kwargs,
    ) -> "NotificationCommand":
        """
        Crea un comando de notificación para eventos de Incident.
        
        Args:
            notification_repo: Repositorio para persistir notificaciones
            evento: Evento de Incident (IncidentCreatedEvent, IncidentAssignedEvent, etc.)
            **kwargs: Parámetros específicos (channel, recipient/user_id)
        
        Returns:
            NotificationCommand: Comando para enviar la notificación
            
        Raises:
            ValueError: Si el canal no es soportado o faltan parámetros
        """
        from backend.domain.commands import EmailNotificationCommand, InAppNotificationCommand
        
        # Validar que es un evento de Incident
        if not isinstance(evento, (IncidentCreatedEvent, IncidentAssignedEvent, IncidentStatusChangedEvent)):
            raise ValueError(f"Evento no es de tipo Incident: {type(evento)}")
        
        channel = kwargs.get("channel", NotificationChannel.IN_APP.value)
        
        if channel == NotificationChannel.EMAIL.value:
            recipient = kwargs.get("recipient")
            if not recipient:
                raise ValueError("Parámetro 'recipient' requerido para EMAIL")
            
            return EmailNotificationCommand(
                notification_repo=notification_repo,
                recipient=recipient,
                evento=evento,
            )
        
        elif channel == NotificationChannel.IN_APP.value:
            user_id = kwargs.get("user_id")
            if not user_id:
                raise ValueError("Parámetro 'user_id' requerido para IN_APP")
            
            return InAppNotificationCommand(
                notification_repo=notification_repo,
                user_id=user_id,
                evento=evento,
            )
        
        else:
            raise ValueError(f"Canal no soportado para Incident: {channel}")
    
    def create_message_builder(self) -> "NotificationMessageBuilder":
        """Retorna el builder para mensajes de Incident"""
        from backend.domain.templates import EmailMessageBuilder
        
        # Por defecto retorna EmailMessageBuilder (puede adaptarse según lógica)
        return EmailMessageBuilder()


class TaskNotificationFactory(NotificationFactory):
    """
    Factory concreta para crear objetos de notificación relacionados con Tareas.
    Crea comandos y message builders específicos para eventos de Task.
    """
    
    def create_command(
        self,
        notification_repo: "NotificationRepository",
        evento: Evento,
        **kwargs,
    ) -> "NotificationCommand":
        """
        Crea un comando de notificación para eventos de Task.
        
        Args:
            notification_repo: Repositorio para persistir notificaciones
            evento: Evento de Task (TaskCreatedEvent, TaskDoneEvent)
            **kwargs: Parámetros específicos (channel, recipient/user_id)
        
        Returns:
            NotificationCommand: Comando para enviar la notificación
            
        Raises:
            ValueError: Si el canal no es soportado o faltan parámetros
        """
        from backend.domain.commands import EmailNotificationCommand, InAppNotificationCommand
        
        # Validar que es un evento de Task
        if not isinstance(evento, (TaskCreatedEvent, TaskDoneEvent)):
            raise ValueError(f"Evento no es de tipo Task: {type(evento)}")
        
        channel = kwargs.get("channel", NotificationChannel.IN_APP.value)
        
        if channel == NotificationChannel.EMAIL.value:
            recipient = kwargs.get("recipient")
            if not recipient:
                raise ValueError("Parámetro 'recipient' requerido para EMAIL")
            
            return EmailNotificationCommand(
                notification_repo=notification_repo,
                recipient=recipient,
                evento=evento,
            )
        
        elif channel == NotificationChannel.IN_APP.value:
            user_id = kwargs.get("user_id")
            if not user_id:
                raise ValueError("Parámetro 'user_id' requerido para IN_APP")
            
            return InAppNotificationCommand(
                notification_repo=notification_repo,
                user_id=user_id,
                evento=evento,
            )
        
        else:
            raise ValueError(f"Canal no soportado para Task: {channel}")
    
    def create_message_builder(self) -> "NotificationMessageBuilder":
        """Retorna el builder para mensajes de Task"""
        from backend.domain.templates import InAppMessageBuilder
        
        # Por defecto retorna InAppMessageBuilder (puede adaptarse según lógica)
        return InAppMessageBuilder()


# Factory helper para obtener la factory correcta según el tipo de evento
def get_notification_factory(evento: Evento) -> NotificationFactory:
    """
    Retorna la factory apropiada según el tipo de evento.
    
    Args:
        evento: Evento de dominio
    
    Returns:
        NotificationFactory: Factory correspondiente al tipo de evento
        
    Raises:
        ValueError: Si el tipo de evento no es reconocido
    """
    if isinstance(evento, (IncidentCreatedEvent, IncidentAssignedEvent, IncidentStatusChangedEvent)):
        return IncidentNotificationFactory()
    
    elif isinstance(evento, (TaskCreatedEvent, TaskDoneEvent)):
        return TaskNotificationFactory()
    
    else:
        raise ValueError(f"Tipo de evento no reconocido para notificaciones: {type(evento)}")
