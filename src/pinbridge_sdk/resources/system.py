"""System and low-level endpoints."""

from __future__ import annotations

from typing import Any

from ..models.system import HealthResponse, RootResponse
from .base import AsyncAPIResource, SyncAPIResource


class SystemResource(SyncAPIResource):
    def root(self) -> RootResponse:
        response = self._request("GET", "/")
        return self._model(RootResponse, response)

    def health(self) -> HealthResponse:
        response = self._request("GET", "/healthz")
        return self._model(HealthResponse, response)

    def stripe_webhook(self, body: str | bytes, *, stripe_signature: str) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/v1/stripe/webhook",
            content=body,
            headers={"stripe-signature": stripe_signature, "content-type": "application/json"},
        )
        payload = self._json(response)
        return payload if isinstance(payload, dict) else {}


class AsyncSystemResource(AsyncAPIResource):
    async def root(self) -> RootResponse:
        response = await self._request("GET", "/")
        return self._model(RootResponse, response)

    async def health(self) -> HealthResponse:
        response = await self._request("GET", "/healthz")
        return self._model(HealthResponse, response)

    async def stripe_webhook(self, body: str | bytes, *, stripe_signature: str) -> dict[str, Any]:
        response = await self._request(
            "POST",
            "/v1/stripe/webhook",
            content=body,
            headers={"stripe-signature": stripe_signature, "content-type": "application/json"},
        )
        payload = self._json(response)
        return payload if isinstance(payload, dict) else {}
