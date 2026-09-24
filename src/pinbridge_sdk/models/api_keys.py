"""API key models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints, model_validator

from .base import PinbridgeModel

APIKeyName = Annotated[str, StringConstraints(max_length=255)]


class APIKeyScope(str, Enum):
    READ = "read"
    WRITE = "write"
    DESTRUCTIVE = "destructive"


class APIKeySource(str, Enum):
    MANUAL = "manual"
    OAUTH = "oauth"


class APIKeyCreate(PinbridgeModel):
    name: APIKeyName
    scopes: list[APIKeyScope] | None = None
    pinterest_account_ids: list[UUID] | None = None


class APIKeyUpdate(PinbridgeModel):
    """Partial update; fields left unset are unchanged. At least one is required."""

    name: APIKeyName | None = None
    scopes: list[APIKeyScope] | None = None
    pinterest_account_ids: list[UUID] | None = None

    @model_validator(mode="after")
    def require_a_change(self) -> APIKeyUpdate:
        if self.name is None and self.scopes is None and self.pinterest_account_ids is None:
            raise ValueError("Provide at least one of name, scopes or pinterest_account_ids")
        return self


class APIKeyResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    name: str
    scopes: list[APIKeyScope] = Field(default_factory=list)
    pinterest_account_ids: list[UUID] | None = None
    source: APIKeySource | None = None
    client_name: str | None = None
    authorized_by_email: str | None = None
    last_used_at: datetime | None = None
    created_at: datetime
    revoked_at: datetime | None = None


class APIKeyCreateResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    name: str
    api_key: str
    scopes: list[APIKeyScope] = Field(default_factory=list)
    pinterest_account_ids: list[UUID] | None = None
    created_at: datetime
