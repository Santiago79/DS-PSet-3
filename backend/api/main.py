from fastapi import FastAPI
from infrastructure import models
from infrastructure.database import engine, Base, SessionLocal
from infrastructure.Observers import NotificationObserver, LoggingObserver
from api.dependencies import get_event_bus
from api.endpoints import router as api_router
from datetime import datetime

# Importaciones de infraestructura y base de datos (sin el prefijo backend.)
from infrastructure import models
from infrastructure.database import engine, Base, SessionLocal
from infrastructure.Observers import NotificationObserver, LoggingObserver
from api.dependencies import get_event_bus

# IMPORTANTE: Importa tus routers para que dejen de salir los errores 404
# Revisa que los nombres 'auth', 'incidents' y 'tasks' coincidan con tus archivos
from api.endpoints import router as api_router 

# Crear tablas en la base de datos al arrancar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpsCenter API")
app.include_router(api_router)

# REGISTRO DE RUTAS: Esto es lo que hace que aparezcan en /docs y funcionen en la UI
app.include_router(api_router)

def initialize_observers() -> None:
    """
    Suscribe los observers al EventBus en la inicialización de la aplicación.
    """
    event_bus = get_event_bus()
    
    # 1. LoggingObserver: Registra eventos en la consola/logs
    logging_observer = LoggingObserver()
    event_bus.subscribe(logging_observer)
    
    # 2. NotificationObserver: Crea registros de notificación en la DB
    db = SessionLocal()
    try:
        # Importación interna corregida sin 'backend.'
        from infrastructure.postgres import PostgresNotificationRepo
        notification_repo = PostgresNotificationRepo(db)
        
        notification_observer = NotificationObserver(notification_repo)
        event_bus.subscribe(notification_observer)
    finally:
        # Es buena práctica no dejar sesiones de DB colgadas aquí
        db.close()


@app.on_event("startup")
async def startup_event() -> None:
    """Evento que se ejecuta al iniciar el servidor"""
    initialize_observers()


@app.get("/")
def read_root():
    """Endpoint de verificación de salud"""
    return {
        "status": "online",
        "message": "OpsCenter API funcionando correctamente",
        "timestamp": datetime.now().isoformat()
    }