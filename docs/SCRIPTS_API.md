# Scripts API - Python SDK

## Overview

`pb.scripts` provides superuser-only helpers for storing and managing function code snippets (for example, Python scripts) through the `/api/scripts` endpoints. The backend takes care of persistence and automatic version bumps whenever a script is updated.

**Table schema**
- `id` (uuidv7, auto-generated)
- `name` (primary key)
- `content` (script body)
- `description` (optional)
- `version` (starts at 1, increments by 1 on every update)
- `created`, `updated` (ISO timestamps)


## Authentication

Authenticate as a superuser before calling any Scripts API method:

```python
from bosbase import BosBase

pb = BosBase("http://127.0.0.1:8090")

pb.collection("_superusers").auth_with_password("admin@example.com", "password")
```

## Creating a Script

`pb.scripts.create` creates the table if it does not exist, writes the script, and returns the stored row with `version = 1`.

```python
python_code = """
def main():
    print("Hello from functions!")


if __name__ == "__main__":
    main()
"""

script = pb.scripts.create({
    "name": "hello.py",
    "content": python_code,
    "description": "Hello from functions!",
})

print(script["id"])       # uuidv7
print(script["version"])  # 1
```

## Reading Scripts

Fetch a single script by name or list all scripts:

```python
script = pb.scripts.get("hello.py")
print(script["content"])

all_scripts = pb.scripts.list()
print([[s["name"], s["version"]] for s in all_scripts])
```

## Updating Scripts (auto-versioned)

Updates increment `version` by 1 automatically and refresh `updated`.

```python
updated = pb.scripts.update("hello.py", {
    "content": """
def main():
    print("Hi from functions!")


if __name__ == "__main__":
    main()
""",
    "description": "Now returns both total and count",
})

print(updated["version"])  # previous version + 1
```

You can update just the description if the code is unchanged:

```python
pb.scripts.update("hello.py", {"description": "Docs-only tweak"})
```

## Executing Scripts

Run a stored script via the backend runner (uses `/api/scripts/{name}/execute`).
The server loads the latest script content, writes it under `EXECUTE_PATH` (defaults to `/pb/functions`), activates `.venv/bin/activate`, and runs `python <name>`. The combined stdout/stderr is returned.
Execution permission is controlled by `pb.scripts_permissions`:
- `anonymous`: anyone can execute
- `user`: requires an authenticated user (or superuser)
- `superuser`: only superuser (default when no permission entry exists)

```python
result = pb.scripts.execute("hello.py")
print(result["output"])  # console output from the python script
```

## Managing Script Permissions

Use `pb.scripts_permissions` to control who can call `/api/scripts/{name}/execute`.
Valid `content` values are:
- `anonymous`: anyone can execute
- `user`: authenticated users in the `users` collection (and superusers)
- `superuser`: only superusers

If no permission row exists for a script, execution is superuser-only.

```python
# create or update permissions (superuser required)
pb.scripts_permissions.create({
    "scriptName": "hello.py",
    "content": "user",
})

perm = pb.scripts_permissions.get("hello.py")
print(perm["content"])  # "user"
```

## Running Shell Commands

Run arbitrary shell commands in the functions directory (defaults to `EXECUTE_PATH` env or `/pb/functions`). Useful for managing dependencies, inspecting files, etc. **Superuser authentication is required.**

```python
result = pb.scripts.command("cat pyproject.toml")
print(result["output"])

result2 = pb.scripts.command('uv add "httpx>0.1.0"')
print(result2["output"])
```

Notes for `command`:
- Superuser auth is required.
- Commands run with `EXECUTE_PATH` as the working directory and inherit environment vars (including `EXECUTE_PATH`).
- The combined stdout/stderr is returned as `result["output"]`; non-zero exit codes surface as errors.

## Managing Script Permissions

Superusers can define who may execute a script using `pb.scripts_permissions`.

Allowed permission levels: `"anonymous"`, `"user"`, `"superuser"` (default when no entry exists).

```python
pb.scripts_permissions.create({
    "scriptName": "hello.py",
    "content": "user",  # allow logged-in users and superusers
})

perm = pb.scripts_permissions.get("hello.py")
print(perm["content"])  # user

pb.scripts_permissions.update("hello.py", {"content": "anonymous"})

pb.scripts_permissions.delete("hello.py")  # back to superuser-only execution
```

## Deleting Scripts

Remove a script by name. Returns `True` when a row was deleted.

```python
removed = pb.scripts.delete("hello.py")
print(removed)  # True or False
```

## Notes

- Script CRUD and `scripts_permissions` require superuser auth; `scripts.execute` obeys the stored permission level; `command` is superuser-only.
- `id` is generated as a UUIDv7 string on insert and backfilled automatically for older rows.
- Execution uses the directory from `EXECUTE_PATH` env/docker-compose (default `/pb/functions`) and expects a `.venv` there with Python available.
- `command` also runs inside `EXECUTE_PATH` and returns combined stdout/stderr.
- Content is stored as plain text.
- Table creation runs automatically on first use of the service instance.
