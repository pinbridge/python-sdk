"""Webhook models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import Field, HttpUrl, StringConstraints

from .base import PinbridgeModel

WebhookSecret = Annotated[str, StringConstraints(min_length=16, max_length=255)]


class WebhookCreate(PinbridgeModel):
    url: HttpUrl
    secret: WebhookSecret
    events: list[str] = Field(default_factory=lambda: ["pin.published", "pin.failed"])
    is_enabled: bool = True


class WebhookUpdate(PinbridgeModel):
    url: HttpUrl | None = None
    secret: WebhookSecret | None = None
    events: list[str] | None = None
    is_enabled: bool | None = None


class WebhookResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    url: str
    events: list[str]
    is_enabled: bool
    created_at: datetime
    updated_at: datetime


class WebhookDeliveryResponse(PinbridgeModel):
    id: UUID
    webhook_id: UUID
    event_type: str
    payload: dict[str, Any]
    attempt_count: int
    last_status_code: int | None = None
    last_error: str | None = None
    next_attempt_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
