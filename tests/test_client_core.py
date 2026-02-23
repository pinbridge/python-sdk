from __future__ import annotations

import httpx
import pytest

from pinbridge_sdk._client_base import ClientCore
from pinbridge_sdk.client import PinbridgeClient
from pinbridge_sdk.resources.base import SyncAPIResource


def test_client_core_builders() -> None:
    core = ClientCore(
        base_url="https://api.pinbridge.test/",
        api_key="k",
        bearer_token="t",
        default_headers={"x-default": "1"},
        follow_redirects=False,
        user_agent="ua",
    )

    assert (
        core.build_url("/v1/pins/{pin_id}", {"pin_id": "abc"})
        == "https://api.pinbridge.test/v1/pins/abc"
    )
    assert core.build_url("v1/pins") == "https://api.pinbridge.test/v1/pins"
    assert core.build_url("https://other.test/path") == "https://other.test/path"

    headers = core.build_headers({"x-extra": "2"})
    assert headers["x-api-key"] == "k"
    assert headers["authorization"] == "Bearer t"
    assert headers["x-default"] == "1"
    assert headers["x-extra"] == "2"

    core.clear_auth()
    cleared = core.auth_headers()
    assert "x-api-key" not in cleared
    assert "authorization" not in cleared


def test_client_init_rejects_transport_and_http_client() -> None:
    with pytest.raises(ValueError, match="either http_client or transport"):
        PinbridgeClient(
            http_client=httpx.Client(), transport=httpx.MockTransport(lambda _: httpx.Response(200))
        )


class _DummyResource(SyncAPIResource):
    def ping(self) -> dict:
        return self._request("GET", "/healthz").json()


def test_register_resource_duplicate_and_resource_lookup() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json={"status": "ok"}))
    with PinbridgeClient(base_url="https://api.pinbridge.test", transport=transport) as client:
        with pytest.raises(ValueError, match="already registered"):
            client.register_resource("system", _DummyResource)

        client.register_resource("dummy", _DummyResource)
        assert client.resource("dummy") is client.dummy  # type: ignore[attr-defined]
        assert client.dummy.ping()["status"] == "ok"  # type: ignore[attr-defined]


def test_with_options_clones_auth_headers_and_custom_resources() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200, json={"status": "ok", "version": "0.1.0", "environment": "test", "database": "ok"}
        )

    transport = httpx.MockTransport(handler)
    with PinbridgeClient(
        base_url="https://api.pinbridge.test",
        api_key="k1",
        bearer_token="t1",
        headers={"x-root": "yes"},
        transport=transport,
    ) as client:
        client.register_resource("dummy", _DummyResource)

        clone = client.with_options(api_key="k2", headers={"x-clone": "1"})
        try:
            clone.system.health()
            clone.dummy.ping()  # type: ignore[attr-defined]
        finally:
            clone.close()

    assert len(seen) == 2
    for request in seen:
        assert request.headers["x-api-key"] == "k2"
        assert request.headers["authorization"] == "Bearer t1"
        assert request.headers["x-root"] == "yes"
        assert request.headers["x-clone"] == "1"
