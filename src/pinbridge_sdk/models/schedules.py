"""Scheduling models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import HttpUrl, StringConstraints

from .base import PinbridgeModel
from .common import ScheduleStatus

ScheduleTitle = Annotated[str, StringConstraints(max_length=500)]


class ScheduleCreate(PinbridgeModel):
    account_id: UUID
    run_at: datetime
    board_id: str
    title: ScheduleTitle
    description: str | None = None
    link_url: HttpUrl | None = None
    image_url: HttpUrl


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
