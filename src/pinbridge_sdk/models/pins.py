"""Pin and job models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from pydantic import Field, HttpUrl, StringConstraints, field_validator, model_validator

from .base import PinbridgeModel
from .common import ImportJobStatus, ImportSourceType, PinMediaType, PinStatus

PinTitle = Annotated[str, StringConstraints(max_length=100)]
PinDescription = Annotated[str, StringConstraints(max_length=800)]
PinAltText = Annotated[str, StringConstraints(max_length=500)]
IdempotencyKey = Annotated[str, StringConstraints(max_length=255)]


class PinCreate(PinbridgeModel):
    account_id: UUID
    board_id: str
    title: PinTitle
    description: PinDescription | None = None
    related_terms: list[str] | None = None
    alt_text: PinAltText | None = None
    dominant_color: str | None = None
    cover_image_url: HttpUrl | None = None
    cover_image_asset_id: UUID | None = None
    link_url: HttpUrl | None = None
    image_url: HttpUrl | None = None
    asset_id: UUID | None = None
    idempotency_key: IdempotencyKey

    @model_validator(mode="after")
    def validate_media_source(self) -> PinCreate:
        if self.image_url is None and self.asset_id is None:
            raise ValueError("Either image_url or asset_id must be provided")
        if self.image_url is not None and self.asset_id is not None:
            raise ValueError("Provide either image_url or asset_id, not both")
        if self.cover_image_url is not None and self.cover_image_asset_id is not None:
            raise ValueError("Provide either cover_image_url or cover_image_asset_id, not both")
        return self

    @field_validator("related_terms", mode="before")
    @classmethod
    def validate_related_terms(cls, value: list[str] | str | None) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            value = [term.strip() for term in value.split(",")]
        cleaned = [term.strip() for term in value if isinstance(term, str) and term.strip()]
        return cleaned or None

    @field_validator("dominant_color")
    @classmethod
    def validate_dominant_color(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if not normalized.startswith("#"):
            normalized = f"#{normalized}"
        if len(normalized) != 7 or any(
            char not in "0123456789ABCDEFabcdef" for char in normalized[1:]
        ):
            raise ValueError("dominant_color must be a 6-digit hex color (for example #6E7874)")
        return normalized.upper()

    @field_validator("link_url")
    @classmethod
    def validate_link_url_length(cls, value: HttpUrl | None) -> HttpUrl | None:
        if value is None:
            return None
        if len(str(value)) > 2048:
            raise ValueError("link_url must be <= 2048 characters")
        return value

    @field_validator("cover_image_url")
    @classmethod
    def validate_cover_image_url_length(cls, value: HttpUrl | None) -> HttpUrl | None:
        if value is None:
            return None
        if len(str(value)) > 2048:
            raise ValueError("cover_image_url must be <= 2048 characters")
        return value


class PinImportCreate(PinCreate):
    run_at: datetime | None = None

    @field_validator("run_at")
    @classmethod
    def validate_run_at_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                "run_at must include a timezone offset (for example 2026-03-06T10:00:00Z)"
            )
        return value.astimezone(timezone.utc)


class PinResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    pinterest_account_id: UUID
    status: PinStatus
    media_type: PinMediaType
    title: str
    description: str | None = None
    related_terms: list[str] | None = None
    alt_text: str | None = None
    dominant_color: str | None = None
    cover_image_url: str | None = None
    link_url: str | None = None
    media_url: str
    image_url: str
    asset_id: UUID | None = None
    board_id: str
    pinterest_pin_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    idempotency_key: str
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None


class JobStatusResponse(PinbridgeModel):
    job_id: UUID
    pin_id: UUID
    status: PinStatus
    submitted_at: datetime
    completed_at: datetime | None = None
    pinterest_pin_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None


class BulkPinImportRowResult(PinbridgeModel):
    row_number: int
    status: str
    pin_id: UUID | None = None
    schedule_id: UUID | None = None
    idempotency_key: str | None = None
    error_code: str | None = None
    error_message: str | None = None


class ImportJobResponse(PinbridgeModel):
    id: UUID
    workspace_id: UUID
    source_type: ImportSourceType
    status: ImportJobStatus
    source_filename: str | None = None
    total_rows: int
    processed_rows: int
    created_rows: int
    existing_rows: int
    failed_rows: int
    results: list[BulkPinImportRowResult] = Field(default_factory=list)
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
