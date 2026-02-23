"""Pinterest integration models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from .base import PinbridgeModel


class OAuthStartResponse(PinbridgeModel):
    authorization_url: str


class OAuthCallbackResponse(PinbridgeModel):
    status: str
    message: str
    account_id: str | None = None


class PinterestAccountResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    pinterest_user_id: str
    display_name: str | None = None
    username: str | None = None
    scopes: str
    created_at: datetime
    updated_at: datetime
    revoked_at: datetime | None = None


class BoardResponse(PinbridgeModel):
    id: str
    name: str
    description: str | None = None
    privacy: str | None = None


class BoardCreateRequest(PinbridgeModel):
    account_id: UUID
    name: str
    description: str | None = None
    privacy: str | None = None
