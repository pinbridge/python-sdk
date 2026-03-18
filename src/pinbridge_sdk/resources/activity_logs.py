"""Activity log resources."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..models.activity_logs import (
    ActivityLogCategory,
    ActivityLogListResponse,
    ActivityLogStatus,
)
from .base import AsyncAPIResource, SyncAPIResource


class ActivityLogsResource(SyncAPIResource):
    def list(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        category: ActivityLogCategory | None = None,
        action: str | None = None,
        status: ActivityLogStatus | None = None,
        resource_type: str | None = None,
        since: datetime | None = None,
    ) -> ActivityLogListResponse:
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if category is not None:
            params["category"] = category.value
        if action is not None:
            params["action"] = action
        if status is not None:
            params["status"] = status.value
        if resource_type is not None:
            params["resource_type"] = resource_type
        if since is not None:
            params["since"] = since.isoformat()
        response = self._request("GET", "/v1/activity-logs", params=params)
        return self._model(ActivityLogListResponse, response)


class AsyncActivityLogsResource(AsyncAPIResource):
    async def list(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        category: ActivityLogCategory | None = None,
        action: str | None = None,
        status: ActivityLogStatus | None = None,
        resource_type: str | None = None,
        since: datetime | None = None,
    ) -> ActivityLogListResponse:
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if category is not None:
            params["category"] = category.value
        if action is not None:
            params["action"] = action
        if status is not None:
            params["status"] = status.value
        if resource_type is not None:
            params["resource_type"] = resource_type
        if since is not None:
            params["since"] = since.isoformat()
        response = await self._request("GET", "/v1/activity-logs", params=params)
        return self._model(ActivityLogListResponse, response)
