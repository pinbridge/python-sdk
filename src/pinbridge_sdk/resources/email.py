"""Email preference resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from ..models.email import EmailPreferencesResponse, EmailPreferencesUpdateRequest
from .base import AsyncAPIResource, SyncAPIResource


def _serialize(data: EmailPreferencesUpdateRequest | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(data, EmailPreferencesUpdateRequest):
        return data.model_dump(mode="json")
    return dict(data)


class EmailResource(SyncAPIResource):
    def get_preferences(self) -> EmailPreferencesResponse:
        response = self._request("GET", "/v1/email/preferences")
        return self._model(EmailPreferencesResponse, response)

    def update_preferences(
        self, data: EmailPreferencesUpdateRequest | Mapping[str, Any]
    ) -> EmailPreferencesResponse:
        response = self._request("PATCH", "/v1/email/preferences", json=_serialize(data))
        return self._model(EmailPreferencesResponse, response)

    def unsubscribe(
        self,
        *,
        workspace_id: UUID | str,
        token: str,
        user_id: UUID | str,
    ) -> dict[str, str]:
        response = self._request(
            "GET",
            "/v1/email/unsubscribe",
            params={
                "workspace_id": str(workspace_id),
                "token": token,
                "user_id": str(user_id),
            },
        )
        return dict(self._json(response) or {})


class AsyncEmailResource(AsyncAPIResource):
    async def get_preferences(self) -> EmailPreferencesResponse:
        response = await self._request("GET", "/v1/email/preferences")
        return self._model(EmailPreferencesResponse, response)

    async def update_preferences(
        self, data: EmailPreferencesUpdateRequest | Mapping[str, Any]
    ) -> EmailPreferencesResponse:
        response = await self._request("PATCH", "/v1/email/preferences", json=_serialize(data))
        return self._model(EmailPreferencesResponse, response)

    async def unsubscribe(
        self,
        *,
        workspace_id: UUID | str,
        token: str,
        user_id: UUID | str,
    ) -> dict[str, str]:
        response = await self._request(
            "GET",
            "/v1/email/unsubscribe",
            params={
                "workspace_id": str(workspace_id),
                "token": token,
                "user_id": str(user_id),
            },
        )
        return dict(self._json(response) or {})
