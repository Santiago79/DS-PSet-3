from __future__ import annotations
from typing import Protocol, Optional, List
from domain.entities import User, Incident, Task


class UserRepository(Protocol):
    """Interfaz para el repositorio de Usuarios"""
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por su ID"""
        ...
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su email"""
        ...
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtiene todos los usuarios con paginación"""
        ...


class IncidentRepository(Protocol):
    """Interfaz para el repositorio de Incidentes"""
    
    def save(self, incident: Incident) -> Incident:
        """Guarda un incidente (crea o actualiza)"""
        ...
    
    def get_by_id(self, incident_id: str) -> Optional[Incident]:
        """Obtiene un incidente por su ID"""
        ...
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Incident]:
        """Obtiene todos los incidentes con paginación"""
        ...
    
    def get_by_created_by(self, user_id: str) -> List[Incident]:
        """Obtiene incidentes creados por un usuario"""
        ...
    
    def get_by_assigned_to(self, user_id: str) -> List[Incident]:
        """Obtiene incidentes asignados a un usuario"""
        ...


class TaskRepository(Protocol):
    """Interfaz para el repositorio de Tareas"""
    
    def save(self, task: Task) -> Task:
        """Guarda una tarea (crea o actualiza)"""
        ...
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Obtiene una tarea por su ID"""
        ...
    
    def get_by_incident_id(self, incident_id: str) -> List[Task]:
        """Obtiene todas las tareas de un incidente"""
        ...
    
    def get_by_assigned_to(self, user_id: str) -> List[Task]:
        """Obtiene tareas asignadas a un usuario"""
        ...