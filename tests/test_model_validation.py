from __future__ import annotations

import pytest
from pydantic import ValidationError

from pinbridge_sdk.models import (
    BillingStatusResponse,
    BoardCreateRequest,
    LoginRequest,
    PinCreate,
    PricingCatalogResponse,
    RegisterRequest,
    ScheduleCreate,
    WebhookCreate,
)


def test_current_billing_payloads_parse() -> None:
    billing = BillingStatusResponse.model_validate(
        {
            "plan": "starter",
            "billing_status": "active",
            "current_period_start": "2026-02-01T00:00:00Z",
            "current_period_end": "2026-03-01T00:00:00Z",
            "subscription_cancel_at": None,
            "quota_calls_monthly": 1000,
            "calls_used": 10,
            "overage_pins_used": 0,
            "quota_reset_at": "2026-03-01T00:00:00Z",
            "pinterest_accounts_limit": 2,
            "overage_billing_threshold_pins": 100,
        }
    )
    pricing = PricingCatalogResponse.model_validate(
        {
            "source": "cache",
            "refreshed_at": "2026-02-28T00:00:00Z",
            "plans": [
                {
                    "plan": "starter",
                    "name": "Starter",
                    "subtitle": "For small teams",
                    "highlight": False,
                    "feature_bullets": ["1000 API calls"],
                    "monthly_overage": None,
                    "quota_calls_monthly": 1000,
                    "pinterest_accounts_limit": 2,
                    "overage_billing_threshold_pins": 100,
                    "monthly_price": {
                        "billing_cycle": "monthly",
                        "unit_amount": 1900,
                        "currency": "usd",
                        "amount_display": "$19",
                    },
                    "annual_price": {
                        "billing_cycle": "annual",
                        "unit_amount": 19000,
                        "currency": "usd",
                        "amount_display": "$190",
                    },
                }
            ],
        }
    )

    assert billing.overage_pins_used == 0
    assert pricing.plans[0].overage_billing_threshold_pins == 100


@pytest.mark.parametrize(
    ("model_cls", "payload"),
    [
        (RegisterRequest, {"email": "not-an-email", "password": "secret123"}),
        (LoginRequest, {"email": "dev@pinbridge.io", "password": "short"}),
        (
            PinCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "board_id": "board-1",
                "title": "Pin",
                "image_url": "not-a-url",
                "idempotency_key": "idem-1",
            },
        ),
        (
            ScheduleCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "run_at": "2026-02-24T12:00:00Z",
                "board_id": "board-1",
                "title": "Scheduled",
                "image_url": "not-a-url",
            },
        ),
        (
            WebhookCreate,
            {"url": "https://example.com/hook", "secret": "short", "events": ["pin.published"]},
        ),
        (
            BoardCreateRequest,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "name": "",
            },
        ),
    ],
)
def test_request_models_reject_invalid_payloads(
    model_cls: type,
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        model_cls.model_validate(payload)
