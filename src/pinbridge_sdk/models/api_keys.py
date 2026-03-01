"""API key models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints

from .base import PinbridgeModel

APIKeyName = Annotated[str, StringConstraints(max_length=255)]


class APIKeyCreate(PinbridgeModel):
    name: APIKeyName


class APIKeyUpdate(PinbridgeModel):
    name: APIKeyName


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
