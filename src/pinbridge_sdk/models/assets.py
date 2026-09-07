"""Asset models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from .base import PinbridgeModel
from .common import WorkspaceEnvironment


class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class AssetResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    workspace_environment: WorkspaceEnvironment | None = None
    asset_type: AssetType
    original_filename: str
    stored_filename: str
    content_type: str
    file_size_bytes: int
    file_size_display: str | None = None
    referenced_by_pin_count: int = 0
    public_url: str
    created_at: datetime
    updated_at: datetime


class AssetListResponse(PinbridgeModel):
    assets: list[AssetResponse]
    total: int
    storage_used_bytes: int
    storage_quota_bytes: int
    storage_used_percent: int


class AssetDeleteResponse(PinbridgeModel):
    deleted: bool
    requires_confirmation: bool
    referenced_pin_count: int
    freed_bytes: int


class BulkAssetDeleteRequest(PinbridgeModel):
    asset_ids: list[UUID]
    confirm: bool = False


class BulkAssetDeleteSummary(PinbridgeModel):
    asset_id: UUID
    workspace_id: UUID
    workspace_environment: WorkspaceEnvironment | None = None
    original_filename: str
    file_size_bytes: int
    referenced_pin_count: int = 0
    freed_bytes: int = 0


class BulkAssetDeleteResponse(PinbridgeModel):
    deleted: list[UUID]
    requires_confirmation: list[UUID]
    total_freed_bytes: int
    deleted_items: list[BulkAssetDeleteSummary] = []
    requires_confirmation_items: list[BulkAssetDeleteSummary] = []
