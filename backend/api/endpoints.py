from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from infrastructure.models import UserORM
from infrastructure.auth_provider import AuthProvider
from domain.entities import User
from domain.enums import Role
from api.dependencies import get_current_user
from api.guards import require_role

router = APIRouter()

@router.post("/login", summary="Autenticar usuario")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica al usuario y devuelve un token JWT.
    **Nota:** Enviar el email en el campo `username`.
    """
    user_orm = db.query(UserORM).filter(UserORM.email == form_data.username).first()
    if not user_orm or not AuthProvider.verify_password(form_data.password, user_orm.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    
    access_token = AuthProvider.create_access_token(
        data={"sub": user_orm.email, "role": user_orm.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint accesible para cualquier usuario autenticado (OPERATOR o superior)
@router.get("/me", dependencies=[Depends(require_role(Role.OPERATOR))], summary="Obtener perfil de usuario")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retorna los datos del usuario actualmente autenticado.
    Requiere rol mínimo: OPERATOR.
    """
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value
    }