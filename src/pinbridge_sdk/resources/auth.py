"""Auth API resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models.auth import (
    AuthResponse,
    ChangePasswordRequest,
    EmailVerificationActionResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MeResponse,
    PasswordResetActionResponse,
    PrimaryEmailChangeActionResponse,
    PrimaryEmailChangeRequest,
    PrimaryEmailChangeRequestResponse,
    ProfileResponse,
    ProfileUpdateRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from .base import AsyncAPIResource, SyncAPIResource


def _serialize_payload(data: Mapping[str, Any] | object) -> dict[str, Any]:
    if hasattr(data, "model_dump"):
        model_dump = data.model_dump
        return model_dump(mode="json", exclude_none=True)
    return dict(data)


class AuthResource(SyncAPIResource):
    def register(self, data: RegisterRequest | Mapping[str, Any]) -> AuthResponse:
        payload = _serialize_payload(data)
        response = self._request("POST", "/v1/auth/register", json=payload)
        return self._model(AuthResponse, response)

    def login(self, data: LoginRequest | Mapping[str, Any]) -> AuthResponse:
        payload = _serialize_payload(data)
        response = self._request("POST", "/v1/auth/login", json=payload)
        return self._model(AuthResponse, response)

    def forgot_password(
        self,
        data: ForgotPasswordRequest | Mapping[str, Any],
    ) -> PasswordResetActionResponse:
        payload = _serialize_payload(data)
        response = self._request("POST", "/v1/auth/forgot-password", json=payload)
        return self._model(PasswordResetActionResponse, response)

    def reset_password(
        self,
        data: ResetPasswordRequest | Mapping[str, Any],
    ) -> PasswordResetActionResponse:
        payload = _serialize_payload(data)
        response = self._request("POST", "/v1/auth/reset-password", json=payload)
        return self._model(PasswordResetActionResponse, response)

    def change_password(
        self,
        data: ChangePasswordRequest | Mapping[str, Any],
    ) -> PasswordResetActionResponse:
        payload = _serialize_payload(data)
        response = self._request("POST", "/v1/auth/change-password", json=payload)
        return self._model(PasswordResetActionResponse, response)

    def request_email_verification(self) -> EmailVerificationActionResponse:
        response = self._request("POST", "/v1/auth/email/verify/request")
        return self._model(EmailVerificationActionResponse, response)

    def verify_email(self, token: str) -> EmailVerificationActionResponse:
        response = self._request("GET", "/v1/auth/email/verify", params={"token": token})
        return self._model(EmailVerificationActionResponse, response)

    def request_email_change(
        self, data: PrimaryEmailChangeRequest | Mapping[str, Any]
    ) -> PrimaryEmailChangeRequestResponse:
        payload = _serialize_payload(data)
        response = self._request("POST", "/v1/auth/email/change/request", json=payload)
        return self._model(PrimaryEmailChangeRequestResponse, response)

    def confirm_email_change(self, token: str) -> PrimaryEmailChangeActionResponse:
        response = self._request("GET", "/v1/auth/email/change/confirm", params={"token": token})
        return self._model(PrimaryEmailChangeActionResponse, response)

    def me(self) -> MeResponse:
        response = self._request("GET", "/v1/auth/me")
        return self._model(MeResponse, response)

    def get_profile(self) -> ProfileResponse:
        response = self._request("GET", "/v1/auth/profile")
        return self._model(ProfileResponse, response)

    def update_profile(self, data: ProfileUpdateRequest | Mapping[str, Any]) -> ProfileResponse:
        payload = _serialize_payload(data)
        payload = {k: v for k, v in payload.items() if v is not None}
        response = self._request("PUT", "/v1/auth/profile", json=payload)
        return self._model(ProfileResponse, response)


class AsyncAuthResource(AsyncAPIResource):
    async def register(self, data: RegisterRequest | Mapping[str, Any]) -> AuthResponse:
        payload = _serialize_payload(data)
        response = await self._request("POST", "/v1/auth/register", json=payload)
        return self._model(AuthResponse, response)

    async def login(self, data: LoginRequest | Mapping[str, Any]) -> AuthResponse:
        payload = _serialize_payload(data)
        response = await self._request("POST", "/v1/auth/login", json=payload)
        return self._model(AuthResponse, response)

    async def forgot_password(
        self,
        data: ForgotPasswordRequest | Mapping[str, Any],
    ) -> PasswordResetActionResponse:
        payload = _serialize_payload(data)
        response = await self._request("POST", "/v1/auth/forgot-password", json=payload)
        return self._model(PasswordResetActionResponse, response)

    async def reset_password(
        self,
        data: ResetPasswordRequest | Mapping[str, Any],
    ) -> PasswordResetActionResponse:
        payload = _serialize_payload(data)
        response = await self._request("POST", "/v1/auth/reset-password", json=payload)
        return self._model(PasswordResetActionResponse, response)

    async def change_password(
        self,
        data: ChangePasswordRequest | Mapping[str, Any],
    ) -> PasswordResetActionResponse:
        payload = _serialize_payload(data)
        response = await self._request("POST", "/v1/auth/change-password", json=payload)
        return self._model(PasswordResetActionResponse, response)

    async def request_email_verification(self) -> EmailVerificationActionResponse:
        response = await self._request("POST", "/v1/auth/email/verify/request")
        return self._model(EmailVerificationActionResponse, response)

    async def verify_email(self, token: str) -> EmailVerificationActionResponse:
        response = await self._request("GET", "/v1/auth/email/verify", params={"token": token})
        return self._model(EmailVerificationActionResponse, response)

    async def request_email_change(
        self, data: PrimaryEmailChangeRequest | Mapping[str, Any]
    ) -> PrimaryEmailChangeRequestResponse:
        payload = _serialize_payload(data)
        response = await self._request("POST", "/v1/auth/email/change/request", json=payload)
        return self._model(PrimaryEmailChangeRequestResponse, response)

    async def confirm_email_change(self, token: str) -> PrimaryEmailChangeActionResponse:
        response = await self._request(
            "GET", "/v1/auth/email/change/confirm", params={"token": token}
        )
        return self._model(PrimaryEmailChangeActionResponse, response)

    async def me(self) -> MeResponse:
        response = await self._request("GET", "/v1/auth/me")
        return self._model(MeResponse, response)

    async def get_profile(self) -> ProfileResponse:
        response = await self._request("GET", "/v1/auth/profile")
        return self._model(ProfileResponse, response)

    async def update_profile(
        self, data: ProfileUpdateRequest | Mapping[str, Any]
    ) -> ProfileResponse:
        payload = _serialize_payload(data)
        payload = {k: v for k, v in payload.items() if v is not None}
        response = await self._request("PUT", "/v1/auth/profile", json=payload)
        return self._model(ProfileResponse, response)
