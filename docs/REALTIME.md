# Realtime API - Python SDK

BosBase exposes realtime change feeds over Server-Sent Events (SSE). The Python SDK manages the SSE connection in a background thread and automatically resubscribes after reconnects.

## Basic Usage

```python
def on_post_update(event):
    print(event["action"], event["record"]["title"])

unsubscribe = pb.collection("posts").subscribe("*", on_post_update)

# Later
unsubscribe()
```

- Topic `"*"` listens to all records.
- Use a record ID to watch a single record: `subscribe("RECORD_ID", callback)`.

## Subscription Options

Each subscription can include query params or headers (used by API rules):

```python
unsubscribe = pb.collection("posts").subscribe(
    "*",
    on_post_update,
    query={
        "filter": pb.filter("status = {:status}", {"status": "published"}),
        "expand": "author",
    },
    headers={"X-App-Instance": "cli"},
)
```

## PB_CONNECT Event

The SDK automatically listens for the `PB_CONNECT` event and stores the server-assigned `clientId`. If you want to react to reconnects, set `pb.realtime.on_disconnect`.

```python
def handle_disconnect(active_topics):
    if active_topics:
        print("Connection lost, waiting for auto-reconnect…")
    else:
        print("No active subscriptions; connection closed.")

pb.realtime.on_disconnect = handle_disconnect
```

## Custom Realtime Topics

 `pb.realtime` can subscribe to raw topics for custom realtime events emitted by server hooks.

```python
def on_job(event):
    print(event)

pb.realtime.subscribe("jobs/finished", on_job)
```

## Unsubscribing

- `unsubscribe(topic)` removes every listener for that topic.
- `unsubscribe_by_prefix("posts/")` removes all collection listeners.
- The returned callable from `subscribe()` removes the specific listener only.

```python
pb.collection("posts").unsubscribe("RECORD_ID")
pb.realtime.unsubscribe()  # remove every topic
```

## Threading Notes

- Callbacks execute on the SSE thread. If you mutate shared state, protect it with locks.
- The SSE loop automatically restarts unless all subscriptions are removed.

## Tips

1. Always expand required relations in the subscription query; event payloads do not re-fetch data.
2. Use `filter` query params to reduce server load and network traffic.
3. Combine realtime events with local caches to keep UI lists in sync.
4. When using OAuth2 auth flows, the SDK internally subscribes to the `@oauth2` topic and cleans it up automatically—no manual action required.
