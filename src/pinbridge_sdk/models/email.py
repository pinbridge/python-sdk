"""Email preference models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from .base import PinbridgeModel


class EmailPreferencesUpdateRequest(PinbridgeModel):
    transactional_enabled: bool
    alerts_enabled: bool
    verification_enabled: bool


class EmailPreferencesResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    user_id: UUID
    transactional_enabled: bool
    alerts_enabled: bool
    verification_enabled: bool
    created_at: datetime
    updated_at: datetime
