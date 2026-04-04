from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from infrastructure.database import get_db
from infrastructure.models import UserORM
from infrastructure.auth_provider import AuthProvider
from domain.entities import User
from domain.enums import Role
from api.dependencies import get_current_user
from api.guards import require_role

# Importamos los nuevos DTOs de Application
from application.dtos import UserResponseDTO, LoginRequestDTO, LoginResponseDTO

router = APIRouter()

@router.post("/login", response_model=LoginResponseDTO, summary="Autenticar usuario")
def login(body: LoginRequestDTO, db: Session = Depends(get_db)):
    """
    Usa el DTO para recibir email/password y retorna el token.
    """
    user_orm = db.query(UserORM).filter(UserORM.email == body.email).first()
    
    if not user_orm or not AuthProvider.verify_password(body.password, user_orm.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    access_token = AuthProvider.create_access_token(
        data={"sub": user_orm.email, "role": user_orm.role}
    )
    
    return LoginResponseDTO(access_token=access_token)

@router.get("/me", response_model=UserResponseDTO, summary="Mi perfil")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Mapea la entidad de dominio al DTO de respuesta.
    """
    return UserResponseDTO(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value
    )