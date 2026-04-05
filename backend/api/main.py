from fastapi import FastAPI
from backend.infrastructure import models
from backend.infrastructure.database import engine, Base, SessionLocal
from backend.infrastructure.Observers import NotificationObserver, LoggingObserver
from backend.api.dependencies import get_event_bus

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpsCenter API")


def initialize_observers() -> None:
    """
    Suscribe los observers al EventBus en la inicialización de la aplicación.
    Esto asegura que todos los eventos publicados disparen las acciones apropiadas.
    """
    event_bus = get_event_bus()
    
    # Suscribir LoggingObserver (sin dependencias)
    logging_observer = LoggingObserver()
    event_bus.subscribe(logging_observer)
    
    # Inicializar repositorio para NotificationObserver
    db = SessionLocal()
    from backend.infrastructure.postgres import PostgresNotificationRepo
    notification_repo = PostgresNotificationRepo(db)
    
    # Crear y suscribir NotificationObserver
    notification_observer = NotificationObserver(notification_repo)
    event_bus.subscribe(notification_observer)


@app.on_event("startup")
async def startup_event() -> None:
    """Evento de startup de FastAPI - inicializa los observers"""
    initialize_observers()


@app.get("/")
def read_root():
    return {"message": "API de OpsCenter funcionando correctamente"}