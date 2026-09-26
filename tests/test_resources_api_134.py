"""Coverage for the API 1.34 surface added in SDK 1.7: list search and sort, the
X-Total-Count total via ``list_page``, asset filters, and the dashboard summary."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import httpx
import pytest
from _payloads import (
    UUID3,
    UUID4,
    asset_list_response,
    dashboard_summary_response,
    pin_response,
    schedule_response,
)

from pinbridge_sdk import AsyncPinbridgeClient, PinbridgeClient
from pinbridge_sdk.models import (
    AssetType,
    DashboardGranularity,
    DashboardSummaryResponse,
    Page,
    PinResponse,
    ScheduleResponse,
)


def _handler(request: httpx.Request) -> httpx.Response:
    method, path, q = request.method, request.url.path, dict(request.url.params)

    if (method, path) == ("GET", "/v1/pins"):
        if q.get("q") == "no-header":
            # An API older than 1.34.0 sends no total.
            return httpx.Response(200, json=[pin_response()])
        assert q == {
            "limit": "1",
            "offset": "2",
            "account_id": UUID3,
            "status": "published",
            "q": "autumn soup",
            "sort": "title_asc",
        }
        return httpx.Response(200, json=[pin_response()], headers={"X-Total-Count": "7"})
    if (method, path) == ("GET", "/v1/schedules"):
        assert q == {"limit": "50", "offset": "0", "q": "berries", "sort": "run_at_asc"}
        return httpx.Response(200, json=[schedule_response()], headers={"X-Total-Count": "1"})
    if (method, path) == ("GET", "/v1/assets"):
        assert q == {
            "sort": "size_asc",
            "limit": "24",
            "offset": "0",
            "q": "hero",
            "asset_type": "video",
            "in_use": "false",
            "since": "2026-09-01T00:00:00+00:00",
            "until": "2026-09-30T00:00:00Z",
        }
        return httpx.Response(200, json=asset_list_response())
    if (method, path) == ("GET", "/v1/dashboard/summary"):
        if "account_id" in q:
            assert q == {"account_id": UUID3}
            return httpx.Response(200, json=dashboard_summary_response(account_id=UUID3))
        assert q == {
            "start": "2026-09-01T00:00:00",
            "end": "2026-09-08T00:00:00",
            "tz": "Asia/Tokyo",
        }
        return httpx.Response(200, json=dashboard_summary_response())
    raise AssertionError(f"Unexpected request: {method} {path} {q}")


def _sync_client() -> PinbridgeClient:
    return PinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(_handler)
    )


def _async_client() -> AsyncPinbridgeClient:
    return AsyncPinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(_handler)
    )


PIN_FILTERS = {
    "limit": 1,
    "offset": 2,
    "account_id": UUID(UUID3),
    "status": "published",
    "q": "autumn soup",
    "sort": "title_asc",
}
ASSET_FILTERS = {
    "sort": "size_asc",
    "limit": 24,
    "q": "hero",
    "asset_type": AssetType.VIDEO,
    "in_use": False,
    "since": datetime(2026, 9, 1, tzinfo=timezone.utc),
    "until": "2026-09-30T00:00:00Z",
}
SUMMARY_RANGE = {
    "start": datetime(2026, 9, 1),
    "end": datetime(2026, 9, 8),
    "tz": "Asia/Tokyo",
}


def _assert_summary(summary: DashboardSummaryResponse) -> None:
    assert summary.granularity is DashboardGranularity.DAY
    assert summary.timezone == "Asia/Tokyo"
    assert summary.start.utcoffset().total_seconds() == 9 * 3600
    assert summary.pins.total == 5
    assert summary.pins.submitted == 4
    assert summary.previous_pins.submitted is None  # an API before 1.38.0
    assert summary.pins.by_status["published"] == 3
    assert summary.pins.success_rate == 0.75
    assert summary.previous_pins.success_rate is None
    assert summary.series[0].created == 2
    assert summary.published_by_account[0].account_id == UUID(UUID3)
    assert summary.queue.queued == 1
    assert summary.schedules.upcoming == 2
    assert summary.import_jobs is not None
    assert summary.import_jobs.by_status == {"completed": 1}


def test_sync_list_search_sort_and_page() -> None:
    with _sync_client() as client:
        pins = client.pins.list(**PIN_FILTERS)
        assert isinstance(pins, list) and isinstance(pins[0], PinResponse)

        page = client.pins.list_page(**PIN_FILTERS)
        assert isinstance(page, Page)
        assert page.total == 7
        assert (page.limit, page.offset) == (1, 2)
        assert isinstance(page.items[0], PinResponse)
        assert page.has_more is True

        legacy = client.pins.list_page(q="no-header", limit=1)
        assert legacy.total is None
        assert legacy.has_more is True  # a full page without a total

        schedules = client.schedules.list_page(q="berries", sort="run_at_asc")
        assert schedules.total == 1
        assert isinstance(schedules.items[0], ScheduleResponse)
        assert schedules.has_more is False
        assert len(client.schedules.list(q="berries", sort="run_at_asc")) == 1

        assets = client.assets.list(**ASSET_FILTERS)
        assert assets.total == 1


def test_sync_dashboard_summary() -> None:
    with _sync_client() as client:
        _assert_summary(client.dashboard.summary(**SUMMARY_RANGE))
        scoped = client.dashboard.summary(account_id=UUID3)
        assert scoped.account_id == UUID(UUID3)
        assert scoped.import_jobs is None


@pytest.mark.asyncio
async def test_async_api_134_surface() -> None:
    async with _async_client() as client:
        pins = await client.pins.list(**PIN_FILTERS)
        assert len(pins) == 1
        page = await client.pins.list_page(**PIN_FILTERS)
        assert page.total == 7

        schedules = await client.schedules.list_page(q="berries", sort="run_at_asc")
        assert schedules.total == 1
        assert len(await client.schedules.list(q="berries", sort="run_at_asc")) == 1

        assets = await client.assets.list(**ASSET_FILTERS)
        assert assets.assets[0].id == UUID(UUID3)

        _assert_summary(await client.dashboard.summary(**SUMMARY_RANGE))
        scoped = await client.dashboard.summary(account_id=UUID3)
        assert scoped.import_jobs is None


def test_page_has_more_uses_total() -> None:
    last = Page[PinResponse](items=[], total=10, limit=5, offset=10)
    assert last.has_more is False
    short = Page[PinResponse](items=[], total=None, limit=5, offset=0)
    assert short.has_more is False


def test_invalid_total_header_is_ignored() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[], headers={"X-Total-Count": "lots"})

    client = PinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(handler)
    )
    with client:
        assert client.pins.list_page().total is None


def test_workspace_id_still_serialized_for_assets() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert dict(request.url.params) == {
            "sort": "created_at_desc",
            "limit": "50",
            "offset": "0",
            "workspace_id": UUID4,
            "in_use": "true",
        }
        return httpx.Response(200, json=asset_list_response())

    client = PinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(handler)
    )
    with client:
        assert client.assets.list(workspace_id=UUID4, in_use=True).total == 1
