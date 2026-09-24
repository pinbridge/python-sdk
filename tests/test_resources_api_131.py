"""Coverage for the API 1.30/1.31 surface added in SDK 1.6: edit, batch, dry run, analytics,
board access, Pinterest-side delete, list filters, and the enum/model drift."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import httpx
import pytest
from _payloads import (
    UUID1,
    UUID3,
    account_analytics_response,
    api_key_response,
    board_access_response,
    pin_analytics_response,
    pin_batch_response,
    pin_delete_response,
    pin_response,
    pin_validation_response,
    pinterest_account_response,
    schedule_response,
)

from pinbridge_sdk import AsyncPinbridgeClient, PinbridgeClient
from pinbridge_sdk.models import (
    APIKeyCreate,
    APIKeyResponse,
    APIKeyScope,
    APIKeyUpdate,
    AuthResponse,
    LoginRequest,
    PinBatchItemStatus,
    PinCreate,
    PinStatus,
    PinterestAccountResponse,
    PinUpdate,
    PinValidationCheckStatus,
    RegisterRequest,
    ScheduleCreate,
    ScheduleStatus,
)

PIN_INPUT = {
    "account_id": UUID3,
    "board_id": "123-board",
    "title": "Hello",
    "image_url": "https://example.com/a.png",
    "idempotency_key": "k-1",
}
SCHEDULE_INPUT = {**{k: v for k, v in PIN_INPUT.items() if k != "idempotency_key"}}
SCHEDULE_INPUT["run_at"] = "2030-01-01T10:00:00Z"


def _request_json(request: httpx.Request) -> dict | list:
    return json.loads(request.content.decode("utf-8")) if request.content else {}


def _handler(request: httpx.Request) -> httpx.Response:
    method, path, q = request.method, request.url.path, request.url.params

    if (method, path) == ("POST", "/v1/pins/validate"):
        assert _request_json(request)["idempotency_key"] == "k-1"
        return httpx.Response(200, json=pin_validation_response(valid=False))
    if (method, path) == ("POST", "/v1/schedules/validate"):
        assert _request_json(request)["run_at"].startswith("2030-01-01T10:00:00")
        return httpx.Response(200, json=pin_validation_response())
    if (method, path) == ("POST", "/v1/pins/batch"):
        body = _request_json(request)
        assert [p["idempotency_key"] for p in body["pins"]] == ["k-1", "k-2"]
        return httpx.Response(200, json=pin_batch_response())
    if (method, path) == ("PATCH", f"/v1/pins/{UUID1}"):
        # explicit None must survive serialisation so the API can clear the field
        assert _request_json(request) == {"title": "Fixed", "description": None}
        return httpx.Response(200, json=pin_response())
    if (method, path) == ("DELETE", f"/v1/pins/{UUID1}"):
        if q.get("delete_from_pinterest") == "true":
            return httpx.Response(200, json=pin_delete_response())
        assert "delete_from_pinterest" not in q
        return httpx.Response(204)
    if (method, path) == ("GET", f"/v1/pins/{UUID1}/analytics"):
        assert dict(q) == {
            "start_date": "2026-09-01",
            "end_date": "2026-09-24",
            "metrics": "IMPRESSION,SAVE",
        }
        return httpx.Response(200, json=pin_analytics_response())
    if (method, path) == ("GET", f"/v1/pinterest/accounts/{UUID3}/analytics"):
        assert dict(q) == {"metrics": "IMPRESSION"}
        return httpx.Response(200, json=account_analytics_response())
    if (method, path) == ("GET", "/v1/pinterest/boards/123-board/access"):
        assert dict(q) == {"account_id": UUID3, "fresh": "true"}
        return httpx.Response(200, json=board_access_response(publishable=False))
    if (method, path) == ("GET", "/v1/pins"):
        assert dict(q) == {
            "limit": "10",
            "offset": "5",
            "account_id": UUID3,
            "board_id": "123-board",
            "status": "failed",
            "error_code": "board_access_denied",
            "since": "2026-09-01T00:00:00+00:00",
            "until": "2026-09-30T00:00:00Z",
        }
        return httpx.Response(200, json=[pin_response()])
    if (method, path) == ("GET", "/v1/schedules"):
        assert dict(q) == {"limit": "50", "offset": "0", "status": "deferred", "board_id": "b"}
        return httpx.Response(200, json=[schedule_response()])
    raise AssertionError(f"Unexpected request: {method} {path} {dict(q)}")


def _sync_client() -> PinbridgeClient:
    return PinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(_handler)
    )


def _async_client() -> AsyncPinbridgeClient:
    return AsyncPinbridgeClient(
        base_url="https://api.pinbridge.test", transport=httpx.MockTransport(_handler)
    )


def test_sync_api_131_surface() -> None:
    with _sync_client() as client:
        dry = client.pins.validate(PinCreate(**PIN_INPUT))
        assert dry.valid is False
        assert dry.checks[1].status is PinValidationCheckStatus.FAILED
        assert dry.checks[1].code == "board_not_found"
        assert dry.resolved == {"board_id": "123-board", "idempotency_key": "k-1"}

        sched = client.schedules.validate(ScheduleCreate(**SCHEDULE_INPUT))
        assert sched.valid is True and sched.dry_run is True

        batch = client.pins.create_batch(
            [PinCreate(**PIN_INPUT), {**PIN_INPUT, "idempotency_key": "k-2"}]
        )
        assert (batch.created_count, batch.failed_count) == (1, 1)
        assert batch.results[0].status is PinBatchItemStatus.CREATED
        assert batch.results[0].pin is not None and batch.results[0].pin.id
        assert batch.results[1].error == {"code": "board_not_found", "message": "Board not found."}

        assert client.pins.update(UUID1, PinUpdate(title="Fixed", description=None)).id
        assert client.pins.update(UUID1, {"title": "Fixed", "description": None}).id

        assert client.pins.delete(UUID1) is None
        removed = client.pins.delete(UUID1, delete_from_pinterest=True)
        assert removed is not None
        assert removed.removed_from_pinterest is False and removed.reason == "not_published"

        analytics = client.pins.analytics(
            UUID1,
            start_date=date(2026, 9, 1),
            end_date="2026-09-24",
            metrics=["IMPRESSION", "SAVE"],
        )
        assert analytics.totals["impression"] == 120
        assert analytics.daily[0].date == date(2026, 9, 1)
        assert analytics.daily[1].data_status is None

        acct = client.pinterest.account_analytics(UUID3, metrics="IMPRESSION")
        assert acct.provider_mode.value == "simulated" and acct.daily == []

        access = client.pinterest.check_board_access("123-board", account_id=UUID3, fresh=True)
        assert access.publishable is False and access.code == "board_not_owned"
        assert access.board == {"id": "123-board", "name": "SDK Board"}

        pins = client.pins.list(
            limit=10,
            offset=5,
            account_id=UUID3,
            board_id="123-board",
            status=PinStatus.FAILED,
            error_code="board_access_denied",
            since=datetime(2026, 9, 1, tzinfo=timezone.utc),
            until="2026-09-30T00:00:00Z",
        )
        assert len(pins) == 1
        assert len(client.schedules.list(status=ScheduleStatus.DEFERRED, board_id="b")) == 1


async def test_async_api_131_surface() -> None:
    async with _async_client() as client:
        assert (await client.pins.validate(PIN_INPUT)).valid is False
        assert (await client.schedules.validate(SCHEDULE_INPUT)).valid is True
        batch = await client.pins.create_batch([PIN_INPUT, {**PIN_INPUT, "idempotency_key": "k-2"}])
        assert batch.existing_count == 0
        assert (await client.pins.update(UUID1, {"title": "Fixed", "description": None})).id
        assert await client.pins.delete(UUID1) is None
        removed = await client.pins.delete(UUID1, delete_from_pinterest=True)
        assert removed is not None and removed.deleted is True
        analytics = await client.pins.analytics(
            UUID1, start_date="2026-09-01", end_date=date(2026, 9, 24), metrics="IMPRESSION,SAVE"
        )
        assert analytics.pinterest_pin_id == "987"
        assert (await client.pinterest.account_analytics(UUID3, metrics=["IMPRESSION"])).account_id
        access = await client.pinterest.check_board_access(
            "123-board", account_id=UUID3, fresh=True
        )
        assert access.publishable is False
        pins = await client.pins.list(
            limit=10,
            offset=5,
            account_id=UUID3,
            board_id="123-board",
            status="failed",
            error_code="board_access_denied",
            since="2026-09-01T00:00:00+00:00",
            until="2026-09-30T00:00:00Z",
        )
        assert pins[0].id
        assert len(await client.schedules.list(status="deferred", board_id="b")) == 1


def test_pin_update_serialization_keeps_explicit_none_and_drops_unset() -> None:
    assert PinUpdate(title="x").model_dump(mode="json", exclude_unset=True) == {"title": "x"}
    assert PinUpdate(description=None).model_dump(mode="json", exclude_unset=True) == {
        "description": None
    }
    with pytest.raises(ValueError):
        PinUpdate(link_url="https://example.com/" + "a" * 2050)


def test_enums_match_api_1_31() -> None:
    assert PinStatus.DEFERRED.value == "deferred"
    assert ScheduleStatus.DEFERRED.value == "deferred"
    assert [s.value for s in APIKeyScope] == ["read", "write", "destructive"]


def test_api_key_models_carry_scopes_and_allow_list() -> None:
    created = APIKeyCreate(
        name="agent", scopes=[APIKeyScope.READ, "write"], pinterest_account_ids=[UUID3]
    )
    assert created.model_dump(mode="json", exclude_none=True) == {
        "name": "agent",
        "scopes": ["read", "write"],
        "pinterest_account_ids": [UUID3],
    }
    assert APIKeyUpdate(scopes=["read"]).model_dump(mode="json", exclude_unset=True) == {
        "scopes": ["read"]
    }
    with pytest.raises(ValueError):
        APIKeyUpdate()
    parsed = APIKeyResponse.model_validate(
        {
            **api_key_response(),
            "scopes": ["read", "write", "destructive"],
            "pinterest_account_ids": None,
            "source": "oauth",
            "client_name": "Claude",
            "authorized_by_email": "owner@example.com",
            "last_used_at": "2026-09-24T10:00:00Z",
        }
    )
    assert parsed.source is not None and parsed.source.value == "oauth"
    assert parsed.last_used_at is not None and parsed.scopes[-1] is APIKeyScope.DESTRUCTIVE
    # keys created before scopes existed still parse
    assert APIKeyResponse.model_validate(api_key_response()).scopes == []


def test_pinterest_account_health_fields_parse_with_defaults() -> None:
    legacy = PinterestAccountResponse.model_validate(pinterest_account_response())
    assert legacy.reconnect_required is False and legacy.missing_scopes == []
    current = PinterestAccountResponse.model_validate(
        {
            **pinterest_account_response(),
            "health_status": "reconnect_required",
            "health_message": "Token expired.",
            "health_checked_at": "2026-09-24T10:00:00Z",
            "missing_scopes": ["boards:write"],
            "reconnect_required": True,
            "token_expires_at": "2026-09-20T10:00:00Z",
        }
    )
    assert current.reconnect_required is True and current.missing_scopes == ["boards:write"]


def test_auth_models_accept_organization_context_and_invite_fields() -> None:
    from _payloads import auth_response

    payload = auth_response()
    parsed = AuthResponse.model_validate(payload)
    assert parsed.available_organizations == [] and parsed.permissions is None
    assert LoginRequest(email="a@b.co", password="secret123", invite_token="t" * 24).invite_token
    reg = RegisterRequest(
        full_name="A",
        email="a@b.co",
        password="secret123",
        marketing_attribution={"utm_source": "x", "referral_code": "REF"},
        next_path="/app",
    )
    dumped = reg.model_dump(mode="json", exclude_none=True)
    assert dumped["marketing_attribution"] == {"utm_source": "x", "referral_code": "REF"}
    assert dumped["next_path"] == "/app"
