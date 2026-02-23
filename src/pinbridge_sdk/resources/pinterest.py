"""Pinterest integration resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

import httpx

from ..models.pinterest import (
    BoardCreateRequest,
    BoardResponse,
    OAuthCallbackResponse,
    OAuthStartResponse,
    PinterestAccountResponse,
)
from .base import AsyncAPIResource, SyncAPIResource


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
