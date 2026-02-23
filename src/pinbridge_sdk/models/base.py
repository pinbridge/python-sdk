"""Base pydantic model used by all SDK models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PinbridgeModel(BaseModel):
    """Model base with forward-compatible parsing behavior."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
