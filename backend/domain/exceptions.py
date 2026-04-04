class OpsError(Exception):
    """Excepción base para todos los errores"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ValidationError(OpsError):
    """Error cuando los datos de entrada no cumplen las reglas básicas"""
    pass

class DomainError(Exception):
    """Excepción base para errores del dominio"""
    pass

class InvalidStateTransitionError(DomainError):
    """Error cuando una transición de estado no es válida"""
    pass
class NotFoundError(DomainError):
    """Error cuando una entidad no existe en el repositorio"""
    pass


class UnauthorizedError(DomainError):
    """Error cuando un usuario no tiene permisos para una acción"""
    pass