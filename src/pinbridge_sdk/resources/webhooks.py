"""Webhook resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from ..models.webhooks import WebhookCreate, WebhookResponse, WebhookUpdate
from .base import AsyncAPIResource, SyncAPIResource


class WebhooksResource(SyncAPIResource):
    def create(self, data: WebhookCreate | Mapping[str, Any]) -> WebhookResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, WebhookCreate)
            else dict(data)
        )
        response = self._request("POST", "/v1/webhooks", json=payload)
        return self._model(WebhookResponse, response)

    def list(self) -> list[WebhookResponse]:
        response = self._request("GET", "/v1/webhooks")
        return self._list(WebhookResponse, response)

    def get(self, webhook_id: UUID | str) -> WebhookResponse:
        response = self._request(
            "GET",
            "/v1/webhooks/{webhook_id}",
            path_params={"webhook_id": webhook_id},
        )
        return self._model(WebhookResponse, response)

    def update(
        self, webhook_id: UUID | str, data: WebhookUpdate | Mapping[str, Any]
    ) -> WebhookResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, WebhookUpdate)
            else dict(data)
        )
        response = self._request(
            "PATCH",
            "/v1/webhooks/{webhook_id}",
            path_params={"webhook_id": webhook_id},
            json=payload,
        )
        return self._model(WebhookResponse, response)

    def delete(self, webhook_id: UUID | str) -> None:
        self._request(
            "DELETE",
            "/v1/webhooks/{webhook_id}",
            path_params={"webhook_id": webhook_id},
        )


class AsyncWebhooksResource(AsyncAPIResource):
    async def create(self, data: WebhookCreate | Mapping[str, Any]) -> WebhookResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, WebhookCreate)
            else dict(data)
        )
        response = await self._request("POST", "/v1/webhooks", json=payload)
        return self._model(WebhookResponse, response)

    async def list(self) -> list[WebhookResponse]:
        response = await self._request("GET", "/v1/webhooks")
        return self._list(WebhookResponse, response)

    async def get(self, webhook_id: UUID | str) -> WebhookResponse:
        response = await self._request(
            "GET",
            "/v1/webhooks/{webhook_id}",
            path_params={"webhook_id": webhook_id},
        )
        return self._model(WebhookResponse, response)

    async def update(
        self,
        webhook_id: UUID | str,
        data: WebhookUpdate | Mapping[str, Any],
    ) -> WebhookResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, WebhookUpdate)
            else dict(data)
        )
        response = await self._request(
            "PATCH",
            "/v1/webhooks/{webhook_id}",
            path_params={"webhook_id": webhook_id},
            json=payload,
        )
        return self._model(WebhookResponse, response)

    async def delete(self, webhook_id: UUID | str) -> None:
        await self._request(
            "DELETE",
            "/v1/webhooks/{webhook_id}",
            path_params={"webhook_id": webhook_id},
        )
