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
    billing_provider: str = "database"
    billing_cycle: BillingCycle | None = None
    billing_status: BillingStatus
    trial_active: bool = False
    trial_ends_at: datetime | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    subscription_cancel_at: datetime | None = None
    quota_calls_monthly: int
    calls_used: int
    quota_reset_at: datetime | None = None
    credits_remaining: int = 0
    credits_enabled: bool = False
    credits_purchase_allowed: bool = False
    quota_exhausted: bool = False
    plan_consumption_percent: int = 0
    storage_quota_bytes: int = 0
    storage_used_bytes: int = 0
    storage_used_percent: int = 0
    storage_warning: str | None = None
    pinterest_accounts_limit: int
    uploaded_media_assets: bool
    bulk_imports: bool


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
    uploaded_media_assets: bool
    bulk_imports: bool
    activity_log_retention_days: int
    overage_billing_threshold_pins: int | None = None
    monthly_price: PricingAmountResponse
    annual_price: PricingAmountResponse


class PricingCatalogResponse(PinbridgeModel):
    source: str
    refreshed_at: datetime
    plans: list[PricingPlanResponse]
