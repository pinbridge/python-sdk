"""Auth request/response models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from .base import PinbridgeModel
from .common import Plan, WorkspaceEnvironment


class RegisterRequest(PinbridgeModel):
    email: str
    password: str
    workspace_name: str | None = None


class LoginRequest(PinbridgeModel):
    email: str
    password: str


class AuthUserResponse(PinbridgeModel):
    id: UUID
    email: str
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
    email: str
    workspace_name: str
    company_name: str | None = None
    company_website: str | None = None
    billing_email: str | None = None
    billing_phone: str | None = None
    tax_id: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_postal_code: str | None = None
    address_country: str | None = None


class ProfileUpdateRequest(PinbridgeModel):
    full_name: str | None = None
    workspace_name: str | None = None
    company_name: str | None = None
    company_website: str | None = None
    billing_email: str | None = None
    billing_phone: str | None = None
    tax_id: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_postal_code: str | None = None
    address_country: str | None = None
