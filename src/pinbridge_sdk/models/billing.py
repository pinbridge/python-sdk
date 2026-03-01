"""Billing models."""

from __future__ import annotations

from datetime import datetime

from .base import PinbridgeModel
from .common import BillingCycle, BillingStatus, Plan


class CheckoutRequest(PinbridgeModel):
    plan: Plan
    billing_cycle: BillingCycle = BillingCycle.MONTHLY


class CheckoutResponse(PinbridgeModel):
    url: str


class PortalResponse(PinbridgeModel):
    url: str


class BillingStatusResponse(PinbridgeModel):
    plan: Plan
    billing_status: BillingStatus
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    subscription_cancel_at: datetime | None = None
    quota_calls_monthly: int
    calls_used: int
    overage_pins_used: int
    quota_reset_at: datetime | None = None
    pinterest_accounts_limit: int
    overage_billing_threshold_pins: int | None = None


class PricingAmountResponse(PinbridgeModel):
    billing_cycle: BillingCycle
    unit_amount: int
    currency: str
    amount_display: str


class PricingPlanResponse(PinbridgeModel):
    plan: Plan
    name: str
    subtitle: str
    highlight: bool = False
    feature_bullets: list[str]
    monthly_overage: str | None = None
    quota_calls_monthly: int
    pinterest_accounts_limit: int
    overage_billing_threshold_pins: int | None = None
    monthly_price: PricingAmountResponse
    annual_price: PricingAmountResponse


class PricingCatalogResponse(PinbridgeModel):
    source: str
    refreshed_at: datetime
    plans: list[PricingPlanResponse]
