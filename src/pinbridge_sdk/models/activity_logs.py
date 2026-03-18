"""Activity log models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from .base import PinbridgeModel


class ActivityLogActorType(str, Enum):
    USER = "user"
    API_KEY = "api_key"
    SYSTEM = "system"
    WORKER = "worker"
    ADMIN = "admin"
    BILLING = "billing"


class ActivityLogCategory(str, Enum):
    SECURITY = "security"
    PUBLISHING = "publishing"
    BILLING = "billing"
    CONFIGURATION = "configuration"
    INTEGRATION = "integration"


class ActivityLogStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    QUEUED = "queued"
    CANCELED = "canceled"


class ActivityLogResponse(PinbridgeModel):
    id: UUID
    actor_user_id: UUID | None = None
    actor_type: ActivityLogActorType
    actor_label: str | None = None
    action: str
    category: ActivityLogCategory
    resource_type: str | None = None
    resource_id: str | None = None
    status: ActivityLogStatus
    message: str
    metadata: dict[str, Any]
    request_id: str | None = None
    retention_days: int
    expires_at: datetime
    created_at: datetime


class ActivityLogListResponse(PinbridgeModel):
    items: list[ActivityLogResponse]
    next_cursor: str | None = None
    current_retention_days: int
    current_retention_label: str
