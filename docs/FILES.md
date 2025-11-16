# Files - Python SDK

File handling is unified across all BosBase services. You use multipart/form-data to upload files and the File API to create secure download links.

## Uploading Files with Records

Pass a `files` dict to `create` or `update`.

```python
with open("avatar.jpg", "rb") as fh:
    pb.collection("users").update(
        "RECORD_ID",
        body={"name": "Jane"},
        files={"avatar": ("avatar.jpg", fh, "image/jpeg")},
    )
```

Multiple files can be uploaded in one request by including several entries in the dict or by sharing the same field name with a list of tuples.

## Direct File Uploads

Use the Files API when you only need to update the file content:

```python
files_service = pb.files

record = pb.collection("documents").get_one("doc123")

with open("updated.pdf", "rb") as fh:
    files_service.get_url(record, "attachment.pdf")  # builds download URL
```

## Building File URLs

```python
url = pb.files.get_url(
    record,
    "cover.png",
    thumb="300x300",
    query={"token": "optionalTemporaryToken"},
)
```

- `thumb` accepts thumbnail presets or raw resizing strings (`600x400`).
- `download=True` forces a download response.
- `token` attaches a private file token (see below).

## Private File Tokens

Generate time-limited tokens tied to the current auth record:

```python
token = pb.files.get_token()

secure_url = pb.files.get_url(
    record,
    "invoice.pdf",
    token=token,
)
```

Tokens expire according to the auth collection settings.

## Handling Protected Files in Batches

When building URLs for exported data, reuse the `get_url` helper:

```python
orders = pb.collection("orders").get_full_list(query={"expand": "customer"})
token = pb.files.get_token()

download_links = [
    pb.files.get_url(order, "receipt.pdf", token=token)
    for order in orders
    if order.get("receipt")
]
```

## Tips

- Always send files as binary mode (`"rb"`).
- When uploading large files wrap the file object with `io.BufferedReader` to benefit from streaming.
- Use thumbnails for previews rather than storing separate preview fields.
- Generate download URLs server-side if you need to sign them with a privileged token; otherwise `get_url` can be called by the client directly.
