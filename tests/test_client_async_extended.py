from __future__ import annotations

import httpx
import pytest

from pinbridge_sdk.async_client import AsyncPinbridgeClient
from pinbridge_sdk.resources.base import AsyncAPIResource


class _DummyAsyncResource(AsyncAPIResource):
    async def ping(self) -> dict:
        response = await self._request("GET", "/healthz")
        return response.json()


async def test_async_client_init_rejects_transport_and_http_client() -> None:
    with pytest.raises(ValueError, match="either http_client or transport"):
        AsyncPinbridgeClient(
            http_client=httpx.AsyncClient(),
            transport=httpx.MockTransport(lambda _: httpx.Response(200)),
        )


async def test_async_register_resource_and_duplicate_handling() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json={"status": "ok"}))
    async with AsyncPinbridgeClient(
        base_url="https://api.pinbridge.test", transport=transport
    ) as client:
        with pytest.raises(ValueError, match="already registered"):
            client.register_resource("system", _DummyAsyncResource)

        client.register_resource("dummy", _DummyAsyncResource)
        assert client.resource("dummy") is client.dummy  # type: ignore[attr-defined]
        payload = await client.dummy.ping()  # type: ignore[attr-defined]
        assert payload["status"] == "ok"
