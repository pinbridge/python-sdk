"""Paged list results."""

from __future__ import annotations

from typing import Generic, TypeVar

from .base import PinbridgeModel

ItemT = TypeVar("ItemT")


class Page(PinbridgeModel, Generic[ItemT]):
    """One page of a list endpoint plus the total the API reported.

    ``total`` comes from the ``X-Total-Count`` response header (API 1.34.0+):
    the number of rows matching the filters and search, ignoring ``limit`` and
    ``offset``. It is ``None`` when the API did not send the header.
    """

    items: list[ItemT]
    total: int | None = None
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Whether another page follows this one."""
        if self.total is not None:
            return self.offset + len(self.items) < self.total
        return len(self.items) == self.limit
