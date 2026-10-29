from __future__ import annotations

import asyncio
import json
from datetime import datetime

import httpx
import pytest
from _payloads import UUID3, UUID4, schedule_response
from pydantic import ValidationError

from pinbridge_sdk import AsyncPinbridgeClient, PinbridgeClient
from pinbridge_sdk.models import ScheduleCreate, ScheduleUpdate

ALT_TEXT = "Bowl of glazed carrots with fresh herbs"


def _schedule() -> ScheduleCreate:
    return ScheduleCreate(
        account_id=UUID4,
        run_at=datetime.fromisoformat("2030-01-01T10:00:00+00:00"),
        board_id="123-board",
        title="Scheduled",
        alt_text=ALT_TEXT,
        image_url="https://example.com/pin.jpg",
    )


def _recording_transport(sent: list[tuple[str, str, dict]]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        sent.append((request.method, request.url.path, json.loads(request.content or b"{}")))
        if request.url.path == "/v1/schedules/validate":
            return httpx.Response(200, json={"valid": True, "checks": [], "resolved": {}})
        return httpx.Response(200, json=schedule_response())

    return httpx.MockTransport(handler)


def test_schedule_models_send_alt_text() -> None:
    sent: list[tuple[str, str, dict]] = []
    with PinbridgeClient(
        base_url="https://api.pinbridge.test", transport=_recording_transport(sent)
    ) as client:
        client.schedules.validate(_schedule())
        client.schedules.create(_schedule())
        client.schedules.update(UUID3, ScheduleUpdate(alt_text="A red bicycle"))
        client.schedules.update(UUID3, ScheduleUpdate(alt_text=None))

    assert [(method, path) for method, path, _ in sent] == [
        ("POST", "/v1/schedules/validate"),
        ("POST", "/v1/schedules"),
        ("PATCH", f"/v1/schedules/{UUID3}"),
        ("PATCH", f"/v1/schedules/{UUID3}"),
    ]
    assert sent[0][2]["alt_text"] == ALT_TEXT
    assert sent[1][2]["alt_text"] == ALT_TEXT
    assert sent[2][2] == {"alt_text": "A red bicycle"}
    # An explicit None clears the alt text; leaving it unset sends nothing.
    assert sent[3][2] == {"alt_text": None}


def test_async_schedule_models_send_alt_text() -> None:
    sent: list[tuple[str, str, dict]] = []

    async def run() -> None:
        async with AsyncPinbridgeClient(
            base_url="https://api.pinbridge.test", transport=_recording_transport(sent)
        ) as client:
            await client.schedules.create(_schedule())
            await client.schedules.update(UUID3, ScheduleUpdate(alt_text="A red bicycle"))

    asyncio.run(run())
    assert sent[0][2]["alt_text"] == ALT_TEXT
    assert sent[1][2] == {"alt_text": "A red bicycle"}


def test_schedule_without_alt_text_sends_no_key() -> None:
    model = ScheduleCreate(
        account_id=UUID4,
        run_at=datetime.fromisoformat("2030-01-01T10:00:00+00:00"),
        board_id="123-board",
        title="Scheduled",
        image_url="https://example.com/pin.jpg",
    )
    assert "alt_text" not in model.model_dump(mode="json", exclude_none=True)
    assert ScheduleUpdate(title="Moved").model_dump(exclude_unset=True) == {"title": "Moved"}


def test_schedule_alt_text_is_limited_to_500_characters() -> None:
    at_limit = ScheduleCreate.model_validate({**_schedule().model_dump(), "alt_text": "x" * 500})
    assert len(at_limit.alt_text or "") == 500
    with pytest.raises(ValidationError):
        ScheduleCreate.model_validate({**_schedule().model_dump(), "alt_text": "x" * 501})
    with pytest.raises(ValidationError):
        ScheduleUpdate(alt_text="x" * 501)
