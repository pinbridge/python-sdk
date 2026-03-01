"""Scheduling models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import HttpUrl, StringConstraints, model_validator

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
    image_url: HttpUrl | None = None
    asset_id: UUID | None = None

    @model_validator(mode="after")
    def validate_media_source(self) -> "ScheduleCreate":
        if self.image_url is None and self.asset_id is None:
            raise ValueError("Either image_url or asset_id must be provided")
        if self.image_url is not None and self.asset_id is not None:
            raise ValueError("Provide either image_url or asset_id, not both")
        return self


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
