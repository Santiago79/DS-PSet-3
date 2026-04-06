"""
Casos de uso (Servicios de aplicación) para Incidentes y Tareas.
Coordinan la lógica de negocio, validaciones y persistencia.
"""

from uuid import uuid4
from datetime import datetime
from typing import List, Optional

from domain.entities import Incident, Task, Notification
from domain.enums import Severity, IncidentStatus, TaskStatus, NotificationStatus
from domain.exceptions import ValidationError, NotFoundError, InvalidStateTransitionError
from domain.factories import IncidentFactory, TaskFactory
from domain.repositories import IncidentRepository, TaskRepository
from domain.interfaces.event_bus import EventBus
from domain.events import (
    IncidentCreatedEvent,
    IncidentAssignedEvent,
    IncidentStatusChangedEvent,
    TaskCreatedEvent,
    TaskDoneEvent,
)
from application.dtos import (
    CreateIncidentDTO,
    IncidentResponseDTO,
    AssignIncidentDTO,
    ChangeStatusDTO,
    CreateTaskDTO,
    TaskResponseDTO,
    NotificationResponseDTO,
    MarkNotificationReadDTO,
)

# ============================================
# Casos de uso - Incidentes
# ============================================

class CreateIncidentUseCase:
    """Caso de uso: Crear un incidente"""
    
    def __init__(self, incident_repo: IncidentRepository, event_bus: EventBus):
        self.incident_repo = incident_repo
        self.event_bus = event_bus
    
    def execute(self, dto: CreateIncidentDTO, created_by: str) -> IncidentResponseDTO:
        # Validar severity
        try:
            severity = Severity(dto.severity)
        except ValueError:
            raise ValidationError(f"Severidad inválida: {dto.severity}")
        
        # Usar Factory para crear incidente con validaciones
        incident = IncidentFactory.create(
            title=dto.title,
            description=dto.description,
            severity=severity,
            created_by=created_by
        )
        
        # Persistir
        saved = self.incident_repo.save(incident)
        
        # Publicar evento INCIDENT_CREATED
        self.event_bus.publish(IncidentCreatedEvent(incident=saved))
        
        return self._to_response(saved, tasks=[])
    
    def _to_response(self, incident: Incident, tasks: List = None) -> IncidentResponseDTO:
        return IncidentResponseDTO(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            severity=incident.severity.value,
            status=incident.status.value,
            created_by=incident.created_by,
            assigned_to=incident.assigned_to,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
            tasks=tasks or []
        )


class GetIncidentsUseCase:
    """Caso de uso: Obtener incidentes según el rol del usuario"""
    
    def __init__(self, incident_repo: IncidentRepository):
        self.incident_repo = incident_repo
    
    def execute(self, user_id: str, user_role: str, skip: int = 0, limit: int = 100) -> List[IncidentResponseDTO]:
        if user_role == "ADMIN":
            incidents = self.incident_repo.get_all(skip, limit)
        elif user_role == "SUPERVISOR":
            incidents = self.incident_repo.get_all(skip, limit)
        else:  # OPERATOR
            # Ver incidentes creados por él o asignados a él
            created = self.incident_repo.get_by_created_by(user_id)
            assigned = self.incident_repo.get_by_assigned_to(user_id)
            # Unir y eliminar duplicados
            incidents = list({inc.id: inc for inc in created + assigned}.values())
        
        return [self._to_response(inc) for inc in incidents]
    
    def _to_response(self, incident: Incident) -> IncidentResponseDTO:
        return IncidentResponseDTO(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            severity=incident.severity.value,
            status=incident.status.value,
            created_by=incident.created_by,
            assigned_to=incident.assigned_to,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
            tasks=[]
        )


class GetIncidentByIdUseCase:
    """Caso de uso: Obtener un incidente por ID con sus tareas"""
    
    def __init__(self, incident_repo: IncidentRepository, task_repo: TaskRepository):
        self.incident_repo = incident_repo
        self.task_repo = task_repo
    
    def execute(self, incident_id: str) -> IncidentResponseDTO:
        incident = self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise NotFoundError(f"Incidente {incident_id} no encontrado")
        
        tasks = self.task_repo.get_by_incident_id(incident_id)
        
        return IncidentResponseDTO(
            id=incident.id,
            title=incident.title,
            description=incident.description,
            severity=incident.severity.value,
            status=incident.status.value,
            created_by=incident.created_by,
            assigned_to=incident.assigned_to,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
            tasks=[self._task_to_response(task) for task in tasks]
        )
    
    def _task_to_response(self, task: Task) -> TaskResponseDTO:
        return TaskResponseDTO(
            id=task.id,
            incident_id=task.incident_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            assigned_to=task.assigned_to,
            created_at=task.created_at,
            updated_at=task.updated_at
        )


class AssignIncidentUseCase:
    """Caso de uso: Asignar un incidente (solo ADMIN/SUPERVISOR)"""
    
    def __init__(self, incident_repo: IncidentRepository, event_bus: EventBus):
        self.incident_repo = incident_repo
        self.event_bus = event_bus
    
    def execute(self, incident_id: str, dto: AssignIncidentDTO) -> IncidentResponseDTO:
        incident = self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise NotFoundError(f"Incidente {incident_id} no encontrado")
        
        incident.assign_to(dto.assigned_to)
        saved = self.incident_repo.save(incident)
        
        # Publicar evento INCIDENT_ASSIGNED
        self.event_bus.publish(IncidentAssignedEvent(incident=saved, assigned_to=dto.assigned_to))
        
        return IncidentResponseDTO(
            id=saved.id,
            title=saved.title,
            description=saved.description,
            severity=saved.severity.value,
            status=saved.status.value,
            created_by=saved.created_by,
            assigned_to=saved.assigned_to,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
            tasks=[]
        )


class ChangeIncidentStatusUseCase:
    """Caso de uso: Cambiar estado de un incidente"""
    
    def __init__(self, incident_repo: IncidentRepository, event_bus: EventBus):
        self.incident_repo = incident_repo
        self.event_bus = event_bus
    
    def execute(self, incident_id: str, dto: ChangeStatusDTO) -> IncidentResponseDTO:
        incident = self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise NotFoundError(f"Incidente {incident_id} no encontrado")
        
        new_status = IncidentStatus(dto.status)
        
        # Capturar el estado anterior
        old_status = incident.status
        
        # Usar los métodos específicos del State Pattern
        if new_status == IncidentStatus.ASSIGNED:
            # Asignar requiere user_id, por eso usamos AssignIncidentUseCase aparte
            raise ValidationError("Use el endpoint /assign para asignar incidentes")
        elif new_status == IncidentStatus.IN_PROGRESS:
            incident.start_progress()
        elif new_status == IncidentStatus.RESOLVED:
            incident.resolve()
        elif new_status == IncidentStatus.CLOSED:
            incident.close()
        elif new_status == IncidentStatus.OPEN:
            incident.reopen()
        
        saved = self.incident_repo.save(incident)
        
        # Publicar evento INCIDENT_STATUS_CHANGED
        self.event_bus.publish(IncidentStatusChangedEvent(
            incident=saved,
            old_status=old_status.value,
            new_status=saved.status.value
        ))
        
        return IncidentResponseDTO(
            id=saved.id,
            title=saved.title,
            description=saved.description,
            severity=saved.severity.value,
            status=saved.status.value,
            created_by=saved.created_by,
            assigned_to=saved.assigned_to,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
            tasks=[]
        )


# ============================================
# Casos de uso - Tareas
# ============================================

class CreateTaskUseCase:
    """Caso de uso: Crear una tarea asociada a un incidente"""
    
    def __init__(self, task_repo: TaskRepository, incident_repo: IncidentRepository, event_bus: EventBus):
        self.task_repo = task_repo
        self.incident_repo = incident_repo
        self.event_bus = event_bus
    
    def execute(self, dto: CreateTaskDTO) -> TaskResponseDTO:
        # Verificar que el incidente existe
        incident = self.incident_repo.get_by_id(dto.incident_id)
        if not incident:
            raise NotFoundError(f"Incidente {dto.incident_id} no encontrado")
        
        # Usar Factory para crear tarea con validaciones
        task = TaskFactory.create(
            incident_id=dto.incident_id,
            title=dto.title,
            description=dto.description,
            assigned_to=dto.assigned_to
        )
        
        saved = self.task_repo.save(task)
        
        # Publicar evento TASK_CREATED
        self.event_bus.publish(TaskCreatedEvent(task=saved))
        
        return TaskResponseDTO(
            id=saved.id,
            incident_id=saved.incident_id,
            title=saved.title,
            description=saved.description,
            status=saved.status.value,
            assigned_to=saved.assigned_to,
            created_at=saved.created_at,
            updated_at=saved.updated_at
        )


class GetTasksUseCase:
    """Caso de uso: Obtener tareas según el rol del usuario"""
    
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo
    
    def execute(self, user_id: str, user_role: str) -> List[TaskResponseDTO]:
        if user_role == "ADMIN":
            tasks = self.task_repo.get_all()
        elif user_role == "SUPERVISOR":
            tasks = self.task_repo.get_all()
        else:  # OPERATOR
            tasks = self.task_repo.get_by_assigned_to(user_id)
        
        return [self._to_response(task) for task in tasks]
    
    def _to_response(self, task: Task) -> TaskResponseDTO:
        return TaskResponseDTO(
            id=task.id,
            incident_id=task.incident_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            assigned_to=task.assigned_to,
            created_at=task.created_at,
            updated_at=task.updated_at
        )


class ChangeTaskStatusUseCase:
    """Caso de uso: Cambiar estado de una tarea"""
    
    def __init__(self, task_repo: TaskRepository, event_bus: EventBus):
        self.task_repo = task_repo
        self.event_bus = event_bus
    
    def execute(self, task_id: str, dto: ChangeStatusDTO) -> TaskResponseDTO:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError(f"Tarea {task_id} no encontrada")
        
        new_status = TaskStatus(dto.status)
        
        if new_status == TaskStatus.IN_PROGRESS:
            task.mark_in_progress()
        elif new_status == TaskStatus.DONE:
            task.mark_done()
        elif new_status == TaskStatus.OPEN:
            # Si quieren permitir resetear a OPEN
            pass
        
        saved = self.task_repo.save(task)
        
        # Publicar evento TASK_DONE si la tarea fue completada
        if saved.status == TaskStatus.DONE:
            self.event_bus.publish(TaskDoneEvent(task=saved))
        
        return TaskResponseDTO(
            id=saved.id,
            incident_id=saved.incident_id,
            title=saved.title,
            description=saved.description,
            status=saved.status.value,
            assigned_to=saved.assigned_to,
            created_at=saved.created_at,
            updated_at=saved.updated_at
        )


# ============================================
# Casos de uso - Notificaciones
# ============================================

class GetNotificationsUseCase:
    """Caso de uso: Obtener notificaciones según el rol del usuario"""
    
    def __init__(self, notification_repo):
        self.notification_repo = notification_repo
    
    def execute(self, user_id: str, user_role: str, unread_only: bool = False) -> List[NotificationResponseDTO]:
        """
        Obtiene notificaciones:
        - ADMIN: todas las notificaciones
        - SUPERVISOR: sus notificaciones
        - OPERATOR: sus notificaciones
        """
        if user_role == "ADMIN":
            notifications = self.notification_repo.find_all()
        else:
            # SUPERVISOR y OPERATOR ven solo sus notificaciones
            notifications = self.notification_repo.find_by_recipient(user_id)
        
        # Filtrar por no leídas si se solicita
        if unread_only:
            notifications = [n for n in notifications if n.status != NotificationStatus.READ]
        
        return [self._to_response(notif) for notif in notifications]
    
    def _to_response(self, notification: Notification) -> NotificationResponseDTO:
        return NotificationResponseDTO(
            id=notification.id,
            recipient=notification.recipient,
            channel=notification.channel,
            message=notification.message,
            event_type=notification.event_type,
            status=notification.status.value,
            created_at=notification.created_at,
            read_at=notification.read_at
        )


class MarkNotificationAsReadUseCase:
    """Caso de uso: Marcar una notificación como leída"""
    
    def __init__(self, notification_repo):
        self.notification_repo = notification_repo
    
    def execute(self, notification_id: str) -> None:
        """Marca una notificación como leída"""
        self.notification_repo.mark_as_read(notification_id)