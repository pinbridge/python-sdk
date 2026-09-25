"""Base resource classes for sync and async clients."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

import httpx

from .._types import HeadersLike, PathValue, RequestData, RequestFiles, RequestJson
from ..models.base import PinbridgeModel
from ..models.pagination import Page

if TYPE_CHECKING:
    from ..async_client import AsyncPinbridgeClient
    from ..client import PinbridgeClient

ModelT = TypeVar("ModelT", bound=PinbridgeModel)

TOTAL_COUNT_HEADER = "X-Total-Count"


def _total_count(response: httpx.Response) -> int | None:
    raw = response.headers.get(TOTAL_COUNT_HEADER)
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


class SyncAPIResource:
    """Base class for synchronous resource groups."""

    def __init__(self, client: PinbridgeClient) -> None:
        self._client = client

    def _request(
        self,
        method: str,
        path: str,
        *,
        path_params: Mapping[str, PathValue] | None = None,
        params: Mapping[str, Any] | None = None,
        json: RequestJson | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        headers: HeadersLike | None = None,
        content: str | bytes | None = None,
        follow_redirects: bool | None = None,
    ) -> httpx.Response:
        return self._client.request(
            method,
            path,
            path_params=path_params,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
            content=content,
            follow_redirects=follow_redirects,
        )

    @staticmethod
    def _json(response: httpx.Response) -> Any:
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def _model(self, model: type[ModelT], response: httpx.Response) -> ModelT:
        data = self._json(response)
        return model.model_validate(data)

    def _list(self, model: type[ModelT], response: httpx.Response) -> list[ModelT]:
        data = self._json(response)
        if not isinstance(data, list):
            raise TypeError("Expected a list response payload.")
        return [model.model_validate(item) for item in data]

    def _page(
        self, model: type[ModelT], response: httpx.Response, *, limit: int, offset: int
    ) -> Page[ModelT]:
        return Page[model](  # type: ignore[valid-type]
            items=self._list(model, response),
            total=_total_count(response),
            limit=limit,
            offset=offset,
        )


class AsyncAPIResource:
    """Base class for asynchronous resource groups."""

    def __init__(self, client: AsyncPinbridgeClient) -> None:
        self._client = client

    async def _request(
        self,
        method: str,
        path: str,
        *,
        path_params: Mapping[str, PathValue] | None = None,
        params: Mapping[str, Any] | None = None,
        json: RequestJson | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        headers: HeadersLike | None = None,
        content: str | bytes | None = None,
        follow_redirects: bool | None = None,
    ) -> httpx.Response:
        return await self._client.request(
            method,
            path,
            path_params=path_params,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
            content=content,
            follow_redirects=follow_redirects,
        )

    @staticmethod
    def _json(response: httpx.Response) -> Any:
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def _model(self, model: type[ModelT], response: httpx.Response) -> ModelT:
        data = self._json(response)
        return model.model_validate(data)

    def _list(self, model: type[ModelT], response: httpx.Response) -> list[ModelT]:
        data = self._json(response)
        if not isinstance(data, list):
            raise TypeError("Expected a list response payload.")
        return [model.model_validate(item) for item in data]

    def _page(
        self, model: type[ModelT], response: httpx.Response, *, limit: int, offset: int
    ) -> Page[ModelT]:
        return Page[model](  # type: ignore[valid-type]
            items=self._list(model, response),
            total=_total_count(response),
            limit=limit,
            offset=offset,
        )
