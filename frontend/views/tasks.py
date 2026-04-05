"""
Vistas de tareas: listado y cambio de estado.
El filtrado por rol (Operator vs Supervisor/Admin) lo aplica el backend en GET /tasks.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

from api_client import ApiError, get_tasks, update_task_status

SESSION_TOKEN = "token"
SESSION_USER = "user"
FLASH_TASK_STATUS_UPDATED = "_flash_task_status_updated"

TASK_STATUSES = ["OPEN", "IN_PROGRESS", "DONE"]


def _token() -> Optional[str]:
    return st.session_state.get(SESSION_TOKEN)


def _user_role() -> Optional[str]:
    user = st.session_state.get(SESSION_USER) or {}
    return user.get("role")


def show_task_list() -> None:
    """
    Tabla con título, estado, incidente asociado y asignado a.
    OPERATOR: la API devuelve solo tareas asignadas a él.
    SUPERVISOR y ADMIN: la API devuelve todas las tareas.
    Por cada fila: selectbox de estado y botón para aplicar PATCH /tasks/{id}/status.
    """
    if st.session_state.pop(FLASH_TASK_STATUS_UPDATED, False):
        st.success("Estado de la tarea actualizado.")

    token = _token()
    if not token:
        st.warning("Sesión no válida.")
        return

    role = _user_role()
    if role == "OPERATOR":
        st.caption(
            "Como operador solo ves las tareas que te están asignadas."
        )
    elif role in ("SUPERVISOR", "ADMIN"):
        st.caption("Como supervisor o administrador ves todas las tareas del sistema.")

    try:
        rows: List[Dict[str, Any]] = get_tasks(token)
    except ApiError as exc:
        st.error(exc.message)
        return

    if not rows:
        st.info("No hay tareas para mostrar.")
        return

    st.subheader("Listado de tareas")

    header = st.columns([2.8, 1.0, 1.0, 1.0, 1.4, 1.0])
    header[0].markdown("**Título**")
    header[1].markdown("**Estado**")
    header[2].markdown("**Incidente**")
    header[3].markdown("**Asignado a**")
    header[4].markdown("**Cambiar estado**")
    header[5].markdown("**Acción**")

    st.divider()

    for task in rows:
        tid = str(task.get("id", ""))
        if not tid:
            continue

        current_status = task.get("status") or "OPEN"
        if current_status not in TASK_STATUSES:
            current_status = "OPEN"

        col_t, col_st, col_inc, col_asg, col_pick, col_btn = st.columns(
            [2.8, 1.0, 1.0, 1.0, 1.4, 1.0]
        )
        col_t.write((task.get("title") or "")[:200] or "—")
        col_st.write(current_status)
        col_inc.write(task.get("incident_id") or "—")
        col_asg.write(task.get("assigned_to") or "—")

        idx = TASK_STATUSES.index(current_status)
        picked = col_pick.selectbox(
            "Estado",
            TASK_STATUSES,
            index=idx,
            key=f"task_status_pick_{tid}",
            label_visibility="collapsed",
        )

        if col_btn.button("Actualizar", key=f"task_status_save_{tid}"):
            if picked == current_status:
                st.info("El estado seleccionado es el mismo que el actual.")
            else:
                try:
                    update_task_status(token, tid, picked)
                    st.session_state[FLASH_TASK_STATUS_UPDATED] = True
                    st.rerun()
                except ApiError as exc:
                    st.error(exc.message)
