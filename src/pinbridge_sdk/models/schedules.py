"""Scheduling models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from .base import PinbridgeModel
from .common import ScheduleStatus


class ScheduleCreate(PinbridgeModel):
    account_id: UUID
    run_at: datetime
    board_id: str
    title: str
    description: str | None = None
    link_url: str | None = None
    image_url: str


class ScheduleResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    pinterest_account_id: UUID
    run_at: datetime
    status: ScheduleStatus
    payload: dict[str, Any]
    last_error: str | None = None
    pin_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
