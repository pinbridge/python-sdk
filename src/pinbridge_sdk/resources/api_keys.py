"""API key resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from ..models.api_keys import APIKeyCreate, APIKeyCreateResponse, APIKeyResponse, APIKeyUpdate
from .base import AsyncAPIResource, SyncAPIResource


class APIKeysResource(SyncAPIResource):
    def create(self, data: APIKeyCreate | Mapping[str, Any]) -> APIKeyCreateResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, APIKeyCreate)
            else dict(data)
        )
        response = self._request("POST", "/v1/api-keys", json=payload)
        return self._model(APIKeyCreateResponse, response)

    def list(self) -> list[APIKeyResponse]:
        response = self._request("GET", "/v1/api-keys")
        return self._list(APIKeyResponse, response)

    def update(self, key_id: UUID | str, data: APIKeyUpdate | Mapping[str, Any]) -> APIKeyResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, APIKeyUpdate)
            else dict(data)
        )
        response = self._request(
            "PATCH",
            "/v1/api-keys/{key_id}",
            path_params={"key_id": key_id},
            json=payload,
        )
        return self._model(APIKeyResponse, response)

    def revoke(self, key_id: UUID | str) -> None:
        self._request("DELETE", "/v1/api-keys/{key_id}", path_params={"key_id": key_id})


class AsyncAPIKeysResource(AsyncAPIResource):
    async def create(self, data: APIKeyCreate | Mapping[str, Any]) -> APIKeyCreateResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, APIKeyCreate)
            else dict(data)
        )
        response = await self._request("POST", "/v1/api-keys", json=payload)
        return self._model(APIKeyCreateResponse, response)

    async def list(self) -> list[APIKeyResponse]:
        response = await self._request("GET", "/v1/api-keys")
        return self._list(APIKeyResponse, response)

    async def update(
        self, key_id: UUID | str, data: APIKeyUpdate | Mapping[str, Any]
    ) -> APIKeyResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, APIKeyUpdate)
            else dict(data)
        )
        response = await self._request(
            "PATCH",
            "/v1/api-keys/{key_id}",
            path_params={"key_id": key_id},
            json=payload,
        )
        return self._model(APIKeyResponse, response)

    async def revoke(self, key_id: UUID | str) -> None:
        await self._request("DELETE", "/v1/api-keys/{key_id}", path_params={"key_id": key_id})
