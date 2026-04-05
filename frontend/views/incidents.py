import streamlit as st

from __future__ import annotations
from typing import Any, Dict, List, Optional

from api_client import ApiError, create_incident, get_incident, get_incidents

SESSION_TOKEN = "token"
SESSION_USER = "user"
FLASH_INCIDENT_CREATED = "_flash_incident_created"


def _token() -> Optional[str]:
    return st.session_state.get(SESSION_TOKEN)


def _user_role() -> Optional[str]:
    user = st.session_state.get(SESSION_USER) or {}
    return user.get("role")


def _fmt_dt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, str):
        return value[:19].replace("T", " ") if len(value) >= 19 else value
    return str(value)


def show_incident_list() -> None:
    """
    Tabla con título, severidad, estado y fecha.
    OPERATOR: la API devuelve solo incidentes creados o asignados a él.
    SUPERVISOR y ADMIN: la API devuelve todos los incidentes.
    """
    token = _token()
    if not token:
        st.warning("Sesión no válida.")
        return

    role = _user_role()
    if role == "OPERATOR":
        st.caption(
            "Como operador solo ves incidentes que creaste o que te fueron asignados."
        )
    elif role in ("SUPERVISOR", "ADMIN"):
        st.caption("Como supervisor o administrador ves todos los incidentes del sistema.")

    try:
        rows: List[Dict[str, Any]] = get_incidents(token, {"skip": 0, "limit": 500})
    except ApiError as exc:
        st.error(exc.message)
        return

    if not rows:
        st.info("No hay incidentes para mostrar.")
        return

    slim: List[Dict[str, Any]] = []
    for r in rows:
        slim.append(
            {
                "title": r.get("title"),
                "severity": r.get("severity"),
                "status": r.get("status"),
                "fecha": _fmt_dt(r.get("created_at")),
            }
        )

    st.subheader("Listado de incidentes")
    st.dataframe(
        slim,
        use_container_width=True,
        hide_index=True,
        column_config={
            "title": st.column_config.TextColumn("Título", width="large"),
            "severity": "Severidad",
            "status": "Estado",
            "fecha": "Fecha",
        },
    )

    def _label(inc_id: str) -> str:
        for r in rows:
            if r.get("id") == inc_id:
                t = (r.get("title") or "")[:100]
                return t if t else str(inc_id)
        return str(inc_id)

    selected = st.selectbox(
        "Ver detalle de",
        options=[r["id"] for r in rows],
        format_func=_label,
        key="incident_detail_select",
    )
    if selected:
        st.divider()
        show_incident_detail(selected)


def show_incident_detail(incident_id: str) -> None:
    #Vista detallada del incidente y tabla de tareas asociadas
    token = _token()
    if not token:
        st.warning("Sesión no válida.")
        return
    if not incident_id:
        return

    st.subheader("Detalle del incidente")
    try:
        inc: Dict[str, Any] = get_incident(token, incident_id)
    except ApiError as exc:
        st.error(exc.message)
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Título**  \n{inc.get('title', '—')}")
        st.markdown(f"**Severidad**  \n{inc.get('severity', '—')}")
        st.markdown(f"**Estado**  \n{inc.get('status', '—')}")
    with c2:
        st.markdown(f"**Creado por**  \n{inc.get('created_by', '—')}")
        st.markdown(f"**Asignado a**  \n{inc.get('assigned_to') or '—'}")
        st.markdown(f"**Creado**  \n{_fmt_dt(inc.get('created_at'))}")

    st.markdown("**Descripción**")
    st.write(inc.get("description") or "—")

    tasks = inc.get("tasks") or []
    st.markdown("**Tareas asociadas**")
    if not tasks:
        st.write("No hay tareas asociadas.")
        return

    task_rows = [
        {
            "title": t.get("title"),
            "status": t.get("status"),
            "asignado": t.get("assigned_to") or "—",
            "creado": _fmt_dt(t.get("created_at")),
        }
        for t in tasks
    ]
    st.dataframe(task_rows, use_container_width=True, hide_index=True)


def show_create_incident_form() -> None:
    #Formulario de alta: título, descripción, severidad. Refresca la lista al crear
    token = _token()
    if not token:
        st.warning("Sesión no válida.")
        return

    st.subheader("Nuevo incidente")
    role = _user_role()
    if role not in ["OPERATOR", "SUPERVISOR", "ADMIN"]:
        st.info(
            "Solo usuarios con rol **OPERATOR**, **SUPERVISOR** o **ADMIN** pueden crear incidentes."
        )
        return

    with st.form("create_incident_form"):
        title = st.text_input("Título", max_chars=500)
        description = st.text_area("Descripción")
        severity = st.selectbox(
            "Severidad",
            ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        )
        submitted = st.form_submit_button("Crear incidente", type="primary")

    if submitted:
        if not (title or "").strip() or not (description or "").strip():
            st.error("El título y la descripción son obligatorios.")
            return
        try:
            create_incident(
                token,
                {
                    "title": title.strip(),
                    "description": description.strip(),
                    "severity": severity,
                },
            )
            st.session_state[FLASH_INCIDENT_CREATED] = True
            st.rerun()
        except ApiError as exc:
            st.error(exc.message)
