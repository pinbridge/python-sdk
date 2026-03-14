"""Pinterest integration models."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import HttpUrl, StringConstraints

from .base import PinbridgeModel

BoardName = Annotated[str, StringConstraints(min_length=1, max_length=180)]


class OAuthStartResponse(PinbridgeModel):
    authorization_url: HttpUrl


class OAuthCallbackResponse(PinbridgeModel):
    status: str
    message: str
    account_id: str | None = None


class PinterestAccountResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    pinterest_user_id: str
    display_name: str | None = None
    username: str | None = None
    scopes: str
    created_at: datetime
    updated_at: datetime
    revoked_at: datetime | None = None


class BoardResponse(PinbridgeModel):
    id: str
    name: str
    description: str | None = None
    privacy: str | None = None


class BoardCreateRequest(PinbridgeModel):
    account_id: UUID
    name: BoardName
    description: str | None = None
    privacy: str | None = None


class RelatedTermsItem(PinbridgeModel):
    term: str
    related_terms: list[str]


class RelatedTermsResponse(PinbridgeModel):
    id: str
    related_term_count: int
    related_terms_list: list[RelatedTermsItem]
    exact_match: bool = False
