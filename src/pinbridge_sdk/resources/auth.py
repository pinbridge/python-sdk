"""Auth API resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models.auth import (
    AuthResponse,
    LoginRequest,
    MeResponse,
    ProfileResponse,
    ProfileUpdateRequest,
    RegisterRequest,
)
from .base import AsyncAPIResource, SyncAPIResource


class AuthResource(SyncAPIResource):
    def register(self, data: RegisterRequest | Mapping[str, Any]) -> AuthResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, RegisterRequest)
            else dict(data)
        )
        response = self._request("POST", "/v1/auth/register", json=payload)
        return self._model(AuthResponse, response)

    def login(self, data: LoginRequest | Mapping[str, Any]) -> AuthResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, LoginRequest)
            else dict(data)
        )
        response = self._request("POST", "/v1/auth/login", json=payload)
        return self._model(AuthResponse, response)

    def me(self) -> MeResponse:
        response = self._request("GET", "/v1/auth/me")
        return self._model(MeResponse, response)

    def get_profile(self) -> ProfileResponse:
        response = self._request("GET", "/v1/auth/profile")
        return self._model(ProfileResponse, response)

    def update_profile(self, data: ProfileUpdateRequest | Mapping[str, Any]) -> ProfileResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, ProfileUpdateRequest)
            else {k: v for k, v in dict(data).items() if v is not None}
        )
        response = self._request("PUT", "/v1/auth/profile", json=payload)
        return self._model(ProfileResponse, response)


class AsyncAuthResource(AsyncAPIResource):
    async def register(self, data: RegisterRequest | Mapping[str, Any]) -> AuthResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, RegisterRequest)
            else dict(data)
        )
        response = await self._request("POST", "/v1/auth/register", json=payload)
        return self._model(AuthResponse, response)

    async def login(self, data: LoginRequest | Mapping[str, Any]) -> AuthResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, LoginRequest)
            else dict(data)
        )
        response = await self._request("POST", "/v1/auth/login", json=payload)
        return self._model(AuthResponse, response)

    async def me(self) -> MeResponse:
        response = await self._request("GET", "/v1/auth/me")
        return self._model(MeResponse, response)

    async def get_profile(self) -> ProfileResponse:
        response = await self._request("GET", "/v1/auth/profile")
        return self._model(ProfileResponse, response)

    async def update_profile(
        self, data: ProfileUpdateRequest | Mapping[str, Any]
    ) -> ProfileResponse:
        payload = (
            data.model_dump(mode="json", exclude_none=True)
            if isinstance(data, ProfileUpdateRequest)
            else {k: v for k, v in dict(data).items() if v is not None}
        )
        response = await self._request("PUT", "/v1/auth/profile", json=payload)
        return self._model(ProfileResponse, response)
