from __future__ import annotations
import os
import requests
from typing import Any, Dict, List, Optional

DEFAULT_BASE_URL = "http://api:8000"

def _base_url() -> str:
    return os.environ.get("API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")

class ApiError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def _detail_from_response(response: requests.Response) -> str:
    try:
        payload = response.json()
        detail = payload.get("detail")
        if isinstance(detail, list):
            return "; ".join(str(x.get("msg", x)) if isinstance(x, dict) else str(x) for x in detail)
        return str(detail or response.reason)
    except:
        return response.text or "Error desconocido"

def _request_json(method: str, path: str, **kwargs) -> Any:
    url = f"{_base_url()}{path}"
    token = kwargs.pop("token", None)
    headers = kwargs.pop("headers", {"Accept": "application/json"})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.request(method, url, headers=headers, timeout=10, **kwargs)
        if response.status_code == 404 and kwargs.get("allow_404"): return None
        if not response.ok: raise ApiError(_detail_from_response(response), response.status_code)
        return response.json() if response.content else None
    except requests.RequestException as e:
        raise ApiError(f"Error de conexión: {e}")

def login(email, password):
    res = _request_json("POST", "/login", json={"email": email, "password": password})
    return res["access_token"]

def get_current_user(token):
    return _request_json("GET", "/me", token=token)

def get_incidents(token, params=None):
    return _request_json("GET", "/incidents", token=token, params=params)

def get_incident(token, incident_id):
    return _request_json("GET", f"/incidents/{incident_id}", token=token)

def create_incident(token, data):
    return _request_json("POST", "/incidents", token=token, json=data)

def get_tasks(token):
    return _request_json("GET", "/tasks", token=token)

def update_task_status(token, task_id, status):
    return _request_json("PATCH", f"/tasks/{task_id}/status", token=token, json={"status": status})

def get_notifications(token, unread_only=False):
    params = {"unread_only": "true"} if unread_only else None
    return _request_json("GET", "/notifications", token=token, params=params) or []

def assign_incident(token, incident_id, assigned_to):
    return _request_json("PATCH", f"/incidents/{incident_id}/assign", token=token, json={"assigned_to": assigned_to})

def update_incident_status(token, incident_id, status):
    return _request_json("PATCH", f"/incidents/{incident_id}/status", token=token, json={"status": status})

def create_task(token, data):
    return _request_json("POST", "/tasks", token=token, json=data)