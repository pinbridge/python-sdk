"""End-to-end coverage for the bulk/lifecycle, team, MCP and email endpoints."""

from __future__ import annotations

import json

import httpx
from _payloads import (
    UUID1,
    UUID3,
    UUID4,
    asset_delete_response,
    asset_list_response,
    bulk_asset_delete_response,
    bulk_operation_response,
    email_preferences_response,
    mcp_quota_response,
    pin_response,
    schedule_response,
    team_action_response,
    team_invitation_accept_response,
    team_invitation_preview_response,
    team_invitation_response,
    team_invitations_list_response,
    team_member_response,
    team_members_list_response,
)

from pinbridge_sdk import AsyncPinbridgeClient, PinbridgeClient
from pinbridge_sdk.models import (
    EmailPreferencesUpdateRequest,
    PinRetryRequest,
    TeamInvitationAcceptRequest,
    TeamInvitationCreateRequest,
    TeamMemberUpdateRequest,
)


def _request_json(request: httpx.Request) -> dict | list:
    if not request.content:
        return {}
    return json.loads(request.content.decode("utf-8"))


def _handler(request: httpx.Request) -> httpx.Response:
    method = request.method
    path = request.url.path

    # --- assets ---
    if (method, path) == ("GET", "/v1/assets"):
        assert request.url.params["sort"] == "created_at_desc"
        assert request.url.params["workspace_id"] == UUID4
        return httpx.Response(200, json=asset_list_response())
    if (method, path) == ("DELETE", f"/v1/assets/{UUID3}"):
        assert request.url.params["confirm"] == "true"
        return httpx.Response(200, json=asset_delete_response())
    if (method, path) == ("DELETE", "/v1/assets"):
        payload = _request_json(request)
        assert payload == {"asset_ids": [UUID3], "confirm": True}
        return httpx.Response(200, json=bulk_asset_delete_response())

    # --- pins lifecycle ---
    if (method, path) == ("POST", f"/v1/pins/{UUID1}/retry"):
        payload = _request_json(request)
        assert payload == {"board_id": "new-board"}
        return httpx.Response(200, json=pin_response())
    if (method, path) == ("POST", "/v1/pins/bulk-delete"):
        assert _request_json(request) == {"ids": [UUID1, UUID3]}
        return httpx.Response(200, json=bulk_operation_response())
    if (method, path) == ("POST", "/v1/pins/bulk-retry"):
        assert _request_json(request) == {"ids": [UUID1, UUID3]}
        return httpx.Response(200, json=bulk_operation_response())

    # --- schedules lifecycle ---
    if (method, path) == ("POST", f"/v1/schedules/{UUID3}/retry"):
        return httpx.Response(200, json=schedule_response())
    if (method, path) == ("DELETE", f"/v1/schedules/{UUID3}"):
        return httpx.Response(204)
    if (method, path) in {
        ("POST", "/v1/schedules/bulk-cancel"),
        ("POST", "/v1/schedules/bulk-retry"),
        ("POST", "/v1/schedules/bulk-delete"),
    }:
        assert _request_json(request) == {"ids": [UUID3]}
        return httpx.Response(200, json=bulk_operation_response())

    # --- team ---
    if (method, path) == ("GET", "/v1/team/invitations/preview"):
        assert request.url.params["token"] == "t" * 24
        return httpx.Response(200, json=team_invitation_preview_response())
    if (method, path) == ("GET", "/v1/team/members"):
        return httpx.Response(200, json=team_members_list_response())
    if (method, path) == ("GET", "/v1/team/invitations"):
        return httpx.Response(200, json=team_invitations_list_response())
    if (method, path) == ("POST", "/v1/team/invitations"):
        payload = _request_json(request)
        assert payload["email"] == "teammate@pinbridge.io"
        assert payload["role"] == "editor"
        return httpx.Response(201, json=team_invitation_response())
    if (method, path) == ("POST", f"/v1/team/invitations/{UUID4}/resend"):
        return httpx.Response(200, json=team_invitation_response())
    if (method, path) == ("DELETE", f"/v1/team/invitations/{UUID4}"):
        return httpx.Response(200, json=team_action_response("Invitation revoked"))
    if (method, path) == ("PATCH", f"/v1/team/members/{UUID1}"):
        assert _request_json(request) == {"role": "admin"}
        return httpx.Response(200, json=team_member_response())
    if (method, path) == ("DELETE", f"/v1/team/members/{UUID1}"):
        return httpx.Response(200, json=team_action_response("Member removed"))
    if (method, path) == ("POST", "/v1/team/invitations/accept"):
        assert _request_json(request) == {"token": "a" * 24}
        return httpx.Response(200, json=team_invitation_accept_response())

    # --- mcp ---
    if (method, path) == ("GET", "/v1/mcp/quota"):
        return httpx.Response(200, json=mcp_quota_response())
    if (method, path) == ("POST", "/v1/mcp/track"):
        return httpx.Response(200, json=mcp_quota_response())

    # --- email ---
    if (method, path) == ("GET", "/v1/email/preferences"):
        return httpx.Response(200, json=email_preferences_response())
    if (method, path) == ("PATCH", "/v1/email/preferences"):
        assert _request_json(request) == {
            "transactional_enabled": False,
            "alerts_enabled": True,
            "verification_enabled": True,
        }
        return httpx.Response(200, json=email_preferences_response())
    if (method, path) == ("GET", "/v1/email/unsubscribe"):
        assert request.url.params["token"] == "unsub-token"
        return httpx.Response(200, json={"message": "You have been unsubscribed."})

    raise AssertionError(f"Unexpected request: {method} {path}")


def test_sync_new_endpoints() -> None:
    transport = httpx.MockTransport(_handler)
    with PinbridgeClient(base_url="https://api.pinbridge.test", transport=transport) as client:
        assert client.assets.list(workspace_id=UUID4).total == 1
        assert client.assets.delete(UUID3, confirm=True).deleted is True
        assert client.assets.bulk_delete([UUID3], confirm=True).total_freed_bytes == 68

        assert client.pins.retry(UUID1, PinRetryRequest(board_id="new-board")).id
        assert client.pins.bulk_delete([UUID1, UUID3]).succeeded_count == 1
        assert client.pins.bulk_retry([UUID1, UUID3]).failed_count == 1

        assert client.schedules.retry(UUID3).id
        client.schedules.delete(UUID3)
        assert client.schedules.bulk_cancel([UUID3]).succeeded_count == 1
        assert client.schedules.bulk_retry([UUID3]).succeeded_count == 1
        assert client.schedules.bulk_delete([UUID3]).succeeded_count == 1

        assert client.team.preview_invitation("t" * 24).team_access_enabled is True
        assert len(client.team.list_members().items) == 1
        assert len(client.team.list_invitations().items) == 1
        assert (
            client.team.create_invitation(
                TeamInvitationCreateRequest(email="teammate@pinbridge.io", role="EDITOR")
            ).role
            == "editor"
        )
        assert client.team.resend_invitation(UUID4).id
        assert client.team.revoke_invitation(UUID4).message == "Invitation revoked"
        assert client.team.update_member(UUID1, TeamMemberUpdateRequest(role="Admin")).role
        assert client.team.remove_member(UUID1).message == "Member removed"
        accepted = client.team.accept_invitation(TeamInvitationAcceptRequest(token="a" * 24))
        assert accepted.organization_role == "editor"
        assert len(accepted.available_organizations) == 1

        assert client.mcp.quota().requests_limit == 100
        assert client.mcp.track().requests_used == 12

        assert client.email.get_preferences().transactional_enabled is True
        updated = client.email.update_preferences(
            EmailPreferencesUpdateRequest(
                transactional_enabled=False,
                alerts_enabled=True,
                verification_enabled=True,
            )
        )
        assert updated.alerts_enabled is False  # server payload
        assert client.email.unsubscribe(workspace_id=UUID3, token="unsub-token", user_id=UUID1) == {
            "message": "You have been unsubscribed."
        }


async def test_async_new_endpoints() -> None:
    transport = httpx.MockTransport(_handler)
    async with AsyncPinbridgeClient(
        base_url="https://api.pinbridge.test", transport=transport
    ) as client:
        assert (await client.assets.list(workspace_id=UUID4)).total == 1
        assert (await client.assets.delete(UUID3, confirm=True)).deleted is True
        assert (await client.assets.bulk_delete([UUID3], confirm=True)).total_freed_bytes == 68

        assert (await client.pins.retry(UUID1, PinRetryRequest(board_id="new-board"))).id
        assert (await client.pins.bulk_delete([UUID1, UUID3])).succeeded_count == 1
        assert (await client.pins.bulk_retry([UUID1, UUID3])).failed_count == 1

        assert (await client.schedules.retry(UUID3)).id
        await client.schedules.delete(UUID3)
        assert (await client.schedules.bulk_cancel([UUID3])).succeeded_count == 1
        assert (await client.schedules.bulk_retry([UUID3])).succeeded_count == 1
        assert (await client.schedules.bulk_delete([UUID3])).succeeded_count == 1

        assert (await client.team.preview_invitation("t" * 24)).team_access_enabled is True
        assert len((await client.team.list_members()).items) == 1
        assert len((await client.team.list_invitations()).items) == 1
        created = await client.team.create_invitation(
            TeamInvitationCreateRequest(email="teammate@pinbridge.io", role="EDITOR")
        )
        assert created.role == "editor"
        assert (await client.team.resend_invitation(UUID4)).id
        assert (await client.team.revoke_invitation(UUID4)).message == "Invitation revoked"
        assert (await client.team.update_member(UUID1, TeamMemberUpdateRequest(role="Admin"))).role
        assert (await client.team.remove_member(UUID1)).message == "Member removed"
        accepted = await client.team.accept_invitation(TeamInvitationAcceptRequest(token="a" * 24))
        assert accepted.organization_role == "editor"

        assert (await client.mcp.quota()).requests_limit == 100
        assert (await client.mcp.track()).requests_used == 12

        assert (await client.email.get_preferences()).transactional_enabled is True
        updated = await client.email.update_preferences(
            EmailPreferencesUpdateRequest(
                transactional_enabled=False,
                alerts_enabled=True,
                verification_enabled=True,
            )
        )
        assert updated.alerts_enabled is False
        assert (
            await client.email.unsubscribe(workspace_id=UUID3, token="unsub-token", user_id=UUID1)
        ) == {"message": "You have been unsubscribed."}
