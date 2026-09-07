"""Team invitation and membership models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints, field_validator

from .auth import (
    AuthOrganizationResponse,
    AuthOrganizationSessionResponse,
    AuthPermissionResponse,
    AuthUserResponse,
    AuthWorkspaceResponse,
    EmailValue,
)
from .base import PinbridgeModel

TeamRole = Annotated[str, StringConstraints(min_length=4, max_length=32)]
InvitationToken = Annotated[str, StringConstraints(min_length=20, max_length=512)]


class TeamInvitationCreateRequest(PinbridgeModel):
    email: EmailValue
    role: TeamRole

    @field_validator("role")
    @classmethod
    def normalize_role(cls, value: str) -> str:
        return value.strip().lower()


class TeamMemberUpdateRequest(PinbridgeModel):
    role: TeamRole

    @field_validator("role")
    @classmethod
    def normalize_role(cls, value: str) -> str:
        return value.strip().lower()


class TeamInvitationAcceptRequest(PinbridgeModel):
    token: InvitationToken

    @field_validator("token")
    @classmethod
    def normalize_token(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Invitation token is required")
        return normalized


class TeamInvitationPreviewResponse(PinbridgeModel):
    organization_id: UUID
    organization_name: str
    email: EmailValue
    role: str
    status: str
    expires_at: datetime
    inviter_name: str | None = None
    inviter_email: EmailValue | None = None
    team_access_enabled: bool


class TeamMemberResponse(PinbridgeModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    invited_by_user_id: UUID | None = None
    accepted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    user: AuthUserResponse
    invited_by: AuthUserResponse | None = None


class TeamMembersListResponse(PinbridgeModel):
    items: list[TeamMemberResponse]


class TeamInvitationResponse(PinbridgeModel):
    id: UUID
    organization_id: UUID
    email: EmailValue
    role: str
    invited_by_user_id: UUID | None = None
    expires_at: datetime
    accepted_at: datetime | None = None
    revoked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    inviter_name: str | None = None
    inviter_email: EmailValue | None = None


class TeamInvitationsListResponse(PinbridgeModel):
    items: list[TeamInvitationResponse]


class TeamActionResponse(PinbridgeModel):
    message: str


class TeamInvitationAcceptResponse(PinbridgeModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserResponse
    organization: AuthOrganizationResponse
    organization_role: str
    permissions: AuthPermissionResponse
    active_project: AuthWorkspaceResponse
    projects: list[AuthWorkspaceResponse]
    available_organizations: list[AuthOrganizationSessionResponse]
    workspace: AuthWorkspaceResponse
