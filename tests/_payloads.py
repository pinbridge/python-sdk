from __future__ import annotations

UUID1 = "11111111-1111-1111-1111-111111111111"
UUID2 = "22222222-2222-2222-2222-222222222222"
UUID3 = "33333333-3333-3333-3333-333333333333"
UUID4 = "44444444-4444-4444-4444-444444444444"
TS = "2026-02-23T12:00:00Z"


def auth_response() -> dict:
    return {
        "access_token": "jwt-token",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {"id": UUID1, "email": "dev@pinbridge.io", "full_name": None, "created_at": TS},
        "workspace": {"id": UUID2, "name": "SDK Workspace", "plan": "starter"},
    }


def me_response() -> dict:
    base = auth_response()
    return {"user": base["user"], "workspace": base["workspace"]}


def profile_response() -> dict:
    return {
        "full_name": "SDK User",
        "email": "dev@pinbridge.io",
        "workspace_name": "SDK Workspace",
        "company_name": None,
        "company_website": None,
        "billing_email": None,
        "billing_phone": None,
        "tax_id": None,
        "address_line1": None,
        "address_line2": None,
        "address_city": None,
        "address_state": None,
        "address_postal_code": None,
        "address_country": None,
    }


def api_key_response() -> dict:
    return {
        "id": UUID3,
        "workspace_id": UUID2,
        "name": "default",
        "created_at": TS,
        "revoked_at": None,
    }


def api_key_create_response() -> dict:
    payload = api_key_response()
    payload["api_key"] = "pb_live_123"
    return payload


def pinterest_account_response() -> dict:
    return {
        "id": UUID4,
        "workspace_id": UUID2,
        "pinterest_user_id": "pin-user-id",
        "display_name": "SDK Pinterest",
        "username": "sdk-pin",
        "scopes": "boards:read,boards:write,pins:read,pins:write",
        "created_at": TS,
        "updated_at": TS,
        "revoked_at": None,
    }


def board_response() -> dict:
    return {
        "id": "123-board",
        "name": "SDK Board",
        "description": "Board from tests",
        "privacy": "PUBLIC",
    }


def pin_response() -> dict:
    return {
        "id": UUID1,
        "workspace_id": UUID2,
        "pinterest_account_id": UUID4,
        "status": "queued",
        "title": "A Pin",
        "description": "Pin description",
        "link_url": "https://example.com",
        "image_url": "https://example.com/image.jpg",
        "board_id": "123-board",
        "pinterest_pin_id": None,
        "error_code": None,
        "error_message": None,
        "idempotency_key": "idem-123",
        "created_at": TS,
        "updated_at": TS,
        "published_at": None,
    }


def job_status_response() -> dict:
    return {
        "job_id": UUID1,
        "pin_id": UUID1,
        "status": "queued",
        "submitted_at": TS,
        "completed_at": None,
        "pinterest_pin_id": None,
        "error_code": None,
        "error_message": None,
    }


def schedule_response() -> dict:
    return {
        "id": UUID3,
        "workspace_id": UUID2,
        "pinterest_account_id": UUID4,
        "run_at": "2026-02-24T12:00:00Z",
        "status": "scheduled",
        "payload": {
            "board_id": "123-board",
            "title": "Scheduled pin",
            "description": "Scheduled",
            "link_url": "https://example.com",
            "image_url": "https://example.com/image.jpg",
        },
        "last_error": None,
        "pin_id": None,
        "created_at": TS,
        "updated_at": TS,
    }


def webhook_response() -> dict:
    return {
        "id": UUID3,
        "workspace_id": UUID2,
        "url": "https://example.com/hook",
        "events": ["pin.published", "pin.failed"],
        "is_enabled": True,
        "created_at": TS,
        "updated_at": TS,
    }


def pricing_catalog_response() -> dict:
    return {
        "source": "cache",
        "refreshed_at": TS,
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
                "bulk_publishing_enabled": False,
                "enhanced_logs_enabled": False,
                "monthly_price": {
                    "billing_cycle": "monthly",
                    "price_id": "price_m",
                    "unit_amount": 1900,
                    "currency": "usd",
                    "amount_display": "$19",
                },
                "annual_price": {
                    "billing_cycle": "annual",
                    "price_id": "price_a",
                    "unit_amount": 19000,
                    "currency": "usd",
                    "amount_display": "$190",
                },
            }
        ],
    }


def billing_status_response() -> dict:
    return {
        "plan": "starter",
        "billing_status": "active",
        "current_period_start": TS,
        "current_period_end": TS,
        "quota_calls_monthly": 1000,
        "calls_used": 10,
        "quota_reset_at": TS,
        "pinterest_accounts_limit": 2,
        "bulk_publishing_enabled": False,
        "enhanced_logs_enabled": False,
    }


def root_response() -> dict:
    return {"service": "PinBridge API", "version": "0.1.0", "docs": "/docs"}


def health_response() -> dict:
    return {"status": "ok", "version": "0.1.0", "environment": "test", "database": "ok"}


def rate_meter_response() -> dict:
    return {
        "account": {
            "account_id": UUID4,
            "tokens_available": 40,
            "capacity": 50,
            "refill_rate": 5,
        },
        "global": {
            "tokens_available": 1000,
            "capacity": 1200,
            "refill_rate": 20,
        },
    }
