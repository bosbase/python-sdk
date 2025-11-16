"""Collection management service."""

from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional

from .base import BaseCrudService
from ..utils import encode_path_segment


class CollectionService(BaseCrudService):
    @property
    def base_crud_path(self) -> str:
        return "/api/collections"

    def delete_collection(
        self,
        collection_id_or_name: str,
        *,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        self.delete(
            collection_id_or_name,
            body=body,
            query=query,
            headers=headers,
        )

    def truncate(
        self,
        collection_id_or_name: str,
        *,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        encoded = encode_path_segment(collection_id_or_name)
        self.client.send(
            f"{self.base_crud_path}/{encoded}/truncate",
            method="DELETE",
            body=body,
            query=query,
            headers=headers,
        )

    def import_collections(
        self,
        collections: Any,
        *,
        delete_missing: bool = False,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        payload = dict(body or {})
        payload["collections"] = collections
        payload["deleteMissing"] = delete_missing

        self.client.send(
            f"{self.base_crud_path}/import",
            method="PUT",
            body=payload,
            query=query,
            headers=headers,
        )

    def get_scaffolds(
        self,
        *,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        payload = dict(body or {})
        return self.client.send(
            f"{self.base_crud_path}/meta/scaffolds",
            body=payload,
            query=query,
            headers=headers,
        )

    def create_from_scaffold(
        self,
        scaffold_type: str,
        name: str,
        *,
        overrides: Optional[Mapping[str, Any]] = None,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        scaffolds = self.get_scaffolds(query=query, headers=headers)
        scaffold = scaffolds.get(scaffold_type)
        if not scaffold:
            raise ValueError(f"Scaffold for type '{scaffold_type}' not found.")

        data = dict(scaffold)
        data["name"] = name
        if overrides:
            data.update(overrides)
        if body:
            data.update(body)
        return self.create(body=data, query=query, headers=headers)

    def create_base(
        self,
        name: str,
        *,
        overrides: Optional[Mapping[str, Any]] = None,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.create_from_scaffold(
            "base",
            name,
            overrides=overrides,
            body=body,
            query=query,
            headers=headers,
        )

    def create_auth(
        self,
        name: str,
        *,
        overrides: Optional[Mapping[str, Any]] = None,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.create_from_scaffold(
            "auth",
            name,
            overrides=overrides,
            body=body,
            query=query,
            headers=headers,
        )

    def create_view(
        self,
        name: str,
        *,
        view_query: Optional[str] = None,
        overrides: Optional[Mapping[str, Any]] = None,
        body: Optional[Mapping[str, Any]] = None,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        scaffold_overrides = dict(overrides or {})
        if view_query is not None:
            scaffold_overrides["viewQuery"] = view_query
        return self.create_from_scaffold(
            "view",
            name,
            overrides=scaffold_overrides,
            body=body,
            query=query,
            headers=headers,
        )

    def get_schema(
        self,
        collection_id_or_name: str,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        encoded = encode_path_segment(collection_id_or_name)
        return self.client.send(
            f"{self.base_crud_path}/{encoded}/schema",
            query=query,
            headers=headers,
        )

    def get_all_schemas(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.client.send(
            f"{self.base_crud_path}/schemas",
            query=query,
            headers=headers,
        )
