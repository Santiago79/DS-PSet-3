class OpsError(Exception):
    """Excepción base para todos los errores"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ValidationError(OpsError):
    """Error cuando los datos de entrada no cumplen las reglas básicas"""
    pass