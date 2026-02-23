"""System and utility endpoint models."""

from __future__ import annotations

from pydantic import Field

from .base import PinbridgeModel


class RootResponse(PinbridgeModel):
    service: str
    version: str
    docs: str


class HealthResponse(PinbridgeModel):
    status: str
    version: str
    environment: str
    database: str


class RateMeterNode(PinbridgeModel):
    tokens_available: float
    capacity: float
    refill_rate: float


class RateMeterAccount(RateMeterNode):
    account_id: str


class RateMeterResponse(PinbridgeModel):
    account: RateMeterAccount
    global_: RateMeterNode = Field(alias="global")
