from __future__ import annotations
from typing import Any, Dict, List, Optional
import streamlit as st

from api_client import ApiError, get_notifications

SESSION_TOKEN = "token"


def _token() -> Optional[str]:
    return st.session_state.get(SESSION_TOKEN)


def _fmt_dt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, str):
        return value[:19].replace("T", " ") if len(value) >= 19 else value
    return str(value)


def _read_label(status: Optional[str]) -> str:
    if (status or "").upper() == "READ":
        return "Leída"
    return "No leída"


def show_notification_list() -> None:
    """
    Lista notificaciones con mensaje, fecha y estado leída/no leída.
    """
    token = _token()
    if not token:
        st.warning("Sesión no válida.")
        return

    unread_only = st.checkbox("Mostrar solo no leídas", value=False)

    try:
        rows: List[Dict[str, Any]] = get_notifications(
            token, unread_only=unread_only
        )
    except ApiError as exc:
        st.error(exc.message)
        return

    if not rows:
        st.info("No hay notificaciones para mostrar.")
        return

    slim = [
        {
            "mensaje": (n.get("message") or "")[:500],
            "fecha": _fmt_dt(n.get("created_at")),
            "estado": _read_label(n.get("status")),
        }
        for n in rows
    ]

    st.dataframe(
        slim,
        use_container_width=True,
        hide_index=True,
        column_config={
            "mensaje": st.column_config.TextColumn("Mensaje", width="large"),
            "fecha": "Fecha",
            "estado": "Estado",
        },
    )
