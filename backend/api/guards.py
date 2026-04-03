from fastapi import HTTPException, status, Depends
from infrastructure.models import UserORM
from api.dependencies import get_current_user

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserORM = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para esta acción"
            )
        return user

# Atajos para usar en los endpoints
is_admin = RoleChecker(["ADMIN"])
is_supervisor_or_admin = RoleChecker(["ADMIN", "SUPERVISOR"])