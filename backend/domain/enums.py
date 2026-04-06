from enum import Enum

class Role(str, Enum):
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    OPERATOR = "OPERATOR"
    
class Severity(str, Enum):
    """Niveles de severidad para incidentes"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    """Estados del ciclo de vida de un incidente"""
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class TaskStatus(str, Enum):
    """Estados del ciclo de vida de una tarea"""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class NotificationStatus(str, Enum):
    """Estados solicitados en el PSet [cite: 98]"""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    READ = "READ"

class NotificationChannel(str, Enum):
    """Canales sugeridos [cite: 95]"""
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"