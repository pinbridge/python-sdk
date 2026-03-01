"""Shared enums and error schema models."""

from __future__ import annotations

from enum import Enum

from .base import PinbridgeModel


class Plan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingStatus(str, Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


class WorkspaceEnvironment(str, Enum):
    PRODUCTION = "production"
    SANDBOX = "sandbox"


class PinStatus(str, Enum):
    QUEUED = "queued"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


class PinMediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class ScheduleStatus(str, Enum):
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELED = "canceled"


class ValidationErrorItem(PinbridgeModel):
    loc: list[str | int]
    msg: str
    type: str


class HTTPValidationError(PinbridgeModel):
    detail: list[ValidationErrorItem]
