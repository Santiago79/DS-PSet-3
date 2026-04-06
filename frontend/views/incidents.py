from __future__ import annotations
import streamlit as st
from typing import Any, Dict, List, Optional
from api_client import ApiError, get_incident, get_incidents, create_incident

SESSION_TOKEN = "token"
SESSION_USER = "user"

def _token() -> Optional[str]:
    return st.session_state.get(SESSION_TOKEN)

def _user_role() -> Optional[str]:
    user = st.session_state.get(SESSION_USER) or {}
    return user.get("role")

def _fmt_dt(value: Any) -> str:
    if not value: return "—"
    return str(value)[:19].replace("T", " ")

def show_incident_list() -> None:
    token = _token()
    
    if "selected_inc_id" in st.session_state:
        if st.button("⬅️ Volver al listado"):
            del st.session_state["selected_inc_id"]
            st.rerun()
        show_incident_detail(st.session_state["selected_inc_id"])
        return

    try:
        rows = get_incidents(token)
    except ApiError as exc:
        st.error(exc.message); return

    if not rows:
        st.info("No hay incidentes registrados."); return

    st.subheader("Listado de incidentes")
    for r in rows:
        # Intentamos mostrar el nombre del creador, si no, el ID
        creador = r.get('creator_name') or r.get('created_by') or "—"
        
        with st.expander(f"📦 {r.get('title')} — {r.get('status')} [{r.get('severity')}]"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Fecha:** {_fmt_dt(r.get('created_at'))}")
                st.write(f"**Creado por:** {creador}")
            with col2:
                if st.button("🔍 Ver detalle completo", key=f"det_{r.get('id')}", use_container_width=True):
                    st.session_state["selected_inc_id"] = r.get('id')
                    st.rerun()

def show_incident_detail(incident_id: str) -> None:
    token = _token()
    try:
        inc = get_incident(token, incident_id)
        
        st.title(f"🛡️ {inc.get('title', 'Sin título')}")
        st.divider()

        # Fila 1: Info Básica
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 📊 Estado")
            st.info(inc.get('status', '—'))
        with c2:
            st.markdown("### ⚠️ Severidad")
            st.warning(inc.get('severity', '—'))
        with c3:
            st.markdown("### 📅 Fecha")
            st.write(_fmt_dt(inc.get('created_at')))

        # Fila 2: Responsables (Nombres en lugar de IDs)
        st.divider()
        u1, u2 = st.columns(2)
        with u1:
            # Prioridad al nombre sobre el ID
            creador_nombre = inc.get('creator_name') or inc.get('created_by') or "—"
            st.markdown("**👤 Creado por:**")
            st.write(creador_nombre)
        with u2:
            # Prioridad al nombre sobre el ID
            asignado_nombre = inc.get('assigned_name') or inc.get('assigned_to') or "No asignado"
            st.markdown("**🛠️ Asignado a:**")
            st.write(asignado_nombre)

        st.divider()
        st.markdown("### 📝 Descripción")
        st.write(inc.get("description") or "*Sin descripción.*")

        # Tareas
        st.divider()
        st.markdown("### 📋 Tareas Asociadas")
        tasks = inc.get("tasks", [])
        if tasks:
            task_list = []
            for t in tasks:
                # También para las tareas, intentamos mostrar nombres
                asignado_tarea = t.get('assigned_name') or t.get('assigned_to') or "—"
                task_list.append({
                    "Título": t.get('title'),
                    "Estado": t.get('status'),
                    "Asignado": asignado_tarea,
                    "Fecha": _fmt_dt(t.get('created_at'))
                })
            st.table(task_list)
        else:
            st.info("Sin tareas vinculadas.")

    except ApiError as e:
        st.error(f"Error: {e.message}")

def show_create_incident_form() -> None:
    token = _token()
    st.subheader("Nuevo incidente")
    with st.form("create_inc_form", clear_on_submit=True):
        t = st.text_input("Título")
        d = st.text_area("Descripción")
        s = st.selectbox("Severidad", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        if st.form_submit_button("Registrar", type="primary"):
            if not t.strip() or not d.strip():
                st.error("Campos obligatorios.")
            else:
                try:
                    create_incident(token, {"title": t.strip(), "description": d.strip(), "severity": s})
                    st.success("Incidente creado.")
                    st.rerun()
                except ApiError as e: st.error(e.message)   