from __future__ import annotations
import streamlit as st

from api_client import (
    ApiError,
    assign_incident,
    create_task,
    get_current_user,
    get_incidents,
    login,
    update_incident_status,
)

from views.notifications import show_notification_list
from views.tasks import show_task_list

st.set_page_config(
    page_title="OpsCenter",
    page_icon="🛡️",
    layout="wide",
)

SESSION_TOKEN = "token"
SESSION_USER = "user"

INCIDENT_STATUSES = [
    "OPEN",
    "ASSIGNED",
    "IN_PROGRESS",
    "RESOLVED",
    "CLOSED",
]


def _nav_entries(role: str | None) -> list[tuple[str, str]]:
    # (etiqueta visible, clave interna). La autorización la aplica el backend
    base = [
        ("Incidentes", "incidents"),
        ("Mis Tareas", "tasks"),
        ("Notificaciones", "notifications"),
    ]
    supervisor_extra = [
        ("Todos los incidentes", "all_incidents"),
        ("Asignar incidentes", "assign_incidents"),
    ]
    admin_extra = [
        ("Cambiar estado de incidentes", "incident_change_status"),
        ("Crear tarea", "create_task"),
    ]
    r = (role or "OPERATOR").upper()
    if r == "OPERATOR":
        return base
    if r == "SUPERVISOR":
        return base + supervisor_extra
    if r == "ADMIN":
        return base + supervisor_extra + admin_extra
    return base


def _init_session() -> None:
    if SESSION_TOKEN not in st.session_state:
        st.session_state[SESSION_TOKEN] = None
    if SESSION_USER not in st.session_state:
        st.session_state[SESSION_USER] = None


def _is_authenticated() -> bool:
    return bool(st.session_state.get(SESSION_TOKEN))


def _logout() -> None:
    st.session_state[SESSION_TOKEN] = None
    st.session_state[SESSION_USER] = None


def _render_login() -> None:
    st.title("OpsCenter")
    st.caption("Inicie sesión para acceder al sistema")

    with st.form("login_form"):
        email = st.text_input("Correo electrónico", autocomplete="email")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar", type="primary")

    if submit:
        if not email.strip() or not password:
            st.error("Ingrese correo y contraseña.")
            return
        try:
            token = login(email.strip(), password)
            st.session_state[SESSION_TOKEN] = token
            st.session_state[SESSION_USER] = get_current_user(token)
            st.success("Sesión iniciada correctamente.")
            st.rerun()
        except ApiError as exc:
            st.error(exc.message)


def _sidebar_user() -> None:
    user = st.session_state.get(SESSION_USER) or {}
    name = user.get("name") or "—"
    role = user.get("role") or "—"
    st.markdown("**Usuario**")
    st.write(name)
    st.markdown("**Rol**")
    st.write(role)
    st.divider()
    if st.button("Cerrar sesión", use_container_width=True):
        _logout()
        st.rerun()


def _page_incidents_list(title: str) -> None:
    st.header(title)
    token = st.session_state[SESSION_TOKEN]
    try:
        rows = get_incidents(token, {"skip": 0, "limit": 200})
    except ApiError as exc:
        st.error(exc.message)
        return

    if not rows:
        st.info("No hay incidentes para mostrar.")
        return

    display_cols = [
        "id",
        "title",
        "severity",
        "status",
        "created_by",
        "assigned_to",
        "created_at",
    ]
    slim = [{k: r.get(k) for k in display_cols} for r in rows]
    st.dataframe(slim, use_container_width=True, hide_index=True)


def _page_assign_incidents() -> None:
    st.header("Asignar incidentes")
    st.caption(
        "El servidor valida permisos (p. ej. SUPERVISOR o ADMIN). "
        "Indica el **ID de usuario** destino tal como está en la base de datos."
    )
    token = st.session_state[SESSION_TOKEN]
    try:
        rows = get_incidents(token, {"skip": 0, "limit": 200})
    except ApiError as exc:
        st.error(exc.message)
        return

    if not rows:
        st.warning("No hay incidentes para listar.")
        return

    def _title(iid: str) -> str:
        for r in rows:
            if r.get("id") == iid:
                t = r.get("title") or iid
                return f"{t[:80]} — {iid[:8]}…"
        return iid

    ids = [r["id"] for r in rows if r.get("id")]
    incident_id = st.selectbox("Incidente", ids, format_func=_title)
    assigned_to = st.text_input("ID del usuario asignado")

    if st.button("Asignar", type="primary"):
        if not assigned_to.strip():
            st.error("Indique el ID del usuario.")
            return
        try:
            assign_incident(token, incident_id, assigned_to.strip())
            st.success("Incidente asignado.")
            st.rerun()
        except ApiError as exc:
            st.error(exc.message)


def _page_incident_change_status() -> None:
    st.header("Cambiar estado de incidentes")
    st.caption("El servidor valida la transición de estado.")
    token = st.session_state[SESSION_TOKEN]
    try:
        rows = get_incidents(token, {"skip": 0, "limit": 200})
    except ApiError as exc:
        st.error(exc.message)
        return

    if not rows:
        st.warning("No hay incidentes para listar.")
        return

    def _title(iid: str) -> str:
        for r in rows:
            if r.get("id") == iid:
                t = r.get("title") or iid
                return f"{t[:80]} — {iid[:8]}…"
        return iid

    ids = [r["id"] for r in rows if r.get("id")]
    incident_id = st.selectbox("Incidente", ids, format_func=_title, key="status_inc_pick")
    current = next((r.get("status") for r in rows if r.get("id") == incident_id), "OPEN")
    idx = (
        INCIDENT_STATUSES.index(current)
        if current in INCIDENT_STATUSES
        else 0
    )
    new_status = st.selectbox(
        "Nuevo estado",
        INCIDENT_STATUSES,
        index=idx,
        key="status_inc_new",
    )

    if st.button("Actualizar estado", type="primary"):
        try:
            update_incident_status(token, incident_id, new_status)
            st.success("Estado actualizado.")
            st.rerun()
        except ApiError as exc:
            st.error(exc.message)


def _page_create_task() -> None:
    st.header("Crear tarea")
    st.caption("Asocia la tarea a un incidente existente. La API valida el rol.")
    token = st.session_state[SESSION_TOKEN]
    try:
        rows = get_incidents(token, {"skip": 0, "limit": 200})
    except ApiError as exc:
        st.error(exc.message)
        return

    if not rows:
        st.warning("No hay incidentes; no se puede crear una tarea.")
        return

    def _title(iid: str) -> str:
        for r in rows:
            if r.get("id") == iid:
                t = r.get("title") or iid
                return f"{t[:80]} — {iid[:8]}…"
        return iid

    ids = [r["id"] for r in rows if r.get("id")]
    incident_id = st.selectbox(
        "Incidente",
        ids,
        format_func=_title,
        key="create_task_inc",
    )
    title = st.text_input("Título de la tarea")
    description = st.text_area("Descripción")
    assigned_to = st.text_input(
        "ID usuario asignado (opcional)",
        help="Vacío si la tarea no va dirigida a un usuario concreto.",
    )

    if st.button("Crear tarea", type="primary"):
        if not (title or "").strip() or not (description or "").strip():
            st.error("Título y descripción son obligatorios.")
            return
        payload: dict = {
            "incident_id": incident_id,
            "title": title.strip(),
            "description": description.strip(),
        }
        if assigned_to.strip():
            payload["assigned_to"] = assigned_to.strip()
        try:
            create_task(token, payload)
            st.success("Tarea creada.")
            st.rerun()
        except ApiError as exc:
            st.error(exc.message)


def _render_app() -> None:
    user = st.session_state.get(SESSION_USER) or {}
    role = user.get("role")
    entries = _nav_entries(role)
    keys = [e[1] for e in entries]
    labels_map = {key: label for label, key in entries}

    with st.sidebar:
        st.markdown("## 🛡️ OpsCenter")
        _sidebar_user()
        page_key = st.radio(
            "Navegación",
            options=keys,
            format_func=lambda k: labels_map[k],
            label_visibility="collapsed",
            key=f"nav_main_{role or 'none'}",
        )

    if page_key == "incidents":
        _page_incidents_list("Incidentes")
    elif page_key == "all_incidents":
        _page_incidents_list("Todos los incidentes")
    elif page_key == "tasks":
        st.header("Mis tareas")
        show_task_list()
    elif page_key == "notifications":
        st.header("Notificaciones")
        show_notification_list()
    elif page_key == "assign_incidents":
        _page_assign_incidents()
    elif page_key == "incident_change_status":
        _page_incident_change_status()
    elif page_key == "create_task":
        _page_create_task()


def main() -> None:
    _init_session()
    if not _is_authenticated():
        _render_login()
    else:
        _render_app()


main()
