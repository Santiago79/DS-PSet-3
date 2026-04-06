from __future__ import annotations

import os
import requests
from typing import Any, Dict, List, Optional

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def _base_url() -> str:
    return os.environ.get("API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _auth_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


class ApiError(Exception):
    #Error devuelto por la API o fallo de red
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _detail_from_response(response: requests.Response) -> str:
    try:
        payload = response.json()
        detail = payload.get("detail")
        if detail is None:
            return response.text or response.reason
        if isinstance(detail, list):
            return "; ".join(
                str(x.get("msg", x)) if isinstance(x, dict) else str(x) for x in detail
            )
        return str(detail)
    except Exception:
        return response.text or response.reason or "Error desconocido"


def _request_json(
    method: str,
    path: str,
    *,
    token: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    allow_404: bool = False,
) -> Any:
    url = f"{_base_url()}{path}"
    headers: Dict[str, str] = {"Accept": "application/json"}
    if json_body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json_body,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise ApiError(f"No se pudo conectar con la API: {exc}") from exc

    if allow_404 and response.status_code == 404:
        return None

    if not response.ok:
        raise ApiError(_detail_from_response(response), response.status_code)

    if response.status_code == 204 or not response.content:
        return None

    return response.json()


def login(email: str, password: str) -> str:
    # Autentica al usuario y devuelve el JWT (access_token)
    data = _request_json(
        "POST",
        "/login",
        json_body={"email": email, "password": password},
    )
    if not isinstance(data, dict) or "access_token" not in data:
        raise ApiError("Respuesta de login inválida")
    return str(data["access_token"])


def get_current_user(token: str) -> Dict[str, Any]:
    # Perfil del usuario autenticado
    data = _request_json("GET", "/me", token=token)
    if not isinstance(data, dict):
        raise ApiError("Respuesta de /me inválida")
    return data


def get_incidents(token: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    # Lista de incidentes (query params opcionales, ej. skip, limit)
    params = {k: v for k, v in (filters or {}).items() if v is not None}
    data = _request_json("GET", "/incidents", token=token, params=params or None)
    if not isinstance(data, list):
        raise ApiError("Respuesta de incidentes inválida")
    return data


def create_incident(token: str, data: Dict[str, Any]) -> Dict[str, Any]:
    # Crea un incidente (title, description, severity)
    result = _request_json("POST", "/incidents", token=token, json_body=data)
    if not isinstance(result, dict):
        raise ApiError("Respuesta de creación de incidente inválida")
    return result


def get_tasks(token: str) -> List[Dict[str, Any]]:
    # Lista de tareas según rol
    data = _request_json("GET", "/tasks", token=token)
    if not isinstance(data, list):
        raise ApiError("Respuesta de tareas inválida")
    return data


def update_task_status(token: str, task_id: str, status: str) -> Dict[str, Any]:
    # Actualiza el estado de una tarea
    result = _request_json(
        "PATCH",
        f"/tasks/{task_id}/status",
        token=token,
        json_body={"status": status},
    )
    if not isinstance(result, dict):
        raise ApiError("Respuesta de actualización de tarea inválida")
    return result


def get_notifications(
    token: str,
    *,
    unread_only: bool = False,
) -> List[Dict[str, Any]]:
    # GET /notifications — filtro unread_only según query de la API
    params: Optional[Dict[str, Any]] = None
    if unread_only:
        params = {"unread_only": "true"}
    result = _request_json(
        "GET",
        "/notifications",
        token=token,
        params=params,
        allow_404=True,
    )
    if result is None:
        return []
    if not isinstance(result, list):
        raise ApiError("Respuesta de notificaciones inválida")
    return result


def assign_incident(token: str, incident_id: str, assigned_to: str) -> Dict[str, Any]:
    result = _request_json(
        "PATCH",
        f"/incidents/{incident_id}/assign",
        token=token,
        json_body={"assigned_to": assigned_to},
    )
    if not isinstance(result, dict):
        raise ApiError("Respuesta de asignación inválida")
    return result


def update_incident_status(token: str, incident_id: str, status: str) -> Dict[str, Any]:
    result = _request_json(
        "PATCH",
        f"/incidents/{incident_id}/status",
        token=token,
        json_body={"status": status},
    )
    if not isinstance(result, dict):
        raise ApiError("Respuesta de cambio de estado inválida")
    return result


def create_task(token: str, data: Dict[str, Any]) -> Dict[str, Any]:
    result = _request_json("POST", "/tasks", token=token, json_body=data)
    if not isinstance(result, dict):
        raise ApiError("Respuesta de creación de tarea inválida")
    return result