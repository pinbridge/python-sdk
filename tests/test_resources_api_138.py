"""Coverage for the API 1.38 surface added in SDK 1.10: the analytics ``include_daily``
switch that returns only the range totals."""

from __future__ import annotations

import httpx
import pytest
from _payloads import UUID1, UUID4

from pinbridge_sdk import AsyncPinbridgeClient, PinbridgeClient


def _handler(request: httpx.Request) -> httpx.Response:
    method, path, q = request.method, request.url.path, dict(request.url.params)
    body = {
        "account_id": UUID4,
        "start_date": "2026-06-28",
        "end_date": "2026-09-25",
        "provider_mode": "pinterest",
        "totals": {"impression": 900},
        "daily": [],
        "source": "stored",
    }
    if (method, path) == ("GET", f"/v1/pins/{UUID1}/analytics"):
        assert q == {"start_date": "2026-06-28", "include_daily": "false"}
        return httpx.Response(200, json={**body, "pin_id": UUID1, "pinterest_pin_id": "1"})
    if (method, path) == ("GET", f"/v1/pinterest/accounts/{UUID4}/analytics"):
        assert q == {"include_daily": "true"}
        return httpx.Response(200, json=body)
    raise AssertionError(f"Unexpected request: {method} {path} {q}")


def test_include_daily_is_sent_as_a_query_flag() -> None:
    with PinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(_handler)
    ) as client:
        analytics = client.pins.analytics(UUID1, start_date="2026-06-28", include_daily=False)
        assert analytics.daily == []
        assert analytics.totals["impression"] == 900
        account = client.pinterest.account_analytics(UUID4, include_daily=True)
        assert account.totals["impression"] == 900


@pytest.mark.asyncio
async def test_async_include_daily() -> None:
    async with AsyncPinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(_handler)
    ) as client:
        analytics = await client.pins.analytics(UUID1, start_date="2026-06-28", include_daily=False)
        assert analytics.daily == []
        account = await client.pinterest.account_analytics(UUID4, include_daily=True)
        assert account.totals["impression"] == 900
