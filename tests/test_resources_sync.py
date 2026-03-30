from __future__ import annotations

import json
from datetime import datetime

import httpx
import pytest
from _payloads import (
    UUID1,
    UUID3,
    UUID4,
    action_response,
    activity_log_list_response,
    api_key_create_response,
    api_key_response,
    asset_response,
    auth_response,
    billing_status_response,
    board_response,
    health_response,
    import_job_response,
    job_status_response,
    me_response,
    pin_response,
    pinterest_account_response,
    pricing_catalog_response,
    profile_response,
    project_switch_response,
    projects_context_response,
    rate_meter_response,
    readiness_response,
    related_terms_response,
    root_response,
    schedule_response,
    webhook_response,
)

from pinbridge_sdk import PinbridgeClient
from pinbridge_sdk.models import (
    APIKeyCreate,
    APIKeyUpdate,
    AssetType,
    BillingCycle,
    BoardCreateRequest,
    ChangePasswordRequest,
    CheckoutRequest,
    ForgotPasswordRequest,
    ImportJobStatus,
    ImportSourceType,
    LoginRequest,
    PinCreate,
    PinImportCreate,
    Plan,
    ProfileUpdateRequest,
    RegisterRequest,
    ResetPasswordRequest,
    ScheduleCreate,
    SwitchProjectRequest,
    WebhookCreate,
    WebhookUpdate,
)


def _request_json(request: httpx.Request) -> dict:
    if not request.content:
        return {}
    return json.loads(request.content.decode("utf-8"))


def test_sync_resource_methods_end_to_end() -> None:
    seen: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        method = request.method
        path = request.url.path
        seen.append((method, path))

        if (method, path) == ("POST", "/v1/auth/register"):
            payload = _request_json(request)
            assert payload["full_name"] == "SDK User"
            assert payload["email"] == "dev@pinbridge.io"
            assert payload["timezone"] == "UTC"
            return httpx.Response(201, json=auth_response())

        if (method, path) == ("POST", "/v1/auth/login"):
            payload = _request_json(request)
            assert payload["password"] == "secret123"
            assert payload["timezone"] == "UTC"
            return httpx.Response(200, json=auth_response())

        if (method, path) == ("POST", "/v1/auth/forgot-password"):
            payload = _request_json(request)
            assert payload["email"] == "dev@pinbridge.io"
            return httpx.Response(200, json=action_response("Password reset email sent"))

        if (method, path) == ("POST", "/v1/auth/reset-password"):
            payload = _request_json(request)
            assert payload["token"] == "t" * 20
            return httpx.Response(200, json=action_response("Password has been reset"))

        if (method, path) == ("POST", "/v1/auth/change-password"):
            payload = _request_json(request)
            assert payload["current_password"] == "secret123"
            return httpx.Response(200, json=action_response("Password changed"))

        if (method, path) == ("POST", "/v1/auth/email/verify/request"):
            return httpx.Response(200, json=action_response("Verification requested"))

        if (method, path) == ("GET", "/v1/auth/email/verify"):
            assert request.url.params["token"] == "v" * 20
            return httpx.Response(200, json=action_response("Email verified"))

        if (method, path) == ("GET", "/v1/auth/me"):
            return httpx.Response(200, json=me_response())

        if (method, path) == ("GET", "/v1/auth/profile"):
            return httpx.Response(200, json=profile_response())

        if (method, path) == ("PUT", "/v1/auth/profile"):
            payload = _request_json(request)
            assert payload == {"workspace_name": "New Name"}
            return httpx.Response(200, json=profile_response())

        if (method, path) == ("GET", "/v1/projects"):
            return httpx.Response(200, json=projects_context_response())

        if (method, path) == ("POST", "/v1/projects/sandbox"):
            payload = _request_json(request)
            assert payload in ({}, {"name": "SDK Sandbox"})
            return httpx.Response(201, json=projects_context_response())

        if (method, path) == ("POST", "/v1/projects/sandbox/reset"):
            return httpx.Response(200, json=projects_context_response())

        if (method, path) == ("POST", "/v1/projects/switch"):
            payload = _request_json(request)
            assert payload["project_id"] == UUID4
            return httpx.Response(200, json=project_switch_response())

        if (method, path) == ("POST", "/v1/api-keys"):
            payload = _request_json(request)
            assert payload["name"] == "primary"
            return httpx.Response(201, json=api_key_create_response())

        if (method, path) == ("GET", "/v1/api-keys"):
            return httpx.Response(200, json=[api_key_response()])

        if (method, path) == ("POST", "/v1/assets/images"):
            assert "multipart/form-data" in request.headers["content-type"]
            assert b"asset-binary" in request.content
            return httpx.Response(201, json=asset_response())

        if (method, path) == ("POST", "/v1/assets/videos"):
            assert "multipart/form-data" in request.headers["content-type"]
            assert b"video-binary" in request.content
            payload = asset_response()
            payload["asset_type"] = "video"
            payload["content_type"] = "video/mp4"
            return httpx.Response(201, json=payload)

        if (method, path) == ("GET", f"/v1/assets/{UUID3}"):
            return httpx.Response(200, json=asset_response())

        if (method, path) == ("GET", f"/v1/assets/{UUID3}/content"):
            return httpx.Response(200, content=b"asset-content")

        if (method, path) == ("PATCH", f"/v1/api-keys/{UUID3}"):
            payload = _request_json(request)
            assert payload["name"] == "renamed"
            return httpx.Response(200, json=api_key_response())

        if (method, path) == ("DELETE", f"/v1/api-keys/{UUID3}"):
            return httpx.Response(204)

        if (method, path) == ("GET", "/v1/pinterest/oauth/start"):
            return httpx.Response(200, json={"authorization_url": "https://pinterest.example/auth"})

        if (method, path) == ("GET", "/v1/pinterest/oauth/callback"):
            assert request.url.params["code"] == "abc"
            assert request.url.params["state"] == "state"
            return httpx.Response(
                200, json={"status": "success", "message": "ok", "account_id": UUID4}
            )

        if (method, path) == ("GET", "/v1/pinterest/accounts"):
            return httpx.Response(200, json=[pinterest_account_response()])

        if (method, path) == ("DELETE", f"/v1/pinterest/accounts/{UUID4}"):
            return httpx.Response(204)

        if (method, path) == ("GET", "/v1/pinterest/boards"):
            assert request.url.params["account_id"] == UUID4
            return httpx.Response(200, json=[board_response()])

        if (method, path) == ("GET", "/v1/pinterest/terms/related"):
            assert request.url.params.get_list("terms") == ["workout", "yoga"]
            assert request.url.params["account_id"] == UUID4
            assert request.url.params["exact_match"] == "true"
            payload = related_terms_response()
            payload["exact_match"] = True
            return httpx.Response(200, json=payload)

        if (method, path) == ("POST", "/v1/pinterest/boards"):
            payload = _request_json(request)
            assert payload["name"] == "SDK Board"
            return httpx.Response(201, json=board_response())

        if (method, path) == ("DELETE", "/v1/pinterest/boards/board-1"):
            assert request.url.params["account_id"] == UUID4
            return httpx.Response(204)

        if (method, path) == ("POST", "/v1/pins"):
            payload = _request_json(request)
            assert payload["idempotency_key"] == "idem-123"
            assert payload["alt_text"] == "Bowl of glazed carrots with herbs"
            assert payload["related_terms"] == ["meal prep", "glazed carrots"]
            assert payload["dominant_color"] == "#E88A2D"
            return httpx.Response(201, json=pin_response())

        if (method, path) == ("POST", "/v1/pins/imports/json"):
            payload = _request_json(request)
            assert len(payload) == 2
            assert payload[0]["run_at"] == "2026-02-24T14:00:00Z"
            assert payload[0]["idempotency_key"] == "bulk-json-1"
            return httpx.Response(202, json=import_job_response())

        if (method, path) == ("POST", "/v1/pins/imports/csv"):
            assert "multipart/form-data" in request.headers["content-type"]
            assert b"account_id,board_id,title" in request.content
            payload = import_job_response()
            payload["source_type"] = "csv"
            payload["source_filename"] = "pins.csv"
            return httpx.Response(202, json=payload)

        if (method, path) == ("GET", "/v1/pins/imports"):
            assert request.url.params["status"] == "completed_with_errors"
            assert request.url.params["source_type"] == "json"
            return httpx.Response(200, json=[import_job_response()])

        if (method, path) == ("GET", f"/v1/pins/imports/{UUID3}"):
            return httpx.Response(200, json=import_job_response())

        if (method, path) == ("GET", "/v1/pins"):
            assert request.url.params["limit"] == "10"
            assert request.url.params["offset"] == "2"
            return httpx.Response(200, json=[pin_response()])

        if (method, path) == ("GET", f"/v1/pins/{UUID1}"):
            return httpx.Response(200, json=pin_response())

        if (method, path) == ("DELETE", f"/v1/pins/{UUID1}"):
            return httpx.Response(204)

        if (method, path) == ("GET", f"/v1/jobs/{UUID1}"):
            return httpx.Response(200, json=job_status_response())

        if (method, path) == ("POST", "/v1/schedules"):
            payload = _request_json(request)
            assert payload["title"] == "Scheduled"
            assert payload["cover_image_url"] == "https://example.com/video-cover.jpg"
            return httpx.Response(201, json=schedule_response())

        if (method, path) == ("GET", "/v1/schedules"):
            return httpx.Response(200, json=[schedule_response()])

        if (method, path) == ("GET", f"/v1/schedules/{UUID3}"):
            return httpx.Response(200, json=schedule_response())

        if (method, path) == ("POST", f"/v1/schedules/{UUID3}/cancel"):
            return httpx.Response(200, json=schedule_response())

        if (method, path) == ("POST", "/v1/webhooks"):
            payload = _request_json(request)
            assert payload["is_enabled"] is True
            return httpx.Response(201, json=webhook_response())

        if (method, path) == ("GET", "/v1/webhooks"):
            return httpx.Response(200, json=[webhook_response()])

        if (method, path) == ("GET", f"/v1/webhooks/{UUID3}"):
            return httpx.Response(200, json=webhook_response())

        if (method, path) == ("PATCH", f"/v1/webhooks/{UUID3}"):
            payload = _request_json(request)
            assert payload == {"is_enabled": False}
            return httpx.Response(200, json=webhook_response())

        if (method, path) == ("DELETE", f"/v1/webhooks/{UUID3}"):
            return httpx.Response(204)

        if (method, path) == ("GET", "/v1/rate-meter"):
            assert request.url.params["account_id"] == UUID4
            return httpx.Response(200, json=rate_meter_response())

        if (method, path) == ("GET", "/v1/billing/pricing"):
            return httpx.Response(200, json=pricing_catalog_response())

        if (method, path) == ("POST", "/v1/billing/checkout"):
            payload = _request_json(request)
            assert payload["plan"] == "starter"
            return httpx.Response(200, json={"url": "https://checkout.stripe.test"})

        if (method, path) == ("POST", "/v1/billing/portal"):
            return httpx.Response(200, json={"url": "https://portal.stripe.test"})

        if (method, path) == ("GET", "/v1/billing/status"):
            return httpx.Response(200, json=billing_status_response())

        if (method, path) == ("GET", "/v1/activity-logs"):
            assert int(request.url.params.get("limit", 50)) <= 200
            return httpx.Response(200, json=activity_log_list_response())

        if (method, path) == ("GET", "/"):
            return httpx.Response(200, json=root_response())

        if (method, path) == ("GET", "/healthz"):
            return httpx.Response(200, json=health_response())
        if (method, path) == ("GET", "/readyz"):
            return httpx.Response(200, json=readiness_response())

        if (method, path) == ("POST", "/v1/stripe/webhook"):
            assert request.headers["stripe-signature"] == "sig"
            return httpx.Response(200, json={"status": "success"})

        raise AssertionError(f"Unexpected request: {method} {path}")

    transport = httpx.MockTransport(handler)
    with PinbridgeClient(base_url="https://api.pinbridge.test", transport=transport) as client:
        auth = client.auth.register(
            RegisterRequest(
                full_name="SDK User",
                email="dev@pinbridge.io",
                password="secret123",
                workspace_name="SDK",
                timezone="UTC",
            )
        )
        assert auth.workspace.plan == Plan.STARTER

        logged = client.auth.login(
            LoginRequest(email="dev@pinbridge.io", password="secret123", timezone="UTC")
        )
        client.set_bearer_token(logged.access_token)
        assert (
            client.auth.forgot_password(ForgotPasswordRequest(email="dev@pinbridge.io")).message
            == "Password reset email sent"
        )
        assert (
            client.auth.reset_password(
                ResetPasswordRequest(token="t" * 20, password="secret456")
            ).message
            == "Password has been reset"
        )
        assert (
            client.auth.change_password(
                ChangePasswordRequest(
                    current_password="secret123",
                    new_password="secret456",
                )
            ).message
            == "Password changed"
        )
        assert client.auth.request_email_verification().message == "Verification requested"
        assert client.auth.verify_email("v" * 20).message == "Email verified"

        assert client.auth.me().workspace.id
        assert client.auth.get_profile().workspace_name == "SDK Workspace"
        assert (
            client.auth.update_profile(
                ProfileUpdateRequest(workspace_name="New Name")
            ).workspace_name
            == "SDK Workspace"
        )
        assert len(client.projects.list().projects) == 2
        assert len(client.projects.create_sandbox({"name": "SDK Sandbox"}).projects) == 2
        assert len(client.projects.reset_sandbox().projects) == 2
        switched = client.projects.switch(SwitchProjectRequest(project_id=UUID4))
        assert switched.active_project.environment.value == "sandbox"
        client.set_bearer_token(switched.access_token)

        key = client.api_keys.create(APIKeyCreate(name="primary"))
        assert key.api_key.startswith("pb_live_")
        assert len(client.api_keys.list()) == 1
        assert client.api_keys.update(UUID3, APIKeyUpdate(name="renamed")).id
        client.api_keys.revoke(UUID3)
        asset = client.assets.upload_image(
            b"asset-binary",
            filename="pin.png",
            content_type="image/png",
        )
        assert asset.asset_type == AssetType.IMAGE
        video_asset = client.assets.upload_video(
            b"video-binary",
            filename="pin.mp4",
            content_type="video/mp4",
        )
        assert video_asset.asset_type == AssetType.VIDEO
        assert client.assets.get(UUID3).id
        assert client.assets.get_content(UUID3) == b"asset-content"

        assert client.pinterest.start_oauth().authorization_url
        callback = client.pinterest.oauth_callback(code="abc", state="state")
        assert callback.message == "ok"
        assert len(client.pinterest.list_accounts()) == 1
        client.pinterest.revoke_account(UUID4)
        assert len(client.pinterest.list_boards(UUID4)) == 1
        related_terms = client.pinterest.list_related_terms(
            UUID4,
            ["workout", " yoga ", "workout"],
            exact_match=True,
        )
        assert related_terms.related_term_count == 3
        assert related_terms.exact_match is True
        assert (
            client.pinterest.create_board(
                BoardCreateRequest(
                    account_id=UUID4, name="SDK Board", description=None, privacy=None
                )
            ).id
            == "123-board"
        )
        client.pinterest.delete_board("board-1", account_id=UUID4)

        created_pin = client.pins.create(
            PinCreate(
                account_id=UUID4,
                board_id="123-board",
                title="A Pin",
                description="Pin description",
                link_url="https://example.com",
                related_terms=["meal prep", "glazed carrots"],
                alt_text="Bowl of glazed carrots with herbs",
                dominant_color="#e88a2d",
                asset_id=UUID3,
                idempotency_key="idem-123",
            )
        )
        assert created_pin.title == "A Pin"
        import_job = client.pins.import_json(
            [
                PinImportCreate(
                    account_id=UUID4,
                    board_id="123-board",
                    title="Bulk A",
                    image_url="https://example.com/bulk-a.jpg",
                    idempotency_key="bulk-json-1",
                    run_at=datetime.fromisoformat("2026-02-24T16:00:00+02:00"),
                ),
                {
                    "account_id": UUID4,
                    "board_id": "123-board",
                    "title": "Bulk B",
                    "image_url": "https://example.com/bulk-b.jpg",
                    "idempotency_key": "bulk-json-2",
                },
            ]
        )
        assert import_job.failed_rows == 1
        csv_job = client.pins.import_csv(
            (
                b"account_id,board_id,title,image_url,idempotency_key\n"
                b"1,board,Title,https://example.com/csv.jpg,csv-1\n"
            ),
            filename="pins.csv",
        )
        assert csv_job.source_filename == "pins.csv"
        assert client.pins.get_import(UUID3).id
        assert (
            len(
                client.pins.list_imports(
                    status=ImportJobStatus.COMPLETED_WITH_ERRORS,
                    source_type=ImportSourceType.JSON,
                )
            )
            == 1
        )
        assert len(client.pins.list(limit=10, offset=2)) == 1
        assert client.pins.get(UUID1).id
        client.pins.delete(UUID1)
        assert client.jobs.get(UUID1).job_id

        schedule = client.schedules.create(
            ScheduleCreate(
                account_id=UUID4,
                run_at=datetime.fromisoformat("2026-02-24T12:00:00+00:00"),
                board_id="123-board",
                title="Scheduled",
                description="Scheduled",
                link_url="https://example.com",
                cover_image_url="https://example.com/video-cover.jpg",
                asset_id=UUID3,
            )
        )
        assert schedule.id
        assert len(client.schedules.list()) == 1
        assert client.schedules.get(UUID3).id
        assert client.schedules.cancel(UUID3).status.name == "SCHEDULED"

        webhook = client.webhooks.create(
            WebhookCreate(
                url="https://example.com/hook", secret="0123456789012345", is_enabled=True
            )
        )
        assert webhook.id
        assert len(client.webhooks.list()) == 1
        assert client.webhooks.get(UUID3).id
        assert client.webhooks.update(UUID3, WebhookUpdate(is_enabled=False)).id
        client.webhooks.delete(UUID3)

        assert client.rate_meter.get(UUID4).global_.capacity == 1200
        assert client.billing.pricing().source == "cache"
        checkout = client.billing.checkout(
            CheckoutRequest(plan=Plan.STARTER, billing_cycle=BillingCycle.MONTHLY)
        )
        assert checkout.url
        assert client.billing.portal().url
        assert client.billing.status().calls_used == 10

        logs = client.activity_logs.list(limit=10)
        assert len(logs.items) == 1
        assert logs.items[0].action == "pin.created"
        assert logs.current_retention_days == 30

        assert client.system.root().service == "PinBridge API"
        assert client.system.health().status == "ok"
        assert client.system.readiness().database == "ok"
        assert client.system.stripe_webhook("{}", stripe_signature="sig")["status"] == "success"

    assert ("POST", "/v1/pins") in seen
    assert ("POST", "/v1/assets/images") in seen
    assert ("POST", "/v1/assets/videos") in seen
    assert ("GET", "/v1/billing/pricing") in seen
    assert ("POST", "/v1/auth/forgot-password") in seen
    assert ("POST", "/v1/auth/reset-password") in seen
    assert ("POST", "/v1/auth/change-password") in seen
    assert ("POST", "/v1/auth/email/verify/request") in seen
    assert ("GET", "/v1/auth/email/verify") in seen
    assert ("GET", f"/v1/assets/{UUID3}/content") in seen


def test_sync_oauth_callback_redirect_and_empty_body_branches() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(302, headers={"location": "https://app.pinbridge.test/callback"})
        return httpx.Response(200, content=b"")

    transport = httpx.MockTransport(handler)
    with PinbridgeClient(base_url="https://api.pinbridge.test", transport=transport) as client:
        redirect = client.pinterest.oauth_callback(code="abc", state="state")
        empty = client.pinterest.oauth_callback(code="abc", state="state")

    assert isinstance(redirect, httpx.Response)
    assert redirect.is_redirect
    assert isinstance(empty, httpx.Response)
    assert empty.status_code == 200


def test_sync_system_webhook_non_dict_payload_returns_empty_dict() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=[1, 2, 3]))
    with PinbridgeClient(base_url="https://api.pinbridge.test", transport=transport) as client:
        payload = client.system.stripe_webhook("{}", stripe_signature="sig")
    assert payload == {}


def test_sync_list_expected_type_error_when_api_payload_is_not_list() -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json={"unexpected": True}))
    with PinbridgeClient(base_url="https://api.pinbridge.test", transport=transport) as client:
        with pytest.raises(TypeError, match="Expected a list"):
            client.pins.list()
