"""Pin and job models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import HttpUrl, StringConstraints

from .base import PinbridgeModel
from .common import PinStatus

PinTitle = Annotated[str, StringConstraints(max_length=500)]
IdempotencyKey = Annotated[str, StringConstraints(max_length=255)]


class PinCreate(PinbridgeModel):
    account_id: UUID
    board_id: str
    title: PinTitle
    description: str | None = None
    link_url: HttpUrl | None = None
    image_url: HttpUrl
    idempotency_key: IdempotencyKey


class PinResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    pinterest_account_id: UUID
    status: PinStatus
    title: str
    description: str | None = None
    link_url: str | None = None
    image_url: str
    board_id: str
    pinterest_pin_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    idempotency_key: str
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None


class JobStatusResponse(PinbridgeModel):
    job_id: UUID
    pin_id: UUID
    status: PinStatus
    submitted_at: datetime
    completed_at: datetime | None = None
    pinterest_pin_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
