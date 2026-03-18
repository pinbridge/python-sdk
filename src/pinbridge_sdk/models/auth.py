"""Auth request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import StringConstraints, field_validator

from .base import PinbridgeModel
from .common import Plan, WorkspaceEnvironment

EmailValue = Annotated[str, StringConstraints(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
PasswordValue = Annotated[str, StringConstraints(min_length=8, max_length=255)]
TokenValue = Annotated[str, StringConstraints(min_length=20, max_length=512)]
FullName255 = Annotated[str, StringConstraints(min_length=1, max_length=255)]
Name255 = Annotated[str, StringConstraints(max_length=255)]
Phone50 = Annotated[str, StringConstraints(max_length=50)]
TaxId100 = Annotated[str, StringConstraints(max_length=100)]
Address120 = Annotated[str, StringConstraints(max_length=120)]
Postal40 = Annotated[str, StringConstraints(max_length=40)]
Country10 = Annotated[str, StringConstraints(max_length=10)]
Timezone64 = Annotated[str, StringConstraints(max_length=64)]


def _normalize_timezone(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    try:
        ZoneInfo(normalized)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("Timezone must be a valid IANA timezone") from exc
    return normalized


class RegisterRequest(PinbridgeModel):
    full_name: FullName255
    email: EmailValue
    password: PasswordValue
    workspace_name: Name255 | None = None
    timezone: Timezone64 | None = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Full name is required")
        return normalized

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str | None) -> str | None:
        return _normalize_timezone(value)


class LoginRequest(PinbridgeModel):
    email: EmailValue
    password: PasswordValue
    timezone: Timezone64 | None = None

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str | None) -> str | None:
        return _normalize_timezone(value)


class ForgotPasswordRequest(PinbridgeModel):
    email: EmailValue


class ResetPasswordRequest(PinbridgeModel):
    token: TokenValue
    password: PasswordValue


class ChangePasswordRequest(PinbridgeModel):
    current_password: PasswordValue
    new_password: PasswordValue


class PasswordResetActionResponse(PinbridgeModel):
    message: str


class EmailVerificationActionResponse(PinbridgeModel):
    message: str
    retry_after_seconds: int | None = None


class AuthUserResponse(PinbridgeModel):
    id: UUID
    email: EmailValue
    full_name: str | None = None
    timezone: str
    email_verified: bool
    created_at: datetime


class AuthWorkspaceResponse(PinbridgeModel):
    id: UUID
    name: str
    environment: WorkspaceEnvironment
    timezone: str
    plan: Plan


class AuthOrganizationResponse(PinbridgeModel):
    id: UUID
    name: str


class AuthResponse(PinbridgeModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserResponse
    organization: AuthOrganizationResponse
    active_project: AuthWorkspaceResponse
    projects: list[AuthWorkspaceResponse]
    workspace: AuthWorkspaceResponse


class MeResponse(PinbridgeModel):
    user: AuthUserResponse
    organization: AuthOrganizationResponse
    active_project: AuthWorkspaceResponse
    projects: list[AuthWorkspaceResponse]
    workspace: AuthWorkspaceResponse


class PrimaryEmailChangeRequest(PinbridgeModel):
    new_email: EmailValue


class PrimaryEmailChangeRequestResponse(PinbridgeModel):
    message: str
    pending_email: EmailValue
    requested_at: datetime
    retry_after_seconds: int | None = None


class PrimaryEmailChangeActionResponse(PinbridgeModel):
    message: str
    new_email: EmailValue
    requires_reauthentication: bool = False


class ProfileResponse(PinbridgeModel):
    full_name: str | None = None
    email: EmailValue
    pending_email_change_to: EmailValue | None = None
    pending_email_change_requested_at: datetime | None = None
    workspace_name: str
    company_name: str | None = None
    company_website: str | None = None
    billing_email: EmailValue | None = None
    billing_phone: str | None = None
    tax_id: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_postal_code: str | None = None
    address_country: str | None = None


class ProfileUpdateRequest(PinbridgeModel):
    full_name: Name255 | None = None
    workspace_name: Name255 | None = None
    company_name: Name255 | None = None
    company_website: Name255 | None = None
    billing_email: EmailValue | None = None
    billing_phone: Phone50 | None = None
    tax_id: TaxId100 | None = None
    address_line1: Name255 | None = None
    address_line2: Name255 | None = None
    address_city: Address120 | None = None
    address_state: Address120 | None = None
    address_postal_code: Postal40 | None = None
    address_country: Country10 | None = None
