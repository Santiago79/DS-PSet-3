"""
Factory Pattern para la creación centralizada de Incidentes y Tareas.
Centraliza validaciones de negocio y asegura que las entidades se creen en estado válido.
"""

from uuid import uuid4
from datetime import datetime
from typing import Optional

from domain.entities import Incident, Task
from domain.enums import Severity, IncidentStatus, TaskStatus
from domain.exceptions import ValidationError


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