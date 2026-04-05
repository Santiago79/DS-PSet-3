from fastapi import FastAPI
from infrastructure import models
from infrastructure.database import engine, Base
from infrastructure.event_bus_impl import InMemoryEventBus
from infrastructure.observers import NotificationObserver, LoggingObserver
from infrastructure.postgres import PostgresNotificationRepo
from sqlalchemy.orm import Session
from infrastructure.database import SessionLocal
from api import endpoints

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpsCenter API")

# Montar routers
app.include_router(endpoints.router)


# ============================================
# Inicialización de Observers
# ============================================

def initialize_observers(event_bus: InMemoryEventBus):
    """
    Suscribe los observadores al EventBus durante la inicialización.
    Se invoca una sola vez al arrancar la aplicación.
    """
    # Inicializar repositorio para NotificationObserver
    db: Session = SessionLocal()
    notification_repo = PostgresNotificationRepo(db)
    
    # Crear y suscribir NotificationObserver
    notification_observer = NotificationObserver(notification_repo)
    event_bus.subscribe(notification_observer)
    
    # Crear y suscribir LoggingObserver
    logging_observer = LoggingObserver()
    event_bus.subscribe(logging_observer)


@app.on_event("startup")
def startup_event():
    """Se ejecuta al iniciar la aplicación"""
    # Importar aquí para evitar circular imports
    from api.dependencies import _event_bus
    initialize_observers(_event_bus)


@app.get("/")
def read_root():
    return {"message": "API de OpsCenter funcionando correctamente"}