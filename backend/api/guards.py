from fastapi import HTTPException, status, Depends
from domain.entities import User
from domain.enums import Role
from api.dependencies import get_current_user

class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            roles_str = [r.value for r in self.allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de estos roles: {roles_str}"
            )
        return user

# Definición de dependencias
is_admin = RoleChecker([Role.ADMIN])
is_supervisor_or_admin = RoleChecker([Role.ADMIN, Role.SUPERVISOR])
is_any_role = RoleChecker([Role.ADMIN, Role.SUPERVISOR, Role.OPERATOR])