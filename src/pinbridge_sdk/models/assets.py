"""Asset models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from .base import PinbridgeModel


class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class AssetResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    asset_type: AssetType
    original_filename: str
    stored_filename: str
    content_type: str
    file_size_bytes: int
    public_url: str
    created_at: datetime
    updated_at: datetime
