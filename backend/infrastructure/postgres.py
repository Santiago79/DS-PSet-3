from __future__ import annotations
from typing import Optional, List
from sqlalchemy.orm import Session

from infrastructure.models import UserORM, IncidentORM, TaskORM
from domain.entities import User, Incident, Task
from domain.enums import Role, Severity, IncidentStatus, TaskStatus


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