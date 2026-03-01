"""Project/environment management models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import StringConstraints

from .base import PinbridgeModel
from .common import Plan, WorkspaceEnvironment

ProjectName = Annotated[str, StringConstraints(max_length=255)]


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
    name: ProjectName | None = None


class SwitchProjectRequest(PinbridgeModel):
    project_id: UUID


class ProjectSwitchResponse(ProjectsContextResponse):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
