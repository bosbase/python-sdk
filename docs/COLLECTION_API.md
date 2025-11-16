# Collection API - Python SDK

The Collection API exposes the same admin endpoints that power the dashboard. Use it for migrations, seed scripts, or CI pipelines.

## Listing Collections

```python
collections = pb.collections.get_list(page=1, per_page=50)
for item in collections["items"]:
    print(item["name"], item["type"])
```

`get_full_list()` fetches all collections in batches, which is useful for snapshots.

## Creating Collections

### Manual Definition

```python
collection = pb.collections.create(
    body={
        "name": "projects",
        "type": "base",
        "schema": [
            {"name": "title", "type": "text", "required": True},
            {"name": "owner", "type": "relation", "collectionId": "users"},
        ],
        "options": {},
    },
)
```

### Using Scaffolds

```python
pb.collections.create_base("articles")
pb.collections.create_auth("customers")
pb.collections.create_view("recent_posts", view_query="SELECT * FROM posts")
```

## Updating Collections

```python
pb.collections.update(
    "articles",
    body={
        "listRule": 'status = "published" || @request.auth.role = "editor"',
        "schema": [
            {"name": "status", "type": "select", "options": {"values": ["draft", "published"]}},
        ],
    },
)
```

Partial updates merge with the existing schema. For field-level helpers see `COLLECTIONS.md`.

## Delete & Truncate

```python
pb.collections.delete_collection("unused")
pb.collections.truncate("logs")  # delete records, keep schema
```

## Import / Export

```python
snapshot = pb.collections.get_full_list()

pb.collections.import_collections(
    collections=snapshot,
    delete_missing=True,
)
```

- `delete_missing=True` removes collections not present in the import payload.
- Use this inside migrations to sync environments.

## Settings and Metadata

`get_scaffolds()` returns the default JSON definitions for base/auth/view collections. You can inspect them to understand required fields.

`get_schema(name)` returns the light-weight schema info for a single collection.

## Tips

1. Keep versioned snapshots of the schema for diffing between environments.
2. Use `truncate()` inside tests to reset state quickly.
3. The API requires superuser credentials. Authenticate with `_superusers` before invoking collection management calls.
4. When migrating production data, use `import_collections(..., delete_missing=False)` to avoid unintentional drops.
