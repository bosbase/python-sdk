"""Authentication store helpers."""

from __future__ import annotations

import base64
import json
import threading
from typing import Any, Callable, Dict, Optional


class AuthStore:
    """In-memory authentication store shared across services."""

    def __init__(self) -> None:
        self._token: str = ""
        self._record: Optional[Dict[str, Any]] = None
        self._lock = threading.RLock()
        self._listeners: list[Callable[[str, Optional[Dict[str, Any]]], None]] = []

    @property
    def token(self) -> str:
        return self._token

    @property
    def record(self) -> Optional[Dict[str, Any]]:
        return self._record

    def is_valid(self) -> bool:
        """Return True when a non-expired JWT token is stored."""
        token = self._token
        if not token:
            return False

        parts = token.split(".")
        if len(parts) != 3:
            return False

        try:
            payload_part = parts[1] + "=" * (-len(parts[1]) % 4)
            payload_raw = base64.urlsafe_b64decode(payload_part.encode("utf-8"))
            payload = json.loads(payload_raw.decode("utf-8"))
        except Exception:
            return False

        exp = payload.get("exp")
        if exp is None:
            return False

        try:
            exp_value = int(exp)
        except (TypeError, ValueError):
            return False

        import time

        return exp_value > int(time.time())

    def add_listener(
        self, callback: Callable[[str, Optional[Dict[str, Any]]], None]
    ) -> None:
        with self._lock:
            self._listeners.append(callback)

    def remove_listener(
        self, callback: Callable[[str, Optional[Dict[str, Any]]], None]
    ) -> None:
        with self._lock:
            if callback in self._listeners:
                self._listeners.remove(callback)

    def save(self, token: str, record: Optional[Dict[str, Any]]) -> None:
        with self._lock:
            self._token = token or ""
            self._record = record
            listeners = list(self._listeners)

        for listener in listeners:
            try:
                listener(self._token, self._record)
            except Exception:
                # best-effort notification
                pass

    def clear(self) -> None:
        self.save("", None)
