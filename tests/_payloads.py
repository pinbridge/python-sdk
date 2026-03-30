from __future__ import annotations

UUID1 = "11111111-1111-1111-1111-111111111111"
UUID2 = "22222222-2222-2222-2222-222222222222"
UUID3 = "33333333-3333-3333-3333-333333333333"
UUID4 = "44444444-4444-4444-4444-444444444444"
TS = "2026-02-23T12:00:00Z"


def auth_response() -> dict:
    workspace = {
        "id": UUID2,
        "name": "SDK Workspace",
        "environment": "production",
        "timezone": "UTC",
        "plan": "starter",
    }
    return {
        "access_token": "jwt-token",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "id": UUID1,
            "email": "dev@pinbridge.io",
            "full_name": None,
            "timezone": "UTC",
            "email_verified": True,
            "created_at": TS,
        },
        "organization": {"id": UUID3, "name": "SDK Org"},
        "active_project": workspace,
        "projects": [workspace],
        "workspace": workspace,
    }


def me_response() -> dict:
    base = auth_response()
    return {
        "user": base["user"],
        "organization": base["organization"],
        "active_project": base["active_project"],
        "projects": base["projects"],
        "workspace": base["workspace"],
    }


def projects_context_response() -> dict:
    workspace = {
        "id": UUID2,
        "name": "SDK Workspace",
        "environment": "production",
        "plan": "starter",
        "created_at": TS,
    }
    sandbox = {
        "id": UUID4,
        "name": "SDK Sandbox",
        "environment": "sandbox",
        "plan": "free",
        "created_at": TS,
    }
    return {
        "organization": {"id": UUID3, "name": "SDK Org"},
        "active_project": workspace,
        "projects": [workspace, sandbox],
    }


def project_switch_response() -> dict:
    base = projects_context_response()
    sandbox = next(project for project in base["projects"] if project["environment"] == "sandbox")
    base["active_project"] = sandbox
    base["access_token"] = "jwt-switched-token"
    base["token_type"] = "bearer"
    base["expires_in"] = 3600
    return base


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


def action_response(message: str = "ok") -> dict:
    return {"message": message}


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


def related_terms_response() -> dict:
    return {
        "id": "workout",
        "related_term_count": 3,
        "related_terms_list": [
            {
                "term": "workout",
                "related_terms": ["home workout", "gym workout"],
            },
            {
                "term": "yoga",
                "related_terms": ["morning yoga"],
            },
        ],
        "exact_match": False,
    }


def pin_response() -> dict:
    return {
        "id": UUID1,
        "workspace_id": UUID2,
        "pinterest_account_id": UUID4,
        "status": "queued",
        "media_type": "image",
        "title": "A Pin",
        "description": "Pin description",
        "related_terms": ["meal prep", "glazed carrots"],
        "alt_text": "Bowl of glazed carrots with herbs",
        "dominant_color": "#E88A2D",
        "cover_image_url": "https://example.com/video-cover.jpg",
        "link_url": "https://example.com",
        "media_url": "https://example.com/image.jpg",
        "image_url": "https://example.com/image.jpg",
        "asset_id": UUID3,
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


def import_job_response() -> dict:
    return {
        "id": UUID3,
        "workspace_id": UUID2,
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
                "pin_id": UUID1,
                "schedule_id": None,
                "idempotency_key": "bulk-1",
                "error_code": None,
                "error_message": None,
            },
            {
                "row_number": 2,
                "status": "failed",
                "pin_id": None,
                "schedule_id": None,
                "idempotency_key": "bulk-2",
                "error_code": "validation_error",
                "error_message": "board_id: Field required",
            },
        ],
        "error_message": None,
        "started_at": TS,
        "completed_at": TS,
        "created_at": TS,
        "updated_at": TS,
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
            "media_type": "image",
            "media_url": "https://example.com/image.jpg",
            "image_url": "https://example.com/image.jpg",
            "asset_id": UUID3,
            "cover_image_url": "https://example.com/video-cover.jpg",
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


def billing_status_response() -> dict:
    return {
        "plan": "starter",
        "billing_provider": "stripe",
        "billing_cycle": "monthly",
        "billing_status": "active",
        "current_period_start": TS,
        "current_period_end": TS,
        "subscription_cancel_at": None,
        "quota_calls_monthly": 1000,
        "calls_used": 10,
        "quota_reset_at": TS,
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


def root_response() -> dict:
    return {"service": "PinBridge API", "version": "1.0.0", "docs": "/docs"}


def health_response() -> dict:
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": "test",
        "checks": {"app": "ok"},
    }


def readiness_response() -> dict:
    return {"status": "ok", "version": "1.0.0", "environment": "test", "database": "ok"}


def asset_response() -> dict:
    return {
        "id": UUID3,
        "workspace_id": UUID2,
        "asset_type": "image",
        "original_filename": "pin.png",
        "stored_filename": f"{UUID3}.png",
        "content_type": "image/png",
        "file_size_bytes": 68,
        "public_url": f"https://api.pinbridge.test/v1/assets/{UUID3}/content",
        "created_at": TS,
        "updated_at": TS,
    }


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
