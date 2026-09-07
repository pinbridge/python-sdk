"""MCP usage tracking and quota resources."""

from __future__ import annotations

from ..models.mcp import MCPQuotaResponse, MCPTrackResponse
from .base import AsyncAPIResource, SyncAPIResource


class MCPResource(SyncAPIResource):
    def quota(self) -> MCPQuotaResponse:
        response = self._request("GET", "/v1/mcp/quota")
        return self._model(MCPQuotaResponse, response)

    def track(self) -> MCPTrackResponse:
        response = self._request("POST", "/v1/mcp/track")
        return self._model(MCPTrackResponse, response)


class AsyncMCPResource(AsyncAPIResource):
    async def quota(self) -> MCPQuotaResponse:
        response = await self._request("GET", "/v1/mcp/quota")
        return self._model(MCPQuotaResponse, response)

    async def track(self) -> MCPTrackResponse:
        response = await self._request("POST", "/v1/mcp/track")
        return self._model(MCPTrackResponse, response)
