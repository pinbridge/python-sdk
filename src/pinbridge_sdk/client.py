"""Synchronous PinBridge API client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from ._client_base import ClientCore
from ._types import HeadersLike, PathValue, RequestData, RequestFiles, RequestJson
from ._version import __version__
from .errors import map_api_error
from .resources import (
    ActivityLogsResource,
    APIKeysResource,
    AssetsResource,
    AuthResource,
    BillingResource,
    JobsResource,
    PinsResource,
    PinterestResource,
    ProjectsResource,
    RateMeterResource,
    SchedulesResource,
    SystemResource,
    WebhooksResource,
)
from .resources.base import SyncAPIResource

ResourceClass = type[SyncAPIResource]


class PinbridgeClient:
    """Synchronous client for PinBridge APIs."""

    DEFAULT_BASE_URL = "https://api.pinbridge.io"
    DEFAULT_TIMEOUT = 30.0

    _builtin_resource_classes: dict[str, ResourceClass] = {
        "activity_logs": ActivityLogsResource,
        "system": SystemResource,
        "auth": AuthResource,
        "api_keys": APIKeysResource,
        "assets": AssetsResource,
        "pinterest": PinterestResource,
        "projects": ProjectsResource,
        "pins": PinsResource,
        "schedules": SchedulesResource,
        "webhooks": WebhooksResource,
        "rate_meter": RateMeterResource,
        "jobs": JobsResource,
        "billing": BillingResource,
    }

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        bearer_token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        headers: HeadersLike | None = None,
        follow_redirects: bool = False,
        user_agent: str = f"pinbridge-python-sdk/{__version__}",
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if http_client is not None and transport is not None:
            raise ValueError("Provide either http_client or transport, not both.")

        self._core = ClientCore(
            base_url=base_url,
            api_key=api_key,
            bearer_token=bearer_token,
            default_headers=headers,
            follow_redirects=follow_redirects,
            user_agent=user_agent,
        )
        self._owns_http_client = http_client is None
        self._http = http_client or httpx.Client(timeout=timeout, transport=transport)
        self._resource_classes: dict[str, ResourceClass] = dict(self._builtin_resource_classes)
        self._resources: dict[str, SyncAPIResource] = {}
        self._bind_all_resources()

    def _bind_all_resources(self) -> None:
        for name, resource_cls in self._resource_classes.items():
            self._bind_resource(name, resource_cls)

    def _bind_resource(self, name: str, resource_cls: ResourceClass) -> SyncAPIResource:
        resource = resource_cls(self)
        self._resources[name] = resource
        setattr(self, name, resource)
        return resource

    def register_resource(
        self, name: str, resource_cls: ResourceClass, *, replace: bool = False
    ) -> None:
        """Register a custom resource group on this client instance."""
        if not replace and name in self._resource_classes:
            raise ValueError(f"Resource '{name}' is already registered.")
        self._resource_classes[name] = resource_cls
        self._bind_resource(name, resource_cls)

    def resource(self, name: str) -> SyncAPIResource:
        return self._resources[name]

    def request(
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
        url = self._core.build_url(path, path_params)
        response = self._http.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            files=files,
            content=content,
            headers=self._core.build_headers(headers),
            follow_redirects=(
                self._core.follow_redirects if follow_redirects is None else follow_redirects
            ),
        )
        if response.status_code >= 400:
            raise map_api_error(response)
        return response

    def set_api_key(self, api_key: str | None) -> None:
        self._core.set_api_key(api_key)

    def set_bearer_token(self, token: str | None) -> None:
        self._core.set_bearer_token(token)

    def clear_auth(self) -> None:
        self._core.clear_auth()

    def close(self) -> None:
        if self._owns_http_client:
            self._http.close()

    def __enter__(self) -> PinbridgeClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()

    def with_options(
        self,
        *,
        api_key: str | None = None,
        bearer_token: str | None = None,
        headers: HeadersLike | None = None,
        follow_redirects: bool | None = None,
    ) -> PinbridgeClient:
        """Create a derived client with overridden request options."""
        merged_headers = dict(self._core._default_headers)
        if headers:
            merged_headers.update(headers)

        cloned = PinbridgeClient(
            base_url=self._core.base_url,
            api_key=api_key if api_key is not None else self._core._api_key,
            bearer_token=bearer_token if bearer_token is not None else self._core._bearer_token,
            headers=merged_headers,
            follow_redirects=(
                self._core.follow_redirects if follow_redirects is None else follow_redirects
            ),
            user_agent=self._core.user_agent,
            http_client=self._http,
        )
        for name, resource_cls in self._resource_classes.items():
            if cloned._resource_classes.get(name) is not resource_cls:
                cloned.register_resource(name, resource_cls, replace=True)
        return cloned
