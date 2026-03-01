"""Auth request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints

from .base import PinbridgeModel
from .common import Plan, WorkspaceEnvironment

EmailValue = Annotated[str, StringConstraints(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
PasswordValue = Annotated[str, StringConstraints(min_length=8, max_length=255)]
Name255 = Annotated[str, StringConstraints(max_length=255)]
Phone50 = Annotated[str, StringConstraints(max_length=50)]
TaxId100 = Annotated[str, StringConstraints(max_length=100)]
Address120 = Annotated[str, StringConstraints(max_length=120)]
Postal40 = Annotated[str, StringConstraints(max_length=40)]
Country10 = Annotated[str, StringConstraints(max_length=10)]


class RegisterRequest(PinbridgeModel):
    email: EmailValue
    password: PasswordValue
    workspace_name: Name255 | None = None


class LoginRequest(PinbridgeModel):
    email: EmailValue
    password: PasswordValue


class AuthUserResponse(PinbridgeModel):
    id: UUID
    email: EmailValue
    full_name: str | None = None
    created_at: datetime


class AuthWorkspaceResponse(PinbridgeModel):
    id: UUID
    name: str
    environment: WorkspaceEnvironment
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


class ProfileResponse(PinbridgeModel):
    full_name: str | None = None
    email: EmailValue
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
