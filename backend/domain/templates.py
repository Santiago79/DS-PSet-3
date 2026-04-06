"""
Implementación del patrón Template Method para construir mensajes de notificación.
La clase base define la estructura del mensaje y las subclases concretas definen
el formato específico para cada canal.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from backend.domain.events import (
    Evento,
    IncidentCreatedEvent,
    IncidentAssignedEvent,
    IncidentStatusChangedEvent,
    TaskCreatedEvent,
    TaskDoneEvent,
)

if TYPE_CHECKING:
    pass


# ============================================
# Template Method Base
# ============================================

class NotificationMessageBuilder(ABC):
    """
    Clase base abstracta que implementa el patrón Template Method.
    Define la estructura del mensaje de notificación y deja que las
    subclases implementen los detalles específicos de formato.
    """
    
    def build(self, evento: Evento) -> str:
        """
        Método template que define el algoritmo para construir un mensaje.
        Sigue el patrón Template Method.
        
        Args:
            evento: El evento de dominio que genera la notificación
        
        Returns:
            str: El mensaje construido con greeting + body + farewell
        """
        greeting = self.greeting()
        body = self.body(evento)
        farewell = self.farewell()
        
        return self._compose_message(greeting, body, farewell)
    
    @abstractmethod
    def greeting(self) -> str:
        """Retorna el saludo inicial del mensaje"""
        pass
    
    @abstractmethod
    def body(self, evento: Evento) -> str:
        """
        Retorna el cuerpo del mensaje basado en el tipo de evento.
        Este método es el que varía según el tipo de evento.
        
        Args:
            evento: El evento de dominio
        
        Returns:
            str: El cuerpo del mensaje formateado
        """
        pass
    
    @abstractmethod
    def farewell(self) -> str:
        """Retorna la despedida al final del mensaje"""
        pass
    
    @abstractmethod
    def _compose_message(self, greeting: str, body: str, farewell: str) -> str:
        """
        Compone los tres componentes en el formato final del mensaje.
        Este método es abstracto porque cada canal puede tener
        un formato de composición diferente.
        
        Args:
            greeting: Saludo inicial
            body: Cuerpo del mensaje
            farewell: Despedida final
        
        Returns:
            str: Mensaje completo formateado
        """
        pass


# ============================================
# Email Message Builder
# ============================================

class EmailMessageBuilder(NotificationMessageBuilder):
    """
    Builder concreto para construir mensajes de email.
    Genera mensajes en formato formal con estructura de email profesional.
    """
    
    def greeting(self) -> str:
        """Saludo formal para email"""
        return "Estimado Usuario,\n"
    
    def body(self, evento: Evento) -> str:
        """
        Construye el cuerpo del email según el tipo de evento.
        
        Args:
            evento: El evento de dominio
        
        Returns:
            str: Cuerpo del email formateado
        """
        if isinstance(evento, IncidentCreatedEvent):
            return self._incident_created_body(evento)
        
        elif isinstance(evento, IncidentAssignedEvent):
            return self._incident_assigned_body(evento)
        
        elif isinstance(evento, IncidentStatusChangedEvent):
            return self._incident_status_changed_body(evento)
        
        elif isinstance(evento, TaskCreatedEvent):
            return self._task_created_body(evento)
        
        elif isinstance(evento, TaskDoneEvent):
            return self._task_done_body(evento)
        
        else:
            return "Se ha generado un evento en el sistema OpsCenter."
    
    def farewell(self) -> str:
        """Despedida formal para email"""
        return "\n\nAtentamente,\nEquipo OpsCenter"
    
    def _compose_message(self, greeting: str, body: str, farewell: str) -> str:
        """Compone los componentes en un formato de email profesional"""
        return f"{greeting}\n{body}{farewell}"
    
    def _incident_created_body(self, evento: IncidentCreatedEvent) -> str:
        """Cuerpo para evento de incidente creado"""
        incident = evento.incident
        return (
            f"Se ha creado un nuevo incidente en el sistema:\n\n"
            f"Título: {incident.title}\n"
            f"Descripción: {incident.description}\n"
            f"Severidad: {incident.severity.value}\n"
            f"Estado: {incident.status.value}\n"
            f"Creado por: {incident.created_by}\n\n"
            f"Por favor, revise la plataforma para más detalles."
        )
    
    def _incident_assigned_body(self, evento: IncidentAssignedEvent) -> str:
        """Cuerpo para evento de incidente asignado"""
        incident = evento.incident
        return (
            f"Ha sido asignado un nuevo incidente:\n\n"
            f"Título: {incident.title}\n"
            f"Descripción: {incident.description}\n"
            f"Severidad: {incident.severity.value}\n"
            f"Asignado a: {evento.assigned_to}\n\n"
            f"Se requiere su atención inmediata."
        )
    
    def _incident_status_changed_body(self, evento: IncidentStatusChangedEvent) -> str:
        """Cuerpo para evento de cambio de estado de incidente"""
        incident = evento.incident
        return (
            f"El estado de un incidente ha cambiado:\n\n"
            f"Título: {incident.title}\n"
            f"Estado anterior: {evento.old_status}\n"
            f"Estado nuevo: {evento.new_status}\n"
            f"Asignado a: {incident.assigned_to or 'Sin asignar'}\n\n"
            f"Visite la plataforma para más información."
        )
    
    def _task_created_body(self, evento: TaskCreatedEvent) -> str:
        """Cuerpo para evento de tarea creada"""
        task = evento.task
        return (
            f"Se ha creado una nueva tarea:\n\n"
            f"Título: {task.title}\n"
            f"Descripción: {task.description}\n"
            f"Estado: {task.status.value}\n"
            f"Asignado a: {task.assigned_to or 'Sin asignar'}\n\n"
            f"Ingrese a la plataforma para revisar los detalles."
        )
    
    def _task_done_body(self, evento: TaskDoneEvent) -> str:
        """Cuerpo para evento de tarea completada"""
        task = evento.task
        return (
            f"Una tarea ha sido completada:\n\n"
            f"Título: {task.title}\n"
            f"Estado: {task.status.value}\n"
            f"Completada por: {task.assigned_to or 'Sistema'}\n\n"
            f"Gracias por tu contribución."
        )


# ============================================
# In-App Message Builder
# ============================================

class InAppMessageBuilder(NotificationMessageBuilder):
    """
    Builder concreto para construir mensajes in-app.
    Genera mensajes cortos y concisos para mostrar en la interfaz de usuario.
    """
    
    def greeting(self) -> str:
        """Saludo breve para in-app"""
        return ""  # Sin saludo para mensajes in-app
    
    def body(self, evento: Evento) -> str:
        """
        Construye el cuerpo del mensaje in-app según el tipo de evento.
        Los mensajes son cortos y directos.
        
        Args:
            evento: El evento de dominio
        
        Returns:
            str: Cuerpo del mensaje formateado
        """
        if isinstance(evento, IncidentCreatedEvent):
            return self._incident_created_body(evento)
        
        elif isinstance(evento, IncidentAssignedEvent):
            return self._incident_assigned_body(evento)
        
        elif isinstance(evento, IncidentStatusChangedEvent):
            return self._incident_status_changed_body(evento)
        
        elif isinstance(evento, TaskCreatedEvent):
            return self._task_created_body(evento)
        
        elif isinstance(evento, TaskDoneEvent):
            return self._task_done_body(evento)
        
        else:
            return "Nuevo evento en el sistema"
    
    def farewell(self) -> str:
        """Sin despedida para in-app"""
        return ""
    
    def _compose_message(self, greeting: str, body: str, farewell: str) -> str:
        """
        Compone los componentes para in-app.
        Simplemente retorna el cuerpo ya que no hay greeting ni farewell.
        """
        return body
    
    def _incident_created_body(self, evento: IncidentCreatedEvent) -> str:
        """Mensaje corto para incidente creado"""
        incident = evento.incident
        return f"🆕 Incidente creado: {incident.title} ({incident.severity.value})"
    
    def _incident_assigned_body(self, evento: IncidentAssignedEvent) -> str:
        """Mensaje corto para incidente asignado"""
        incident = evento.incident
        return f"📌 Te han asignado: {incident.title}"
    
    def _incident_status_changed_body(self, evento: IncidentStatusChangedEvent) -> str:
        """Mensaje corto para cambio de estado"""
        incident = evento.incident
        return f"🔄 {incident.title}: {evento.old_status} → {evento.new_status}"
    
    def _task_created_body(self, evento: TaskCreatedEvent) -> str:
        """Mensaje corto para tarea creada"""
        task = evento.task
        return f"✓ Nueva tarea: {task.title}"
    
    def _task_done_body(self, evento: TaskDoneEvent) -> str:
        """Mensaje corto para tarea completada"""
        task = evento.task
        return f"✔️ Tarea completada: {task.title}"
