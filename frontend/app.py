from __future__ import annotations

import streamlit as st

from api_client import (
    ApiError,
    get_current_user,
    get_incidents,
    get_notifications,
    login,
)
from views.tasks import show_task_list

st.set_page_config(
    page_title="OpsCenter",
    page_icon="🛡️",
    layout="wide",
)

# Claves de sesión
SESSION_TOKEN = "token"
SESSION_USER = "user"


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


def _page_inicio() -> None:
    st.header("Inicio")
    st.info(
        "Use el menú de la barra lateral para navegar entre incidentes, tareas y notificaciones."
    )


def _page_incidentes() -> None:
    st.header("Incidentes")
    token = st.session_state[SESSION_TOKEN]
    try:
        rows = get_incidents(token, {"skip": 0, "limit": 100})
    except ApiError as exc:
        st.error(exc.message)
        return

    if not rows:
        st.write("No hay incidentes para mostrar.")
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


def _page_tareas() -> None:
    st.header("Tareas")
    show_task_list()


def _page_notificaciones() -> None:
    st.header("Notificaciones")
    token = st.session_state[SESSION_TOKEN]
    try:
        rows = get_notifications(token)
    except ApiError as exc:
        st.error(exc.message)
        return

    if not rows:
        st.write("No hay notificaciones (o el endpoint aún no está disponible en la API).")
        return

    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_app() -> None:
    with st.sidebar:
        st.markdown("## 🛡️ OpsCenter")
        _sidebar_user()
        page = st.radio(
            "Navegación",
            (
                "Inicio",
                "Incidentes",
                "Tareas",
                "Notificaciones",
            ),
            label_visibility="collapsed",
        )

    if page == "Inicio":
        _page_inicio()
    elif page == "Incidentes":
        _page_incidentes()
    elif page == "Tareas":
        _page_tareas()
    else:
        _page_notificaciones()


def main() -> None:
    _init_session()
    if not _is_authenticated():
        _render_login()
    else:
        _render_app()


main()