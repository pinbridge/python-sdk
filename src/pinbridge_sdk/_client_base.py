"""Shared internals for sync and async API clients."""

from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urljoin

import httpx

from ._types import HeadersLike, PathValue

# Drawing a pin from a template can take the API up to a minute (the wait for a free
# renderer included) plus the photo downloads, longer than the client's 30 s default.
TEMPLATE_DRAW_TIMEOUT_SECONDS = 90.0


def template_draw_timeout(current: httpx.Timeout) -> httpx.Timeout:
    """The client's timeout, with a read timeout of at least 90 seconds.

    A read timeout the caller set longer, or turned off, is kept.
    """
    read = current.read
    if read is not None:
        read = max(read, TEMPLATE_DRAW_TIMEOUT_SECONDS)
    return httpx.Timeout(connect=current.connect, read=read, write=current.write, pool=current.pool)


class ClientCore:
    """Shared state and helpers for request building."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None,
        bearer_token: str | None,
        default_headers: HeadersLike | None,
        follow_redirects: bool,
        user_agent: str,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._bearer_token = bearer_token
        self._default_headers = dict(default_headers or {})
        self.follow_redirects = follow_redirects
        self.user_agent = user_agent

    def set_api_key(self, api_key: str | None) -> None:
        self._api_key = api_key

    def set_bearer_token(self, token: str | None) -> None:
        self._bearer_token = token

    def clear_auth(self) -> None:
        self._api_key = None
        self._bearer_token = None

    def auth_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._api_key:
            headers["x-api-key"] = self._api_key
        if self._bearer_token:
            headers["authorization"] = f"Bearer {self._bearer_token}"
        return headers

    def build_headers(self, headers: HeadersLike | None = None) -> dict[str, str]:
        merged = {
            "accept": "application/json",
            "user-agent": self.user_agent,
            **self._default_headers,
            **self.auth_headers(),
        }
        if headers:
            merged.update(headers)
        return merged

    def build_url(self, path: str, path_params: Mapping[str, PathValue] | None = None) -> str:
        if path_params:
            serialized_params = {key: str(value) for key, value in path_params.items()}
            path = path.format(**serialized_params)

        if path.startswith("http://") or path.startswith("https://"):
            return path

        normalized_path = path if path.startswith("/") else f"/{path}"
        return urljoin(f"{self.base_url}/", normalized_path.lstrip("/"))
