# 🛡️ OpsCenter

Plataforma interna de gestión de incidentes operativos para equipos fintech.

---

## 1. ¿Qué problema resuelve?

Los equipos de operaciones de una fintech gestionaban sus incidentes mediante correo electrónico, hojas de cálculo y mensajería informal. Esto generaba:

- **Poca trazabilidad**: no existía un historial centralizado de quién hizo qué y cuándo.
- **Mala asignación de responsables**: los incidentes podían quedar sin dueño o asignados a la persona equivocada.
- **Baja visibilidad del estado real**: no había un ciclo de vida formal (OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED).
- **Notificaciones inconsistentes**: algunos usuarios no se enteraban de cambios relevantes.

**OpsCenter** unifica la creación, asignación, seguimiento y notificación de incidentes en una sola plataforma con roles bien definidos, auditoría de eventos y notificaciones automáticas.

---

## 2. Arquitectura

El sistema sigue **Arquitectura Hexagonal** (Ports & Adapters), que garantiza alta cohesión, bajo acoplamiento y que el dominio no depende de ninguna tecnología externa.

```
┌──────────────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit · ui)                    │
│       login · incidentes · tareas · notificaciones               │
└───────────────────────────────┬──────────────────────────────────┘
                                │  HTTP / REST
┌───────────────────────────────▼──────────────────────────────────┐
│                   API Layer  (backend/api/)                      │
│   endpoints.py · guards.py · dependencies.py · main.py           │
│   Rutas FastAPI · Guards JWT · serialización de DTOs             │
└───────────────────────────────┬──────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────┐
│              Application Layer  (backend/application/)           │
│           use_cases.py · dtos.py                                 │
│     Casos de uso · DTOs Pydantic · orquestación del flujo        │
└──────────┬───────────────────────────────────────┬───────────────┘
           │  Domain Interfaces (Ports)            │
┌──────────▼────────────────────────┐  ┌───────────▼───────────────┐
│  Domain Layer (backend/domain/)   │  │ Infrastructure (backend/  │
│  entities.py · enums.py           │  │ infrastructure/)          │
│  states.py · events.py            │  │  models.py  (SQLAlchemy)  │
│  commands.py · templates.py       │  │  postgres.py (repos ORM)  │
│  factories.py · repositories.py   │  │  event_bus_impl.py        │
│  interfaces/ (EventBus,           │  │  Observers.py             │
│  ObservadorEvento)               │  │  auth_provider.py  (JWT)  │
│  exceptions.py                    │  │  database.py              │
└───────────────────────────────────┘  └───────────────────────────┘
```

### Capas

| Capa | Módulo | Responsabilidad |
|------|--------|-----------------|
| **Domain** | `backend/domain/` | Entidades, enums, reglas de negocio, States, Commands, Templates, Factories, interfaces de repositorio y EventBus. **No depende de ninguna librería externa.** |
| **Application** | `backend/application/` | Casos de uso (`use_cases.py`), DTOs Pydantic (`dtos.py`), orquestación del flujo entre dominio e infraestructura. |
| **Infrastructure** | `backend/infrastructure/` | Modelos ORM SQLAlchemy (`models.py`), repos concretos (`postgres.py`), `InMemoryEventBus`, `NotificationObserver`, `LoggingObserver`, `AuthProvider` (JWT con jose + bcrypt). |
| **API** | `backend/api/` | Rutas FastAPI (`endpoints.py`), guards de autorización (`guards.py`), dependencias de inyección (`dependencies.py`). |
| **Frontend** | `frontend/` | App Streamlit (`app.py`), cliente HTTP (`api_client.py`), vistas por módulo (`views/`). |

---

## 3. Cómo correr el proyecto

### Pre-requisitos

- Docker ≥ 24
- Docker Compose ≥ 2

### Levantar todos los servicios

```bash
docker compose up --build
```

Esto levanta tres servicios:

| Servicio | Puerto local | Descripción |
|----------|-------------|-------------|
| `db`     | 5433        | PostgreSQL 15 |
| `api`    | 8000        | Backend FastAPI |
| `ui`     | 8501        | Frontend Streamlit |

### Verificar que el backend está listo

```bash
curl http://localhost:8000/docs
```

### Acceder al frontend

Abre tu navegador en: [http://localhost:8501](http://localhost:8501)

---

## 4. Cómo usar el sistema

### Credenciales de ejemplo

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | `admin@opscenter.com` | `admin123` |
| Supervisor | `supervisor@opscenter.com` | `super123` |
| Operator | `operator@opscenter.com` | `oper123` |

> Los usuarios de ejemplo se crean automáticamente al iniciar la aplicación si no existen (seed en el startup de la API).

### Pasos básicos

1. **Login**: ingresa con alguna de las credenciales de la tabla anterior.
2. **Ver incidentes**: navega a la sección *Incidentes* para ver el listado según tu rol.
3. **Crear incidente** *(Operator, Supervisor, Admin)*: completa título, descripción y severidad (LOW / MEDIUM / HIGH / CRITICAL).
4. **Asignar incidente** *(Supervisor, Admin)*: desde el detalle de un incidente, selecciona el responsable → estado cambia a ASSIGNED.
5. **Cambiar estado** *(Supervisor, Admin)*: flujo OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED. Cada transición es validada por el State Pattern.
6. **Ver tareas**: navega a *Tareas*; los Operators ven solo sus tareas asignadas.
7. **Actualizar estado de tarea**: selecciona el nuevo estado (OPEN / IN_PROGRESS / DONE) y presiona *Actualizar*.
8. **Ver notificaciones**: navega a *Notificaciones* para ver los avisos generados automáticamente.

### Endpoints principales

```
POST   /login                        Autenticación → JWT
GET    /me                           Perfil del usuario actual
GET    /incidents                    Listar incidentes (filtrado por rol)
POST   /incidents                    Crear incidente
GET    /incidents/{id}               Detalle de incidente + tareas asociadas
PATCH  /incidents/{id}/assign        Asignar incidente (SUPERVISOR / ADMIN)
PATCH  /incidents/{id}/status        Cambiar estado de incidente (SUPERVISOR / ADMIN)
POST   /tasks                        Crear tarea (SUPERVISOR / ADMIN)
GET    /tasks                        Listar tareas (filtrado por rol)
PATCH  /tasks/{id}/status            Cambiar estado de tarea
GET    /notifications                Listar notificaciones (?unread_only=true)
```

Documentación interactiva en: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Patrones de diseño aplicados

### Observer

**Archivos**: `domain/interfaces/observador_evento.py`, `domain/interfaces/event_bus.py`, `infrastructure/event_bus_impl.py`, `infrastructure/Observers.py`

**Uso**: Cada vez que un caso de uso completa una operación significativa (incidente creado, asignado, estado cambiado, tarea creada, tarea completada), publica un `Evento` en el `InMemoryEventBus`. El bus itera sobre todos los observers suscritos y llama a `on_event()`.

**Observers concretos** (ambos en `infrastructure/Observers.py`):
- `NotificationObserver`: determina el destinatario según el tipo de evento y delega la creación del comando a la `NotificationFactory` correspondiente.
- `LoggingObserver`: registra el evento en el logger de Python con timestamp, tipo de evento y datos relevantes.

---

### Command

**Archivo**: `domain/commands.py`

**Uso**: Encapsula el envío de cada notificación como un objeto independiente con método `execute()`. El comando recibe el repositorio de notificaciones, el evento y el destinatario. Al ejecutarse, usa su `message_builder` (Template Method) para construir el mensaje, crea la entidad `Notification` con el estado resultante (SENT / FAILED) y la persiste.

**Comandos concretos**:
- `EmailNotificationCommand`: construye el mensaje con `EmailMessageBuilder`, simula el envío (`_send_email`) y persiste la notificación.
- `InAppNotificationCommand`: construye el mensaje con `InAppMessageBuilder`, valida que no esté vacío y persiste la notificación directamente en la base de datos.

---

### State

**Archivo**: `domain/states.py`, usado por `domain/entities.py` (`Incident`)

**Uso**: Controla las transiciones válidas del ciclo de vida de `Incident`. La entidad almacena `_status` (enum) y `_state` (objeto State, con lazy loading). Cada método de la entidad (`assign_to`, `start_progress`, `resolve`, `close`, `reopen`) delega en el estado actual. Si la transición no es válida, el estado lanza `InvalidStateTransitionError`.

**Transiciones permitidas por estado**:

| Estado actual | assign | start_progress | resolve | close | reopen |
|---------------|--------|----------------|---------|-------|--------|
| OPEN | ✓ → ASSIGNED | ✗ | ✗ | ✗ | ✗ |
| ASSIGNED | ✓ reasigna | ✓ → IN_PROGRESS | ✗ | ✗ | ✓ → OPEN |
| IN_PROGRESS | ✓ → ASSIGNED | noop | ✓ → RESOLVED | ✗ | ✗ |
| RESOLVED | ✗ | ✗ | noop | ✓ → CLOSED | ✓ → OPEN |
| CLOSED | ✗ | ✗ | ✗ | noop | ✓ → OPEN |

La función `create_state_from_status()` actúa como factory interna para hacer lazy loading del estado a partir del enum persistido.

---

### Template Method

**Archivo**: `domain/templates.py`

**Uso**: `NotificationMessageBuilder` define el algoritmo de construcción del mensaje como `build(evento) = _compose_message(greeting(), body(evento), farewell())`. Las subclases implementan los cuatro métodos abstractos para cada canal.

**Builders concretos**:
- `EmailMessageBuilder`: genera mensajes formales multilínea con saludo ("Estimado Usuario,"), cuerpo detallado según el tipo de evento y firma del equipo ("Atentamente, Equipo OpsCenter").
- `InAppMessageBuilder`: genera mensajes compactos de una línea con emojis para mostrar en la interfaz (`greeting` y `farewell` retornan `""`, `_compose_message` retorna solo el `body`).

---

### Factory

**Archivo**: `domain/factories.py`

**Uso**: Centraliza la creación de entidades del dominio, asegurando que las validaciones de negocio siempre se apliquen antes de instanciar la entidad.

- `IncidentFactory.create(...)`: valida título (≥ 3 chars), descripción (≥ 5 chars), severity válida, created_by no vacío; retorna un `Incident` con `_status=OPEN`.
- `TaskFactory.create(...)`: valida incident_id y título (≥ 3 chars); retorna una `Task` con `_status=OPEN`.

---

## 6. Justificación del patrón creacional adicional: Abstract Factory

**Patrón**: Abstract Factory  
**Archivo**: `domain/factories.py` — `NotificationFactory`, `IncidentNotificationFactory`, `TaskNotificationFactory`  
**Función auxiliar**: `get_notification_factory(evento)` (selecciona la factory correcta según el tipo de evento)

**Problema que resuelve**: El sistema genera notificaciones para dos familias de eventos distintas (Incident y Task), y para cada una necesita crear dos objetos relacionados entre sí: un `NotificationMessageBuilder` y un `NotificationCommand`. Ambos deben corresponder al mismo dominio. Sin Abstract Factory, nada impediría que el `NotificationObserver` combinara un builder de Task con un comando de Incident, generando mensajes incoherentes.

**Solución**: `NotificationFactory` define la interfaz con dos métodos:

```
NotificationFactory
├── create_command(repo, evento, **kwargs) → NotificationCommand
└── create_message_builder()               → NotificationMessageBuilder

IncidentNotificationFactory    →  valida eventos Incident
├── create_command(...)        →  EmailNotificationCommand o InAppNotificationCommand
└── create_message_builder()   →  EmailMessageBuilder (por defecto)

TaskNotificationFactory        →  valida eventos Task
├── create_command(...)        →  EmailNotificationCommand o InAppNotificationCommand
└── create_message_builder()   →  InAppMessageBuilder (por defecto)
```

El `NotificationObserver` llama a `get_notification_factory(evento)` para obtener la factory correcta, luego llama a `create_command(...)` para obtener el comando listo para ejecutar. Esto garantiza que siempre se use la familia de objetos correcta según el tipo de evento.

**Beneficio principal**: agregar un nuevo tipo de evento (ej. eventos de usuario) solo requiere crear una nueva subclase de `NotificationFactory` sin modificar `NotificationObserver` ni los comandos existentes — principio Open/Closed.

---

## 7. Diagramas UML

Los diagramas se encuentran en `/docs`:

| Archivo | Descripción |
|---------|-------------|
| `use_case_diagram.png` | Actores ADMIN, SUPERVISOR, OPERATOR y sus casos de uso con los endpoints reales |
| `class_diagram.png` | Todas las clases del dominio, infraestructura, patrones y DTOs con sus relaciones exactas |
| `sequence_diagram.png` | Flujo completo: Operator crea incidente → ORM → EventBus → Observers → AbstractFactory → TemplateMethod → Command → NotificationORM |

---

## 8. Estructura del proyecto

```
DS-PSet-3/
├── backend/
│   ├── domain/
│   │   ├── interfaces/
│   │   │   ├── event_bus.py          # Interfaz abstracta EventBus
│   │   │   └── observador_evento.py  # Interfaz abstracta ObservadorEvento
│   │   ├── entities.py               # User, Incident, Task, Notification
│   │   ├── enums.py                  # Role, Severity, IncidentStatus, TaskStatus, ...
│   │   ├── states.py                 # State Pattern: IncidentState + 5 estados concretos
│   │   ├── events.py                 # Evento base + 5 eventos concretos
│   │   ├── commands.py               # Command Pattern: NotificationCommand + 2 concretos
│   │   ├── templates.py              # Template Method: NotificationMessageBuilder + 2 builders
│   │   ├── factories.py              # Factory (Incident/Task) + Abstract Factory (Notification)
│   │   ├── repositories.py           # Interfaces Protocol de repositorios
│   │   └── exceptions.py             # ValidationError, NotFoundError, InvalidStateTransitionError
│   ├── application/
│   │   ├── use_cases.py              # 8 casos de uso (Create/Get/Assign/ChangeStatus...)
│   │   └── dtos.py                   # DTOs Pydantic de entrada y salida
│   ├── infrastructure/
│   │   ├── models.py                 # ORM SQLAlchemy: UserORM, IncidentORM, TaskORM, NotificationORM
│   │   ├── postgres.py               # Implementaciones concretas de repositorios con ORM
│   │   ├── event_bus_impl.py         # InMemoryEventBus
│   │   ├── Observers.py              # NotificationObserver, LoggingObserver
│   │   ├── auth_provider.py          # JWT (jose) + bcrypt (passlib)
│   │   ├── database.py               # Sesión SQLAlchemy
│   │   └── notification_providers.py # Proveedores de canal
│   ├── api/
│   │   ├── endpoints.py              # Rutas FastAPI
│   │   ├── guards.py                 # require_role, require_any_role
│   │   ├── dependencies.py           # Inyección de dependencias (use cases)
│   │   └── main.py                   # App FastAPI + startup seed
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py                        # Punto de entrada Streamlit
│   ├── api_client.py                 # Cliente HTTP hacia la API
│   ├── views/
│   │   ├── incidents.py              # Vista de incidentes
│   │   ├── tasks.py                  # Vista de tareas + cambio de estado
│   │   └── notifications.py          # Vista de notificaciones
│   ├── Dockerfile
│   └── requirements.txt
├── docs/
│   ├── use_case_diagram.puml
│   ├── class_diagram.puml
│   └── sequence_diagram.puml
├── docker-compose.yml
└── README.md
```