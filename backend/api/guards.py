from fastapi import Depends, HTTPException, status
from domain.entities import User
from domain.enums import Role
from api.dependencies import get_current_user

def require_role(required_role: Role):
    """
    Dependencia de FastAPI que verifica si el usuario autenticado tiene el rol necesario.
    Implementa una jerarquía: ADMIN tiene acceso a todo, SUPERVISOR a lo suyo y lo de OPERATOR.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Definimos la jerarquía de permisos
        hierarchy = {
            Role.ADMIN: [Role.ADMIN, Role.SUPERVISOR, Role.OPERATOR],
            Role.SUPERVISOR: [Role.SUPERVISOR, Role.OPERATOR],
            Role.OPERATOR: [Role.OPERATOR]
        }
        
        # Obtenemos los roles permitidos para el nivel requerido
        allowed_roles = hierarchy.get(required_role, [])
        
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere el nivel de acceso: {required_role.value}"
            )
        
        return current_user

    return role_checker