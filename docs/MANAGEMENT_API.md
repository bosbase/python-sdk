# Management API Documentation

This document covers the management API capabilities available in the Python SDK, which correspond to the features available in the backend management UI.

> **Note**: All management API operations require superuser authentication.

## Table of Contents

- [Settings Service](#settings-service)
  - [Application Configuration](#application-configuration)
  - [Mail Configuration](#mail-configuration)
  - [Storage Configuration](#storage-configuration)
  - [Backup Configuration](#backup-configuration)
  - [Log Configuration](#log-configuration)
- [Backup Service](#backup-service)
- [Log Service](#log-service)
- [Cron Service](#cron-service)
- [Health Service](#health-service)
- [Collection Service](#collection-service)

---

## Settings Service

The Settings Service provides comprehensive management of application settings, matching the capabilities available in the backend management UI.

### Application Configuration

Manage application settings including meta information, trusted proxy, rate limits, and batch configuration.

#### Get Application Settings

```python
settings = pb.settings.get_application_settings()
# Returns: { meta, trustedProxy, rateLimits, batch }
```

**Example:**
```python
app_settings = pb.settings.get_application_settings()
print(app_settings["meta"]["appName"])  # Application name
print(app_settings["rateLimits"]["rules"])  # Rate limit rules
```

#### Update Application Settings

```python
pb.settings.update_application_settings({
    "meta": {
        "appName": "My App",
        "appURL": "https://example.com",
        "hideControls": False
    },
    "trustedProxy": {
        "headers": ["X-Forwarded-For"],
        "useLeftmostIP": True
    },
    "rateLimits": {
        "enabled": True,
        "rules": [
            {
                "label": "api/users",
                "duration": 3600,
                "maxRequests": 100
            }
        ]
    },
    "batch": {
        "enabled": True,
        "maxRequests": 100,
        "interval": 200
    }
})
```

#### Individual Settings Updates

**Update Meta Settings:**
```python
pb.settings.update_meta({
    "appName": "My App",
    "appURL": "https://example.com",
    "senderName": "My App",
    "senderAddress": "noreply@example.com",
    "hideControls": False
})
```

**Update Trusted Proxy:**
```python
pb.settings.update_trusted_proxy({
    "headers": ["X-Forwarded-For", "X-Real-IP"],
    "useLeftmostIP": True
})
```

**Update Rate Limits:**
```python
pb.settings.update_rate_limits({
    "enabled": True,
    "rules": [
        {
            "label": "api/users",
            "audience": "public",
            "duration": 3600,
            "maxRequests": 100
        }
    ]
})
```

**Update Batch Configuration:**
```python
pb.settings.update_batch({
    "enabled": True,
    "maxRequests": 100,
    "timeout": 30,
    "maxBodySize": 10485760
})
```

---

### Mail Configuration

Manage SMTP email settings and sender information.

#### Get Mail Settings

```python
mail_settings = pb.settings.get_mail_settings()
# Returns: { meta: { senderName, senderAddress }, smtp }
```

**Example:**
```python
mail = pb.settings.get_mail_settings()
print(mail["meta"]["senderName"])  # Sender name
print(mail["smtp"]["host"])  # SMTP host
```

#### Update Mail Settings

Update both sender info and SMTP configuration in one call:

```python
pb.settings.update_mail_settings({
    "senderName": "My App",
    "senderAddress": "noreply@example.com",
    "smtp": {
        "enabled": True,
        "host": "smtp.example.com",
        "port": 587,
        "username": "user@example.com",
        "password": "password",
        "authMethod": "PLAIN",
        "tls": True,
        "localName": "localhost"
    }
})
```

#### Update SMTP Only

```python
pb.settings.update_smtp({
    "enabled": True,
    "host": "smtp.example.com",
    "port": 587,
    "username": "user@example.com",
    "password": "password",
    "authMethod": "PLAIN",
    "tls": True,
    "localName": "localhost"
})
```

#### Test Email

Send a test email to verify SMTP configuration:

```python
pb.settings.test_mail(
    "test@example.com",
    "verification",  # template: verification, password-reset, email-change, otp, login-alert
    "_superusers"  # collection (optional, defaults to _superusers)
)
```

**Email Templates:**
- `verification` - Email verification template
- `password-reset` - Password reset template
- `email-change` - Email change confirmation template
- `otp` - One-time password template
- `login-alert` - Login alert template

---

### Storage Configuration

Manage S3 storage configuration for file storage.

#### Get Storage S3 Configuration

```python
s3_config = pb.settings.get_storage_s3()
# Returns: { enabled, bucket, region, endpoint, accessKey, secret, forcePathStyle }
```

#### Update Storage S3 Configuration

```python
pb.settings.update_storage_s3({
    "enabled": True,
    "bucket": "my-bucket",
    "region": "us-east-1",
    "endpoint": "https://s3.amazonaws.com",
    "accessKey": "ACCESS_KEY",
    "secret": "SECRET_KEY",
    "forcePathStyle": False
})
```

#### Test Storage S3 Connection

```python
pb.settings.test_storage_s3()
# Returns: True if connection succeeds
```

---

### Backup Configuration

Manage auto-backup scheduling and S3 storage for backups.

#### Get Backup Settings

```python
backup_settings = pb.settings.get_backup_settings()
# Returns: { cron, cronMaxKeep, s3 }
```

**Example:**
```python
backups = pb.settings.get_backup_settings()
print(backups["cron"])  # Cron expression (e.g., "0 0 * * *")
print(backups["cronMaxKeep"])  # Maximum backups to keep
```

#### Update Backup Settings

```python
pb.settings.update_backup_settings({
    "cron": "0 0 * * *",  # Daily at midnight (empty string to disable)
    "cronMaxKeep": 10,  # Keep maximum 10 backups
    "s3": {
        "enabled": True,
        "bucket": "backup-bucket",
        "region": "us-east-1",
        "endpoint": "https://s3.amazonaws.com",
        "accessKey": "ACCESS_KEY",
        "secret": "SECRET_KEY",
        "forcePathStyle": False
    }
})
```

#### Set Auto-Backup Schedule

```python
# Enable daily backups at midnight, keep 10 backups
pb.settings.set_auto_backup_schedule("0 0 * * *", 10)

# Disable auto-backup
pb.settings.disable_auto_backup()
```

**Common Cron Expressions:**
- `"0 0 * * *"` - Daily at midnight
- `"0 0 * * 0"` - Weekly on Sunday at midnight
- `"0 0 1 * *"` - Monthly on the 1st at midnight
- `"0 0 * * 1,3"` - Twice weekly (Monday and Wednesday)

#### Test Backups S3 Connection

```python
pb.settings.test_backups_s3()
# Returns: True if connection succeeds
```

---

### Log Configuration

Manage log retention and logging settings.

#### Get Log Settings

```python
log_settings = pb.settings.get_log_settings()
# Returns: { maxDays, minLevel, logIP, logAuthId }
```

#### Update Log Settings

```python
pb.settings.update_log_settings({
    "maxDays": 30,  # Retain logs for 30 days
    "minLevel": 0,  # Minimum log level (negative=debug/info, 0=warning, positive=error)
    "logIP": True,  # Log IP addresses
    "logAuthId": True  # Log authentication IDs
})
```

#### Individual Log Settings

```python
# Set log retention days
pb.settings.set_log_retention_days(30)

# Set minimum log level
pb.settings.set_min_log_level(0)  # -100 to 100

# Enable/disable IP logging
pb.settings.set_log_ip_addresses(True)

# Enable/disable auth ID logging
pb.settings.set_log_auth_ids(True)
```

**Log Levels:**
- Negative values: Debug/Info levels
- `0`: Default/Warning level
- Positive values: Error levels

---

## Backup Service

Manage application backups - create, list, upload, delete, and restore backups.

### List All Backups

```python
backups = pb.backups.get_full_list()
# Returns: Array of { key, size, modified }
```

**Example:**
```python
backups = pb.backups.get_full_list()
for backup in backups:
    print(f"{backup['key']}: {backup['size']} bytes, modified: {backup['modified']}")
```

### Create Backup

```python
pb.backups.create("backup-2024-01-01")
# Creates a new backup with the specified basename
```

### Upload Backup

Upload an existing backup file:

```python
with open("backup.zip", "rb") as fh:
    pb.backups.upload({"file": ("backup.zip", fh, "application/zip")})
```

### Delete Backup

```python
pb.backups.delete("backup-2024-01-01")
# Deletes the specified backup file
```

### Restore Backup

```python
pb.backups.restore("backup-2024-01-01")
# Restores the application from the specified backup
```

**Warning**: Restoring a backup will replace all current application data!

### Get Backup Download URL

```python
# First, get a file token
token = pb.files.get_token()

# Then build the download URL
url = pb.backups.get_download_url(token, "backup-2024-01-01")
print(url)  # Full URL to download the backup
```

---

## Log Service

Query and analyze application logs.

### List Logs

```python
result = pb.logs.get_list(1, 30, {
    "filter": "level >= 0",
    "sort": "-created"
})
# Returns: { page, perPage, totalItems, totalPages, items }
```

**Example with filtering:**
```python
# Get error logs from the last 24 hours
from datetime import datetime, timedelta

yesterday = datetime.utcnow() - timedelta(days=1)

error_logs = pb.logs.get_list(1, 50, {
    "filter": f'level > 0 && created >= "{yesterday.isoformat()}"',
    "sort": "-created"
})

for log in error_logs["items"]:
    print(f"[{log['level']}] {log['message']}")
```

### Get Single Log

```python
log = pb.logs.get_one("log-id")
# Returns: log dict with full log details
```

### Get Log Statistics

```python
stats = pb.logs.get_stats({
    "filter": "level >= 0"  # Optional filter
})
# Returns: list of { total, date } - hourly statistics
```

**Example:**
```python
stats = pb.logs.get_stats()
for stat in stats:
    print(f"{stat['date']}: {stat['total']} requests")
```

---

## Cron Service

Manage and execute cron jobs.

### List All Cron Jobs

```python
cron_jobs = pb.crons.get_full_list()
# Returns: list of { id, expression }
```

**Example:**
```python
cron_jobs = pb.crons.get_full_list()
for job in cron_jobs:
    print(f"Job {job['id']}: {job['expression']}")
```

### Run Cron Job

Manually trigger a cron job:

```python
pb.crons.run("job-id")
# Executes the specified cron job immediately
```

**Example:**
```python
cron_jobs = pb.crons.get_full_list()
backup_job = next((job for job in cron_jobs if "backup" in job["id"]), None)
if backup_job:
    pb.crons.run(backup_job["id"])
    print("Backup job executed manually")
```

---

## Health Service

Check the health status of the API.

### Check Health

```python
health = pb.health.check()
# Returns: Health status information
```

**Example:**
```python
try:
    health = pb.health.check()
    print("API is healthy:", health)
except Exception as error:
    print("Health check failed:", error)
```

---

## Collection Service

Manage collections (schemas) programmatically.

### List Collections

```python
collections = pb.collections.get_list(1, 30)
# Returns: Paginated list of collections
```

### Get Collection

```python
collection = pb.collections.get_one("collection-id-or-name")
# Returns: Full collection schema
```

### Create Collection

```python
collection = pb.collections.create(body={
    "name": "posts",
    "type": "base",
    "schema": [
        {
            "name": "title",
            "type": "text",
            "required": True
        },
        {
            "name": "content",
            "type": "editor",
            "required": False
        }
    ]
})
```

### Update Collection

```python
pb.collections.update("collection-id", body={
    "schema": [
        # Updated schema
    ]
})
```

### Delete Collection

```python
pb.collections.delete("collection-id")
```

### Truncate Collection

Delete all records in a collection (keeps the schema):

```python
pb.collections.truncate("collection-id")
```

### Import Collections

```python
collections = [
    {
        "name": "collection1",
        # ... collection schema
    },
    {
        "name": "collection2",
        # ... collection schema
    }
]

pb.collections.import_collections(collections, False)  # False = don't delete missing collections
```

---

## Complete Example: Automated Backup Management

```python
from bosbase import BosBase

pb = BosBase("http://127.0.0.1:8090")

# Authenticate as superuser
pb.collection("_superusers").auth_with_password("admin@example.com", "password")

# Check current backup settings
backup_settings = pb.settings.get_backup_settings()
print("Current backup schedule:", backup_settings["cron"])

# List all existing backups
backups = pb.backups.get_full_list()
print(f"Found {len(backups)} backups")

# Create a new backup
from datetime import date
pb.backups.create(f"manual-backup-{date.today().isoformat()}")
print("Backup created successfully")

# Get updated backup list
updated_backups = pb.backups.get_full_list()
print(f"Now have {len(updated_backups)} backups")

# Configure auto-backup (daily at 2 AM, keep 7 backups)
pb.settings.set_auto_backup_schedule("0 2 * * *", 7)
print("Auto-backup configured")

# Test backup S3 connection if configured
try:
    pb.settings.test_backups_s3()
    print("S3 backup storage is working")
except Exception as error:
    print("S3 backup storage test failed:", error)
```

---

## Complete Example: Log Monitoring

```python
from bosbase import BosBase

pb = BosBase("http://127.0.0.1:8090")

# Authenticate as superuser
pb.collection("_superusers").auth_with_password("admin@example.com", "password")

# Get log settings
log_settings = pb.settings.get_log_settings()
print("Log retention:", log_settings["maxDays"], "days")
print("Minimum log level:", log_settings["minLevel"])

# Get recent error logs
error_logs = pb.logs.get_list(1, 20, {
    "filter": "level > 0",
    "sort": "-created"
})

print(f"Found {error_logs['totalItems']} error logs")
for log in error_logs["items"]:
    print(f"[{log['level']}] {log['message']} - {log['created']}")

# Get hourly statistics for the last 24 hours
from datetime import datetime, timedelta
cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
stats = pb.logs.get_stats({
    "filter": f'created >= "{cutoff}"'
})

print("Hourly request statistics:")
for stat in stats:
    print(f"{stat['date']}: {stat['total']} requests")

# Update log settings to retain logs for 14 days
pb.settings.set_log_retention_days(14)
print("Log retention updated to 14 days")
```

---

## Complete Example: Application Configuration Management

```python
from bosbase import BosBase

pb = BosBase("http://127.0.0.1:8090")

# Authenticate as superuser
pb.collection("_superusers").auth_with_password("admin@example.com", "password")

# Get current application settings
app_settings = pb.settings.get_application_settings()
print("App Name:", app_settings.get("meta", {}).get("appName"))
print("App URL:", app_settings.get("meta", {}).get("appURL"))

# Update application configuration
pb.settings.update_application_settings({
    "meta": {
        "appName": "My Production App",
        "appURL": "https://api.example.com",
        "hideControls": False
    },
    "rateLimits": {
        "enabled": True,
        "rules": [
            {
                "label": "api/users",
                "duration": 3600,
                "maxRequests": 100
            },
            {
                "label": "api/posts",
                "duration": 3600,
                "maxRequests": 200
            }
        ]
    },
    "batch": {
        "enabled": True,
        "maxRequests": 100,
        "interval": 200
    }
})

print("Application settings updated")

# Configure trusted proxy
pb.settings.update_trusted_proxy({
    "headers": ["X-Forwarded-For", "X-Real-IP"],
    "useLeftmostIP": True
})

print("Trusted proxy configured")
```

---

## Error Handling

All management API methods can throw `ClientResponseError`. Always handle errors appropriately:

```python
from bosbase.exceptions import ClientResponseError

try:
    pb.backups.create("my-backup")
    print("Backup created successfully")
except ClientResponseError as error:
    if error.status == 401:
        print("Authentication required")
    elif error.status == 403:
        print("Superuser access required")
    else:
        print("Error:", error.message)
```

---

## Notes

1. **Authentication**: All management API operations require superuser authentication. Use `pb.collection('_superusers').auth_with_password()` to authenticate.

2. **Rate Limiting**: Be mindful of rate limits when making multiple management API calls.

3. **Backup Safety**: Always test backup restoration in a safe environment before using in production.

4. **Log Retention**: Setting appropriate log retention helps manage storage usage.

5. **Cron Jobs**: Manual cron execution is useful for testing but should be used carefully in production.

For more information on specific services, see:
- [Backups API](./BACKUPS_API.md) - Detailed backup operations
- [Logs API](./LOGS_API.md) - Detailed log operations
- [Collections API](./COLLECTION_API.md) - Collection management
