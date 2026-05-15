# Collections - Python SDK Documentation

This document provides comprehensive documentation for working with Collections and Fields in the BosBase Python SDK. This documentation is designed to be AI-readable and includes practical examples for all operations.

## Table of Contents

- [Overview](#overview)
- [Collection Types](#collection-types)
- [Collections API](#collections-api)
- [Records API](#records-api)
- [Field Types](#field-types)
- [Examples](#examples)

## Overview

**Collections** represent your application data. Under the hood they are backed by plain SQLite tables that are generated automatically with the collection **name** and **fields** (columns).

A single entry of a collection is called a **record** (a single row in the SQL table).

You can manage your **collections** from the Dashboard, or with the Python SDK using the `collections` service.

Similarly, you can manage your **records** from the Dashboard, or with the Python SDK using the `collection(name)` method which returns a `RecordService` instance.

## Collection Types

Currently there are 3 collection types: **Base**, **View** and **Auth**.

### Base Collection

**Base collection** is the default collection type and it could be used to store any application data (articles, products, posts, etc.).

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")
pb.collection("_superusers").auth_with_password("admin@example.com", "password")

# Create a base collection
collection = pb.collections.create_base("articles", overrides={
    "fields": [
        {
            "name": "title",
            "type": "text",
            "required": True,
            "min": 6,
            "max": 100
        },
        {
            "name": "description",
            "type": "text"
        }
    ],
    "listRule": "@request.auth.id != '' || status = 'public'",
    "viewRule": "@request.auth.id != '' || status = 'public'"
})
```

### View Collection

**View collection** is a read-only collection type where the data is populated from a plain SQL `SELECT` statement, allowing users to perform aggregations or any other custom queries.

For example, the following query will create a read-only collection with 3 _posts_ fields - _id_, _name_ and _totalComments_:

```python
# Create a view collection
view_collection = pb.collections.create_view(
    "post_stats",
    view_query="""SELECT posts.id, posts.name, count(comments.id) as totalComments
   FROM posts
   LEFT JOIN comments on comments.postId = posts.id
   GROUP BY posts.id"""
)
```

**Note**: View collections don't receive realtime events because they don't have create/update/delete operations.

### Auth Collection

**Auth collection** has everything from the **Base collection** but with some additional special fields to help you manage your app users and also provide various authentication options.

Each Auth collection has the following special system fields: `email`, `emailVisibility`, `verified`, `password` and `tokenKey`. They cannot be renamed or deleted but can be configured using their specific field options.

```python
# Create an auth collection
users_collection = pb.collections.create_auth("users", overrides={
    "fields": [
        {
            "name": "name",
            "type": "text",
            "required": True
        },
        {
            "name": "role",
            "type": "select",
            "options": {
                "values": ["employee", "staff", "admin"]
            }
        }
    ]
})
```

You can have as many Auth collections as you want (users, managers, staffs, members, clients, etc.) each with their own set of fields, separate login and records managing endpoints.

## Collections API

### Initialize Client

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")

# Authenticate as superuser (required for collection management)
pb.collection("_superusers").auth_with_password("admin@example.com", "password")
```

### List Collections

```python
# Get paginated list
result = pb.collections.get_list(1, 50)

# Get all collections
all_collections = pb.collections.get_full_list()
```

### Get Collection

```python
# By ID or name
collection = pb.collections.get_one("articles")
# or
collection = pb.collections.get_one("COLLECTION_ID")
```

### Create Collection

#### Using Scaffolds (Recommended)

```python
# Create base collection
base = pb.collections.create_base("articles", overrides={
    "fields": [
        {
            "name": "title",
            "type": "text",
            "required": True
        }
    ]
})

# Create auth collection
auth = pb.collections.create_auth("users")

# Create view collection
view = pb.collections.create_view("stats", view_query="SELECT id, name FROM posts")
```

#### Manual Creation

```python
collection = pb.collections.create(body={
    "type": "base",
    "name": "articles",
    "fields": [
        {
            "name": "title",
            "type": "text",
            "required": True,
            "min": 6,
            "max": 100
        },
        {
            "name": "description",
            "type": "text"
        },
        {
            "name": "published",
            "type": "bool",
            "required": True
        },
        {
            "name": "views",
            "type": "number",
            "min": 0
        },
        # Note: created and updated fields must be explicitly added if you want to use them
        {
            "name": "created",
            "type": "autodate",
            "required": False,
            "options": {
                "onCreate": True,
                "onUpdate": False
            }
        },
        {
            "name": "updated",
            "type": "autodate",
            "required": False,
            "options": {
                "onCreate": True,
                "onUpdate": True
            }
        }
    ],
    "listRule": "@request.auth.id != '' || published = true",
    "viewRule": "@request.auth.id != '' || published = true",
    "createRule": "@request.auth.id != ''",
    "updateRule": "@request.auth.id != ''",
    "deleteRule": "@request.auth.id != ''"
})
```

### Update Collection

```python
collection = pb.collections.update("articles", body={
    "listRule": "@request.auth.id != '' || published = true && status = 'public'"
})
```

### Delete Collection

```python
# Warning: This will delete the collection and all its records
pb.collections.delete_collection("articles")
```

### Truncate Collection

Deletes all records but keeps the collection structure:

```python
pb.collections.truncate("articles")
```

### Import Collections

```python
collections_to_import = [
    {
        "type": "base",
        "name": "articles",
        "fields": [...]
    },
    {
        "type": "auth",
        "name": "users",
        "fields": [...]
    }
]

# Import collections (delete_missing will delete collections not in the import list)
pb.collections.import_collections(collections_to_import, False)
```

### Get Scaffolds

```python
scaffolds = pb.collections.get_scaffolds()
# Returns: {"base": {...}, "auth": {...}, "view": {...}}
```

## Records API

### Get Record Service

```python
# Get a RecordService instance for a collection
articles = pb.collection("articles")
```

### List Records
**Important Note:** Bosbase does not initialize `created` and `updated` fields by default. To use these fields, you must explicitly add them when initializing the collection with the proper options:

```python
# Paginated list
result = pb.collection("articles").get_list(1, 20, query={
    "filter": "published = true",
    "sort": "-created",
    "expand": "author",
    "fields": "id,title,description"
})

print(result["items"])      # List of records
print(result["page"])       # Current page number
print(result["perPage"])    # Items per page
print(result["totalItems"]) # Total items count
print(result["totalPages"]) # Total pages count

# Get all records (automatically paginates)
all_records = pb.collection("articles").get_full_list(query={
    "filter": "published = true",
    "sort": "-created"
})
```

### Get Single Record

```python
record = pb.collection("articles").get_one("RECORD_ID", query={
    "expand": "author,category",
    "fields": "id,title,description,author"
})
```

### Get First Matching Record

```python
record = pb.collection("articles").get_first_list_item(
    'title ~ "example" && published = true',
    query={"expand": "author"}
)
```

### Create Record

```python
# Simple create
record = pb.collection("articles").create(body={
    "title": "My First Article",
    "description": "This is a test article",
    "published": True,
    "views": 0
})

# With file upload
with open("cover.jpg", "rb") as fh:
    record = pb.collection("articles").create(
        body={"title": "My Article"},
        files={"cover": ("cover.jpg", fh, "image/jpeg")}
    )

# With field modifiers
record = pb.collection("articles").create(body={
    "title": "My Article",
    "views+": 1,       # Increment views by 1
    "tags+": "new-tag" # Append to tags array
})
```

### Update Record

```python
# Simple update
record = pb.collection("articles").update("RECORD_ID", body={
    "title": "Updated Title",
    "published": True
})

# With field modifiers
record = pb.collection("articles").update("RECORD_ID", body={
    "views+": 1,          # Increment views
    "tags+": "new-tag",   # Append tag
    "tags-": "old-tag"    # Remove tag
})

# With file upload
with open("new_cover.jpg", "rb") as fh:
    record = pb.collection("articles").update(
        "RECORD_ID",
        files={"cover": ("new_cover.jpg", fh, "image/jpeg")}
    )
```

### Delete Record

```python
pb.collection("articles").delete("RECORD_ID")
```

### Batch Operations

```python
batch = pb.create_batch()
batch.collection("articles").create(body={"title": "Article 1"})
batch.collection("articles").create(body={"title": "Article 2"})
batch.collection("articles").update("RECORD_ID", body={"published": True})
results = batch.send()
```

## Field Types

All collection fields (with exception of the `JSONField`) are **non-nullable and use a zero-default** for their respective type as fallback value when missing (empty string for `text`, 0 for `number`, etc.).

### BoolField

Stores a single `False` (default) or `True` value.

```python
# Create field
{
    "name": "published",
    "type": "bool",
    "required": True
}

# Usage
pb.collection("articles").create(body={"published": True})
```

### NumberField

Stores numeric/float64 value: `0` (default), `2`, `-1`, `1.5`.

**Available modifiers:**
- `fieldName+` - adds number to the existing record value
- `fieldName-` - subtracts number from the existing record value

```python
# Create field
{
    "name": "views",
    "type": "number",
    "min": 0,
    "max": 1000000,
    "onlyInt": False  # Allow decimals
}

# Usage
pb.collection("articles").create(body={"views": 0})

# Increment
pb.collection("articles").update("RECORD_ID", body={"views+": 1})

# Decrement
pb.collection("articles").update("RECORD_ID", body={"views-": 5})
```

### TextField

Stores string values: `""` (default), `"example"`.

**Available modifiers:**
- `fieldName:autogenerate` - autogenerate a field value if the `AutogeneratePattern` field option is set.

```python
# Create field
{
    "name": "title",
    "type": "text",
    "required": True,
    "min": 6,
    "max": 100,
    "pattern": "^[A-Z]",         # Must start with uppercase
    "autogeneratePattern": "[a-z0-9]{8}"  # Auto-generate pattern
}

# Usage
pb.collection("articles").create(body={"title": "My Article"})

# Auto-generate
pb.collection("articles").create(body={"slug:autogenerate": "article-"})
# Results in: 'article-[random8chars]'
```

### EmailField

Stores a single email string address: `""` (default), `"john@example.com"`.

```python
# Create field
{
    "name": "email",
    "type": "email",
    "required": True
}

# Usage
pb.collection("users").create(body={"email": "user@example.com"})
```

### URLField

Stores a single URL string value: `""` (default), `"https://example.com"`.

```python
# Create field
{
    "name": "website",
    "type": "url",
    "required": False
}

# Usage
pb.collection("users").create(body={"website": "https://example.com"})
```

### EditorField

Stores HTML formatted text: `""` (default), `<p>example</p>`.

```python
# Create field
{
    "name": "content",
    "type": "editor",
    "required": True,
    "maxSize": 10485760  # 10MB
}

# Usage
pb.collection("articles").create(body={
    "content": "<p>This is HTML content</p><p>With multiple paragraphs</p>"
})
```

### DateField

Stores a single datetime string value: `""` (default), `"2022-01-01 00:00:00.000Z"`.

All BosBase dates follow the RFC3339 format `Y-m-d H:i:s.uZ` (e.g. `2024-11-10 18:45:27.123Z`).

```python
# Create field
{
    "name": "published_at",
    "type": "date",
    "required": False
}

# Usage
pb.collection("articles").create(body={"published_at": "2024-11-10 18:45:27.123Z"})

# Filter by date
records = pb.collection("articles").get_list(1, 20, query={
    "filter": "created >= '2024-11-19 00:00:00.000Z' && created <= '2024-11-19 23:59:59.999Z'"
})
```

### AutodateField

Similar to DateField but its value is auto set on record create/update. Usually used for timestamp fields like "created" and "updated".

**Important Note:** Bosbase does not initialize `created` and `updated` fields by default. To use these fields, you must explicitly add them when initializing the collection with the proper options:

```python
# Create field with proper options
{
    "name": "created",
    "type": "autodate",
    "required": False,
    "options": {
        "onCreate": True,   # Set on record creation
        "onUpdate": False   # Don't update on record update
    }
}

# For updated field
{
    "name": "updated",
    "type": "autodate",
    "required": False,
    "options": {
        "onCreate": True,  # Set on record creation
        "onUpdate": True   # Update on record update
    }
}

# The value is automatically set by the backend based on the options
```

### SelectField

Stores single or multiple string values from a predefined list.

For **single** `select` (the `MaxSelect` option is <= 1) the field value is a string: `""`, `"optionA"`.

For **multiple** `select` (the `MaxSelect` option is >= 2) the field value is an array: `[]`, `["optionA", "optionB"]`.

**Available modifiers:**
- `fieldName+` - appends one or more values
- `+fieldName` - prepends one or more values
- `fieldName-` - subtracts/removes one or more values

```python
# Single select
{
    "name": "status",
    "type": "select",
    "options": {
        "values": ["draft", "published", "archived"]
    },
    "maxSelect": 1
}

# Multiple select
{
    "name": "tags",
    "type": "select",
    "options": {
        "values": ["tech", "design", "business", "marketing"]
    },
    "maxSelect": 5
}

# Usage - Single
pb.collection("articles").create(body={"status": "published"})

# Usage - Multiple
pb.collection("articles").create(body={"tags": ["tech", "design"]})

# Modify - Append
pb.collection("articles").update("RECORD_ID", body={"tags+": "marketing"})

# Modify - Remove
pb.collection("articles").update("RECORD_ID", body={"tags-": "tech"})
```

### FileField

Manages record file(s). BosBase stores in the database only the file name. The file itself is stored either on the local disk or in S3.

For **single** `file` (the `MaxSelect` option is <= 1) the stored value is a string: `""`, `"file1_Ab24ZjL.png"`.

For **multiple** `file` (the `MaxSelect` option is >= 2) the stored value is an array: `[]`, `["file1_Ab24ZjL.png", "file2_Frq24ZjL.txt"]`.

**Available modifiers:**
- `fieldName+` - appends one or more files
- `+fieldName` - prepends one or more files
- `fieldName-` - deletes one or more files

```python
# Single file
{
    "name": "cover",
    "type": "file",
    "maxSelect": 1,
    "maxSize": 5242880,  # 5MB
    "mimeTypes": ["image/jpeg", "image/png"]
}

# Multiple files
{
    "name": "documents",
    "type": "file",
    "maxSelect": 10,
    "maxSize": 10485760,  # 10MB
    "mimeTypes": ["application/pdf", "application/docx"]
}

# Usage - Upload file
with open("cover.jpg", "rb") as fh:
    record = pb.collection("articles").create(
        body={"title": "My Article"},
        files={"cover": ("cover.jpg", fh, "image/jpeg")}
    )

# Modify - Add file
with open("new_doc.pdf", "rb") as fh:
    pb.collection("articles").update(
        "RECORD_ID",
        files={"documents": ("new_doc.pdf", fh, "application/pdf")}
    )

# Modify - Remove file
pb.collection("articles").update("RECORD_ID", body={"documents-": "old_file_abc123.pdf"})
```

### RelationField

Stores single or multiple collection record references.

For **single** `relation` (the `MaxSelect` option is <= 1) the field value is a string: `""`, `"RECORD_ID"`.

For **multiple** `relation` (the `MaxSelect` option is >= 2) the field value is an array: `[]`, `["RECORD_ID1", "RECORD_ID2"]`.

**Available modifiers:**
- `fieldName+` - appends one or more ids
- `+fieldName` - prepends one or more ids
- `fieldName-` - subtracts/removes one or more ids

```python
# Single relation
{
    "name": "author",
    "type": "relation",
    "options": {
        "collectionId": "users",
        "cascadeDelete": False
    },
    "maxSelect": 1
}

# Multiple relation
{
    "name": "categories",
    "type": "relation",
    "options": {
        "collectionId": "categories"
    },
    "maxSelect": 5
}

# Usage - Single
pb.collection("articles").create(body={
    "title": "My Article",
    "author": "USER_RECORD_ID"
})

# Usage - Multiple
pb.collection("articles").create(body={
    "title": "My Article",
    "categories": ["CAT_ID1", "CAT_ID2"]
})

# Modify - Add relation
pb.collection("articles").update("RECORD_ID", body={"categories+": "CAT_ID3"})

# Modify - Remove relation
pb.collection("articles").update("RECORD_ID", body={"categories-": "CAT_ID1"})

# Expand relations when fetching
record = pb.collection("articles").get_one("RECORD_ID", query={"expand": "author,categories"})
# record["expand"]["author"] - full author record
# record["expand"]["categories"] - list of category records
```

### JSONField

Stores any serialized JSON value, including `None` (default). This is the only nullable field type.

```python
# Create field
{
    "name": "metadata",
    "type": "json",
    "required": False
}

# Usage
pb.collection("articles").create(body={
    "title": "My Article",
    "metadata": {
        "seo": {
            "title": "SEO Title",
            "description": "SEO Description"
        },
        "custom": {
            "tags": ["tag1", "tag2"],
            "priority": 10
        }
    }
})

# Can also store arrays
pb.collection("articles").create(body={
    "title": "My Article",
    "metadata": [1, 2, 3, {"nested": "object"}]
})
```

### GeoPointField

Stores geographic coordinates (longitude, latitude) as a serialized json object.

The default/zero value of a `geoPoint` is the "Null Island", aka. `{"lon":0,"lat":0}`.

```python
# Create field
{
    "name": "location",
    "type": "geoPoint",
    "required": False
}

# Usage
pb.collection("places").create(body={
    "name": "Tokyo Tower",
    "location": {
        "lon": 139.6917,
        "lat": 35.6586
    }
})
```

## Examples

### Complete Example: Blog System

```python
from bosbase import BosBase
from datetime import datetime

pb = BosBase("http://localhost:8090")
pb.collection("_superusers").auth_with_password("admin@example.com", "password")

# 1. Create users (auth) collection
users_collection = pb.collections.create_auth("users", overrides={
    "fields": [
        {
            "name": "name",
            "type": "text",
            "required": True
        },
        {
            "name": "avatar",
            "type": "file",
            "maxSelect": 1,
            "mimeTypes": ["image/jpeg", "image/png"]
        }
    ]
})

# 2. Create categories (base) collection
categories_collection = pb.collections.create_base("categories", overrides={
    "fields": [
        {
            "name": "name",
            "type": "text",
            "required": True
        },
        {
            "name": "slug",
            "type": "text",
            "required": True
        }
    ]
})

# 3. Create articles (base) collection
articles_collection = pb.collections.create_base("articles", overrides={
    "fields": [
        {
            "name": "title",
            "type": "text",
            "required": True,
            "min": 6,
            "max": 200
        },
        {
            "name": "slug",
            "type": "text",
            "required": True,
            "autogeneratePattern": "[a-z0-9-]{10,}"
        },
        {
            "name": "content",
            "type": "editor",
            "required": True
        },
        {
            "name": "excerpt",
            "type": "text",
            "max": 500
        },
        {
            "name": "cover",
            "type": "file",
            "maxSelect": 1,
            "mimeTypes": ["image/jpeg", "image/png"]
        },
        {
            "name": "author",
            "type": "relation",
            "options": {
                "collectionId": users_collection["id"]
            },
            "maxSelect": 1,
            "required": True
        },
        {
            "name": "categories",
            "type": "relation",
            "options": {
                "collectionId": categories_collection["id"]
            },
            "maxSelect": 5
        },
        {
            "name": "tags",
            "type": "select",
            "options": {
                "values": ["tech", "design", "business", "marketing", "lifestyle"]
            },
            "maxSelect": 10
        },
        {
            "name": "status",
            "type": "select",
            "options": {
                "values": ["draft", "published", "archived"]
            },
            "maxSelect": 1,
            "required": True
        },
        {
            "name": "published",
            "type": "bool",
            "required": True
        },
        {
            "name": "views",
            "type": "number",
            "min": 0,
            "onlyInt": True
        },
        {
            "name": "published_at",
            "type": "date"
        },
        {
            "name": "metadata",
            "type": "json"
        }
    ],
    "listRule": "@request.auth.id != '' || (published = true && status = 'published')",
    "viewRule": "@request.auth.id != '' || (published = true && status = 'published')",
    "createRule": "@request.auth.id != ''",
    "updateRule": "author = @request.auth.id || @request.auth.role = 'admin'",
    "deleteRule": "author = @request.auth.id || @request.auth.role = 'admin'"
})

# 4. Create a user
user = pb.collection("users").create(body={
    "email": "author@example.com",
    "emailVisibility": True,
    "password": "securepassword123",
    "passwordConfirm": "securepassword123",
    "name": "John Doe"
})

# 5. Authenticate as the user
pb.collection("users").auth_with_password("author@example.com", "securepassword123")

# 6. Create a category
category = pb.collection("categories").create(body={
    "name": "Technology",
    "slug": "technology"
})

# 7. Create an article
article = pb.collection("articles").create(body={
    "title": "Getting Started with BosBase",
    "slug:autogenerate": "getting-started-",
    "content": "<p>This is my first article about BosBase...</p>",
    "excerpt": "Learn how to get started with BosBase...",
    "author": user["id"],
    "categories": [category["id"]],
    "tags": ["tech", "tutorial"],
    "status": "published",
    "published": True,
    "views": 0,
    "published_at": datetime.utcnow().isoformat(),
    "metadata": {
        "seo": {
            "title": "Getting Started with BosBase - SEO Title",
            "description": "SEO description here"
        }
    }
})

# 8. Update article views
pb.collection("articles").update(article["id"], body={"views+": 1})

# 9. Add a tag to the article
pb.collection("articles").update(article["id"], body={"tags+": "beginner"})

# 10. Fetch article with expanded relations
full_article = pb.collection("articles").get_one(article["id"], query={"expand": "author,categories"})

print(full_article["expand"]["author"]["name"])          # John Doe
print(full_article["expand"]["categories"][0]["name"])   # Technology

# 11. List published articles
published_articles = pb.collection("articles").get_list(1, 20, query={
    "filter": 'published = true && status = "published"',
    "sort": "-created",
    "expand": "author,categories"
})

# 12. Search articles
search_results = pb.collection("articles").get_list(1, 20, query={
    "filter": 'title ~ "BosBase" || content ~ "BosBase"',
    "sort": "-views"
})
```

### Realtime Subscriptions

```python
def on_event(event):
    print("Action:", event["action"])  # 'create', 'update', or 'delete'
    print("Record:", event["record"])

# Subscribe to all changes in a collection
unsubscribe_all = pb.collection("articles").subscribe("*", on_event)

# Subscribe to changes in a specific record
unsubscribe_record = pb.collection("articles").subscribe("RECORD_ID", on_event)

# Unsubscribe
pb.collection("articles").unsubscribe("RECORD_ID")
pb.collection("articles").unsubscribe("*")
pb.collection("articles").unsubscribe()  # Unsubscribe from all
```

### Authentication with Auth Collections

```python
# Create an auth collection
customers_collection = pb.collections.create_auth("customers", overrides={
    "fields": [
        {
            "name": "name",
            "type": "text",
            "required": True
        },
        {
            "name": "phone",
            "type": "text"
        }
    ]
})

# Register a new customer
customer = pb.collection("customers").create(body={
    "email": "customer@example.com",
    "emailVisibility": True,
    "password": "password123",
    "passwordConfirm": "password123",
    "name": "Jane Doe",
    "phone": "+1234567890"
})

# Authenticate
auth = pb.collection("customers").auth_with_password("customer@example.com", "password123")

print(auth["token"])   # Auth token
print(auth["record"])  # Customer record

# Check if authenticated
if pb.auth_store.is_valid():
    print("Current user:", pb.auth_store.record)

# Logout
pb.auth_store.clear()
```
