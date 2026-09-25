"""Schedule resources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any
from uuid import UUID

from ..models.bulk import BulkOperationResponse
from ..models.common import ScheduleStatus
from ..models.pagination import Page
from ..models.pins import PinValidationResponse
from ..models.schedules import ScheduleCreate, ScheduleResponse, ScheduleSort, ScheduleUpdate
from .base import AsyncAPIResource, SyncAPIResource
from .pins import _iso, _serialize_bulk_ids


def _serialize_schedule_create(data: ScheduleCreate | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(data, ScheduleCreate):
        return data.model_dump(mode="json", exclude_none=True)
    return dict(data)


def _serialize_schedule_filters(
    *,
    limit: int,
    offset: int,
    account_id: UUID | str | None,
    board_id: str | None,
    status: ScheduleStatus | str | None,
    since: datetime | str | None,
    until: datetime | str | None,
    q: str | None,
    sort: ScheduleSort | str | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if account_id is not None:
        params["account_id"] = str(account_id)
    if board_id is not None:
        params["board_id"] = board_id
    if status is not None:
        params["status"] = status.value if isinstance(status, ScheduleStatus) else status
    if since is not None:
        params["since"] = _iso(since)
    if until is not None:
        params["until"] = _iso(until)
    if q is not None:
        params["q"] = q
    if sort is not None:
        params["sort"] = sort
    return params


class SchedulesResource(SyncAPIResource):
    def create(self, data: ScheduleCreate | Mapping[str, Any]) -> ScheduleResponse:
        response = self._request("POST", "/v1/schedules", json=_serialize_schedule_create(data))
        return self._model(ScheduleResponse, response)

    def validate(self, data: ScheduleCreate | Mapping[str, Any]) -> PinValidationResponse:
        """Dry-run a schedule request (``POST /v1/schedules/validate``); nothing is stored."""
        response = self._request(
            "POST", "/v1/schedules/validate", json=_serialize_schedule_create(data)
        )
        return self._model(PinValidationResponse, response)

    def get(self, schedule_id: UUID | str) -> ScheduleResponse:
        response = self._request(
            "GET",
            "/v1/schedules/{schedule_id}",
            path_params={"schedule_id": schedule_id},
        )
        return self._model(ScheduleResponse, response)

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        account_id: UUID | str | None = None,
        board_id: str | None = None,
        status: ScheduleStatus | str | None = None,
        since: datetime | str | None = None,
        until: datetime | str | None = None,
        q: str | None = None,
        sort: ScheduleSort | str | None = None,
    ) -> list[ScheduleResponse]:
        """List schedules, latest ``run_at`` first by default.

        ``q`` searches the pin title, description and link URL; ``sort`` picks the
        order, e.g. ``run_at_asc`` for the next run first (both need API 1.34.0+).
        Use :meth:`list_page` to also get the total.
        """
        params = _serialize_schedule_filters(
            limit=limit,
            offset=offset,
            account_id=account_id,
            board_id=board_id,
            status=status,
            since=since,
            until=until,
            q=q,
            sort=sort,
        )
        response = self._request("GET", "/v1/schedules", params=params)
        return self._list(ScheduleResponse, response)

    def list_page(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        account_id: UUID | str | None = None,
        board_id: str | None = None,
        status: ScheduleStatus | str | None = None,
        since: datetime | str | None = None,
        until: datetime | str | None = None,
        q: str | None = None,
        sort: ScheduleSort | str | None = None,
    ) -> Page[ScheduleResponse]:
        """Same filters as :meth:`list`, plus the total matching schedules (API 1.34.0+)."""
        params = _serialize_schedule_filters(
            limit=limit,
            offset=offset,
            account_id=account_id,
            board_id=board_id,
            status=status,
            since=since,
            until=until,
            q=q,
            sort=sort,
        )
        response = self._request("GET", "/v1/schedules", params=params)
        return self._page(ScheduleResponse, response, limit=limit, offset=offset)

    def update(
        self, schedule_id: UUID | str, data: ScheduleUpdate | Mapping[str, Any]
    ) -> ScheduleResponse:
        """Edit a pending schedule in place (``PATCH /v1/schedules/{id}``)."""
        payload = (
            data.model_dump(mode="json", exclude_unset=True)
            if isinstance(data, ScheduleUpdate)
            else dict(data)
        )
        response = self._request(
            "PATCH",
            "/v1/schedules/{schedule_id}",
            path_params={"schedule_id": schedule_id},
            json=payload,
        )
        return self._model(ScheduleResponse, response)

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
        response = await self._request(
            "POST", "/v1/schedules", json=_serialize_schedule_create(data)
        )
        return self._model(ScheduleResponse, response)

    async def validate(self, data: ScheduleCreate | Mapping[str, Any]) -> PinValidationResponse:
        """Dry-run a schedule request (``POST /v1/schedules/validate``); nothing is stored."""
        response = await self._request(
            "POST", "/v1/schedules/validate", json=_serialize_schedule_create(data)
        )
        return self._model(PinValidationResponse, response)

    async def get(self, schedule_id: UUID | str) -> ScheduleResponse:
        response = await self._request(
            "GET",
            "/v1/schedules/{schedule_id}",
            path_params={"schedule_id": schedule_id},
        )
        return self._model(ScheduleResponse, response)

    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        account_id: UUID | str | None = None,
        board_id: str | None = None,
        status: ScheduleStatus | str | None = None,
        since: datetime | str | None = None,
        until: datetime | str | None = None,
        q: str | None = None,
        sort: ScheduleSort | str | None = None,
    ) -> list[ScheduleResponse]:
        """List schedules, latest ``run_at`` first by default.

        ``q`` searches the pin title, description and link URL; ``sort`` picks the
        order, e.g. ``run_at_asc`` for the next run first (both need API 1.34.0+).
        Use :meth:`list_page` to also get the total.
        """
        params = _serialize_schedule_filters(
            limit=limit,
            offset=offset,
            account_id=account_id,
            board_id=board_id,
            status=status,
            since=since,
            until=until,
            q=q,
            sort=sort,
        )
        response = await self._request("GET", "/v1/schedules", params=params)
        return self._list(ScheduleResponse, response)

    async def list_page(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        account_id: UUID | str | None = None,
        board_id: str | None = None,
        status: ScheduleStatus | str | None = None,
        since: datetime | str | None = None,
        until: datetime | str | None = None,
        q: str | None = None,
        sort: ScheduleSort | str | None = None,
    ) -> Page[ScheduleResponse]:
        """Same filters as :meth:`list`, plus the total matching schedules (API 1.34.0+)."""
        params = _serialize_schedule_filters(
            limit=limit,
            offset=offset,
            account_id=account_id,
            board_id=board_id,
            status=status,
            since=since,
            until=until,
            q=q,
            sort=sort,
        )
        response = await self._request("GET", "/v1/schedules", params=params)
        return self._page(ScheduleResponse, response, limit=limit, offset=offset)

    async def update(
        self, schedule_id: UUID | str, data: ScheduleUpdate | Mapping[str, Any]
    ) -> ScheduleResponse:
        """Edit a pending schedule in place (``PATCH /v1/schedules/{id}``)."""
        payload = (
            data.model_dump(mode="json", exclude_unset=True)
            if isinstance(data, ScheduleUpdate)
            else dict(data)
        )
        response = await self._request(
            "PATCH",
            "/v1/schedules/{schedule_id}",
            path_params={"schedule_id": schedule_id},
            json=payload,
        )
        return self._model(ScheduleResponse, response)

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
