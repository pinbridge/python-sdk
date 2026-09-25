"""Dashboard resources."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from ..models.dashboard import DashboardSummaryResponse
from .base import AsyncAPIResource, SyncAPIResource
from .pins import _iso


def _serialize_summary_params(
    *,
    start: datetime | str | None,
    end: datetime | str | None,
    tz: str | None,
    account_id: UUID | str | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if start is not None:
        params["start"] = _iso(start)
    if end is not None:
        params["end"] = _iso(end)
    if tz is not None:
        params["tz"] = tz
    if account_id is not None:
        params["account_id"] = str(account_id)
    return params


class DashboardResource(SyncAPIResource):
    def summary(
        self,
        *,
        start: datetime | str | None = None,
        end: datetime | str | None = None,
        tz: str | None = None,
        account_id: UUID | str | None = None,
    ) -> DashboardSummaryResponse:
        """Publishing activity for ``[start, end)`` (``GET /v1/dashboard/summary``, API 1.34.0+).

        Defaults to the 30 days up to now; ranges can span up to 366 days. ``tz``
        is an IANA zone name for the series buckets, and a naive ``start``/``end``
        is read as wall-clock time in that zone. Ranges up to 48 hours get an
        hourly series, longer ones a daily series.
        """
        response = self._request(
            "GET",
            "/v1/dashboard/summary",
            params=_serialize_summary_params(start=start, end=end, tz=tz, account_id=account_id),
        )
        return self._model(DashboardSummaryResponse, response)


class AsyncDashboardResource(AsyncAPIResource):
    async def summary(
        self,
        *,
        start: datetime | str | None = None,
        end: datetime | str | None = None,
        tz: str | None = None,
        account_id: UUID | str | None = None,
    ) -> DashboardSummaryResponse:
        """Publishing activity for ``[start, end)`` (``GET /v1/dashboard/summary``, API 1.34.0+).

        Defaults to the 30 days up to now; ranges can span up to 366 days. ``tz``
        is an IANA zone name for the series buckets, and a naive ``start``/``end``
        is read as wall-clock time in that zone. Ranges up to 48 hours get an
        hourly series, longer ones a daily series.
        """
        response = await self._request(
            "GET",
            "/v1/dashboard/summary",
            params=_serialize_summary_params(start=start, end=end, tz=tz, account_id=account_id),
        )
        return self._model(DashboardSummaryResponse, response)
