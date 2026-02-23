"""API key models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from .base import PinbridgeModel


class APIKeyCreate(PinbridgeModel):
    name: str


class APIKeyUpdate(PinbridgeModel):
    name: str


class APIKeyResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    name: str
    created_at: datetime
    revoked_at: datetime | None = None


class APIKeyCreateResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    name: str
    api_key: str
    created_at: datetime
