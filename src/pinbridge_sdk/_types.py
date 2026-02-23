"""Shared typing aliases."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

JsonDict = dict[str, Any]
HeadersLike = Mapping[str, str]
PathValue = str | int | UUID
