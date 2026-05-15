# Redis API - Python SDK

Redis support is powered by [rueidis](https://github.com/redis/rueidis) and is **disabled unless `REDIS_URL` is provided** on the server. `REDIS_PASSWORD` is optional for instances that don't use auth. Routes are superuser-only; regular users and misconfigured nodes simply won't expose the endpoints.

- Set `REDIS_URL` (eg. `redis://redis:6379` or `rediss://cache:6379`). Optionally set `REDIS_PASSWORD`.
- Authenticate as a superuser before calling the Redis endpoints.
- When `ttl_seconds` is omitted during updates, the existing TTL is preserved. Use `ttl_seconds=0` to remove a TTL, or a positive value to set a new one.

## Discover keys

```python
from bosbase import BosBase

pb = BosBase("http://127.0.0.1:8090")
pb.collection("_superusers").auth_with_password("root@example.com", "hunter2")

# Scan keys with an optional cursor, match pattern, and count hint.
page = pb.redis.list_keys(pattern="session:*", count=100)
print(page["cursor"])  # pass this back into list_keys to continue scanning
print(page["items"])   # [{"key": "session:123"}, ...]
```

## Create, read, update, delete keys

```python
# Create a key if it does NOT already exist.
pb.redis.create_key({
    "key": "session:123",
    "value": {"prompt": "hello", "tokens": 42},
    "ttlSeconds": 3600,  # optional
})

# Read the value back with the current TTL (if any).
entry = pb.redis.get_key("session:123")
print(entry["value"], entry.get("ttlSeconds"))  # ttlSeconds is absent when the key is persistent

# Update an existing key (preserves TTL when ttlSeconds is omitted).
pb.redis.update_key("session:123", {
    "value": {"prompt": "updated", "tokens": 99},
    # "ttlSeconds": 0    # uncomment to remove TTL
    # "ttlSeconds": 120  # or set a new TTL
})

# Delete the key.
pb.redis.delete_key("session:123")
```

API responses:
- `list_keys` returns `{"cursor": str, "items": [{"key": str}, ...]}`.
- `create_key`, `get_key`, and `update_key` return `{"key": ..., "value": ..., "ttlSeconds": ...}` (ttlSeconds may be absent).
- `create_key` fails with HTTP 409 if the key already exists.
