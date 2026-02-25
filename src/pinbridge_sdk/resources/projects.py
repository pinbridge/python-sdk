"""Projects API resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models.projects import (
    CreateSandboxProjectRequest,
    ProjectsContextResponse,
    ProjectSwitchResponse,
    SwitchProjectRequest,
)
from .base import AsyncAPIResource, SyncAPIResource


class ProjectsResource(SyncAPIResource):
    def list(self) -> ProjectsContextResponse:
        response = self._request("GET", "/v1/projects")
        return self._model(ProjectsContextResponse, response)

    def create_sandbox(
        self,
        data: CreateSandboxProjectRequest | Mapping[str, Any] | None = None,
    ) -> ProjectsContextResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, CreateSandboxProjectRequest)
            else dict(data) if data is not None else {}
        )
        response = self._request("POST", "/v1/projects/sandbox", json=payload)
        return self._model(ProjectsContextResponse, response)

    def switch(self, data: SwitchProjectRequest | Mapping[str, Any]) -> ProjectSwitchResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, SwitchProjectRequest)
            else dict(data)
        )
        response = self._request("POST", "/v1/projects/switch", json=payload)
        return self._model(ProjectSwitchResponse, response)


class AsyncProjectsResource(AsyncAPIResource):
    async def list(self) -> ProjectsContextResponse:
        response = await self._request("GET", "/v1/projects")
        return self._model(ProjectsContextResponse, response)

    async def create_sandbox(
        self,
        data: CreateSandboxProjectRequest | Mapping[str, Any] | None = None,
    ) -> ProjectsContextResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, CreateSandboxProjectRequest)
            else dict(data) if data is not None else {}
        )
        response = await self._request("POST", "/v1/projects/sandbox", json=payload)
        return self._model(ProjectsContextResponse, response)

    async def switch(self, data: SwitchProjectRequest | Mapping[str, Any]) -> ProjectSwitchResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, SwitchProjectRequest)
            else dict(data)
        )
        response = await self._request("POST", "/v1/projects/switch", json=payload)
        return self._model(ProjectSwitchResponse, response)
