from __future__ import annotations
import streamlit as st
from api_client import ApiError, login, get_current_user
from views.notifications import show_notification_list
from views.tasks import show_task_list
from views.incidents import show_incident_list, show_create_incident_form  

st.set_page_config(page_title="OpsCenter", page_icon="🛡️", layout="wide")

if "token" not in st.session_state: st.session_state["token"] = None

def _render_login():
    st.title("🛡️ OpsCenter Login")
    with st.form("login"):
        e = st.text_input("Email")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Entrar"):
            try:
                tk = login(e, p)
                st.session_state["token"] = tk
                st.session_state["user"] = get_current_user(tk)
                st.rerun()
            except ApiError as ex: st.error(ex.message)

def _render_app():
    user = st.session_state["user"]
    role = user.get("role", "OPERATOR")
    
    with st.sidebar:
        st.title("OpsCenter")
        st.write(f"👤 {user.get('name')} ({role})")
        # Menú simplificado
        menu = ["Incidentes", "Crear Incidente", "Tareas", "Notificaciones"]
        if role in ["ADMIN", "SUPERVISOR"]: menu += ["Asignar", "Admin Estados"]
        
        choice = st.radio("Navegación", menu)
        if st.button("Cerrar Sesión"):
            st.session_state["token"] = None; st.rerun()

    if choice == "Incidentes": show_incident_list()
    elif choice == "Crear Incidente": show_create_incident_form()
    elif choice == "Tareas": show_task_list()
    elif choice == "Notificaciones": show_notification_list()
    # Las demás páginas de admin se mantienen en app.py o sus vistas...

if not st.session_state["token"]: _render_login()
else: _render_app()