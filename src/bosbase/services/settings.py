"""Application settings API."""

from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional

from .base import BaseService


class SettingsService(BaseService):
    def get_all(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.client.send("/api/settings", query=query, headers=headers)

    def update(
        self,
        *,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.client.send(
            "/api/settings",
            method="PATCH",
            body=body,
            query=query,
            headers=headers,
        )

    def test_s3(
        self,
        *,
        filesystem: str = "storage",
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        payload = dict(body or {})
        payload.setdefault("filesystem", filesystem)
        self.client.send(
            "/api/settings/test/s3",
            method="POST",
            body=payload,
            query=query,
            headers=headers,
        )

    def test_email(
        self,
        to_email: str,
        template: str,
        *,
        collection: Optional[str] = None,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        payload = dict(body or {})
        payload.setdefault("email", to_email)
        payload.setdefault("template", template)
        if collection:
            payload.setdefault("collection", collection)
        self.client.send(
            "/api/settings/test/email",
            method="POST",
            body=payload,
            query=query,
            headers=headers,
        )

    def generate_apple_client_secret(
        self,
        client_id: str,
        team_id: str,
        key_id: str,
        private_key: str,
        duration: int,
        *,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        payload = dict(body or {})
        payload.setdefault("clientId", client_id)
        payload.setdefault("teamId", team_id)
        payload.setdefault("keyId", key_id)
        payload.setdefault("privateKey", private_key)
        payload.setdefault("duration", duration)
        return self.client.send(
            "/api/settings/apple/generate-client-secret",
            method="POST",
            body=payload,
            query=query,
            headers=headers,
        )

    def get_category(
        self,
        category: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        settings = self.get_all(query=query, headers=headers)
        return settings.get(category)

    def update_meta(
        self,
        *,
        app_name: Optional[str] = None,
        app_url: Optional[str] = None,
        sender_name: Optional[str] = None,
        sender_address: Optional[str] = None,
        hide_controls: Optional[bool] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        meta = {
            key: value
            for key, value in {
                "appName": app_name,
                "appURL": app_url,
                "senderName": sender_name,
                "senderAddress": sender_address,
                "hideControls": hide_controls,
            }.items()
            if value is not None
        }
        return self.update(body={"meta": meta}, query=query, headers=headers)

    def get_application_settings(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        settings = self.get_all(query=query, headers=headers)
        return {
            "meta": settings.get("meta"),
            "trustedProxy": settings.get("trustedProxy"),
            "rateLimits": settings.get("rateLimits"),
            "batch": settings.get("batch"),
        }

    def update_application_settings(
        self,
        *,
        meta: Optional[Mapping[str, Any]] = None,
        trusted_proxy: Optional[Mapping[str, Any]] = None,
        rate_limits: Optional[Mapping[str, Any]] = None,
        batch: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if meta is not None:
            payload["meta"] = dict(meta)
        if trusted_proxy is not None:
            payload["trustedProxy"] = dict(trusted_proxy)
        if rate_limits is not None:
            payload["rateLimits"] = dict(rate_limits)
        if batch is not None:
            payload["batch"] = dict(batch)
        return self.update(body=payload, query=query, headers=headers)

    # ------------------------------------------------------------------
    # Mail helpers
    # ------------------------------------------------------------------

    def update_smtp(
        self,
        *,
        enabled: Optional[bool] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_method: Optional[str] = None,
        tls: Optional[bool] = None,
        local_name: Optional[str] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        smtp: Dict[str, Any] = {}
        if enabled is not None:
            smtp["enabled"] = enabled
        if host is not None:
            smtp["host"] = host
        if port is not None:
            smtp["port"] = port
        if username is not None:
            smtp["username"] = username
        if password is not None:
            smtp["password"] = password
        if auth_method is not None:
            smtp["authMethod"] = auth_method
        if tls is not None:
            smtp["tls"] = tls
        if local_name is not None:
            smtp["localName"] = local_name
        return self.update(body={"smtp": smtp}, query=query, headers=headers)

    def get_mail_settings(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        settings = self.get_all(query=query, headers=headers)
        meta = settings.get("meta") or {}
        return {
            "meta": {
                "senderName": meta.get("senderName"),
                "senderAddress": meta.get("senderAddress"),
            },
            "smtp": settings.get("smtp"),
        }

    def update_mail_settings(
        self,
        *,
        sender_name: Optional[str] = None,
        sender_address: Optional[str] = None,
        smtp: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if sender_name is not None or sender_address is not None:
            meta: Dict[str, Any] = {}
            if sender_name is not None:
                meta["senderName"] = sender_name
            if sender_address is not None:
                meta["senderAddress"] = sender_address
            payload["meta"] = meta
        if smtp is not None:
            payload["smtp"] = dict(smtp)
        return self.update(body=payload, query=query, headers=headers)

    def test_mail(
        self,
        to_email: str,
        template: str = "verification",
        collection: str = "_superusers",
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        self.test_email(to_email, template, collection=collection, query=query, headers=headers)

    # ------------------------------------------------------------------
    # S3 / Storage helpers
    # ------------------------------------------------------------------

    def update_s3(
        self,
        *,
        enabled: Optional[bool] = None,
        bucket: Optional[str] = None,
        region: Optional[str] = None,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret: Optional[str] = None,
        force_path_style: Optional[bool] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        s3: Dict[str, Any] = {}
        if enabled is not None:
            s3["enabled"] = enabled
        if bucket is not None:
            s3["bucket"] = bucket
        if region is not None:
            s3["region"] = region
        if endpoint is not None:
            s3["endpoint"] = endpoint
        if access_key is not None:
            s3["accessKey"] = access_key
        if secret is not None:
            s3["secret"] = secret
        if force_path_style is not None:
            s3["forcePathStyle"] = force_path_style
        return self.update(body={"s3": s3}, query=query, headers=headers)

    def get_storage_s3(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        return self.get_category("s3", query=query, headers=headers)

    def update_storage_s3(
        self,
        *,
        enabled: Optional[bool] = None,
        bucket: Optional[str] = None,
        region: Optional[str] = None,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret: Optional[str] = None,
        force_path_style: Optional[bool] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.update_s3(
            enabled=enabled,
            bucket=bucket,
            region=region,
            endpoint=endpoint,
            access_key=access_key,
            secret=secret,
            force_path_style=force_path_style,
            query=query,
            headers=headers,
        )

    def test_storage_s3(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        self.test_s3(filesystem="storage", query=query, headers=headers)

    # ------------------------------------------------------------------
    # Backup helpers
    # ------------------------------------------------------------------

    def update_backups(
        self,
        *,
        cron: Optional[str] = None,
        cron_max_keep: Optional[int] = None,
        s3: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        if cron is not None:
            config["cron"] = cron
        if cron_max_keep is not None:
            config["cronMaxKeep"] = cron_max_keep
        if s3 is not None:
            config["s3"] = dict(s3)
        return self.update(body={"backups": config}, query=query, headers=headers)

    def get_backup_settings(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        settings = self.get_all(query=query, headers=headers)
        return settings.get("backups") or {}

    def update_backup_settings(
        self,
        *,
        cron: Optional[str] = None,
        cron_max_keep: Optional[int] = None,
        s3: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.update_backups(
            cron=cron,
            cron_max_keep=cron_max_keep,
            s3=s3,
            query=query,
            headers=headers,
        )

    def set_auto_backup_schedule(
        self,
        cron: str,
        cron_max_keep: Optional[int] = None,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.update_backups(
            cron=cron or "",
            cron_max_keep=cron_max_keep,
            query=query,
            headers=headers,
        )

    def disable_auto_backup(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.update_backups(cron="", query=query, headers=headers)

    def test_backups_s3(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        self.test_s3(filesystem="backups", query=query, headers=headers)

    # ------------------------------------------------------------------
    # Batch / Rate limits / Trusted proxy helpers
    # ------------------------------------------------------------------

    def update_batch(
        self,
        *,
        enabled: Optional[bool] = None,
        max_requests: Optional[int] = None,
        timeout: Optional[int] = None,
        max_body_size: Optional[int] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        if enabled is not None:
            config["enabled"] = enabled
        if max_requests is not None:
            config["maxRequests"] = max_requests
        if timeout is not None:
            config["timeout"] = timeout
        if max_body_size is not None:
            config["maxBodySize"] = max_body_size
        return self.update(body={"batch": config}, query=query, headers=headers)

    def update_rate_limits(
        self,
        *,
        enabled: Optional[bool] = None,
        rules: Optional[list] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        if enabled is not None:
            config["enabled"] = enabled
        if rules is not None:
            config["rules"] = rules
        return self.update(body={"rateLimits": config}, query=query, headers=headers)

    def update_trusted_proxy(
        self,
        *,
        headers_list: Optional[list] = None,
        use_leftmost_ip: Optional[bool] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        if headers_list is not None:
            config["headers"] = headers_list
        if use_leftmost_ip is not None:
            config["useLeftmostIP"] = use_leftmost_ip
        return self.update(body={"trustedProxy": config}, query=query, headers=headers)

    # ------------------------------------------------------------------
    # Log helpers
    # ------------------------------------------------------------------

    def update_logs(
        self,
        *,
        max_days: Optional[int] = None,
        min_level: Optional[int] = None,
        log_ip: Optional[bool] = None,
        log_auth_id: Optional[bool] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        if max_days is not None:
            config["maxDays"] = max_days
        if min_level is not None:
            config["minLevel"] = min_level
        if log_ip is not None:
            config["logIP"] = log_ip
        if log_auth_id is not None:
            config["logAuthId"] = log_auth_id
        return self.update(body={"logs": config}, query=query, headers=headers)

    def get_log_settings(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        settings = self.get_all(query=query, headers=headers)
        return settings.get("logs") or {}

    def update_log_settings(
        self,
        *,
        max_days: Optional[int] = None,
        min_level: Optional[int] = None,
        log_ip: Optional[bool] = None,
        log_auth_id: Optional[bool] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.update_logs(
            max_days=max_days,
            min_level=min_level,
            log_ip=log_ip,
            log_auth_id=log_auth_id,
            query=query,
            headers=headers,
        )

    def set_log_retention_days(
        self,
        max_days: int,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.update_logs(max_days=max_days, query=query, headers=headers)

    def set_min_log_level(
        self,
        min_level: int,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.update_logs(min_level=min_level, query=query, headers=headers)

    def set_log_ip_addresses(
        self,
        enabled: bool,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.update_logs(log_ip=enabled, query=query, headers=headers)

    def set_log_auth_ids(
        self,
        enabled: bool,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.update_logs(log_auth_id=enabled, query=query, headers=headers)
