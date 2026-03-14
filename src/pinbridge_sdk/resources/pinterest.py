"""Pinterest integration resources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

import httpx

from ..models.pinterest import (
    BoardCreateRequest,
    BoardResponse,
    OAuthCallbackResponse,
    OAuthStartResponse,
    PinterestAccountResponse,
    RelatedTermsResponse,
)
from .base import AsyncAPIResource, SyncAPIResource


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

    async def delete_board(self, board_id: str, *, account_id: UUID | str) -> None:
        await self._request(
            "DELETE",
            "/v1/pinterest/boards/{board_id}",
            path_params={"board_id": board_id},
            params={"account_id": str(account_id)},
        )
