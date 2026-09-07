"""Schedule resources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from ..models.bulk import BulkOperationResponse
from ..models.schedules import ScheduleCreate, ScheduleResponse
from .base import AsyncAPIResource, SyncAPIResource
from .pins import _serialize_bulk_ids


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

    def retry(self, schedule_id: UUID | str) -> ScheduleResponse:
        response = self._request(
            "POST",
            "/v1/schedules/{schedule_id}/retry",
            path_params={"schedule_id": schedule_id},
        )
        return self._model(ScheduleResponse, response)

    def delete(self, schedule_id: UUID | str) -> None:
        self._request(
            "DELETE",
            "/v1/schedules/{schedule_id}",
            path_params={"schedule_id": schedule_id},
        )

    def bulk_cancel(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = self._request("POST", "/v1/schedules/bulk-cancel", json=_serialize_bulk_ids(ids))
        return self._model(BulkOperationResponse, response)

    def bulk_retry(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = self._request("POST", "/v1/schedules/bulk-retry", json=_serialize_bulk_ids(ids))
        return self._model(BulkOperationResponse, response)

    def bulk_delete(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = self._request("POST", "/v1/schedules/bulk-delete", json=_serialize_bulk_ids(ids))
        return self._model(BulkOperationResponse, response)


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

    async def retry(self, schedule_id: UUID | str) -> ScheduleResponse:
        response = await self._request(
            "POST",
            "/v1/schedules/{schedule_id}/retry",
            path_params={"schedule_id": schedule_id},
        )
        return self._model(ScheduleResponse, response)

    async def delete(self, schedule_id: UUID | str) -> None:
        await self._request(
            "DELETE",
            "/v1/schedules/{schedule_id}",
            path_params={"schedule_id": schedule_id},
        )

    async def bulk_cancel(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = await self._request(
            "POST", "/v1/schedules/bulk-cancel", json=_serialize_bulk_ids(ids)
        )
        return self._model(BulkOperationResponse, response)

    async def bulk_retry(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = await self._request(
            "POST", "/v1/schedules/bulk-retry", json=_serialize_bulk_ids(ids)
        )
        return self._model(BulkOperationResponse, response)

    async def bulk_delete(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = await self._request(
            "POST", "/v1/schedules/bulk-delete", json=_serialize_bulk_ids(ids)
        )
        return self._model(BulkOperationResponse, response)
