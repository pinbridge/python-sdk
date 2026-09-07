"""MCP usage and quota models."""

from __future__ import annotations

from .base import PinbridgeModel


class MCPQuotaResponse(PinbridgeModel):
    week: str
    requests_used: int
    requests_limit: int  # 0 = unlimited
    quota_exhausted: bool
    resets_at: str


class MCPTrackResponse(PinbridgeModel):
    week: str
    requests_used: int
    requests_limit: int
    quota_exhausted: bool
    resets_at: str
