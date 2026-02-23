"""Billing and usage resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from ..models.billing import (
    BillingStatusResponse,
    CheckoutRequest,
    CheckoutResponse,
    PortalResponse,
    PricingCatalogResponse,
)
from ..models.system import RateMeterResponse
from .base import AsyncAPIResource, SyncAPIResource


class BillingResource(SyncAPIResource):
    def pricing(self) -> PricingCatalogResponse:
        response = self._request("GET", "/v1/billing/pricing")
        return self._model(PricingCatalogResponse, response)

    def checkout(self, data: CheckoutRequest | Mapping[str, Any]) -> CheckoutResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, CheckoutRequest)
            else dict(data)
        )
        response = self._request("POST", "/v1/billing/checkout", json=payload)
        return self._model(CheckoutResponse, response)

    def portal(self) -> PortalResponse:
        response = self._request("POST", "/v1/billing/portal")
        return self._model(PortalResponse, response)

    def status(self) -> BillingStatusResponse:
        response = self._request("GET", "/v1/billing/status")
        return self._model(BillingStatusResponse, response)


class RateMeterResource(SyncAPIResource):
    def get(self, account_id: UUID | str) -> RateMeterResponse:
        response = self._request("GET", "/v1/rate-meter", params={"account_id": str(account_id)})
        return self._model(RateMeterResponse, response)


class AsyncBillingResource(AsyncAPIResource):
    async def pricing(self) -> PricingCatalogResponse:
        response = await self._request("GET", "/v1/billing/pricing")
        return self._model(PricingCatalogResponse, response)

    async def checkout(self, data: CheckoutRequest | Mapping[str, Any]) -> CheckoutResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, CheckoutRequest)
            else dict(data)
        )
        response = await self._request("POST", "/v1/billing/checkout", json=payload)
        return self._model(CheckoutResponse, response)

    async def portal(self) -> PortalResponse:
        response = await self._request("POST", "/v1/billing/portal")
        return self._model(PortalResponse, response)

    async def status(self) -> BillingStatusResponse:
        response = await self._request("GET", "/v1/billing/status")
        return self._model(BillingStatusResponse, response)


class AsyncRateMeterResource(AsyncAPIResource):
    async def get(self, account_id: UUID | str) -> RateMeterResponse:
        response = await self._request(
            "GET",
            "/v1/rate-meter",
            params={"account_id": str(account_id)},
        )
        return self._model(RateMeterResponse, response)
