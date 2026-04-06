from __future__ import annotations
import streamlit as st
from typing import Any, Dict, List, Optional
from api_client import ApiError, get_notifications

SESSION_TOKEN = "token"

def _token() -> Optional[str]:
    return st.session_state.get(SESSION_TOKEN)

def _fmt_dt(value: Any) -> str:
    if value is None: return "—"
    return str(value)[:19].replace("T", " ")

def show_notification_list() -> None:
    token = _token()
    if not token:
        st.warning("Sesión no válida.")
        return

    st.subheader("🔔 Centro de Notificaciones")
    
    # --- EL TRUCO FRONTEND ---
    # Creamos un registro local de IDs leídos en esta sesión
    if "local_read_notifs" not in st.session_state:
        st.session_state["local_read_notifs"] = set()

    unread_only = st.toggle("Ver solo no leídas", value=True)

    try:
        # Traemos la lista del backend
        rows: List[Dict[str, Any]] = get_notifications(token, unread_only=unread_only)
    except ApiError as exc:
        st.error(exc.message)
        return

    # Filtramos la lista combinando lo que dice el backend + nuestra memoria local
    display_rows = []
    for n in rows:
        nid = n.get("id")
        is_read_db = (n.get("status") or "").upper() == "READ"
        is_read_local = nid in st.session_state["local_read_notifs"]
        
        # Está leída si la base de datos lo dice, o si le dimos clic nosotros hoy
        is_read_total = is_read_db or is_read_local
        
        # Si queremos ver solo no leídas y esta ya se leyó, la saltamos
        if unread_only and is_read_total:
            continue
            
        n["_is_read_total"] = is_read_total
        display_rows.append(n)

    if not display_rows:
        st.info("No tienes notificaciones pendientes.")
        return

    # Renderizado de tarjetas
    for n in display_rows:
        is_read = n["_is_read_total"]
        
        with st.container(border=True):
            col_text, col_btn = st.columns([4, 1])
            
            with col_text:
                msg = n.get("message", "")
                if not is_read:
                    st.markdown(f"**{msg}**")
                else:
                    st.write(msg)
                
                st.caption(f"📅 {_fmt_dt(n.get('created_at'))} • Tipo: {n.get('event_type')}")

            with col_btn:
                # El botón ahora solo actualiza la memoria de Streamlit
                if not is_read:
                    if st.button("Marcar leída", key=f"read_{n.get('id')}", use_container_width=True):
                        st.session_state["local_read_notifs"].add(n.get("id"))
                        st.rerun()
                else:
                    st.write("✅ Vista")