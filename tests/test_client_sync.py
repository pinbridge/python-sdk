from __future__ import annotations

import json

import httpx
import pytest

from pinbridge_sdk import AuthenticationError, PinbridgeClient
from pinbridge_sdk.models.common import PinStatus
from pinbridge_sdk.resources.base import SyncAPIResource


@pytest.fixture
def base_url() -> str:
    return "https://api.pinbridge.test"


def test_request_includes_auth_headers(base_url: str) -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["x-api-key"] = request.headers.get("x-api-key", "")
        seen["authorization"] = request.headers.get("authorization", "")
        seen["x-custom"] = request.headers.get("x-custom", "")
        return httpx.Response(
            200,
            json={
                "status": "ok",
                "version": "0.1.0",
                "environment": "test",
                "checks": {"app": "ok"},
            },
        )

    transport = httpx.MockTransport(handler)
    with PinbridgeClient(
        base_url=base_url,
        api_key="pk_test",
        bearer_token="jwt_token",
        headers={"x-custom": "v1"},
        transport=transport,
    ) as client:
        client.system.health()

    assert seen["x-api-key"] == "pk_test"
    assert seen["authorization"] == "Bearer jwt_token"
    assert seen["x-custom"] == "v1"


def test_api_error_is_mapped(base_url: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Invalid access token"})

    transport = httpx.MockTransport(handler)
    with PinbridgeClient(base_url=base_url, transport=transport) as client:
        with pytest.raises(AuthenticationError) as exc:
            client.auth.me()

    assert exc.value.status_code == 401
    assert "Invalid access token" in exc.value.message


def test_typed_list_parsing(base_url: str) -> None:
    body = [
        {
            "id": "f410a8fe-9f2e-4cf9-8cdf-5a4b81d56f1c",
            "workspace_id": "f410a8fe-9f2e-4cf9-8cdf-5a4b81d56f1d",
            "pinterest_account_id": "f410a8fe-9f2e-4cf9-8cdf-5a4b81d56f1e",
            "status": "queued",
            "media_type": "image",
            "title": "Pin title",
            "description": None,
            "related_terms": ["meal prep"],
            "alt_text": "Pin alt text",
            "dominant_color": "#E88A2D",
            "cover_image_url": None,
            "link_url": None,
            "media_url": "https://images.example.com/pin.jpg",
            "image_url": "https://images.example.com/pin.jpg",
            "board_id": "123",
            "pinterest_pin_id": None,
            "error_code": None,
            "error_message": None,
            "idempotency_key": "abc-123",
            "created_at": "2026-02-23T12:00:00Z",
            "updated_at": "2026-02-23T12:00:00Z",
            "published_at": None,
        }
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    transport = httpx.MockTransport(handler)
    with PinbridgeClient(base_url=base_url, transport=transport) as client:
        pins = client.pins.list()

    assert pins[0].status == PinStatus.QUEUED


def test_oauth_callback_returns_redirect_response(base_url: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            302, headers={"location": "https://app.example.com/app?oauth_status=success"}
        )

    transport = httpx.MockTransport(handler)
    with PinbridgeClient(base_url=base_url, transport=transport) as client:
        result = client.pinterest.oauth_callback(code="abc", state="state-token")

    assert isinstance(result, httpx.Response)
    assert result.status_code == 302


def test_register_custom_resource(base_url: str) -> None:
    class DiagnosticsResource(SyncAPIResource):
        def ping(self) -> str:
            response = self._request("GET", "/healthz")
            return json.loads(response.content.decode("utf-8"))["status"]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "status": "ok",
                "version": "0.1.0",
                "environment": "test",
                "checks": {"app": "ok"},
            },
        )

    transport = httpx.MockTransport(handler)
    with PinbridgeClient(base_url=base_url, transport=transport) as client:
        client.register_resource("diagnostics", DiagnosticsResource)
        status = client.diagnostics.ping()  # type: ignore[attr-defined]

    assert status == "ok"
