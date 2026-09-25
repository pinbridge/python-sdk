"""Dashboard summary models (``GET /v1/dashboard/summary``)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from .base import PinbridgeModel


class DashboardGranularity(str, Enum):
    """Series bucket size: hourly for ranges up to 48 hours, else daily."""

    HOUR = "hour"
    DAY = "day"


class DashboardPinStats(PinbridgeModel):
    """Pins submitted in a period, grouped by their current status."""

    total: int
    by_status: dict[str, int]
    success_rate: float | None = None


class DashboardSeriesPoint(PinbridgeModel):
    """One hour or day of pin activity; ``start`` is in the requested time zone."""

    start: datetime
    created: int
    published: int
    failed: int


class DashboardAccountCount(PinbridgeModel):
    account_id: UUID
    published: int


class DashboardQueue(PinbridgeModel):
    """Pins waiting to publish right now, regardless of the requested range."""

    queued: int
    deferred: int
    publishing: int


class DashboardScheduleStats(PinbridgeModel):
    by_status: dict[str, int]
    upcoming: int


class DashboardImportJobStats(PinbridgeModel):
    by_status: dict[str, int]


class DashboardSummaryResponse(PinbridgeModel):
    """Publishing activity for a time range.

    ``previous_pins`` holds the same figures for the equal-length period just
    before ``start``. ``import_jobs`` is ``None`` when filtered by account.
    """

    start: datetime
    end: datetime
    timezone: str
    granularity: DashboardGranularity
    previous_start: datetime
    previous_end: datetime
    account_id: UUID | None = None
    pins: DashboardPinStats
    previous_pins: DashboardPinStats
    series: list[DashboardSeriesPoint]
    published_by_account: list[DashboardAccountCount]
    queue: DashboardQueue
    schedules: DashboardScheduleStats
    import_jobs: DashboardImportJobStats | None = None
