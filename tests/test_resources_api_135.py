"""Coverage for the API 1.35 surface added in SDK 1.8: pins deleted on Pinterest
(``removed_from_pinterest_at``, the ``removed`` list filter), ``failed_at``, the
analytics ``source`` parameter and fields, and account health fields."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest
from _payloads import UUID1, UUID4, pin_response, pinterest_account_response

from pinbridge_sdk import AsyncPinbridgeClient, PinbridgeClient
from pinbridge_sdk.models import PinAnalyticsResponse, PinResponse

REMOVED_AT = "2026-09-25T02:10:00Z"


def _removed_pin() -> dict:
    return {
        **pin_response(),
        "status": "published",
        "pinterest_pin_id": "1124281494506724754",
        "published_at": "2026-05-08T13:13:05Z",
        "failed_at": "2026-05-08T13:13:04Z",
        "removed_from_pinterest_at": REMOVED_AT,
    }


def _analytics(source: str) -> dict:
    return {
        "pin_id": UUID1,
        "pinterest_pin_id": "1124281494506724754",
        "account_id": UUID4,
        "start_date": "2026-09-01",
        "end_date": "2026-09-24",
        "provider_mode": "pinterest",
        "totals": {"impression": 52, "save": 3, "total_comments": 2},
        "daily": [],
        "source": source,
        "data_as_of": "2026-09-25T02:00:00Z",
        "history_start": "2026-06-27",
        "removed_from_pinterest_at": REMOVED_AT,
    }


def _handler(request: httpx.Request) -> httpx.Response:
    method, path, q = request.method, request.url.path, dict(request.url.params)
    if (method, path) == ("GET", "/v1/pins"):
        assert q["removed"] in {"true", "false"}
        rows = [_removed_pin()] if q["removed"] == "true" else []
        return httpx.Response(200, json=rows, headers={"X-Total-Count": str(len(rows))})
    if (method, path) == ("GET", f"/v1/pins/{UUID1}/analytics"):
        assert q == {"start_date": "2026-09-01", "source": "stored"}
        return httpx.Response(200, json=_analytics("stored"))
    if (method, path) == ("GET", f"/v1/pinterest/accounts/{UUID4}/analytics"):
        assert q == {"source": "live"}
        return httpx.Response(
            200,
            json={
                "account_id": UUID4,
                "start_date": "2026-08-26",
                "end_date": "2026-09-24",
                "provider_mode": "pinterest",
                "totals": {},
                "daily": [],
                "source": "live",
            },
        )
    if (method, path) == ("GET", "/v1/pinterest/accounts"):
        return httpx.Response(
            200,
            json=[
                {
                    **pinterest_account_response(),
                    "token_expires_at": "2026-10-20T00:00:00Z",
                    "health_status": "reconnect_required",
                    "health_message": "Reconnect this account.",
                    "health_checked_at": "2026-09-25T10:00:00Z",
                    "reconnect_required": True,
                    "missing_scopes": [],
                }
            ],
        )
    raise AssertionError(f"Unexpected request: {method} {path} {q}")


def _sync_client() -> PinbridgeClient:
    return PinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(_handler)
    )


def test_removed_filter_and_fields() -> None:
    with _sync_client() as client:
        page = client.pins.list_page(removed=True)
        assert page.total == 1
        pin = page.items[0]
        assert isinstance(pin, PinResponse)
        assert pin.removed_from_pinterest_at == datetime(2026, 9, 25, 2, 10, tzinfo=timezone.utc)
        assert pin.failed_at is not None
        assert client.pins.list(removed=False) == []


def test_analytics_source_and_stored_fields() -> None:
    with _sync_client() as client:
        analytics = client.pins.analytics(UUID1, start_date="2026-09-01", source="stored")
        assert isinstance(analytics, PinAnalyticsResponse)
        assert analytics.source == "stored"
        assert analytics.totals["impression"] == 52
        assert analytics.history_start is not None
        assert analytics.removed_from_pinterest_at is not None
        account = client.pinterest.account_analytics(UUID4, source="live")
        assert account.source == "live"


def test_account_health_fields() -> None:
    with _sync_client() as client:
        (account,) = client.pinterest.list_accounts()
        assert account.reconnect_required is True
        assert account.health_status == "reconnect_required"
        assert account.token_expires_at is not None


@pytest.mark.asyncio
async def test_async_api_135_surface() -> None:
    async with AsyncPinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(_handler)
    ) as client:
        page = await client.pins.list_page(removed=True)
        assert page.items[0].removed_from_pinterest_at is not None
        analytics = await client.pins.analytics(UUID1, start_date="2026-09-01", source="stored")
        assert analytics.source == "stored"
        account = await client.pinterest.account_analytics(UUID4, source="live")
        assert account.source == "live"
