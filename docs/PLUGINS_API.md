# Plugins Proxy API - Python SDK

## Overview

The `plugins` helper forwards HTTP requests from the Python SDK to the Go backend, which then proxies them to your Python plugin (the target is set with `PLUGIN_URL` in `docker-compose`). It works with the standard HTTP verbs and does not require user or superuser authentication.

**Key points**
- Supports `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`, plus `SSE` and `WEBSOCKET` helpers.
- Paths are routed through `/api/plugins/{your-plugin-path}` (leading slashes are trimmed; `/api/plugins/...` is accepted as-is).
- Query params, request bodies, and headers are passed through unchanged to the plugin service.
- Public endpoint—no auth required (the SDK will still include your auth token if one is set).

## Quick start

```python
from bosbase import BosBase

pb = BosBase("http://127.0.0.1:8080")

# Simple GET to your plugin (e.g., FastAPI /health)
health = pb.plugins("GET", "/health")

print(health)  # {"status": "ok"}
```

## Send bodies and headers

```python
pb.plugins("POST", "tasks", body={
    "title": "Generate docs",
    "priority": "high"
}, headers={"X-Plugin-Key": "demo-secret"})
```

## Work with query parameters

```python
summary = pb.plugins("GET", "reports/summary", query={
    "since": "2024-01-01",
    "limit": 50,
    "tags": ["ops", "ml"]
})
```

## Other verbs

```python
# Update
pb.plugins("PATCH", "tasks/42", body={"status": "done"})

# Delete
pb.plugins("DELETE", "tasks/42")

# Check liveness without a body
pb.plugins("HEAD", "health")

# Discover plugin-supported methods
pb.plugins("OPTIONS", "tasks")
```

## Server-Sent Events (SSE)

Use the `SSE` method to open an SSE stream to your plugin (query params are appended automatically). When an auth token is present it is sent as `?token=...`.

```python
def on_event(event):
    print("update:", event.data)

def on_end(event):
    pass  # stream ended

stream = pb.plugins("SSE", "events/updates",
    query={"topic": "team-alpha"},
    headers={"X-Plugin-Key": "secret"},
    on_message=on_event,
    on_end=on_end
)

# Remember to close when done
stream.close()
```

## WebSockets

Use the `WEBSOCKET` (or `WS`) method to open a WebSocket to your plugin. The SDK converts your base URL to `ws://`/`wss://`, preserves query params, and appends `token` if you are authenticated.

```python
import json

def on_open(ws):
    ws.send(json.dumps({"type": "join", "name": "lea"}))

def on_message(ws, message):
    print("chat message:", message)

def on_error(ws, error):
    print("error:", error)

socket = pb.plugins("WEBSOCKET", "ws/chat",
    query={"room": "general"},
    websocket_protocols=["json"],
    headers={"X-Plugin-Key": "secret"},
    on_open=on_open,
    on_message=on_message,
    on_error=on_error
)
```

## Notes and behavior
- Implemented SSE and WebSocket support on plugins, forwarding via /api/plugins, preserving query params, and now passing headers to EventSource/WebSocket constructors when supported.
- Requests are sent to `/api/plugins/...` on the Go backend, which forwards them to the Python plugin service.
- All request options are supported: `headers`, `body`, `query`, and custom options.
- Body serialization follows the normal client rules; set `Content-Type` yourself when you need a different encoding.
- Because the endpoint is public, add any plugin-side checks you need (tokens, IP allowlists, etc.) without changing the SDK.
- When a user token is present, SSE/WebSocket URLs include `?token=...` so your plugin can still authenticate the caller.
