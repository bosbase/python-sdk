# AI Development Guide - Python SDK

This guide provides a comprehensive, fast reference for AI systems to quickly develop applications using the BosBase Python SDK. All examples are production-ready and follow best practices.

## Table of Contents

1. [Authentication](#authentication)
2. [Initialize Collections](#initialize-collections)
3. [Define Collection Fields](#define-collection-fields)
4. [Add Data to Collections](#add-data-to-collections)
5. [Modify Collection Data](#modify-collection-data)
6. [Delete Data from Collections](#delete-data-from-collections)
7. [Query Collection Contents](#query-collection-contents)
8. [Add and Delete Fields from Collections](#add-and-delete-fields-from-collections)
9. [Query Collection Field Information](#query-collection-field-information)
10. [Upload Files](#upload-files)
11. [Query Logs](#query-logs)
12. [Send Emails](#send-emails)

---

## Authentication

### Initialize Client

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")
```

### Password Authentication

```python
# Authenticate with email/username and password
auth_data = pb.collection("users").auth_with_password(
    "user@example.com",
    "password123"
)

# Auth data is automatically stored
print(pb.auth_store.is_valid())  # True
print(pb.auth_store.token)       # JWT token
print(pb.auth_store.record)      # User record
```

### OAuth2 Authentication

```python
# Get OAuth2 providers
methods = pb.collection("users").list_auth_methods()
print(methods["oauth2"]["providers"])  # Available providers

# Authenticate with OAuth2
def open_url(url: str):
    # Open OAuth2 URL in browser
    import webbrowser
    webbrowser.open(url)

auth_data = pb.collection("users").auth_with_oauth2(
    "google",
    url_callback=open_url,
)
```

### OTP Authentication

```python
# Request OTP
otp_response = pb.collection("users").request_verification("user@example.com")

# Authenticate with OTP
auth_data = pb.collection("users").auth_with_otp(
    otp_response["otpId"],
    "123456"  # OTP code
)
```

### Check Authentication Status

```python
if pb.auth_store.is_valid():
    print("Authenticated as:", pb.auth_store.record["email"])
else:
    print("Not authenticated")
```

### Logout

```python
pb.auth_store.clear()
```

---

## Initialize Collections

### Create Base Collection

```python
collection = pb.collections.create(body={
    "name": "posts",
    "type": "base",
    "fields": [
        {
            "name": "title",
            "type": "text",
            "required": True,
        },
    ],
})

print("Collection ID:", collection["id"])
```

### Create Auth Collection

```python
auth_collection = pb.collections.create(body={
    "name": "users",
    "type": "auth",
    "fields": [
        {
            "name": "name",
            "type": "text",
            "required": False,
        },
    ],
    "passwordAuth": {
        "enabled": True,
        "identityFields": ["email", "username"],
    },
})
```

### Create View Collection

```python
view_collection = pb.collections.create(body={
    "name": "published_posts",
    "type": "view",
    "viewQuery": "SELECT * FROM posts WHERE published = true",
})
```

### Get Collection by ID or Name

```python
collection = pb.collections.get_one("posts")
# or by ID
collection = pb.collections.get_one("_pbc_2287844090")
```

---

## Define Collection Fields

### Add Field to Collection

```python
updated_collection = pb.collections.add_field("posts", {
    "name": "content",
    "type": "editor",
    "required": False,
})
```

### Common Field Types

```python
# Text field
{
    "name": "title",
    "type": "text",
    "required": True,
    "min": 10,
    "max": 255,
}

# Number field
{
    "name": "views",
    "type": "number",
    "required": False,
    "min": 0,
}

# Boolean field
{
    "name": "published",
    "type": "bool",
    "required": False,
}

# Date field
{
    "name": "published_at",
    "type": "date",
    "required": False,
}

# File field
{
    "name": "avatar",
    "type": "file",
    "required": False,
    "maxSelect": 1,
    "maxSize": 2097152,  # 2MB
    "mimeTypes": ["image/jpeg", "image/png"],
}

# Relation field
{
    "name": "author",
    "type": "relation",
    "required": True,
    "collectionId": "_pbc_users_auth_",
    "maxSelect": 1,
}

# Select field
{
    "name": "status",
    "type": "select",
    "required": True,
    "options": {
        "values": ["draft", "published", "archived"],
    },
}
```

### Update Field

```python
updated_collection = pb.collections.update_field("posts", "title", {
    "max": 500,
    "required": True,
})
```

### Remove Field

```python
updated_collection = pb.collections.remove_field("posts", "old_field")
```

---

## Add Data to Collections

### Create Single Record

```python
record = pb.collection("posts").create(body={
    "title": "My First Post",
    "content": "This is the content",
    "published": True,
})

print("Created record ID:", record["id"])
```

### Create Record with File Upload

```python
with open("image.jpg", "rb") as fh:
    record = pb.collection("posts").create(
        body={"title": "Post with Image"},
        files={"image": ("image.jpg", fh, "image/jpeg")}
    )
```

### Create Record with Relations

```python
record = pb.collection("posts").create(body={
    "title": "My Post",
    "author": "user_record_id",      # Related record ID
    "categories": ["cat1_id", "cat2_id"],  # Multiple relations
})
```

### Batch Create Records

```python
batch = pb.create_batch()
batch.collection("posts").create(body={"title": "Post 1"})
batch.collection("posts").create(body={"title": "Post 2"})
results = batch.send()
```

---

## Modify Collection Data

### Update Single Record

```python
updated = pb.collection("posts").update("record_id", body={
    "title": "Updated Title",
    "content": "Updated content",
})
```

### Update Record with File

```python
with open("new_image.jpg", "rb") as fh:
    updated = pb.collection("posts").update(
        "record_id",
        body={"title": "Updated Title"},
        files={"image": ("new_image.jpg", fh, "image/jpeg")}
    )
```

### Partial Update

```python
# Only update specific fields
updated = pb.collection("posts").update("record_id", body={
    "views": 100,  # Only update views
})
```

---

## Delete Data from Collections

### Delete Single Record

```python
pb.collection("posts").delete("record_id")
```

### Delete Multiple Records

```python
# Using batch
batch = pb.create_batch()
batch.collection("posts").delete("record_id_1")
batch.collection("posts").delete("record_id_2")
batch.send()
```

### Delete All Records (Truncate)

```python
pb.collections.truncate("posts")
```

---

## Query Collection Contents

### List Records with Pagination

```python
result = pb.collection("posts").get_list(1, 50)

print(result["page"])        # 1
print(result["perPage"])     # 50
print(result["totalItems"])  # Total count
print(result["items"])       # List of records
```

### Filter Records

```python
result = pb.collection("posts").get_list(1, 50, query={
    "filter": "published = true && views > 100",
    "sort": "-created",
})
```

### Filter Operators

```python
# Equality
filter_expr = 'status = "published"'

# Comparison
filter_expr = "views > 100"
filter_expr = 'created >= "2023-01-01"'

# Text search
filter_expr = 'title ~ "python"'

# Multiple conditions
filter_expr = 'status = "published" && views > 100'
filter_expr = 'status = "draft" || status = "pending"'

# Relation filter
filter_expr = 'author.id = "user_id"'
```

### Sort Records

```python
# Single field
sort = "-created"  # DESC
sort = "title"     # ASC

# Multiple fields
sort = "-created,title"  # DESC by created, then ASC by title
```

### Expand Relations

```python
result = pb.collection("posts").get_list(1, 50, query={
    "expand": "author,categories",
})

# Access expanded data
for post in result["items"]:
    print(post["expand"]["author"]["name"])
    print(post["expand"]["categories"])
```

### Get Single Record

```python
record = pb.collection("posts").get_one("record_id", query={
    "expand": "author",
})
```

### Get First Matching Record

```python
record = pb.collection("posts").get_first_list_item(
    'slug = "my-post-slug"',
    query={"expand": "author"}
)
```

### Get All Records

```python
all_records = pb.collection("posts").get_full_list(query={
    "filter": "published = true",
    "sort": "-created",
})
```

---

## Add and Delete Fields from Collections

### Add Field

```python
collection = pb.collections.add_field("posts", {
    "name": "tags",
    "type": "select",
    "options": {
        "values": ["tech", "science", "art"],
    },
})
```

### Update Field

```python
collection = pb.collections.update_field("posts", "tags", {
    "options": {
        "values": ["tech", "science", "art", "music"],
    },
})
```

### Remove Field

```python
collection = pb.collections.remove_field("posts", "old_field")
```

### Get Field Information

```python
field = pb.collections.get_field("posts", "title")
print(field["type"], field["required"], field.get("options"))
```

---

## Query Collection Field Information

### Get All Fields for a Collection

```python
collection = pb.collections.get_one("posts")
for field in collection["fields"]:
    print(field["name"], field["type"], field.get("required"))
```

### Get Collection Schema (Simplified)

```python
schema = pb.collections.get_schema("posts")
print(schema["fields"])  # List of field info
```

### Get All Collection Schemas

```python
schemas = pb.collections.get_all_schemas()
for collection in schemas["collections"]:
    print(collection["name"], collection["fields"])
```

### Query Field Information for Single Collection

```python
# Method 1: Get full collection
collection = pb.collections.get_one("posts")
title_field = next((f for f in collection["fields"] if f["name"] == "title"), None)

# Method 2: Get specific field
field = pb.collections.get_field("posts", "title")

# Method 3: Get schema
schema = pb.collections.get_schema("posts")
title_field_info = next((f for f in schema["fields"] if f["name"] == "title"), None)
```

---

## Upload Files

### Upload File with Record Creation

```python
with open("image.jpg", "rb") as fh:
    record = pb.collection("posts").create(
        body={"title": "Post Title"},
        files={"image": ("image.jpg", fh, "image/jpeg")}
    )
```

### Upload File with Record Update

```python
with open("new_image.jpg", "rb") as fh:
    updated = pb.collection("posts").update(
        "record_id",
        files={"image": ("new_image.jpg", fh, "image/jpeg")}
    )
```

### Get File URL

```python
record = pb.collection("posts").get_one("record_id")
file_url = pb.files.get_url(record, record["image"])
```

### Get File URL with Options

```python
file_url = pb.files.get_url(record, record["image"],
    thumb="100x100",  # Thumbnail
    download=True,    # Force download
)
```

### Get Private File Token

```python
# For accessing private files
token = pb.files.get_token()
# Use token in file URL
secure_url = pb.files.get_url(record, record["file"], token=token)
```

---

## Query Logs

### List Logs

```python
logs = pb.logs.get_list(1, 50)
print(logs["items"])  # List of log entries
```

### Filter Logs

```python
logs = pb.logs.get_list(1, 50, query={
    "filter": "level >= 400",  # Error level and above
    "sort": "-created",
})
```

### Get Single Log

```python
log = pb.logs.get_one("log_id")
print(log["message"], log["data"])
```

### Get Log Statistics

```python
stats = pb.logs.get_stats(query={"filter": "level >= 400"})

for stat in stats:
    print(stat["date"], stat["total"])
```

### Log Levels

- `0` - Debug
- `1` - Info
- `2` - Warning
- `3` - Error
- `4` - Fatal

---

## Send Emails

**Note**: Email sending is typically handled server-side via hooks or backend code. The SDK doesn't provide direct email sending methods, but you can trigger email-related operations.

### Trigger Email Verification

```python
# Request verification email
pb.collection("users").request_verification("user@example.com")
```

### Trigger Password Reset Email

```python
# Request password reset email
pb.collection("users").request_password_reset("user@example.com")
```

### Email Change Request

```python
# Request email change
pb.collection("users").request_email_change("newemail@example.com")
```

### Server-Side Email Sending

Email sending is configured in the backend settings and triggered automatically by:
- User registration (verification email)
- Password reset requests
- Email change requests
- Custom hooks

To send custom emails, you would typically:
1. Create a backend hook that uses `app.NewMailClient()`
2. Or use the admin API to configure email templates
3. Or trigger email-related record operations that automatically send emails

---

## Complete Example: Full Application Flow

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")

def setup_application():
    # 1. Authenticate
    pb.collection("users").auth_with_password("admin@example.com", "password")

    # 2. Create collection
    collection = pb.collections.create(body={
        "name": "posts",
        "type": "base",
        "fields": [
            {"name": "title", "type": "text", "required": True},
            {"name": "content", "type": "editor"},
            {"name": "published", "type": "bool"},
        ],
    })

    # 3. Add more fields
    pb.collections.add_field("posts", {
        "name": "views",
        "type": "number",
        "min": 0,
    })

    # 4. Create records
    post = pb.collection("posts").create(body={
        "title": "Hello World",
        "content": "My first post",
        "published": True,
        "views": 0,
    })

    # 5. Query records
    posts = pb.collection("posts").get_list(1, 10, query={
        "filter": "published = true",
        "sort": "-created",
    })

    # 6. Update record
    pb.collection("posts").update(post["id"], body={"views": 100})

    # 7. Query logs
    logs = pb.logs.get_list(1, 20, query={"filter": "level >= 400"})

    print("Application setup complete!")

setup_application()
```

---

## Quick Reference

### Common Patterns

```python
# Check if authenticated
if pb.auth_store.is_valid():
    pass  # ...

# Get current user
user = pb.auth_store.record

# Refresh auth token
pb.collection("users").auth_refresh()

# Error handling
from bosbase.exceptions import ClientResponseError

try:
    pb.collection("posts").create(body={"title": "Test"})
except ClientResponseError as err:
    if err.status == 400:
        print("Validation error:", err.response)
    elif err.status == 401:
        print("Not authenticated")
```

### Field Types Reference

- `text` - Text input
- `number` - Numeric value
- `bool` - Boolean
- `email` - Email address
- `url` - URL
- `date` - Date
- `select` - Single select
- `json` - JSON data
- `file` - File upload
- `relation` - Relation to another collection
- `editor` - Rich text editor

---

## Best Practices

1. **Always handle errors**: Wrap API calls in try-except
2. **Check authentication**: Verify `pb.auth_store.is_valid()` before operations
3. **Use pagination**: Don't fetch all records at once for large collections
4. **Validate data**: Ensure required fields are provided
5. **Use filters**: Filter data on the server, not client-side
6. **Expand relations wisely**: Only expand what you need
7. **Handle file uploads**: Use the `files` parameter for file fields
8. **Refresh tokens**: Use `auth_refresh()` to maintain sessions

---

## LangChaingo Recipes

### Quick Completion

```python
from bosbase import LangChaingoCompletionRequest, LangChaingoCompletionMessage, LangChaingoModelConfig

req = LangChaingoCompletionRequest(
    model=LangChaingoModelConfig(provider="openai", model="gpt-4o-mini"),
    messages=[
        LangChaingoCompletionMessage(role="system", content="Answer with one concise line."),
        LangChaingoCompletionMessage(role="user", content="Give me a fun fact about Mars.")
    ],
    temperature=0.4
)

result = pb.langchaingo.completions(req)
print(result.content)
```

### Retrieval-Augmented Answering

```python
from bosbase import LangChaingoRAGRequest, LangChaingoModelConfig

req = LangChaingoRAGRequest(
    collection="knowledge-base",
    question="Why is the sky blue?",
    top_k=3,
    return_sources=True
)

rag = pb.langchaingo.rag(req)
print(rag.answer)
print(rag.sources)
```

---

This guide provides all essential operations for building applications with the BosBase Python SDK. For more detailed information, refer to the specific API documentation files.
