"""Project/environment management models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from .base import PinbridgeModel
from .common import Plan, WorkspaceEnvironment


class OrganizationResponse(PinbridgeModel):
    id: UUID
    name: str


class ProjectResponse(PinbridgeModel):
    id: UUID
    name: str
    environment: WorkspaceEnvironment
    plan: Plan
    created_at: datetime


class ProjectsContextResponse(PinbridgeModel):
    organization: OrganizationResponse
    active_project: ProjectResponse
    projects: list[ProjectResponse]


class CreateSandboxProjectRequest(PinbridgeModel):
    name: str | None = None


class SwitchProjectRequest(PinbridgeModel):
    project_id: UUID


class ProjectSwitchResponse(ProjectsContextResponse):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
