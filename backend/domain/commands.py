"""
Implementación del patrón Command para manejar el envío de notificaciones.
Cada comando representa una acción de envío por un canal específico.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from backend.domain.entities import Notification
from backend.domain.enums import NotificationStatus, NotificationChannel
from backend.domain.events import Evento
from backend.domain.templates import EmailMessageBuilder, InAppMessageBuilder

if TYPE_CHECKING:
    from backend.domain.repositories import NotificationRepository


# ============================================
# Comando Abstracto
# ============================================

class NotificationCommand(ABC):
    """
    Clase abstracta para comandos de envío de notificaciones.
    Define el contrato que todo comando debe cumplir.
    """
    
    def __init__(self, notification_repo: "NotificationRepository"):
        """
        Args:
            notification_repo: Repositorio para persistir notificaciones
        """
        self.notification_repo = notification_repo
    
    @abstractmethod
    def execute(self) -> None:
        """
        Ejecuta el comando de envío de notificación.
        Debe persistir la notificación con estado SENT o FAILED.
        """
        pass


# ============================================
# Comandos Concretos
# ============================================

class EmailNotificationCommand(NotificationCommand):
    """
    Comando para enviar notificaciones por correo electrónico.
    Usa EmailMessageBuilder (Template Method) para construir el mensaje.
    """
    
    def __init__(
        self,
        notification_repo: "NotificationRepository",
        recipient: str,
        evento: Evento,
    ):
        """
        Args:
            notification_repo: Repositorio para persistir notificaciones
            recipient: Email del destinatario
            evento: Evento de dominio que genera la notificación
        """
        super().__init__(notification_repo)
        self.recipient = recipient
        self.evento = evento
        self.message_builder = EmailMessageBuilder()
    
    def execute(self) -> None:
        """Envía notificación por email y persiste el resultado"""
        try:
            # Usar el builder para construir el mensaje (Template Method)
            message = self.message_builder.build(self.evento)
            
            # Simulación de envío de email
            # En producción, aquí irían llamadas a un servicio de email (SendGrid, AWS SES, etc.)
            self._send_email(message)
            
            # Si el envío fue exitoso, crear notificación con estado SENT
            notification = Notification(
                recipient=self.recipient,
                channel=NotificationChannel.EMAIL.value,
                message=message,
                event_type="EMAIL_SENT",
                status=NotificationStatus.SENT,
            )
        except Exception as e:
            # Si falla, crear notificación con estado FAILED
            notification = Notification(
                recipient=self.recipient,
                channel=NotificationChannel.EMAIL.value,
                message=f"Error enviando email: {str(e)}",
                event_type="EMAIL_FAILED",
                status=NotificationStatus.FAILED,
            )
        
        # Persistir la notificación
        self.notification_repo.save(notification)
    
    def _send_email(self, message: str) -> None:
        """Intenta enviar el email. Puede lanzar excepciones."""
        # Aquí iría la lógica real de envío de email
        # Por ahora es un placeholder que simula envío exitoso
        pass
        # Por ahora es un placeholder que simula envío exitoso
        pass


class InAppNotificationCommand(NotificationCommand):
    """
    Comando para enviar notificaciones en la aplicación.
    Usa InAppMessageBuilder (Template Method) para construir el mensaje.
    """
    
    def __init__(
        self,
        notification_repo: "NotificationRepository",
        user_id: str,
        evento: Evento,
    ):
        """
        Args:
            notification_repo: Repositorio para persistir notificaciones
            user_id: ID del usuario destinatario
            evento: Evento de dominio que genera la notificación
        """
        super().__init__(notification_repo)
        self.user_id = user_id
        self.evento = evento
        self.message_builder = InAppMessageBuilder()
    
    def execute(self) -> None:
        """Envía notificación in-app y persiste el resultado"""
        try:
            # Usar el builder para construir el mensaje (Template Method)
            message = self.message_builder.build(self.evento)
            
            # Las notificaciones in-app generalmente no fallan (solo se persisten)
            # Pero podemos simular validaciones
            self._validate_message(message)
            
            notification = Notification(
                recipient=self.user_id,
                channel=NotificationChannel.IN_APP.value,
                message=message,
                event_type="IN_APP_NOTIFICATION",
                status=NotificationStatus.SENT,
            )
        except Exception as e:
            notification = Notification(
                recipient=self.user_id,
                channel=NotificationChannel.IN_APP.value,
                message=f"Error creando notificación: {str(e)}",
                event_type="IN_APP_FAILED",
                status=NotificationStatus.FAILED,
            )
        
        # Persistir la notificación
        self.notification_repo.save(notification)
    
    def _validate_message(self, message: str) -> None:
        """Valida que el mensaje sea válido"""
        if not message or len(message.strip()) == 0:
            raise ValueError("El mensaje no puede estar vacío")
