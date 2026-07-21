"""Small API client for the Streamlit frontend."""

from __future__ import annotations

import os
from typing import Any

import httpx


class APIClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("REBOOTX_API_BASE_URL", "http://127.0.0.1:8000")).rstrip("/")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            response = client.request(method, f"{self.base_url}{path}", json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(f"Request failed ({response.status_code}): {response.text}") from exc
            return response.json()

    def get_health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def assess_upgrade(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/assess-upgrade", payload)

    def capture_upgrade(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/capture-upgrade", payload)

    def get_knowledge_stats(self) -> dict[str, Any]:
        return self._request("GET", "/api/v1/knowledge/stats")

    def reload_knowledge(self) -> dict[str, Any]:
        return self._request("POST", "/api/v1/reload-knowledge")


def get_api_base_url() -> str:
    return os.getenv("REBOOTX_API_BASE_URL", "http://127.0.0.1:8000")
