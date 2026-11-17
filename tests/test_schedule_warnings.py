"""Schedule create and update keep the warnings the API returns (DEV-852)."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import httpx
from _payloads import UUID3, UUID4, schedule_response

from pinbridge_sdk import AsyncPinbridgeClient, PinbridgeClient
from pinbridge_sdk.models import ScheduleCreate, ScheduleResponse, ScheduleUpdate, ScheduleWarning

MEDIA_WARNING = {
    "code": "media_link_may_expire",
    "message": "image_url is a Dropbox temporary link. Links like this stop working 4 hours "
    "after they are made, so it may no longer work when this schedule runs at "
    "2030-01-01 10:00 UTC, and the pin would fail.",
    "remediation": "The schedule was created. To be safe, upload the file with POST "
    "/v1/assets/images (or /v1/assets/videos) and set asset_id on the schedule, or link to a "
    "copy on your own site.",
    "field": "image_url",
    "expires_at": None,
}
QUOTA_WARNING = {
    "code": "quota_may_be_exceeded",
    "message": "This month already has 25 pins published or scheduled.",
    "limit_type": "monthly_pins",
    "plan": "playground",
    "plan_name": "Playground",
    "limit": 25,
    "used": 25,
    "recommended_plan": "starter",
    "recommended_plan_name": "Starter",
    "recommended_limit": 300,
    "upgrade_url": "https://app.pinbridge.io/billing",
    "a_field_from_a_newer_api": True,
}


def _with_warnings(*warnings: dict) -> dict:
    return {**schedule_response(), "warnings": list(warnings)}


def _transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method in ("POST", "PATCH"):
            return httpx.Response(200, json=_with_warnings(MEDIA_WARNING, QUOTA_WARNING))
        return httpx.Response(200, json=schedule_response())

    return httpx.MockTransport(handler)


def _schedule() -> ScheduleCreate:
    return ScheduleCreate(
        account_id=UUID4,
        run_at=datetime(2030, 1, 1, 10, 0, tzinfo=timezone.utc),
        board_id="123-board",
        title="Scheduled",
        image_url="https://dl.dropboxusercontent.com/scl/fi/abc/pin.jpg",
    )


def _assert_warnings(schedule: ScheduleResponse) -> None:
    assert [warning.code for warning in schedule.warnings] == [
        "media_link_may_expire",
        "quota_may_be_exceeded",
    ]
    media, quota = schedule.warnings
    assert isinstance(media, ScheduleWarning)
    assert media.field == "image_url"
    assert media.expires_at is None
    assert media.remediation is not None and "asset_id" in media.remediation
    assert (quota.limit, quota.used, quota.recommended_plan) == (25, 25, "starter")


def test_create_and_update_keep_the_warnings() -> None:
    with PinbridgeClient(base_url="https://api.pinbridge.test", transport=_transport()) as client:
        created = client.schedules.create(_schedule())
        updated = client.schedules.update(UUID3, ScheduleUpdate(title="Renamed"))
        fetched = client.schedules.get(UUID3)

    _assert_warnings(created)
    _assert_warnings(updated)
    # A plain read has no warnings; the field is still there, empty.
    assert fetched.warnings == []


def test_async_create_keeps_the_warnings() -> None:
    async def run() -> ScheduleResponse:
        async with AsyncPinbridgeClient(
            base_url="https://api.pinbridge.test", transport=_transport()
        ) as client:
            return await client.schedules.create(_schedule())

    _assert_warnings(asyncio.run(run()))


def test_warnings_reach_a_json_dump() -> None:
    """The MCP server answers with model_dump(mode="json"); the warnings must be in it."""
    schedule = ScheduleResponse.model_validate(
        _with_warnings({**MEDIA_WARNING, "expires_at": "2030-01-01T09:30:00Z"})
    )

    dumped = schedule.model_dump(mode="json")

    assert dumped["warnings"][0]["code"] == "media_link_may_expire"
    assert dumped["warnings"][0]["expires_at"] == "2030-01-01T09:30:00Z"
