from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from infrastructure.database import get_db
from infrastructure.models import UserORM
from infrastructure.auth_provider import SECRET_KEY, ALGORITHM
from domain.entities import User
from domain.enums import Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Consultamos la infraestructura (ORM)
    user_orm = db.query(UserORM).filter(UserORM.email == email).first()
    if user_orm is None:
        raise credentials_exception
        
    # Mapeamos a la Entidad de Dominio (Arquitectura Hexagonal)
    return User(
        id=user_orm.id,
        name=user_orm.name,
        email=user_orm.email,
        hashed_password=user_orm.hashed_password,
        role=Role(user_orm.role)
    )