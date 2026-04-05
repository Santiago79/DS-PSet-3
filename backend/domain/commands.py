"""
Implementación del patrón Command para manejar el envío de notificaciones.
Cada comando representa una acción de envío por un canal específico.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from backend.domain.entities import Notification
from backend.domain.enums import NotificationStatus, NotificationChannel

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
    """
    
    def __init__(
        self,
        notification_repo: "NotificationRepository",
        recipient: str,
        subject: str,
        body: str,
    ):
        """
        Args:
            notification_repo: Repositorio para persistir notificaciones
            recipient: Email del destinatario
            subject: Asunto del email
            body: Cuerpo del email
        """
        super().__init__(notification_repo)
        self.recipient = recipient
        self.subject = subject
        self.body = body
    
    def execute(self) -> None:
        """Envía notificación por email y persiste el resultado"""
        try:
            # Simulación de envío de email
            # En producción, aquí irían llamadas a un servicio de email (SendGrid, AWS SES, etc.)
            self._send_email()
            
            # Si el envío fue exitoso, crear notificación con estado SENT
            notification = Notification(
                recipient=self.recipient,
                channel=NotificationChannel.EMAIL.value,
                message=self.body,
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
    
    def _send_email(self) -> None:
        """Intenta enviar el email. Puede lanzar excepciones."""
        # Aquí iría la lógica real de envío de email
        # Por ahora es un placeholder que simula envío exitoso
        pass


class InAppNotificationCommand(NotificationCommand):
    """
    Comando para enviar notificaciones en la aplicación.
    """
    
    def __init__(
        self,
        notification_repo: "NotificationRepository",
        user_id: str,
        message: str,
    ):
        """
        Args:
            notification_repo: Repositorio para persistir notificaciones
            user_id: ID del usuario destinatario
            message: Contenido del mensaje
        """
        super().__init__(notification_repo)
        self.user_id = user_id
        self.message = message
    
    def execute(self) -> None:
        """Envía notificación in-app y persiste el resultado"""
        try:
            # Las notificaciones in-app generalmente no fallan (solo se persisten)
            # Pero podemos simular validaciones
            self._validate_message()
            
            notification = Notification(
                recipient=self.user_id,
                channel=NotificationChannel.IN_APP.value,
                message=self.message,
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
    
    def _validate_message(self) -> None:
        """Valida que el mensaje sea válido"""
        if not self.message or len(self.message.strip()) == 0:
            raise ValueError("El mensaje no puede estar vacío")
