# Built-in Users Collection Guide - Python SDK

This guide explains how to use the built-in `users` collection for authentication, registration, and API rules. **The `users` collection is automatically created when BosBase is initialized and does not need to be created manually.**

## Table of Contents

1. [Overview](#overview)
2. [Users Collection Structure](#users-collection-structure)
3. [User Registration](#user-registration)
4. [User Login/Authentication](#user-loginauthentication)
5. [API Rules and Filters with Users](#api-rules-and-filters-with-users)
6. [Using Users with Other Collections](#using-users-with-other-collections)
7. [Complete Examples](#complete-examples)

---

## Overview

The `users` collection is a **built-in auth collection** that is automatically created when BosBase starts. It has:

- **Collection ID**: `_pb_users_auth_`
- **Collection Name**: `users`
- **Type**: `auth` (authentication collection)
- **Purpose**: User accounts, authentication, and authorization

**Important**:
- Do NOT create a new `users` collection manually
- DO use the existing built-in `users` collection
- The collection already has proper API rules configured
- It supports password, OAuth2, and OTP authentication

### Getting Users Collection Information

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")
pb.collection("_superusers").auth_with_password("admin@example.com", "password")

# Get the users collection details
users_collection = pb.collections.get_one("users")
# or by ID
users_collection = pb.collections.get_one("_pb_users_auth_")

print("Collection ID:", users_collection["id"])
print("Collection Name:", users_collection["name"])
print("Collection Type:", users_collection["type"])
print("Fields:", users_collection["fields"])
print("API Rules:", {
    "listRule": users_collection.get("listRule"),
    "viewRule": users_collection.get("viewRule"),
    "createRule": users_collection.get("createRule"),
    "updateRule": users_collection.get("updateRule"),
    "deleteRule": users_collection.get("deleteRule"),
})
```

---

## Users Collection Structure

### System Fields (Automatically Created)

These fields are automatically added to all auth collections (including `users`):

| Field Name | Type | Description | Required | Hidden |
|------------|------|-------------|----------|--------|
| `id` | text | Unique record identifier | Yes | No |
| `email` | email | User email address | Yes* | No |
| `username` | text | Username (optional, if enabled) | No* | No |
| `password` | password | Hashed password | Yes* | Yes |
| `tokenKey` | text | Token key for auth tokens | Yes | Yes |
| `emailVisibility` | bool | Whether email is visible to others | No | No |
| `verified` | bool | Whether email is verified | No | No |
| `created` | date | Record creation timestamp | Yes | No |
| `updated` | date | Last update timestamp | Yes | No |

*Required based on authentication method configuration (password auth, username auth, etc.)

### Custom Fields (Pre-configured)

The built-in `users` collection includes these custom fields:

| Field Name | Type | Description | Required |
|------------|------|-------------|----------|
| `name` | text | User's display name | No (max: 255 characters) |
| `avatar` | file | User avatar image | No (max: 1 file, images only) |

### Default API Rules

The `users` collection comes with these default API rules:

```python
{
    "listRule": "id = @request.auth.id",    # Users can only list themselves
    "viewRule": "id = @request.auth.id",    # Users can only view themselves
    "createRule": "",                        # Anyone can register (public)
    "updateRule": "id = @request.auth.id",  # Users can only update themselves
    "deleteRule": "id = @request.auth.id"   # Users can only delete themselves
}
```

**Understanding the Rules:**

1. **`listRule: "id = @request.auth.id"`**
   - Users can only see their own record when listing
   - If not authenticated, returns empty list (not an error)
   - Superusers can see all users

2. **`viewRule: "id = @request.auth.id"`**
   - Users can only view their own record
   - If trying to view another user, returns 404
   - Superusers can view any user

3. **`createRule: ""`** (empty string)
   - **Public registration** - Anyone can create a user account
   - No authentication required
   - This enables self-registration

4. **`updateRule: "id = @request.auth.id"`**
   - Users can only update their own record
   - Prevents users from modifying other users' data
   - Superusers can update any user

5. **`deleteRule: "id = @request.auth.id"`**
   - Users can only delete their own account
   - Prevents users from deleting other users
   - Superusers can delete any user

**Note**: These rules ensure user privacy and security. Users can only access and modify their own data unless they are superusers.

---

## User Registration

### Basic Registration

Users can register by creating a record in the `users` collection. The `createRule` is set to `""` (empty string), meaning **anyone can register**.

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")

# Register a new user
new_user = pb.collection("users").create(body={
    "email": "user@example.com",
    "password": "securepassword123",
    "passwordConfirm": "securepassword123",
    "name": "John Doe",
})

print("User registered:", new_user["id"])
print("Email:", new_user["email"])
```

### Registration with Email Verification

```python
# Register user (verification email sent automatically if configured)
new_user = pb.collection("users").create(body={
    "email": "user@example.com",
    "password": "securepassword123",
    "passwordConfirm": "securepassword123",
    "name": "John Doe",
})

# User will receive verification email
# After clicking link, verified field becomes True
```

### Registration with Username

If username authentication is enabled in the collection settings:

```python
new_user = pb.collection("users").create(body={
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "passwordConfirm": "securepassword123",
    "name": "John Doe",
})
```

### Registration with Avatar Upload

```python
with open("avatar.jpg", "rb") as fh:
    new_user = pb.collection("users").create(
        body={
            "email": "user@example.com",
            "password": "securepassword123",
            "passwordConfirm": "securepassword123",
            "name": "John Doe",
        },
        files={"avatar": ("avatar.jpg", fh, "image/jpeg")}
    )
```

### Check if Email Exists

```python
from bosbase.exceptions import ClientResponseError

try:
    existing = pb.collection("users").get_first_list_item('email = "user@example.com"')
    print("Email already exists")
except ClientResponseError as err:
    if err.status == 404:
        print("Email is available")
```

---

## User Login/Authentication

### Password Authentication

```python
# Login with email and password
auth_data = pb.collection("users").auth_with_password(
    "user@example.com",
    "password123"
)

# Auth data is automatically stored
print(pb.auth_store.is_valid())  # True
print(pb.auth_store.token)       # JWT token
print(pb.auth_store.record)      # User record
```

### Login with Username

If username authentication is enabled:

```python
auth_data = pb.collection("users").auth_with_password(
    "johndoe",    # username instead of email
    "password123"
)
```

### OAuth2 Authentication

```python
def open_browser(url: str):
    print(f"Please visit: {url}")

# Login with OAuth2 (e.g., Google)
auth_data = pb.collection("users").auth_with_oauth2(
    "google",
    url_callback=open_browser
)

# If user doesn't exist, account is created automatically
print(pb.auth_store.record)
```

### OTP Authentication

```python
# Step 1: Request OTP
otp_result = pb.collection("users").request_otp("user@example.com")

# Step 2: Authenticate with OTP code from email
auth_data = pb.collection("users").auth_with_otp(
    otp_result["otpId"],
    "123456"  # OTP code from email
)
```

### Check Current Authentication

```python
if pb.auth_store.is_valid():
    user = pb.auth_store.record
    print("Logged in as:", user["email"])
    print("User ID:", user["id"])
    print("Name:", user.get("name"))
else:
    print("Not authenticated")
```

### Refresh Auth Token

```python
# Refresh the authentication token
pb.collection("users").auth_refresh()
```

### Logout

```python
pb.auth_store.clear()
```

### Get Current User

```python
current_user = pb.auth_store.record
if current_user:
    print("Current user:", current_user["email"])
    print("User ID:", current_user["id"])
    print("Name:", current_user.get("name"))
    print("Verified:", current_user.get("verified"))
```

### Accessing User Fields

```python
# After authentication, access user fields
user = pb.auth_store.record

# System fields
print(user["id"])                   # User ID
print(user["email"])                # Email
print(user.get("username"))         # Username (if enabled)
print(user.get("verified"))         # Email verification status
print(user.get("emailVisibility"))  # Email visibility setting
print(user.get("created"))          # Creation date
print(user.get("updated"))          # Last update date

# Custom fields (from users collection)
print(user.get("name"))    # Display name
print(user.get("avatar"))  # Avatar filename
```

---

## API Rules and Filters with Users

### Understanding @request.auth

The `@request.auth` identifier provides access to the currently authenticated user's data in API rules and filters.

**Available Properties:**
- `@request.auth.id` - User's record ID
- `@request.auth.email` - User's email
- `@request.auth.username` - User's username (if enabled)
- `@request.auth.*` - Any field from the user record

### Common API Rule Patterns

#### 1. Require Authentication

```python
# Only authenticated users can access
list_rule = '@request.auth.id != ""'
view_rule = '@request.auth.id != ""'
create_rule = '@request.auth.id != ""'
```

#### 2. Owner-Based Access

```python
# Users can only access their own records
view_rule = "author = @request.auth.id"
update_rule = "author = @request.auth.id"
delete_rule = "author = @request.auth.id"
```

#### 3. Public with User-Specific Data

```python
# Public can see published, users can see their own
list_rule = '@request.auth.id != "" && author = @request.auth.id || status = "published"'
view_rule = '@request.auth.id != "" && author = @request.auth.id || status = "published"'
```

#### 4. Role-Based Access (if you add a role field)

```python
# Assuming you add a 'role' select field to users collection
list_rule = '@request.auth.id != "" && @request.auth.role = "admin"'
update_rule = '@request.auth.role = "admin" || author = @request.auth.id'
```

#### 5. Verified Users Only

```python
# Only verified users can create
create_rule = '@request.auth.id != "" && @request.auth.verified = true'
```

### Setting API Rules for Other Collections

When creating collections that relate to users:

```python
# Create posts collection with user-based rules
posts_collection = pb.collections.create(body={
    "name": "posts",
    "type": "base",
    "fields": [
        {
            "name": "title",
            "type": "text",
            "required": True,
        },
        {
            "name": "content",
            "type": "editor",
        },
        {
            "name": "author",
            "type": "relation",
            "collectionId": "_pb_users_auth_",  # Reference to users collection
            "maxSelect": 1,
            "required": True,
        },
        {
            "name": "status",
            "type": "select",
            "options": {
                "values": ["draft", "published"],
            },
        },
    ],
    # Public can see published posts, users can see their own
    "listRule": '@request.auth.id != "" && author = @request.auth.id || status = "published"',
    "viewRule": '@request.auth.id != "" && author = @request.auth.id || status = "published"',
    # Only authenticated users can create
    "createRule": '@request.auth.id != ""',
    # Only authors can update their posts
    "updateRule": "author = @request.auth.id",
    # Only authors can delete their posts
    "deleteRule": "author = @request.auth.id",
})
```

### Using Filters with Users

```python
# Get posts by current user
my_posts = pb.collection("posts").get_list(1, 20, query={
    "filter": "author = @request.auth.id",
})

# Get posts by verified users only
verified_posts = pb.collection("posts").get_list(1, 20, query={
    "filter": "author.verified = true",
    "expand": "author",
})

# Get posts where author name contains "John"
posts = pb.collection("posts").get_list(1, 20, query={
    "filter": 'author.name ~ "John"',
    "expand": "author",
})
```

---

## Using Users with Other Collections

### Creating Relations to Users

When creating collections that need to reference users:

```python
# Create a posts collection with author relation
posts_collection = pb.collections.create(body={
    "name": "posts",
    "type": "base",
    "fields": [
        {
            "name": "title",
            "type": "text",
            "required": True,
        },
        {
            "name": "author",
            "type": "relation",
            "collectionId": "_pb_users_auth_",  # Users collection ID
            "maxSelect": 1,
            "required": True,
        },
    ],
})
```

### Creating Records with User Relations

```python
# Authenticate first
pb.collection("users").auth_with_password("user@example.com", "password")

# Create a post with current user as author
post = pb.collection("posts").create(body={
    "title": "My First Post",
    "author": pb.auth_store.record["id"],  # Current user's ID
})
```

### Querying with User Relations

```python
# Get posts with author information
posts = pb.collection("posts").get_list(1, 20, query={
    "expand": "author",  # Expand the author relation
})

for post in posts["items"]:
    print("Post:", post["title"])
    print("Author:", post["expand"]["author"]["name"])
    print("Author Email:", post["expand"]["author"]["email"])

# Filter posts by author
user_posts = pb.collection("posts").get_list(1, 20, query={
    "filter": 'author = "USER_ID"',
    "expand": "author",
})
```

### Updating User Profile

```python
# Users can update their own profile
pb.collection("users").update(pb.auth_store.record["id"], body={
    "name": "Updated Name",
})

# Update with avatar
with open("new_avatar.jpg", "rb") as fh:
    pb.collection("users").update(
        pb.auth_store.record["id"],
        body={"name": "New Name"},
        files={"avatar": ("new_avatar.jpg", fh, "image/jpeg")}
    )
```

---

## Complete Examples

### Example 1: User Registration and Login Flow

```python
from bosbase import BosBase
from bosbase.exceptions import ClientResponseError

pb = BosBase("http://localhost:8090")

def register_and_login():
    try:
        # 1. Register new user
        new_user = pb.collection("users").create(body={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "passwordConfirm": "securepassword123",
            "name": "New User",
        })

        print("Registration successful:", new_user["id"])

        # 2. Login with credentials
        auth_data = pb.collection("users").auth_with_password(
            "newuser@example.com",
            "securepassword123"
        )

        print("Login successful")
        print("Token:", auth_data["token"])
        print("User:", auth_data["record"])

        return auth_data
    except ClientResponseError as err:
        print("Error:", err.message)
        if err.response:
            print("Validation errors:", err.response)

register_and_login()
```

### Example 2: Creating User-Related Collections

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")

# Authenticate as superuser to create collections
pb.collection("_superusers").auth_with_password("admin@example.com", "adminpassword")

def setup_user_related_collections():
    # Create posts collection linked to users
    posts_collection = pb.collections.create(body={
        "name": "posts",
        "type": "base",
        "fields": [
            {
                "name": "title",
                "type": "text",
                "required": True,
            },
            {
                "name": "content",
                "type": "editor",
            },
            {
                "name": "author",
                "type": "relation",
                "collectionId": "_pb_users_auth_",  # Link to users
                "maxSelect": 1,
                "required": True,
            },
            {
                "name": "status",
                "type": "select",
                "options": {
                    "values": ["draft", "published"],
                },
            },
        ],
        # API rules using users collection
        "listRule": '@request.auth.id != "" && author = @request.auth.id || status = "published"',
        "viewRule": '@request.auth.id != "" && author = @request.auth.id || status = "published"',
        "createRule": '@request.auth.id != ""',
        "updateRule": "author = @request.auth.id",
        "deleteRule": "author = @request.auth.id",
    })

    # Create comments collection
    comments_collection = pb.collections.create(body={
        "name": "comments",
        "type": "base",
        "fields": [
            {
                "name": "content",
                "type": "text",
                "required": True,
            },
            {
                "name": "post",
                "type": "relation",
                "collectionId": posts_collection["id"],
                "maxSelect": 1,
                "required": True,
            },
            {
                "name": "author",
                "type": "relation",
                "collectionId": "_pb_users_auth_",  # Link to users
                "maxSelect": 1,
                "required": True,
            },
        ],
        "listRule": '@request.auth.id != ""',
        "viewRule": '@request.auth.id != ""',
        "createRule": '@request.auth.id != ""',
        "updateRule": "author = @request.auth.id",
        "deleteRule": "author = @request.auth.id",
    })

    print("Collections created successfully")

setup_user_related_collections()
```

### Example 3: User Creates and Manages Their Posts

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")

def user_post_management():
    # 1. User logs in
    pb.collection("users").auth_with_password("user@example.com", "password")
    user_id = pb.auth_store.record["id"]

    # 2. User creates a post
    post = pb.collection("posts").create(body={
        "title": "My First Post",
        "content": "This is my content",
        "author": user_id,
        "status": "draft",
    })

    print("Post created:", post["id"])

    # 3. User lists their own posts
    my_posts = pb.collection("posts").get_list(1, 20, query={
        "filter": f'author = "{user_id}"',
        "sort": "-created",
    })

    print("My posts:", len(my_posts["items"]))

    # 4. User updates their post
    pb.collection("posts").update(post["id"], body={
        "title": "Updated Title",
        "status": "published",
    })

    # 5. User views their post with author info
    updated_post = pb.collection("posts").get_one(post["id"], query={"expand": "author"})

    print("Post author:", updated_post["expand"]["author"]["name"])

    # 6. User deletes their post
    pb.collection("posts").delete(post["id"])

    print("Post deleted")

user_post_management()
```

### Example 4: Public Posts with User Information

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")

def view_public_posts():
    # No authentication required for public posts

    # Get published posts with author information
    posts = pb.collection("posts").get_list(1, 20, query={
        "filter": 'status = "published"',
        "expand": "author",
        "sort": "-created",
    })

    for post in posts["items"]:
        print("Title:", post["title"])
        print("Author:", post["expand"]["author"]["name"])
        # Email visibility depends on author's emailVisibility setting
        if post["expand"]["author"].get("emailVisibility"):
            print("Author Email:", post["expand"]["author"]["email"])

view_public_posts()
```

### Example 5: Email Verification Flow

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")

def email_verification_flow():
    # 1. User registers
    new_user = pb.collection("users").create(body={
        "email": "user@example.com",
        "password": "password123",
        "passwordConfirm": "password123",
        "name": "User Name",
    })

    print("User registered, verification email sent")
    print("Verified status:", new_user.get("verified"))  # False

    # 2. User clicks verification link in email
    # (This is handled by the backend automatically)

    # 3. Check verification status
    user = pb.collection("users").get_one(new_user["id"])
    print("Verified:", user.get("verified"))

    # 4. Request new verification email if needed
    pb.collection("users").request_verification("user@example.com")

email_verification_flow()
```

### Example 6: Password Reset Flow

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")

def password_reset_flow():
    # 1. User requests password reset
    pb.collection("users").request_password_reset("user@example.com")
    print("Password reset email sent")

    # 2. User clicks link in email and gets reset token
    # (Token is in the URL query parameter)

    # 3. User confirms password reset with token
    pb.collection("users").confirm_password_reset(
        "RESET_TOKEN_FROM_EMAIL",
        "newpassword123",
        "newpassword123"  # passwordConfirm
    )

    print("Password reset successful")

    # 4. User can now login with new password
    pb.collection("users").auth_with_password(
        "user@example.com",
        "newpassword123"
    )

password_reset_flow()
```

### Example 7: Using Users in API Rules for Other Collections

```python
from bosbase import BosBase

pb = BosBase("http://localhost:8090")

# Authenticate as superuser
pb.collection("_superusers").auth_with_password("admin@example.com", "adminpassword")

# Create a blog system with user-based access control
def create_blog_system():
    # Create posts collection
    posts = pb.collections.create(body={
        "name": "posts",
        "type": "base",
        "fields": [
            {"name": "title", "type": "text", "required": True},
            {"name": "content", "type": "editor"},
            {"name": "author", "type": "relation", "collectionId": "_pb_users_auth_", "maxSelect": 1, "required": True},
            {"name": "status", "type": "select", "options": {"values": ["draft", "published"]}},
        ],
        # Public can see published, authors can see their own
        "listRule": 'status = "published" || author = @request.auth.id',
        "viewRule": 'status = "published" || author = @request.auth.id',
        "createRule": '@request.auth.id != ""',
        "updateRule": "author = @request.auth.id",
        "deleteRule": "author = @request.auth.id",
    })

    # Create comments collection
    comments = pb.collections.create(body={
        "name": "comments",
        "type": "base",
        "fields": [
            {"name": "content", "type": "text", "required": True},
            {"name": "post", "type": "relation", "collectionId": posts["id"], "maxSelect": 1, "required": True},
            {"name": "author", "type": "relation", "collectionId": "_pb_users_auth_", "maxSelect": 1, "required": True},
        ],
        # Anyone can see comments on published posts, authors can see their own
        "listRule": 'post.status = "published" || author = @request.auth.id',
        "viewRule": 'post.status = "published" || author = @request.auth.id',
        "createRule": '@request.auth.id != "" && post.status = "published"',
        "updateRule": "author = @request.auth.id",
        "deleteRule": "author = @request.auth.id",
    })

    print("Blog system created with user-based access control")

create_blog_system()
```

---

## Best Practices

1. **Always use the built-in `users` collection** - Don't create a new one
2. **Use `_pb_users_auth_` as collectionId** when creating relations
3. **Check authentication** before user-specific operations
4. **Use `@request.auth.id`** in API rules for user-based access control
5. **Expand user relations** when you need user information
6. **Respect emailVisibility** - Don't expose emails unless user allows it
7. **Handle verification** - Check `verified` field for email verification status
8. **Use proper error handling** for registration/login failures

---

## Common Patterns

### Pattern 1: Owner-Only Access

```python
# Users can only access their own records
update_rule = "author = @request.auth.id"
delete_rule = "author = @request.auth.id"
```

### Pattern 2: Public Read, Authenticated Write

```python
list_rule = 'status = "published" || author = @request.auth.id'
view_rule = 'status = "published" || author = @request.auth.id'
create_rule = '@request.auth.id != ""'
```

### Pattern 3: Verified Users Only

```python
create_rule = '@request.auth.id != "" && @request.auth.verified = true'
```

### Pattern 4: Filter by Current User

```python
my_records = pb.collection("posts").get_list(1, 20, query={
    "filter": f'author = "{pb.auth_store.record["id"]}"',
})
```

---

This guide covers all essential operations with the built-in `users` collection. Remember: **always use the existing `users` collection, never create a new one manually.**
