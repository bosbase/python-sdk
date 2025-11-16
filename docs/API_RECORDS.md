# Records API - Python SDK

The Records API provides CRUD access to collection data. Every record operation hangs off a `RecordService` returned by `pb.collection("<name>")`.

```python
from bosbase import BosBase

pb = BosBase("http://127.0.0.1:8090")
pb.collection("_superusers").auth_with_password("admin@example.com", "password")

posts = pb.collection("posts")
```

## Listing Records

```python
result = posts.get_list(page=1, per_page=20, query={"sort": "-created"})
for record in result["items"]:
    print(record["title"])
```

- `get_full_list()` fetches everything in batches (client-side pagination).
- `get_first_list_item(filter=...)` returns the first match or raises a 404 error.

## Filtering and Sorting

```python
expr = pb.filter(
    '(status = {:status} && published >= {:start}) || tags @> {:highlight}',
    {"status": "published", "start": "2024-01-01 00:00:00", "highlight": "launch"},
)

records = posts.get_list(
    page=1,
    per_page=5,
    query={"filter": expr, "sort": "-published", "expand": "author"},
)
```

## Retrieving Records

```python
record = posts.get_one("RECORD_ID", query={"expand": "author,comments"})
count = posts.get_count(filter="status = 'published'")
```

## Creating Records

```python
article = posts.create(
    body={
        "title": "Hello from Python",
        "status": "draft",
    },
)
```

### File Uploads

Provide a dict of file tuples (`(filename, fileobj, content_type)`):

```python
with open("cover.png", "rb") as fh:
    posts.create(
        body={"title": "With cover"},
        files={"cover": ("cover.png", fh, "image/png")},
    )
```

## Updating & Deleting

```python
posts.update("RECORD_ID", body={"status": "published"})
posts.delete("RECORD_ID")
```

When you update/delete the authenticated record, the auth store is automatically kept in sync.

## Auth Collections

`RecordService` contains all auth-specific helpers when the collection is auth-enabled:

```python
users = pb.collection("users")

auth_data = users.auth_with_password("demo@example.com", "secret")

users.request_password_reset("demo@example.com")
users.confirm_password_reset(token, "newPass", "newPass")

otp = users.request_otp("demo@example.com")
auth_data = users.auth_with_otp(otp["otpId"], "123456")

auth_data = users.auth_refresh()
users.request_verification("demo@example.com")
users.confirm_verification(token)

impersonated = users.impersonate("TARGET_ID", duration=300)
print(impersonated.auth_store.token)
```

OAuth2 helper:

```python
def open_browser(url: str) -> None:
    print("Open in browser:", url)

auth_data = users.auth_with_oauth2(
    "google",
    url_callback=open_browser,
    scopes=["profile", "email"],
)
```

## Batch Operations

Use `pb.create_batch()` for transactional multi-collection writes:

```python
batch = pb.create_batch()

batch.collection("posts").create(body={"title": "from batch"})
batch.collection("posts").update("abc123", body={"title": "edited"})
batch.collection("comments").delete("comment123")

results = batch.send()
for res in results:
    print(res["status"])
```

## Tips

- Always request only needed relations via `expand` to minimize payloads.
- Reuse filters and sort orders between SDK and dashboard for consistency.
- Combine `get_list(skip_total=True)` for cheap infinite scrolling.
- Use `query={"fields": "id,title"}` when building search indexes to limit data transfer.
