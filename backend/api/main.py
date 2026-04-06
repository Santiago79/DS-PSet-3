from fastapi import FastAPI
from datetime import datetime
import uuid

from infrastructure import models
from infrastructure.database import engine, Base, SessionLocal
from infrastructure.Observers import NotificationObserver, LoggingObserver
from api.dependencies import get_event_bus
from infrastructure.auth_provider import AuthProvider
from domain.enums import Role
from api.endpoints import router as api_router
from infrastructure.postgres import PostgresNotificationRepo

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpsCenter API")
app.include_router(api_router)


def create_default_users():
    """Crea usuarios por defecto si la base está vacía."""
    usuarios = [
        ("admin@opscenter.com", "Admin User", "admin123", Role.ADMIN.value),
        ("supervisor@opscenter.com", "Supervisor User", "supervisor123", Role.SUPERVISOR.value),
        ("operator@opscenter.com", "Operator User", "operator123", Role.OPERATOR.value),
    ]
    
    db = SessionLocal()
    try:
        for email, name, password, role in usuarios:
            user = db.query(models.UserORM).filter(models.UserORM.email == email).first()
            if not user:
                nuevo = models.UserORM(
                    id=str(uuid.uuid4()),
                    name=name,
                    email=email,
                    hashed_password=AuthProvider.get_password_hash(password),
                    role=role
                )
                db.add(nuevo)
                print(f"--- Usuario creado: {email} ({role}) ---")
        db.commit()
        print("--- Todos los usuarios por defecto creados/verificados ---")
    except Exception as e:
        print(f"--- Error al crear usuarios: {e} ---")
        db.rollback()
    finally:
        db.close()


def initialize_observers() -> None:
    """Suscribe los observers al EventBus."""
    event_bus = get_event_bus()
    
    logging_observer = LoggingObserver()
    event_bus.subscribe(logging_observer)
    
    db = SessionLocal()
    notification_repo = PostgresNotificationRepo(db)
    notification_observer = NotificationObserver(notification_repo)
    event_bus.subscribe(notification_observer)


@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar el servidor."""
    create_default_users()  # ← Crear usuarios por defecto
    initialize_observers()


@app.get("/")
def read_root():
    return {"message": "API de OpsCenter funcionando correctamente"}