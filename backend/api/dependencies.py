from backend.application.use_cases import AssignIncidentUseCase, ChangeIncidentStatusUseCase, ChangeTaskStatusUseCase, CreateIncidentUseCase, CreateTaskUseCase, GetIncidentByIdUseCase, GetIncidentsUseCase, GetTasksUseCase
from backend.infrastructure.postgres import PostgresIncidentRepo, PostgresTaskRepo
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
def get_incident_repo(db: Session = Depends(get_db)) -> PostgresIncidentRepo:
    """Dependencia para obtener el repositorio de Incidentes"""
    return PostgresIncidentRepo(db)


def get_task_repo(db: Session = Depends(get_db)) -> PostgresTaskRepo:
    """Dependencia para obtener el repositorio de Tareas"""
    return PostgresTaskRepo(db)
def get_create_incident_uc(
    incident_repo: PostgresIncidentRepo = Depends(get_incident_repo),
) -> CreateIncidentUseCase:
    return CreateIncidentUseCase(incident_repo)


def get_get_incidents_uc(
    incident_repo: PostgresIncidentRepo = Depends(get_incident_repo),
) -> GetIncidentsUseCase:
    return GetIncidentsUseCase(incident_repo)


def get_get_incident_by_id_uc(
    incident_repo: PostgresIncidentRepo = Depends(get_incident_repo),
    task_repo: PostgresTaskRepo = Depends(get_task_repo),
) -> GetIncidentByIdUseCase:
    return GetIncidentByIdUseCase(incident_repo, task_repo)


def get_assign_incident_uc(
    incident_repo: PostgresIncidentRepo = Depends(get_incident_repo),
) -> AssignIncidentUseCase:
    return AssignIncidentUseCase(incident_repo)

def get_change_incident_status_uc(
    incident_repo: PostgresIncidentRepo = Depends(get_incident_repo),
) -> ChangeIncidentStatusUseCase:
    return ChangeIncidentStatusUseCase(incident_repo)
def get_create_task_uc(
    task_repo: PostgresTaskRepo = Depends(get_task_repo),
    incident_repo: PostgresIncidentRepo = Depends(get_incident_repo),
) -> CreateTaskUseCase:
    return CreateTaskUseCase(task_repo, incident_repo)


def get_get_tasks_uc(
    task_repo: PostgresTaskRepo = Depends(get_task_repo),
) -> GetTasksUseCase:
    return GetTasksUseCase(task_repo)


def get_change_task_status_uc(
    task_repo: PostgresTaskRepo = Depends(get_task_repo),
) -> ChangeTaskStatusUseCase:
    return ChangeTaskStatusUseCase(task_repo)