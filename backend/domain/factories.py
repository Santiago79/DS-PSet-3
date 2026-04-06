"""
Factory Pattern para la creación centralizada de Incidentes y Tareas.
Centraliza validaciones de negocio y asegura que las entidades se creen en estado válido.
"""

from uuid import uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from domain.entities import Incident, Task, Notification
from domain.enums import Severity, IncidentStatus, TaskStatus, NotificationStatus, NotificationChannel
from domain.exceptions import ValidationError
from domain.events import Evento

if TYPE_CHECKING:
    from domain.commands import EmailNotificationCommand, InAppNotificationCommand
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
# NotificationCommandFactory
# ============================================

class NotificationCommandFactory:
    """
    Factory para crear los comandos apropiados según el canal de notificación.
    Centraliza la creación de comandos y facilita su extensión.
    """
    
    @staticmethod
    def create_command(
        channel: str,
        notification_repo: "NotificationRepository",
        evento: Evento,
        **kwargs,
    ):
        """
        Crea un comando de notificación según el canal especificado.
        
        Args:
            channel: Canal de notificación ("email", "in_app", "sms", etc.)
            notification_repo: Repositorio para persistir notificaciones
            evento: Evento de dominio que genera la notificación
            **kwargs: Parámetros específicos für each channel
                - Para EMAIL: recipient
                - Para IN_APP: user_id
        
        Returns:
            NotificationCommand: Comando apropiado para el canal
        
        Raises:
            ValueError: Si el canal no es soportado o faltan parámetros
        """
        # Importar aquí para evitar circular imports
        from domain.commands import EmailNotificationCommand, InAppNotificationCommand
        
        if channel == NotificationChannel.EMAIL.value:
            return NotificationCommandFactory._create_email_command(
                notification_repo, evento, kwargs, EmailNotificationCommand
            )
        
        elif channel == NotificationChannel.IN_APP.value:
            return NotificationCommandFactory._create_in_app_command(
                notification_repo, evento, kwargs, InAppNotificationCommand
            )
        
        else:
            raise ValueError(f"Canal de notificación no soportado: {channel}")
    
    @staticmethod
    def _create_email_command(
        notification_repo: "NotificationRepository",
        evento: Evento,
        kwargs: dict,
        EmailNotificationCommand,
    ):
        """Crea un comando de email con validación de parámetros"""
        required_params = ["recipient"]
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Parámetro requerido faltante para EMAIL: {param}")
        
        return EmailNotificationCommand(
            notification_repo=notification_repo,
            recipient=kwargs["recipient"],
            evento=evento,
        )
    
    @staticmethod
    def _create_in_app_command(
        notification_repo: "NotificationRepository",
        evento: Evento,
        kwargs: dict,
        InAppNotificationCommand,
    ):
        """Crea un comando in-app con validación de parámetros"""
        required_params = ["user_id"]
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Parámetro requerido faltante para IN_APP: {param}")
        
        return InAppNotificationCommand(
            notification_repo=notification_repo,
            user_id=kwargs["user_id"],
            evento=evento,
        )