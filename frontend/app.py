from __future__ import annotations
import streamlit as st
from api_client import (
    ApiError, 
    login, 
    get_current_user, 
    get_incidents, 
    assign_incident, 
    update_incident_status, 
    create_task
)
from views.notifications import show_notification_list
from views.tasks import show_task_list
from views.incidents import show_incident_list, show_create_incident_form  

st.set_page_config(page_title="OpsCenter", page_icon="🛡️", layout="wide")

# Inicialización de sesión
if "token" not in st.session_state: st.session_state["token"] = None
if "user" not in st.session_state: st.session_state["user"] = None

INCIDENT_STATUSES = ["OPEN", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"]

def _render_login():
    st.title("🛡️ OpsCenter Login")
    with st.form("login"):
        e = st.text_input("Email")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Ingresar", type="primary"):
            try:
                tk = login(e, p)
                st.session_state["token"] = tk
                st.session_state["user"] = get_current_user(tk)
                st.rerun()
            except ApiError as ex: st.error(ex.message)

# --- FUNCIONES DE PÁGINAS DE ADMIN ---

def _page_assign_incidents(token):
    st.header("Asignar incidentes")
    try:
        rows = get_incidents(token)
        if not rows: st.info("No hay incidentes."); return
        
        ids = [r["id"] for r in rows]
        incident_id = st.selectbox("Seleccione Incidente", ids, format_func=lambda x: next(r["title"] for r in rows if r["id"]==x))
        assigned_to = st.text_input("ID del usuario (UUID)")
        
        if st.button("Confirmar Asignación", type="primary"):
            assign_incident(token, incident_id, assigned_to)
            st.success("¡Asignado correctamente!")
    except ApiError as e: st.error(e.message)

def _page_change_status(token):
    st.header("Gestionar Estados")
    try:
        rows = get_incidents(token)
        ids = [r["id"] for r in rows]
        incident_id = st.selectbox("Incidente", ids, format_func=lambda x: next(r["title"] for r in rows if r["id"]==x))
        new_status = st.selectbox("Nuevo Estado", INCIDENT_STATUSES)
        
        if st.button("Actualizar", type="primary"):
            update_incident_status(token, incident_id, new_status)
            st.success("Estado actualizado.")
    except ApiError as e: st.error(e.message)

def _page_create_task(token):
    st.header("Nueva Tarea")
    try:
        rows = get_incidents(token)
        ids = [r["id"] for r in rows]
        incident_id = st.selectbox("Vincular a Incidente", ids)
        t = st.text_input("Título de tarea")
        d = st.text_area("Descripción")
        if st.button("Crear Tarea"):
            create_task(token, {"incident_id": incident_id, "title": t, "description": d})
            st.success("Tarea creada.")
    except ApiError as e: st.error(e.message)

# --- RENDERIZADO PRINCIPAL ---

def _render_app():
    user = st.session_state["user"]
    token = st.session_state["token"]
    role = user.get("role", "OPERATOR").upper()
    
    with st.sidebar:
        st.title("🛡️ OpsCenter")
        st.write(f"👤 **{user.get('name')}**")
        st.markdown(f"**{user.get('id')}**")
        st.caption(f"Rol: {role}")
        st.divider()
        
        # Construcción dinámica del menú
        menu = ["Incidentes", "Crear Incidente", "Mis Tareas", "Notificaciones"]
        if role in ["ADMIN", "SUPERVISOR"]:
            menu += ["Asignar Incidentes", "Control de Estados", "Gestionar Tareas"]
        
        choice = st.radio("Navegación", menu)
        
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state["token"] = None
            st.rerun()

    # Routing de páginas
    if choice == "Incidentes": show_incident_list()
    elif choice == "Crear Incidente": show_create_incident_form()
    elif choice == "Mis Tareas": show_task_list()
    elif choice == "Notificaciones": show_notification_list()
    elif choice == "Asignar Incidentes": _page_assign_incidents(token)
    elif choice == "Control de Estados": _page_change_status(token)
    elif choice == "Gestionar Tareas": _page_create_task(token)

if not st.session_state["token"]:
    _render_login()
else:
    _render_app()
