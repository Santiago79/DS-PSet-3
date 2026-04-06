from __future__ import annotations
import streamlit as st
from typing import Any, Dict, List, Optional
from api_client import ApiError, create_incident, get_incident, get_incidents

SESSION_TOKEN = "token"
SESSION_USER = "user"

def _token() -> Optional[str]:
    return st.session_state.get(SESSION_TOKEN)

def _user_role() -> Optional[str]:
    user = st.session_state.get(SESSION_USER) or {}
    return user.get("role")

def _fmt_dt(value: Any) -> str:
    return str(value)[:19].replace("T", " ") if value else "—"

def show_incident_list() -> None:
    token = _token()
    
    # Lógica para alternar entre LISTA y DETALLE
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
        st.info("No hay incidentes."); return

    st.subheader("Listado de incidentes")
    for r in rows:
        with st.expander(f"📦 {r.get('title')} ({r.get('status')})"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Severidad:** {r.get('severity')}")
                st.write(f"**Creado:** {_fmt_dt(r.get('created_at'))}")
            with c2:
                if st.button("🔍 Ver detalle completo", key=f"det_{r.get('id')}"):
                    st.session_state["selected_inc_id"] = r.get('id')
                    st.rerun()

def show_incident_detail(incident_id: str) -> None:
    token = _token()
    try:
        inc = get_incident(token, incident_id)
        st.title(f"Detalle: {inc.get('title')}")
        st.write(f"**Descripción:** {inc.get('description')}")
        st.divider()
        st.subheader("Tareas asociadas")
        tasks = inc.get("tasks", [])
        if tasks:
            st.table([{"Tarea": t['title'], "Estado": t['status']} for t in tasks])
        else:
            st.write("Sin tareas.")
    except ApiError as e:
        st.error(e.message)

def show_create_incident_form() -> None:
    token = _token()
    with st.form("create_inc"):
        t = st.text_input("Título")
        d = st.text_area("Descripción")
        s = st.selectbox("Severidad", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        if st.form_submit_button("Crear", type="primary"):
            try:
                create_incident(token, {"title": t, "description": d, "severity": s})
                st.success("¡Incidente creado!"); st.rerun()
            except ApiError as e: st.error(e.message)