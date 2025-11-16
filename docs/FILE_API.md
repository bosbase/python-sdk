# File API - Python SDK

In addition to uploading files through record mutations, BosBase exposes a dedicated File API for generating signed URLs and serving files.

## Download URLs

```python
files = pb.files
record = pb.collection("documents").get_one("doc123")

public_url = files.get_url(record, "manual.pdf")
```

`get_url` automatically encodes the collection name, record ID, and filename.

### Thumbnails

Add a `thumb` parameter to request dynamic thumbnails:

```python
thumb_url = files.get_url(record, "cover.png", thumb="300x300")
```

### Forced Download

```python
download = files.get_url(record, "backup.zip", download=True)
```

## File Tokens

Protected files require a temporary token tied to the authenticated record.

```python
token = files.get_token()
secure_url = files.get_url(record, "invoice.pdf", token=token)
```

Tokens follow the configuration under *Auth Collection → File tokens*. They expire automatically; request new tokens when needed.

## Serving Files from Backups

When generating download links inside automation scripts:

```python
token = files.get_token()
backups = pb.backups.get_full_list()

links = [
    pb.backups.get_download_url(token, backup["key"])
    for backup in backups
]
```

## Tips

1. Generate the token on the server and forward the URL to clients if you do not want clients to know about the API base URL.
2. Combine `token` + `thumb` for secure preview images.
3. The URLs can be safely cached because they include the token and filename; once the token expires the link stops working.
4. Use HTTPS when exposing URLs to the public internet—BosBase does not add TLS itself.
