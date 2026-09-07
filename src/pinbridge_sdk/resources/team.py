"""Team invitation and membership resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from ..models.team import (
    TeamActionResponse,
    TeamInvitationAcceptRequest,
    TeamInvitationAcceptResponse,
    TeamInvitationCreateRequest,
    TeamInvitationPreviewResponse,
    TeamInvitationResponse,
    TeamInvitationsListResponse,
    TeamMemberResponse,
    TeamMembersListResponse,
    TeamMemberUpdateRequest,
)
from .base import AsyncAPIResource, SyncAPIResource


def _serialize(
    data: (
        TeamInvitationCreateRequest
        | TeamMemberUpdateRequest
        | TeamInvitationAcceptRequest
        | Mapping[str, Any]
    ),
) -> dict[str, Any]:
    if isinstance(
        data,
        (TeamInvitationCreateRequest, TeamMemberUpdateRequest, TeamInvitationAcceptRequest),
    ):
        return data.model_dump(mode="json", exclude_none=True)
    return dict(data)


class TeamResource(SyncAPIResource):
    def preview_invitation(self, token: str) -> TeamInvitationPreviewResponse:
        response = self._request("GET", "/v1/team/invitations/preview", params={"token": token})
        return self._model(TeamInvitationPreviewResponse, response)

    def list_members(self) -> TeamMembersListResponse:
        response = self._request("GET", "/v1/team/members")
        return self._model(TeamMembersListResponse, response)

    def list_invitations(self) -> TeamInvitationsListResponse:
        response = self._request("GET", "/v1/team/invitations")
        return self._model(TeamInvitationsListResponse, response)

    def create_invitation(
        self, data: TeamInvitationCreateRequest | Mapping[str, Any]
    ) -> TeamInvitationResponse:
        response = self._request("POST", "/v1/team/invitations", json=_serialize(data))
        return self._model(TeamInvitationResponse, response)

    def resend_invitation(self, invitation_id: UUID | str) -> TeamInvitationResponse:
        response = self._request(
            "POST",
            "/v1/team/invitations/{invitation_id}/resend",
            path_params={"invitation_id": invitation_id},
        )
        return self._model(TeamInvitationResponse, response)

    def revoke_invitation(self, invitation_id: UUID | str) -> TeamActionResponse:
        response = self._request(
            "DELETE",
            "/v1/team/invitations/{invitation_id}",
            path_params={"invitation_id": invitation_id},
        )
        return self._model(TeamActionResponse, response)

    def update_member(
        self,
        member_id: UUID | str,
        data: TeamMemberUpdateRequest | Mapping[str, Any],
    ) -> TeamMemberResponse:
        response = self._request(
            "PATCH",
            "/v1/team/members/{member_id}",
            path_params={"member_id": member_id},
            json=_serialize(data),
        )
        return self._model(TeamMemberResponse, response)

    def remove_member(self, member_id: UUID | str) -> TeamActionResponse:
        response = self._request(
            "DELETE",
            "/v1/team/members/{member_id}",
            path_params={"member_id": member_id},
        )
        return self._model(TeamActionResponse, response)

    def accept_invitation(
        self, data: TeamInvitationAcceptRequest | Mapping[str, Any]
    ) -> TeamInvitationAcceptResponse:
        response = self._request("POST", "/v1/team/invitations/accept", json=_serialize(data))
        return self._model(TeamInvitationAcceptResponse, response)


class AsyncTeamResource(AsyncAPIResource):
    async def preview_invitation(self, token: str) -> TeamInvitationPreviewResponse:
        response = await self._request(
            "GET", "/v1/team/invitations/preview", params={"token": token}
        )
        return self._model(TeamInvitationPreviewResponse, response)

    async def list_members(self) -> TeamMembersListResponse:
        response = await self._request("GET", "/v1/team/members")
        return self._model(TeamMembersListResponse, response)

    async def list_invitations(self) -> TeamInvitationsListResponse:
        response = await self._request("GET", "/v1/team/invitations")
        return self._model(TeamInvitationsListResponse, response)

    async def create_invitation(
        self, data: TeamInvitationCreateRequest | Mapping[str, Any]
    ) -> TeamInvitationResponse:
        response = await self._request("POST", "/v1/team/invitations", json=_serialize(data))
        return self._model(TeamInvitationResponse, response)

    async def resend_invitation(self, invitation_id: UUID | str) -> TeamInvitationResponse:
        response = await self._request(
            "POST",
            "/v1/team/invitations/{invitation_id}/resend",
            path_params={"invitation_id": invitation_id},
        )
        return self._model(TeamInvitationResponse, response)

    async def revoke_invitation(self, invitation_id: UUID | str) -> TeamActionResponse:
        response = await self._request(
            "DELETE",
            "/v1/team/invitations/{invitation_id}",
            path_params={"invitation_id": invitation_id},
        )
        return self._model(TeamActionResponse, response)

    async def update_member(
        self,
        member_id: UUID | str,
        data: TeamMemberUpdateRequest | Mapping[str, Any],
    ) -> TeamMemberResponse:
        response = await self._request(
            "PATCH",
            "/v1/team/members/{member_id}",
            path_params={"member_id": member_id},
            json=_serialize(data),
        )
        return self._model(TeamMemberResponse, response)

    async def remove_member(self, member_id: UUID | str) -> TeamActionResponse:
        response = await self._request(
            "DELETE",
            "/v1/team/members/{member_id}",
            path_params={"member_id": member_id},
        )
        return self._model(TeamActionResponse, response)

    async def accept_invitation(
        self, data: TeamInvitationAcceptRequest | Mapping[str, Any]
    ) -> TeamInvitationAcceptResponse:
        response = await self._request("POST", "/v1/team/invitations/accept", json=_serialize(data))
        return self._model(TeamInvitationAcceptResponse, response)
