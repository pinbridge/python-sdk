from __future__ import annotations

import httpx

from pinbridge_sdk import AsyncPinbridgeClient


async def test_async_client_health() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "status": "ok",
                "version": "0.1.0",
                "environment": "test",
                "database": "ok",
            },
        )

    transport = httpx.MockTransport(handler)
    async with AsyncPinbridgeClient(
        base_url="https://api.pinbridge.test", transport=transport
    ) as client:
        health = await client.system.health()

    assert health.status == "ok"
