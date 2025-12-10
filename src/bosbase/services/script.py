"""Script management APIs."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional

from .base import BaseService
from ..utils import encode_path_segment


class ScriptService(BaseService):
    """Manage and execute scripts (superuser only)."""

    def create(
        self,
        name: str,
        content: str,
        *,
        description: Optional[str] = None,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> dict:
        if not name or not name.strip():
            raise ValueError("script name is required")
        if not content or not content.strip():
            raise ValueError("script content is required")

        payload = dict(body or {})
        payload.setdefault("name", name.strip())
        payload.setdefault("content", content.strip())
        if description is not None:
            payload.setdefault("description", description)

        return self.client.send(
            "/api/scripts",
            method="POST",
            body=payload,
            query=query,
            headers=headers,
        )

    def command(
        self,
        command: str,
        *,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> dict:
        if not command or not command.strip():
            raise ValueError("command is required")
        payload = dict(body or {})
        payload.setdefault("command", command.strip())
        return self.client.send(
            "/api/scripts/command",
            method="POST",
            body=payload,
            query=query,
            headers=headers,
        )

    def get(
        self,
        name: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> dict:
        normalized = self._normalize_name(name)
        return self.client.send(
            f"/api/scripts/{encode_path_segment(normalized)}",
            query=query,
            headers=headers,
        )

    def list(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> list[dict]:
        data = self.client.send("/api/scripts", query=query, headers=headers)
        items = data.get("items", []) if isinstance(data, dict) else data or []
        return list(items)

    def update(
        self,
        name: str,
        *,
        content: Optional[str] = None,
        description: Optional[str] = None,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> dict:
        if content is None and description is None:
            raise ValueError("content or description must be provided")
        normalized = self._normalize_name(name)
        payload = dict(body or {})
        if content is not None:
            payload["content"] = content
        if description is not None:
            payload["description"] = description

        return self.client.send(
            f"/api/scripts/{encode_path_segment(normalized)}",
            method="PATCH",
            body=payload,
            query=query,
            headers=headers,
        )

    def execute(
        self,
        name: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> dict:
        normalized = self._normalize_name(name)
        return self.client.send(
            f"/api/scripts/{encode_path_segment(normalized)}/execute",
            method="POST",
            query=query,
            headers=headers,
        )

    def delete(
        self,
        name: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        normalized = self._normalize_name(name)
        self.client.send(
            f"/api/scripts/{encode_path_segment(normalized)}",
            method="DELETE",
            query=query,
            headers=headers,
        )

    def _normalize_name(self, name: str) -> str:
        if not name or not name.strip():
            raise ValueError("script name is required")
        return name.strip()
