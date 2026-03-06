"""Pin and job resources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from ..models.common import ImportJobStatus, ImportSourceType
from ..models.pins import (
    ImportJobResponse,
    JobStatusResponse,
    PinCreate,
    PinImportCreate,
    PinResponse,
)
from .assets import UploadableFile, _normalize_upload
from .base import AsyncAPIResource, SyncAPIResource


def _serialize_pin_input(data: PinCreate | PinImportCreate | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(data, PinCreate):
        return data.model_dump(mode="json", exclude_none=True)
    return dict(data)


def _serialize_import_rows(
    rows: Sequence[PinCreate | PinImportCreate | Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [_serialize_pin_input(row) for row in rows]


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

    def list(self, *, limit: int = 50, offset: int = 0) -> list[PinResponse]:
        response = self._request("GET", "/v1/pins", params={"limit": limit, "offset": offset})
        return self._list(PinResponse, response)

    def delete(self, pin_id: UUID | str) -> None:
        self._request("DELETE", "/v1/pins/{pin_id}", path_params={"pin_id": pin_id})


class JobsResource(SyncAPIResource):
    def get(self, job_id: UUID | str) -> JobStatusResponse:
        response = self._request("GET", "/v1/jobs/{job_id}", path_params={"job_id": job_id})
        return self._model(JobStatusResponse, response)


class AsyncPinsResource(AsyncAPIResource):
    async def create(self, data: PinCreate | Mapping[str, Any]) -> PinResponse:
        payload = _serialize_pin_input(data)
        response = await self._request("POST", "/v1/pins", json=payload)
        return self._model(PinResponse, response)

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

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[PinResponse]:
        response = await self._request("GET", "/v1/pins", params={"limit": limit, "offset": offset})
        return self._list(PinResponse, response)

    async def delete(self, pin_id: UUID | str) -> None:
        await self._request("DELETE", "/v1/pins/{pin_id}", path_params={"pin_id": pin_id})


class AsyncJobsResource(AsyncAPIResource):
    async def get(self, job_id: UUID | str) -> JobStatusResponse:
        response = await self._request("GET", "/v1/jobs/{job_id}", path_params={"job_id": job_id})
        return self._model(JobStatusResponse, response)
