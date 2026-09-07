"""Shared models for bulk-action endpoints."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from .base import PinbridgeModel

BulkOperationItemStatus = Literal["succeeded", "skipped", "failed"]


class BulkOperationItemResult(PinbridgeModel):
    id: UUID
    status: BulkOperationItemStatus
    error_code: str | None = None
    error_message: str | None = None


class BulkOperationResponse(PinbridgeModel):
    succeeded_count: int
    skipped_count: int
    failed_count: int
    results: list[BulkOperationItemResult]
