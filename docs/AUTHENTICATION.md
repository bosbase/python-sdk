# Authentication - Python SDK

The Python SDK keeps auth tokens and the authenticated record inside a local `AuthStore`. All services reuse the stored token on every request.

```python
from bosbase import BosBase

pb = BosBase("http://127.0.0.1:8090")
```

## Superusers / Admin API

```python
pb.collection("_superusers").auth_with_password(
    "admin@example.com",
    "password",
)
```

The `_superusers` collection is an auth collection, so you can call all `RecordService` auth helpers on it as well (`auth_refresh`, `request_password_reset`, etc.).

## Auth Collections

Authenticate with the collection that represents your end users:

```python
users = pb.collection("users")

auth_data = users.auth_with_password("demo@example.com", "secret123")
print(auth_data["token"])
print(pb.auth_store.record)  # automatically populated
```

### Refreshing Tokens

```python
if not pb.auth_store.is_valid():
    users.auth_refresh()
```

### Logout

```python
pb.auth_store.clear()
```

## OAuth2 Flow

`auth_with_oauth2` uses realtime callbacks to complete the flow without extra HTTP servers.

```python
def open_oauth_url(url: str) -> None:
    print("Visit:", url)

auth_data = users.auth_with_oauth2(
    "google",
    url_callback=open_oauth_url,
    scopes=["profile", "email"],
    create_data={"name": "Google User"},
)
```

If you already have the OAuth2 code/verifier pair (for example in server‑side code), call `auth_with_oauth2_code()`.

## OTP & MFA Helpers

```python
otp = users.request_otp("demo@example.com")
users.auth_with_otp(otp["otpId"], "123456")
```

MFA enforcement is configured per auth collection and is evaluated automatically by the backend.

## Password Reset & Verification

```python
users.request_password_reset("demo@example.com")
users.confirm_password_reset(token, "newpass", "newpass")

users.request_verification("demo@example.com")
users.confirm_verification(verification_token)

users.request_email_change("new@example.com")
users.confirm_email_change(change_token, "currentPassword")
```

## Auth Store

`pb.auth_store` exposes:

- `token`: the current JWT
- `record`: the current auth record (or `None`)
- `is_valid()`: quick expiry check
- `save(new_token, record)`
- `clear()`

You can also instantiate the client with a custom store:

```python
from bosbase import BosBase, AuthStore

class MemoryStore(AuthStore):
    pass  # override save/clear if you want to hook external persistence

pb = BosBase("http://127.0.0.1:8090", auth_store=MemoryStore())
```

## Impersonation

Superusers can generate short-lived tokens for another auth collection:

```python
customer_client = users.impersonate("CUSTOMER_ID", duration=600)
customer_profile = customer_client.collection("profiles").get_first_list_item(
    "user = {:id}", {"id": customer_client.auth_store.record["id"]}
)
```

## Tips

- Store tokens in memory when running inside trusted server environments.
- When exposing the SDK in desktop/CLI apps, wrap `pb.auth_store` with encrypted storage.
- Use `pb.auth_store.on_change` style hooks by building your own store subclass that notifies the UI whenever `save()` or `clear()` is called.
