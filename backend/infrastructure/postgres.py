from __future__ import annotations
from typing import Optional, List
from sqlalchemy.orm import Session

from infrastructure.models import UserORM, IncidentORM, TaskORM, NotificationORM
from domain.entities import User, Incident, Task, Notification
from domain.enums import Role, Severity, IncidentStatus, TaskStatus, NotificationStatus


# ============================================
# Repositorio de Usuarios
# ============================================

class PostgresUserRepo:
    """Implementación con PostgreSQL del repositorio de Usuarios"""
    
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: str) -> Optional[User]:
        model = self.session.get(UserORM, user_id)
        if not model:
            return None
        return self._to_domain(model)

    def get_by_email(self, email: str) -> Optional[User]:
        model = self.session.query(UserORM).filter(UserORM.email == email).first()
        if not model:
            return None
        return self._to_domain(model)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        models = self.session.query(UserORM).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model: UserORM) -> User:
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            hashed_password=model.hashed_password,
            role=Role(model.role)
        )


# ============================================
# Repositorio de Incidentes
# ============================================

class PostgresIncidentRepo:
    """Implementación con PostgreSQL del repositorio de Incidentes"""
    
    def __init__(self, session: Session):
        self.session = session

    def save(self, incident: Incident) -> Incident:
        existing = self.session.get(IncidentORM, incident.id)
        
        if existing:
            existing.title = incident.title
            existing.description = incident.description
            existing.severity = incident.severity.value
            existing.status = incident.status.value
            existing.assigned_to = incident.assigned_to
            existing.updated_at = incident.updated_at
        else:
            model = IncidentORM(
                id=incident.id,
                title=incident.title,
                description=incident.description,
                severity=incident.severity.value,
                status=incident.status.value,
                created_by=incident.created_by,
                assigned_to=incident.assigned_to,
                created_at=incident.created_at,
                updated_at=incident.updated_at
            )
            self.session.add(model)
        
        self.session.commit()
        return incident

    def get_by_id(self, incident_id: str) -> Optional[Incident]:
        model = self.session.get(IncidentORM, incident_id)
        if not model:
            return None
        return self._to_domain(model)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Incident]:
        models = self.session.query(IncidentORM).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]

    def get_by_created_by(self, user_id: str) -> List[Incident]:
        models = self.session.query(IncidentORM).filter(IncidentORM.created_by == user_id).all()
        return [self._to_domain(model) for model in models]

    def get_by_assigned_to(self, user_id: str) -> List[Incident]:
        models = self.session.query(IncidentORM).filter(IncidentORM.assigned_to == user_id).all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model: IncidentORM) -> Incident:
        return Incident(
            id=model.id,
            title=model.title,
            description=model.description,
            severity=Severity(model.severity),
            created_by=model.created_by,
            assigned_to=model.assigned_to,
            created_at=model.created_at,
            updated_at=model.updated_at,
            _status=IncidentStatus(model.status)
        )


# ============================================
# Repositorio de Tareas
# ============================================

class PostgresTaskRepo:
    """Implementación con PostgreSQL del repositorio de Tareas"""
    
    def __init__(self, session: Session):
        self.session = session

    def save(self, task: Task) -> Task:
        existing = self.session.get(TaskORM, task.id)
        
        if existing:
            existing.title = task.title
            existing.description = task.description
            existing.status = task.status.value
            existing.assigned_to = task.assigned_to
            existing.updated_at = task.updated_at
        else:
            model = TaskORM(
                id=task.id,
                incident_id=task.incident_id,
                title=task.title,
                description=task.description,
                status=task.status.value,
                assigned_to=task.assigned_to,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            self.session.add(model)
        
        self.session.commit()
        return task

    def get_by_id(self, task_id: str) -> Optional[Task]:
        model = self.session.get(TaskORM, task_id)
        if not model:
            return None
        return self._to_domain(model)

    def get_by_incident_id(self, incident_id: str) -> List[Task]:
        models = self.session.query(TaskORM).filter(TaskORM.incident_id == incident_id).all()
        return [self._to_domain(model) for model in models]

    def get_by_assigned_to(self, user_id: str) -> List[Task]:
        models = self.session.query(TaskORM).filter(TaskORM.assigned_to == user_id).all()
        return [self._to_domain(model) for model in models]
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Obtiene todas las tareas con paginación para ADMIN y SUPERVISOR"""
        models = self.session.query(TaskORM).offset(skip).limit(limit).all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model: TaskORM) -> Task:
        return Task(
            id=model.id,
            incident_id=model.incident_id,
            title=model.title,
            description=model.description,
            assigned_to=model.assigned_to,
            created_at=model.created_at,
            updated_at=model.updated_at,
            _status=TaskStatus(model.status)
        )


# ============================================
# Repositorio de Notificaciones
# ============================================

class PostgresNotificationRepo:
    """Implementación con PostgreSQL del repositorio de Notificaciones"""
    
    def __init__(self, session: Session):
        self.session = session

    def save(self, notification: Notification) -> Notification:
        """Guarda una notificación (crea o actualiza)"""
        existing = self.session.get(NotificationORM, notification.id)
        
        if existing:
            existing.recipient = notification.recipient
            existing.channel = notification.channel
            existing.message = notification.message
            existing.event_type = notification.event_type
            existing.status = notification.status.value
            existing.read_at = notification.read_at
        else:
            model = NotificationORM(
                id=notification.id,
                recipient=notification.recipient,
                channel=notification.channel,
                message=notification.message,
                event_type=notification.event_type,
                status=notification.status.value,
                created_at=notification.created_at,
                read_at=notification.read_at
            )
            self.session.add(model)
        
        self.session.commit()
        return notification

    def find_by_recipient(self, user_id: str) -> List[Notification]:
        """Obtiene todas las notificaciones de un usuario por su ID"""
        models = self.session.query(NotificationORM).filter(
            NotificationORM.recipient == user_id
        ).all()
        return [self._to_domain(model) for model in models]

    def find_all(self) -> List[Notification]:
        """Obtiene todas las notificaciones del sistema"""
        models = self.session.query(NotificationORM).all()
        return [self._to_domain(model) for model in models]

    def mark_as_read(self, notification_id: str) -> None:
        """Marca una notificación como leída"""
        notification = self.session.get(NotificationORM, notification_id)
        if notification:
            from datetime import datetime, timezone
            notification.read_at = datetime.now(timezone.utc)
            notification.status = NotificationStatus.READ.value
            self.session.commit()

    def _to_domain(self, model: NotificationORM) -> Notification:
        return Notification(
            id=model.id,
            recipient=model.recipient,
            channel=model.channel,
            message=model.message,
            event_type=model.event_type,
            status=NotificationStatus(model.status),
            created_at=model.created_at,
            read_at=model.read_at
        )
