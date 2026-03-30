from __future__ import annotations

import pytest
from pydantic import ValidationError

from pinbridge_sdk.models import (
    BillingStatusResponse,
    BoardCreateRequest,
    ImportJobResponse,
    LoginRequest,
    PinCreate,
    PinImportCreate,
    PricingCatalogResponse,
    RegisterRequest,
    ScheduleCreate,
    WebhookCreate,
)


def test_current_billing_payloads_parse() -> None:
    billing = BillingStatusResponse.model_validate(
        {
            "plan": "starter",
            "billing_provider": "stripe",
            "billing_status": "active",
            "current_period_start": "2026-02-01T00:00:00Z",
            "current_period_end": "2026-03-01T00:00:00Z",
            "subscription_cancel_at": None,
            "quota_calls_monthly": 1000,
            "calls_used": 10,
            "quota_reset_at": "2026-03-01T00:00:00Z",
            "credits_remaining": 0,
            "credits_enabled": False,
            "credits_purchase_allowed": True,
            "quota_exhausted": False,
            "plan_consumption_percent": 1,
            "storage_quota_bytes": 7516192768,
            "storage_used_bytes": 0,
            "storage_used_percent": 0,
            "storage_warning": None,
            "pinterest_accounts_limit": 2,
            "uploaded_media_assets": True,
            "bulk_imports": True,
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
                    "uploaded_media_assets": True,
                    "bulk_imports": True,
                    "activity_log_retention_days": 30,
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

    assert billing.credits_remaining == 0
    assert billing.storage_quota_bytes == 7516192768
    assert pricing.plans[0].overage_billing_threshold_pins == 100


def test_import_job_payloads_parse() -> None:
    job = ImportJobResponse.model_validate(
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "workspace_id": "22222222-2222-2222-2222-222222222222",
            "source_type": "json",
            "status": "completed_with_errors",
            "source_filename": None,
            "total_rows": 2,
            "processed_rows": 2,
            "created_rows": 1,
            "existing_rows": 0,
            "failed_rows": 1,
            "results": [
                {
                    "row_number": 1,
                    "status": "created",
                    "pin_id": "11111111-1111-1111-1111-111111111111",
                    "schedule_id": None,
                    "idempotency_key": "bulk-1",
                    "error_code": None,
                    "error_message": None,
                }
            ],
            "error_message": None,
            "started_at": "2026-02-23T12:00:00Z",
            "completed_at": "2026-02-23T12:00:00Z",
            "created_at": "2026-02-23T12:00:00Z",
            "updated_at": "2026-02-23T12:00:00Z",
        }
    )

    assert job.status.value == "completed_with_errors"
    assert job.results[0].status == "created"


@pytest.mark.parametrize(
    ("model_cls", "payload"),
    [
        (
            RegisterRequest,
            {"full_name": "SDK User", "email": "not-an-email", "password": "secret123"},
        ),
        (
            RegisterRequest,
            {
                "full_name": "SDK User",
                "email": "dev@pinbridge.io",
                "password": "secret123",
                "timezone": "Not/A_Real_Timezone",
            },
        ),
        (LoginRequest, {"email": "dev@pinbridge.io", "password": "short"}),
        (
            LoginRequest,
            {
                "email": "dev@pinbridge.io",
                "password": "secret123",
                "timezone": "Not/A_Real_Timezone",
            },
        ),
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
            PinCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "board_id": "board-1",
                "title": "Pin",
                "image_url": "https://example.com/pin.jpg",
                "asset_id": "33333333-3333-3333-3333-333333333333",
                "idempotency_key": "idem-1",
            },
        ),
        (
            PinCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "board_id": "board-1",
                "title": "x" * 101,
                "image_url": "https://example.com/pin.jpg",
                "idempotency_key": "idem-1",
            },
        ),
        (
            PinCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "board_id": "board-1",
                "title": "Pin",
                "description": "x" * 801,
                "image_url": "https://example.com/pin.jpg",
                "idempotency_key": "idem-1",
            },
        ),
        (
            PinCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "board_id": "board-1",
                "title": "Pin",
                "image_url": "https://example.com/pin.jpg",
                "link_url": f"https://example.com/{'x' * 2100}",
                "idempotency_key": "idem-1",
            },
        ),
        (
            PinCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "board_id": "board-1",
                "title": "Pin",
                "image_url": "https://example.com/pin.jpg",
                "alt_text": "x" * 501,
                "idempotency_key": "idem-1",
            },
        ),
        (
            PinCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "board_id": "board-1",
                "title": "Pin",
                "image_url": "https://example.com/pin.jpg",
                "dominant_color": "orange",
                "idempotency_key": "idem-1",
            },
        ),
        (
            PinCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "board_id": "board-1",
                "title": "Pin",
                "image_url": "https://example.com/pin.jpg",
                "cover_image_url": "https://example.com/cover.jpg",
                "cover_image_asset_id": "33333333-3333-3333-3333-333333333333",
                "idempotency_key": "idem-1",
            },
        ),
        (
            PinImportCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "board_id": "board-1",
                "title": "Import row",
                "image_url": "https://example.com/pin.jpg",
                "idempotency_key": "idem-2",
                "run_at": "2026-02-24T12:00:00",
            },
        ),
        (
            ScheduleCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "run_at": "2026-02-24T12:00:00",
                "board_id": "board-1",
                "title": "Scheduled",
                "image_url": "not-a-url",
            },
        ),
        (
            ScheduleCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "run_at": "2026-02-24T12:00:00Z",
                "board_id": "board-1",
                "title": "Scheduled",
                "image_url": "https://example.com/pin.jpg",
                "asset_id": "33333333-3333-3333-3333-333333333333",
            },
        ),
        (
            ScheduleCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "run_at": "2026-02-24T12:00:00Z",
                "board_id": "board-1",
                "title": "x" * 101,
                "image_url": "https://example.com/pin.jpg",
            },
        ),
        (
            ScheduleCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "run_at": "2026-02-24T12:00:00Z",
                "board_id": "board-1",
                "title": "Scheduled",
                "description": "x" * 801,
                "image_url": "https://example.com/pin.jpg",
            },
        ),
        (
            ScheduleCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "run_at": "2026-02-24T12:00:00Z",
                "board_id": "board-1",
                "title": "Scheduled",
                "link_url": f"https://example.com/{'x' * 2100}",
                "image_url": "https://example.com/pin.jpg",
            },
        ),
        (
            ScheduleCreate,
            {
                "account_id": "44444444-4444-4444-4444-444444444444",
                "run_at": "2026-02-24T12:00:00Z",
                "board_id": "board-1",
                "title": "Scheduled",
                "image_url": "https://example.com/pin.jpg",
                "cover_image_url": "https://example.com/cover.jpg",
                "cover_image_asset_id": "33333333-3333-3333-3333-333333333333",
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


def test_pin_create_normalizes_related_terms_and_dominant_color() -> None:
    model = PinCreate.model_validate(
        {
            "account_id": "44444444-4444-4444-4444-444444444444",
            "board_id": "board-1",
            "title": "Pin",
            "image_url": "https://example.com/pin.jpg",
            "idempotency_key": "idem-1",
            "related_terms": " meals, , carrots ,meal prep ",
            "dominant_color": "6e7874",
        }
    )

    assert model.related_terms == ["meals", "carrots", "meal prep"]
    assert model.dominant_color == "#6E7874"
