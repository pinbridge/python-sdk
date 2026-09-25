"""Pinterest integration resources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any
from uuid import UUID

import httpx

from ..models.pins import AnalyticsSource
from ..models.pinterest import (
    AccountAnalyticsResponse,
    BoardAccessResponse,
    BoardCreateRequest,
    BoardResponse,
    BoardUpdateRequest,
    OAuthCallbackResponse,
    OAuthStartResponse,
    PinterestAccountResponse,
    RelatedTermsResponse,
)
from .base import AsyncAPIResource, SyncAPIResource
from .pins import _serialize_analytics_params


def _normalize_terms_input(terms: str | Sequence[str]) -> list[str]:
    normalized_terms: list[str] = []
    seen: set[str] = set()

    raw_values = [terms] if isinstance(terms, str) else list(terms)
    for raw_value in raw_values:
        for segment in raw_value.split(","):
            cleaned = " ".join(segment.strip().split())
            if not cleaned:
                continue
            dedupe_key = cleaned.casefold()
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            normalized_terms.append(cleaned)

    if not normalized_terms:
        raise ValueError("At least one terms value is required")

    return normalized_terms


class PinterestResource(SyncAPIResource):
    def start_oauth(self) -> OAuthStartResponse:
        response = self._request("GET", "/v1/pinterest/oauth/start")
        return self._model(OAuthStartResponse, response)

    def oauth_callback(
        self,
        *,
        code: str,
        state: str,
        follow_redirects: bool = False,
    ) -> OAuthCallbackResponse | httpx.Response:
        response = self._request(
            "GET",
            "/v1/pinterest/oauth/callback",
            params={"code": code, "state": state},
            follow_redirects=follow_redirects,
        )
        if response.is_redirect:
            return response
        if not response.content:
            return response
        return OAuthCallbackResponse.model_validate(response.json())

    def list_accounts(self) -> list[PinterestAccountResponse]:
        response = self._request("GET", "/v1/pinterest/accounts")
        return self._list(PinterestAccountResponse, response)

    def revoke_account(self, account_id: UUID | str) -> None:
        self._request(
            "DELETE",
            "/v1/pinterest/accounts/{account_id}",
            path_params={"account_id": account_id},
        )

    def list_boards(self, account_id: UUID | str) -> list[BoardResponse]:
        response = self._request(
            "GET", "/v1/pinterest/boards", params={"account_id": str(account_id)}
        )
        return self._list(BoardResponse, response)

    def check_board_access(
        self, board_id: str, *, account_id: UUID | str, fresh: bool = False
    ) -> BoardAccessResponse:
        """Report whether an account can publish to a board and why not."""
        response = self._request(
            "GET",
            "/v1/pinterest/boards/{board_id}/access",
            path_params={"board_id": board_id},
            params={"account_id": str(account_id), "fresh": fresh},
        )
        return self._model(BoardAccessResponse, response)

    def account_analytics(
        self,
        account_id: UUID | str,
        *,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        metrics: Sequence[str] | str | None = None,
        source: AnalyticsSource | None = None,
    ) -> AccountAnalyticsResponse:
        """Pinterest analytics for a whole connected account over a date range.

        ``source`` (API 1.33.0+): ``auto`` (default), ``stored`` (up to 366 days) or
        ``live`` (up to 90 days).
        """
        response = self._request(
            "GET",
            "/v1/pinterest/accounts/{account_id}/analytics",
            path_params={"account_id": account_id},
            params=_serialize_analytics_params(
                start_date=start_date, end_date=end_date, metrics=metrics, source=source
            ),
        )
        return self._model(AccountAnalyticsResponse, response)

    def list_related_terms(
        self,
        account_id: UUID | str,
        terms: str | Sequence[str],
        *,
        exact_match: bool = False,
    ) -> RelatedTermsResponse:
        response = self._request(
            "GET",
            "/v1/pinterest/terms/related",
            params={
                "account_id": str(account_id),
                "terms": _normalize_terms_input(terms),
                "exact_match": exact_match,
            },
        )
        return self._model(RelatedTermsResponse, response)

    def create_board(self, data: BoardCreateRequest | Mapping[str, Any]) -> BoardResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, BoardCreateRequest)
            else dict(data)
        )
        response = self._request("POST", "/v1/pinterest/boards", json=payload)
        return self._model(BoardResponse, response)

    def update_board(
        self, board_id: str, data: BoardUpdateRequest | Mapping[str, Any]
    ) -> BoardResponse:
        """Rename a board or change its description/privacy on Pinterest."""
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, BoardUpdateRequest)
            else dict(data)
        )
        response = self._request(
            "PATCH",
            "/v1/pinterest/boards/{board_id}",
            path_params={"board_id": board_id},
            json=payload,
        )
        return self._model(BoardResponse, response)

    def delete_board(self, board_id: str, *, account_id: UUID | str) -> None:
        self._request(
            "DELETE",
            "/v1/pinterest/boards/{board_id}",
            path_params={"board_id": board_id},
            params={"account_id": str(account_id)},
        )


class AsyncPinterestResource(AsyncAPIResource):
    async def start_oauth(self) -> OAuthStartResponse:
        response = await self._request("GET", "/v1/pinterest/oauth/start")
        return self._model(OAuthStartResponse, response)

    async def oauth_callback(
        self,
        *,
        code: str,
        state: str,
        follow_redirects: bool = False,
    ) -> OAuthCallbackResponse | httpx.Response:
        response = await self._request(
            "GET",
            "/v1/pinterest/oauth/callback",
            params={"code": code, "state": state},
            follow_redirects=follow_redirects,
        )
        if response.is_redirect:
            return response
        if not response.content:
            return response
        return OAuthCallbackResponse.model_validate(response.json())

    async def list_accounts(self) -> list[PinterestAccountResponse]:
        response = await self._request("GET", "/v1/pinterest/accounts")
        return self._list(PinterestAccountResponse, response)

    async def revoke_account(self, account_id: UUID | str) -> None:
        await self._request(
            "DELETE",
            "/v1/pinterest/accounts/{account_id}",
            path_params={"account_id": account_id},
        )

    async def list_boards(self, account_id: UUID | str) -> list[BoardResponse]:
        response = await self._request(
            "GET",
            "/v1/pinterest/boards",
            params={"account_id": str(account_id)},
        )
        return self._list(BoardResponse, response)

    async def check_board_access(
        self, board_id: str, *, account_id: UUID | str, fresh: bool = False
    ) -> BoardAccessResponse:
        """Report whether an account can publish to a board and why not."""
        response = await self._request(
            "GET",
            "/v1/pinterest/boards/{board_id}/access",
            path_params={"board_id": board_id},
            params={"account_id": str(account_id), "fresh": fresh},
        )
        return self._model(BoardAccessResponse, response)

    async def account_analytics(
        self,
        account_id: UUID | str,
        *,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        metrics: Sequence[str] | str | None = None,
        source: AnalyticsSource | None = None,
    ) -> AccountAnalyticsResponse:
        """Pinterest analytics for a whole connected account over a date range.

        ``source`` (API 1.33.0+): ``auto`` (default), ``stored`` (up to 366 days) or
        ``live`` (up to 90 days).
        """
        response = await self._request(
            "GET",
            "/v1/pinterest/accounts/{account_id}/analytics",
            path_params={"account_id": account_id},
            params=_serialize_analytics_params(
                start_date=start_date, end_date=end_date, metrics=metrics, source=source
            ),
        )
        return self._model(AccountAnalyticsResponse, response)

    async def list_related_terms(
        self,
        account_id: UUID | str,
        terms: str | Sequence[str],
        *,
        exact_match: bool = False,
    ) -> RelatedTermsResponse:
        response = await self._request(
            "GET",
            "/v1/pinterest/terms/related",
            params={
                "account_id": str(account_id),
                "terms": _normalize_terms_input(terms),
                "exact_match": exact_match,
            },
        )
        return self._model(RelatedTermsResponse, response)

    async def create_board(self, data: BoardCreateRequest | Mapping[str, Any]) -> BoardResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, BoardCreateRequest)
            else dict(data)
        )
        response = await self._request("POST", "/v1/pinterest/boards", json=payload)
        return self._model(BoardResponse, response)

    async def update_board(
        self, board_id: str, data: BoardUpdateRequest | Mapping[str, Any]
    ) -> BoardResponse:
        """Rename a board or change its description/privacy on Pinterest."""
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, BoardUpdateRequest)
            else dict(data)
        )
        response = await self._request(
            "PATCH",
            "/v1/pinterest/boards/{board_id}",
            path_params={"board_id": board_id},
            json=payload,
        )
        return self._model(BoardResponse, response)

    async def delete_board(self, board_id: str, *, account_id: UUID | str) -> None:
        await self._request(
            "DELETE",
            "/v1/pinterest/boards/{board_id}",
            path_params={"board_id": board_id},
            params={"account_id": str(account_id)},
        )
