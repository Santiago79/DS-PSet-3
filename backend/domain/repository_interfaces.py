from __future__ import annotations
from typing import Protocol, List
from domain.entities import Notification


class NotificationRepository(Protocol):
    """Interfaz para el repositorio de Notificaciones"""
    
    def save(self, notification: Notification) -> Notification:
        """Guarda una notificación (crea o actualiza)"""
        ...
    
    def find_by_recipient(self, user_id: str) -> List[Notification]:
        """Obtiene todas las notificaciones de un usuario por su ID"""
        ...
    
    def find_all(self) -> List[Notification]:
        """Obtiene todas las notificaciones del sistema"""
        ...
    
    def mark_as_read(self, notification_id: str) -> None:
        """Marca una notificación como leída"""
        ...
