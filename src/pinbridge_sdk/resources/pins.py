"""Pin and job resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from ..models.pins import JobStatusResponse, PinCreate, PinResponse
from .base import AsyncAPIResource, SyncAPIResource


class PinsResource(SyncAPIResource):
    def create(self, data: PinCreate | Mapping[str, Any]) -> PinResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, PinCreate)
            else dict(data)
        )
        response = self._request("POST", "/v1/pins", json=payload)
        return self._model(PinResponse, response)

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
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, PinCreate)
            else dict(data)
        )
        response = await self._request("POST", "/v1/pins", json=payload)
        return self._model(PinResponse, response)

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
