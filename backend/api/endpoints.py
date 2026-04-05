from typing import List

from backend.application.use_cases import (
    AssignIncidentUseCase,
    ChangeIncidentStatusUseCase,
    ChangeTaskStatusUseCase,
    CreateIncidentUseCase,
    CreateTaskUseCase,
    GetIncidentByIdUseCase,
    GetIncidentsUseCase,
    GetTasksUseCase,
)
from backend.domain.exceptions import InvalidStateTransitionError, NotFoundError, ValidationError
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.infrastructure.database import get_db
from backend.infrastructure.models import UserORM
from backend.infrastructure.auth_provider import AuthProvider
from backend.domain.entities import User
from backend.domain.enums import Role
from backend.api.dependencies import (
    get_assign_incident_uc,
    get_change_incident_status_uc,
    get_change_task_status_uc,
    get_create_incident_uc,
    get_create_task_uc,
    get_current_user,
    get_get_incident_by_id_uc,
    get_get_incidents_uc,
    get_get_tasks_uc,
)
from backend.api.guards import require_role
from backend.application.dtos import (
    AssignIncidentDTO,
    ChangeStatusDTO,
    CreateIncidentDTO,
    CreateTaskDTO,
    IncidentResponseDTO,
    TaskResponseDTO,
    UserResponseDTO,
    LoginRequestDTO,
    LoginResponseDTO,
)

router = APIRouter()
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



@router.post(
    "/incidents",
    response_model=IncidentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un incidente",
    dependencies=[Depends(require_role(Role.OPERATOR))]
)
def create_incident(
    dto: CreateIncidentDTO,
    current_user: User = Depends(get_current_user),
    use_case: CreateIncidentUseCase = Depends(get_create_incident_uc),
):
    """
    Crea un nuevo incidente.
    
    - **OPERATOR, SUPERVISOR, ADMIN** pueden crear incidentes.
    - El incidente se crea con estado OPEN.
    """
    try:
        result = use_case.execute(dto, current_user.id)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/incidents",
    response_model=List[IncidentResponseDTO],
    summary="Listar incidentes"
)
def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    use_case: GetIncidentsUseCase = Depends(get_get_incidents_uc),
):
    """
    Lista incidentes según el rol del usuario:
    - **ADMIN**: todos los incidentes
    - **SUPERVISOR**: todos los incidentes
    - **OPERATOR**: solo incidentes creados o asignados a él
    """
    result = use_case.execute(current_user.id, current_user.role.value, skip, limit)
    return result


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponseDTO,
    summary="Obtener detalle de un incidente"
)
def get_incident_by_id(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    use_case: GetIncidentByIdUseCase = Depends(get_get_incident_by_id_uc),
):
    """
    Obtiene el detalle de un incidente incluyendo sus tareas asociadas.
    """
    try:
        result = use_case.execute(incident_id)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    "/incidents/{incident_id}/assign",
    response_model=IncidentResponseDTO,
    summary="Asignar un incidente",
    dependencies=[Depends(require_role(Role.SUPERVISOR))]
)
def assign_incident(
    incident_id: str,
    dto: AssignIncidentDTO,
    use_case: AssignIncidentUseCase = Depends(get_assign_incident_uc),
):
    """
    Asigna un incidente a un usuario.
    - **SUPERVISOR y ADMIN** pueden asignar incidentes.
    """
    try:
        result = use_case.execute(incident_id, dto)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/incidents/{incident_id}/status",
    response_model=IncidentResponseDTO,
    summary="Cambiar estado de un incidente",
    dependencies=[Depends(require_role(Role.SUPERVISOR))]
)
def change_incident_status(
    incident_id: str,
    dto: ChangeStatusDTO,
    use_case: ChangeIncidentStatusUseCase = Depends(get_change_incident_status_uc),
):
    """
    Cambia el estado de un incidente.
    - **SUPERVISOR y ADMIN** pueden cambiar estados.
    - Estados posibles: OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED
    """
    try:
        result = use_case.execute(incident_id, dto)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ValidationError, InvalidStateTransitionError) as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post(
    "/tasks",
    response_model=TaskResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una tarea",
    dependencies=[Depends(require_role(Role.SUPERVISOR))]
)
def create_task(
    dto: CreateTaskDTO,
    use_case: CreateTaskUseCase = Depends(get_create_task_uc),
):
    """
    Crea una tarea asociada a un incidente.
    - **SUPERVISOR y ADMIN** pueden crear tareas.
    """
    try:
        result = use_case.execute(dto)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/tasks",
    response_model=List[TaskResponseDTO],
    summary="Listar tareas"
)
def get_tasks(
    current_user: User = Depends(get_current_user),
    use_case: GetTasksUseCase = Depends(get_get_tasks_uc),
):
    """
    Lista tareas según el rol del usuario:
    - **ADMIN**: todas las tareas
    - **SUPERVISOR**: todas las tareas
    - **OPERATOR**: solo tareas asignadas a él
    """
    result = use_case.execute(current_user.id, current_user.role.value)
    return result


@router.patch(
    "/tasks/{task_id}/status",
    response_model=TaskResponseDTO,
    summary="Cambiar estado de una tarea"
)
def change_task_status(
    task_id: str,
    dto: ChangeStatusDTO,
    current_user: User = Depends(get_current_user),
    use_case: ChangeTaskStatusUseCase = Depends(get_change_task_status_uc),
):
    """
    Cambia el estado de una tarea.
    - **OPERATOR** puede cambiar estado de tareas asignadas a él.
    - **SUPERVISOR y ADMIN** pueden cambiar cualquier tarea.
    - Estados posibles: OPEN, IN_PROGRESS, DONE
    """
    try:
        result = use_case.execute(task_id, dto)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))