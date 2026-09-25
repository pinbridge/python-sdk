"""Pin and job resources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any
from uuid import UUID

from ..models.bulk import BulkOperationResponse
from ..models.common import ImportJobStatus, ImportSourceType, PinStatus
from ..models.pagination import Page
from ..models.pins import (
    AnalyticsSource,
    ImportJobResponse,
    JobStatusResponse,
    PinAnalyticsResponse,
    PinBatchResponse,
    PinCreate,
    PinDeleteResponse,
    PinImportCreate,
    PinResponse,
    PinRetryRequest,
    PinSort,
    PinUpdate,
    PinValidationResponse,
)
from .assets import UploadableFile, _normalize_upload
from .base import AsyncAPIResource, SyncAPIResource


def _serialize_pin_input(data: PinCreate | PinImportCreate | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(data, PinCreate):
        return data.model_dump(mode="json", exclude_none=True)
    return dict(data)


def _serialize_bulk_ids(ids: Sequence[UUID | str]) -> dict[str, Any]:
    return {"ids": [str(item) for item in ids]}


def _serialize_pin_retry(
    data: PinRetryRequest | Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if data is None:
        return None
    if isinstance(data, PinRetryRequest):
        return data.model_dump(mode="json", exclude_none=True)
    return dict(data)


def _serialize_import_rows(
    rows: Sequence[PinCreate | PinImportCreate | Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [_serialize_pin_input(row) for row in rows]


def _serialize_pin_update(data: PinUpdate | Mapping[str, Any]) -> dict[str, Any]:
    # exclude_unset (not exclude_none) so an explicit None still clears a field.
    if isinstance(data, PinUpdate):
        return data.model_dump(mode="json", exclude_unset=True)
    return dict(data)


def _serialize_pin_batch(pins: Sequence[PinCreate | Mapping[str, Any]]) -> dict[str, Any]:
    return {"pins": [_serialize_pin_input(pin) for pin in pins]}


def _iso(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    return value.isoformat() if isinstance(value, datetime) else value


def _serialize_pin_filters(
    *,
    limit: int,
    offset: int,
    account_id: UUID | str | None,
    board_id: str | None,
    status: PinStatus | str | None,
    error_code: str | None,
    since: datetime | str | None,
    until: datetime | str | None,
    q: str | None,
    sort: PinSort | str | None,
    removed: bool | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if account_id is not None:
        params["account_id"] = str(account_id)
    if board_id is not None:
        params["board_id"] = board_id
    if status is not None:
        params["status"] = status.value if isinstance(status, PinStatus) else status
    if error_code is not None:
        params["error_code"] = error_code
    if since is not None:
        params["since"] = _iso(since)
    if until is not None:
        params["until"] = _iso(until)
    if q is not None:
        params["q"] = q
    if sort is not None:
        params["sort"] = sort
    if removed is not None:
        params["removed"] = "true" if removed else "false"
    return params


def _serialize_analytics_params(
    *,
    start_date: date | str | None,
    end_date: date | str | None,
    metrics: Sequence[str] | str | None,
    source: AnalyticsSource | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if start_date is not None:
        params["start_date"] = (
            start_date.isoformat() if isinstance(start_date, date) else start_date
        )
    if end_date is not None:
        params["end_date"] = end_date.isoformat() if isinstance(end_date, date) else end_date
    if metrics is not None:
        params["metrics"] = metrics if isinstance(metrics, str) else ",".join(metrics)
    if source is not None:
        params["source"] = source
    return params


def _serialize_import_filters(
    *,
    limit: int,
    offset: int,
    status: ImportJobStatus | str | None,
    source_type: ImportSourceType | str | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if status is not None:
        params["status"] = status.value if isinstance(status, ImportJobStatus) else status
    if source_type is not None:
        params["source_type"] = (
            source_type.value if isinstance(source_type, ImportSourceType) else source_type
        )
    return params


class PinsResource(SyncAPIResource):
    def create(self, data: PinCreate | Mapping[str, Any]) -> PinResponse:
        payload = _serialize_pin_input(data)
        response = self._request("POST", "/v1/pins", json=payload)
        return self._model(PinResponse, response)

    def validate(self, data: PinCreate | Mapping[str, Any]) -> PinValidationResponse:
        """Dry-run a pin request (``POST /v1/pins/validate``); nothing is published."""
        response = self._request("POST", "/v1/pins/validate", json=_serialize_pin_input(data))
        return self._model(PinValidationResponse, response)

    def create_batch(self, pins: Sequence[PinCreate | Mapping[str, Any]]) -> PinBatchResponse:
        """Publish up to 100 pins in one call with a per-item outcome."""
        response = self._request("POST", "/v1/pins/batch", json=_serialize_pin_batch(pins))
        return self._model(PinBatchResponse, response)

    def import_json(
        self,
        rows: Sequence[PinCreate | PinImportCreate | Mapping[str, Any]],
    ) -> ImportJobResponse:
        response = self._request("POST", "/v1/pins/imports/json", json=_serialize_import_rows(rows))
        return self._model(ImportJobResponse, response)

    def import_csv(
        self,
        file: UploadableFile,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> ImportJobResponse:
        resolved_filename, body, resolved_content_type = _normalize_upload(
            file,
            filename=filename,
            content_type=content_type or "text/csv",
        )
        response = self._request(
            "POST",
            "/v1/pins/imports/csv",
            files={"file": (resolved_filename, body, resolved_content_type)},
        )
        return self._model(ImportJobResponse, response)

    def get_import(self, job_id: UUID | str) -> ImportJobResponse:
        response = self._request(
            "GET",
            "/v1/pins/imports/{job_id}",
            path_params={"job_id": job_id},
        )
        return self._model(ImportJobResponse, response)

    def list_imports(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        status: ImportJobStatus | str | None = None,
        source_type: ImportSourceType | str | None = None,
    ) -> list[ImportJobResponse]:
        params = _serialize_import_filters(
            limit=limit,
            offset=offset,
            status=status,
            source_type=source_type,
        )
        response = self._request(
            "GET",
            "/v1/pins/imports",
            params=params,
        )
        return self._list(ImportJobResponse, response)

    def get(self, pin_id: UUID | str) -> PinResponse:
        response = self._request("GET", "/v1/pins/{pin_id}", path_params={"pin_id": pin_id})
        return self._model(PinResponse, response)

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        account_id: UUID | str | None = None,
        board_id: str | None = None,
        status: PinStatus | str | None = None,
        error_code: str | None = None,
        since: datetime | str | None = None,
        until: datetime | str | None = None,
        q: str | None = None,
        sort: PinSort | str | None = None,
        removed: bool | None = None,
    ) -> list[PinResponse]:
        """List pins, newest first by default.

        ``q`` searches title, description and link URL; ``sort`` picks the order
        (both need API 1.34.0+). ``removed=True`` keeps only published pins that were
        deleted on Pinterest, ``False`` leaves them out (API 1.35.0+). Use
        :meth:`list_page` to also get the total.
        """
        params = _serialize_pin_filters(
            limit=limit,
            offset=offset,
            account_id=account_id,
            board_id=board_id,
            status=status,
            error_code=error_code,
            since=since,
            until=until,
            q=q,
            sort=sort,
            removed=removed,
        )
        response = self._request("GET", "/v1/pins", params=params)
        return self._list(PinResponse, response)

    def list_page(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        account_id: UUID | str | None = None,
        board_id: str | None = None,
        status: PinStatus | str | None = None,
        error_code: str | None = None,
        since: datetime | str | None = None,
        until: datetime | str | None = None,
        q: str | None = None,
        sort: PinSort | str | None = None,
        removed: bool | None = None,
    ) -> Page[PinResponse]:
        """Same filters as :meth:`list`, plus the total matching pins (API 1.34.0+)."""
        params = _serialize_pin_filters(
            limit=limit,
            offset=offset,
            account_id=account_id,
            board_id=board_id,
            status=status,
            error_code=error_code,
            since=since,
            until=until,
            q=q,
            sort=sort,
            removed=removed,
        )
        response = self._request("GET", "/v1/pins", params=params)
        return self._page(PinResponse, response, limit=limit, offset=offset)

    def update(self, pin_id: UUID | str, data: PinUpdate | Mapping[str, Any]) -> PinResponse:
        """Edit title, description, link, alt text or board (``PATCH /v1/pins/{id}``)."""
        response = self._request(
            "PATCH",
            "/v1/pins/{pin_id}",
            path_params={"pin_id": pin_id},
            json=_serialize_pin_update(data),
        )
        return self._model(PinResponse, response)

    def delete(
        self, pin_id: UUID | str, *, delete_from_pinterest: bool = False
    ) -> PinDeleteResponse | None:
        """Delete a pin record; with ``delete_from_pinterest`` also remove it on Pinterest.

        Returns ``None`` for a record-only delete (HTTP 204) and a
        :class:`PinDeleteResponse` describing the upstream outcome otherwise.
        """
        if not delete_from_pinterest:
            self._request("DELETE", "/v1/pins/{pin_id}", path_params={"pin_id": pin_id})
            return None
        response = self._request(
            "DELETE",
            "/v1/pins/{pin_id}",
            path_params={"pin_id": pin_id},
            params={"delete_from_pinterest": True},
        )
        return self._model(PinDeleteResponse, response)

    def analytics(
        self,
        pin_id: UUID | str,
        *,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        metrics: Sequence[str] | str | None = None,
        source: AnalyticsSource | None = None,
    ) -> PinAnalyticsResponse:
        """Pinterest analytics for a published pin over a date range.

        ``source`` (API 1.33.0+): ``auto`` (default) reads PinBridge's stored history
        when it covers the range, ``stored`` forces it (up to 366 days), ``live``
        asks Pinterest (up to 90 days). A pin deleted on Pinterest is answered from
        the stored history (API 1.35.0+).
        """
        response = self._request(
            "GET",
            "/v1/pins/{pin_id}/analytics",
            path_params={"pin_id": pin_id},
            params=_serialize_analytics_params(
                start_date=start_date, end_date=end_date, metrics=metrics, source=source
            ),
        )
        return self._model(PinAnalyticsResponse, response)

    def retry(
        self,
        pin_id: UUID | str,
        data: PinRetryRequest | Mapping[str, Any] | None = None,
    ) -> PinResponse:
        response = self._request(
            "POST",
            "/v1/pins/{pin_id}/retry",
            path_params={"pin_id": pin_id},
            json=_serialize_pin_retry(data),
        )
        return self._model(PinResponse, response)

    def bulk_delete(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = self._request("POST", "/v1/pins/bulk-delete", json=_serialize_bulk_ids(ids))
        return self._model(BulkOperationResponse, response)

    def bulk_retry(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = self._request("POST", "/v1/pins/bulk-retry", json=_serialize_bulk_ids(ids))
        return self._model(BulkOperationResponse, response)


class JobsResource(SyncAPIResource):
    def get(self, job_id: UUID | str) -> JobStatusResponse:
        response = self._request("GET", "/v1/jobs/{job_id}", path_params={"job_id": job_id})
        return self._model(JobStatusResponse, response)


class AsyncPinsResource(AsyncAPIResource):
    async def create(self, data: PinCreate | Mapping[str, Any]) -> PinResponse:
        payload = _serialize_pin_input(data)
        response = await self._request("POST", "/v1/pins", json=payload)
        return self._model(PinResponse, response)

    async def validate(self, data: PinCreate | Mapping[str, Any]) -> PinValidationResponse:
        """Dry-run a pin request (``POST /v1/pins/validate``); nothing is published."""
        response = await self._request("POST", "/v1/pins/validate", json=_serialize_pin_input(data))
        return self._model(PinValidationResponse, response)

    async def create_batch(self, pins: Sequence[PinCreate | Mapping[str, Any]]) -> PinBatchResponse:
        """Publish up to 100 pins in one call with a per-item outcome."""
        response = await self._request("POST", "/v1/pins/batch", json=_serialize_pin_batch(pins))
        return self._model(PinBatchResponse, response)

    async def import_json(
        self,
        rows: Sequence[PinCreate | PinImportCreate | Mapping[str, Any]],
    ) -> ImportJobResponse:
        response = await self._request(
            "POST",
            "/v1/pins/imports/json",
            json=_serialize_import_rows(rows),
        )
        return self._model(ImportJobResponse, response)

    async def import_csv(
        self,
        file: UploadableFile,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> ImportJobResponse:
        resolved_filename, body, resolved_content_type = _normalize_upload(
            file,
            filename=filename,
            content_type=content_type or "text/csv",
        )
        response = await self._request(
            "POST",
            "/v1/pins/imports/csv",
            files={"file": (resolved_filename, body, resolved_content_type)},
        )
        return self._model(ImportJobResponse, response)

    async def get_import(self, job_id: UUID | str) -> ImportJobResponse:
        response = await self._request(
            "GET",
            "/v1/pins/imports/{job_id}",
            path_params={"job_id": job_id},
        )
        return self._model(ImportJobResponse, response)

    async def list_imports(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        status: ImportJobStatus | str | None = None,
        source_type: ImportSourceType | str | None = None,
    ) -> list[ImportJobResponse]:
        params = _serialize_import_filters(
            limit=limit,
            offset=offset,
            status=status,
            source_type=source_type,
        )
        response = await self._request(
            "GET",
            "/v1/pins/imports",
            params=params,
        )
        return self._list(ImportJobResponse, response)

    async def get(self, pin_id: UUID | str) -> PinResponse:
        response = await self._request("GET", "/v1/pins/{pin_id}", path_params={"pin_id": pin_id})
        return self._model(PinResponse, response)

    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        account_id: UUID | str | None = None,
        board_id: str | None = None,
        status: PinStatus | str | None = None,
        error_code: str | None = None,
        since: datetime | str | None = None,
        until: datetime | str | None = None,
        q: str | None = None,
        sort: PinSort | str | None = None,
        removed: bool | None = None,
    ) -> list[PinResponse]:
        """List pins, newest first by default.

        ``q`` searches title, description and link URL; ``sort`` picks the order
        (both need API 1.34.0+). ``removed=True`` keeps only published pins that were
        deleted on Pinterest, ``False`` leaves them out (API 1.35.0+). Use
        :meth:`list_page` to also get the total.
        """
        params = _serialize_pin_filters(
            limit=limit,
            offset=offset,
            account_id=account_id,
            board_id=board_id,
            status=status,
            error_code=error_code,
            since=since,
            until=until,
            q=q,
            sort=sort,
            removed=removed,
        )
        response = await self._request("GET", "/v1/pins", params=params)
        return self._list(PinResponse, response)

    async def list_page(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        account_id: UUID | str | None = None,
        board_id: str | None = None,
        status: PinStatus | str | None = None,
        error_code: str | None = None,
        since: datetime | str | None = None,
        until: datetime | str | None = None,
        q: str | None = None,
        sort: PinSort | str | None = None,
        removed: bool | None = None,
    ) -> Page[PinResponse]:
        """Same filters as :meth:`list`, plus the total matching pins (API 1.34.0+)."""
        params = _serialize_pin_filters(
            limit=limit,
            offset=offset,
            account_id=account_id,
            board_id=board_id,
            status=status,
            error_code=error_code,
            since=since,
            until=until,
            q=q,
            sort=sort,
            removed=removed,
        )
        response = await self._request("GET", "/v1/pins", params=params)
        return self._page(PinResponse, response, limit=limit, offset=offset)

    async def update(self, pin_id: UUID | str, data: PinUpdate | Mapping[str, Any]) -> PinResponse:
        """Edit title, description, link, alt text or board (``PATCH /v1/pins/{id}``)."""
        response = await self._request(
            "PATCH",
            "/v1/pins/{pin_id}",
            path_params={"pin_id": pin_id},
            json=_serialize_pin_update(data),
        )
        return self._model(PinResponse, response)

    async def delete(
        self, pin_id: UUID | str, *, delete_from_pinterest: bool = False
    ) -> PinDeleteResponse | None:
        """Delete a pin record; with ``delete_from_pinterest`` also remove it on Pinterest."""
        if not delete_from_pinterest:
            await self._request("DELETE", "/v1/pins/{pin_id}", path_params={"pin_id": pin_id})
            return None
        response = await self._request(
            "DELETE",
            "/v1/pins/{pin_id}",
            path_params={"pin_id": pin_id},
            params={"delete_from_pinterest": True},
        )
        return self._model(PinDeleteResponse, response)

    async def analytics(
        self,
        pin_id: UUID | str,
        *,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        metrics: Sequence[str] | str | None = None,
        source: AnalyticsSource | None = None,
    ) -> PinAnalyticsResponse:
        """Pinterest analytics for a published pin over a date range.

        ``source`` (API 1.33.0+): ``auto`` (default) reads PinBridge's stored history
        when it covers the range, ``stored`` forces it (up to 366 days), ``live``
        asks Pinterest (up to 90 days). A pin deleted on Pinterest is answered from
        the stored history (API 1.35.0+).
        """
        response = await self._request(
            "GET",
            "/v1/pins/{pin_id}/analytics",
            path_params={"pin_id": pin_id},
            params=_serialize_analytics_params(
                start_date=start_date, end_date=end_date, metrics=metrics, source=source
            ),
        )
        return self._model(PinAnalyticsResponse, response)

    async def retry(
        self,
        pin_id: UUID | str,
        data: PinRetryRequest | Mapping[str, Any] | None = None,
    ) -> PinResponse:
        response = await self._request(
            "POST",
            "/v1/pins/{pin_id}/retry",
            path_params={"pin_id": pin_id},
            json=_serialize_pin_retry(data),
        )
        return self._model(PinResponse, response)

    async def bulk_delete(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = await self._request(
            "POST", "/v1/pins/bulk-delete", json=_serialize_bulk_ids(ids)
        )
        return self._model(BulkOperationResponse, response)

    async def bulk_retry(self, ids: Sequence[UUID | str]) -> BulkOperationResponse:
        response = await self._request("POST", "/v1/pins/bulk-retry", json=_serialize_bulk_ids(ids))
        return self._model(BulkOperationResponse, response)


class AsyncJobsResource(AsyncAPIResource):
    async def get(self, job_id: UUID | str) -> JobStatusResponse:
        response = await self._request("GET", "/v1/jobs/{job_id}", path_params={"job_id": job_id})
        return self._model(JobStatusResponse, response)
