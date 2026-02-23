"""Schedule resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from ..models.schedules import ScheduleCreate, ScheduleResponse
from .base import AsyncAPIResource, SyncAPIResource


class SchedulesResource(SyncAPIResource):
    def create(self, data: ScheduleCreate | Mapping[str, Any]) -> ScheduleResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, ScheduleCreate)
            else dict(data)
        )
        response = self._request("POST", "/v1/schedules", json=payload)
        return self._model(ScheduleResponse, response)

    def get(self, schedule_id: UUID | str) -> ScheduleResponse:
        response = self._request(
            "GET",
            "/v1/schedules/{schedule_id}",
            path_params={"schedule_id": schedule_id},
        )
        return self._model(ScheduleResponse, response)

    def list(self, *, limit: int = 50, offset: int = 0) -> list[ScheduleResponse]:
        response = self._request(
            "GET",
            "/v1/schedules",
            params={"limit": limit, "offset": offset},
        )
        return self._list(ScheduleResponse, response)

    def cancel(self, schedule_id: UUID | str) -> ScheduleResponse:
        response = self._request(
            "POST",
            "/v1/schedules/{schedule_id}/cancel",
            path_params={"schedule_id": schedule_id},
        )
        return self._model(ScheduleResponse, response)


class AsyncSchedulesResource(AsyncAPIResource):
    async def create(self, data: ScheduleCreate | Mapping[str, Any]) -> ScheduleResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, ScheduleCreate)
            else dict(data)
        )
        response = await self._request("POST", "/v1/schedules", json=payload)
        return self._model(ScheduleResponse, response)

    async def get(self, schedule_id: UUID | str) -> ScheduleResponse:
        response = await self._request(
            "GET",
            "/v1/schedules/{schedule_id}",
            path_params={"schedule_id": schedule_id},
        )
        return self._model(ScheduleResponse, response)

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[ScheduleResponse]:
        response = await self._request(
            "GET",
            "/v1/schedules",
            params={"limit": limit, "offset": offset},
        )
        return self._list(ScheduleResponse, response)

    async def cancel(self, schedule_id: UUID | str) -> ScheduleResponse:
        response = await self._request(
            "POST",
            "/v1/schedules/{schedule_id}/cancel",
            path_params={"schedule_id": schedule_id},
        )
        return self._model(ScheduleResponse, response)
