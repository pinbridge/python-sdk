"""Asset resources."""

from __future__ import annotations

from collections.abc import Sequence
from mimetypes import guess_type
from pathlib import Path
from typing import Any, BinaryIO
from uuid import UUID

from ..models.assets import (
    AssetDeleteResponse,
    AssetListResponse,
    AssetResponse,
    BulkAssetDeleteResponse,
)
from .base import AsyncAPIResource, SyncAPIResource

UploadableFile = bytes | bytearray | str | Path | BinaryIO


def _normalize_upload(
    file: UploadableFile,
    *,
    filename: str | None,
    content_type: str | None,
) -> tuple[str, bytes, str]:
    if isinstance(file, (bytes, bytearray)):
        resolved_filename = filename or "upload.bin"
        resolved_content_type = (
            content_type or guess_type(resolved_filename)[0] or "application/octet-stream"
        )
        return resolved_filename, bytes(file), resolved_content_type

    if isinstance(file, (str, Path)):
        path = Path(file)
        resolved_filename = filename or path.name
        resolved_content_type = (
            content_type or guess_type(resolved_filename)[0] or "application/octet-stream"
        )
        return resolved_filename, path.read_bytes(), resolved_content_type

    resolved_filename = filename or Path(getattr(file, "name", "upload.bin")).name
    resolved_content_type = (
        content_type or guess_type(resolved_filename)[0] or "application/octet-stream"
    )
    return resolved_filename, file.read(), resolved_content_type


def _serialize_asset_list_params(
    *,
    workspace_id: UUID | str | None,
    sort: str,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    params: dict[str, Any] = {"sort": sort, "limit": limit, "offset": offset}
    if workspace_id is not None:
        params["workspace_id"] = str(workspace_id)
    return params


def _serialize_bulk_asset_delete(
    asset_ids: Sequence[UUID | str],
    *,
    confirm: bool,
) -> dict[str, Any]:
    return {"asset_ids": [str(asset_id) for asset_id in asset_ids], "confirm": confirm}


class AssetsResource(SyncAPIResource):
    def _upload(
        self,
        path: str,
        file: UploadableFile,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> AssetResponse:
        resolved_filename, body, resolved_content_type = _normalize_upload(
            file,
            filename=filename,
            content_type=content_type,
        )
        response = self._request(
            "POST",
            path,
            files={"file": (resolved_filename, body, resolved_content_type)},
        )
        return self._model(AssetResponse, response)

    def upload_image(
        self,
        file: UploadableFile,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> AssetResponse:
        return self._upload(
            "/v1/assets/images",
            file,
            filename=filename,
            content_type=content_type,
        )

    def upload_video(
        self,
        file: UploadableFile,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> AssetResponse:
        return self._upload(
            "/v1/assets/videos",
            file,
            filename=filename,
            content_type=content_type,
        )

    def get(self, asset_id: UUID | str) -> AssetResponse:
        response = self._request(
            "GET",
            "/v1/assets/{asset_id}",
            path_params={"asset_id": asset_id},
        )
        return self._model(AssetResponse, response)

    def get_content(self, asset_id: UUID | str) -> bytes:
        response = self._request(
            "GET",
            "/v1/assets/{asset_id}/content",
            path_params={"asset_id": asset_id},
        )
        return bytes(response.content)

    def list(
        self,
        *,
        workspace_id: UUID | str | None = None,
        sort: str = "created_at_desc",
        limit: int = 50,
        offset: int = 0,
    ) -> AssetListResponse:
        response = self._request(
            "GET",
            "/v1/assets",
            params=_serialize_asset_list_params(
                workspace_id=workspace_id,
                sort=sort,
                limit=limit,
                offset=offset,
            ),
        )
        return self._model(AssetListResponse, response)

    def delete(self, asset_id: UUID | str, *, confirm: bool = False) -> AssetDeleteResponse:
        response = self._request(
            "DELETE",
            "/v1/assets/{asset_id}",
            path_params={"asset_id": asset_id},
            params={"confirm": confirm},
        )
        return self._model(AssetDeleteResponse, response)

    def bulk_delete(
        self,
        asset_ids: Sequence[UUID | str],
        *,
        confirm: bool = False,
    ) -> BulkAssetDeleteResponse:
        response = self._request(
            "DELETE",
            "/v1/assets",
            json=_serialize_bulk_asset_delete(asset_ids, confirm=confirm),
        )
        return self._model(BulkAssetDeleteResponse, response)


class AsyncAssetsResource(AsyncAPIResource):
    async def _upload(
        self,
        path: str,
        file: UploadableFile,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> AssetResponse:
        resolved_filename, body, resolved_content_type = _normalize_upload(
            file,
            filename=filename,
            content_type=content_type,
        )
        response = await self._request(
            "POST",
            path,
            files={"file": (resolved_filename, body, resolved_content_type)},
        )
        return self._model(AssetResponse, response)

    async def upload_image(
        self,
        file: UploadableFile,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> AssetResponse:
        return await self._upload(
            "/v1/assets/images",
            file,
            filename=filename,
            content_type=content_type,
        )

    async def upload_video(
        self,
        file: UploadableFile,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> AssetResponse:
        return await self._upload(
            "/v1/assets/videos",
            file,
            filename=filename,
            content_type=content_type,
        )

    async def get(self, asset_id: UUID | str) -> AssetResponse:
        response = await self._request(
            "GET",
            "/v1/assets/{asset_id}",
            path_params={"asset_id": asset_id},
        )
        return self._model(AssetResponse, response)

    async def get_content(self, asset_id: UUID | str) -> bytes:
        response = await self._request(
            "GET",
            "/v1/assets/{asset_id}/content",
            path_params={"asset_id": asset_id},
        )
        return bytes(response.content)

    async def list(
        self,
        *,
        workspace_id: UUID | str | None = None,
        sort: str = "created_at_desc",
        limit: int = 50,
        offset: int = 0,
    ) -> AssetListResponse:
        response = await self._request(
            "GET",
            "/v1/assets",
            params=_serialize_asset_list_params(
                workspace_id=workspace_id,
                sort=sort,
                limit=limit,
                offset=offset,
            ),
        )
        return self._model(AssetListResponse, response)

    async def delete(self, asset_id: UUID | str, *, confirm: bool = False) -> AssetDeleteResponse:
        response = await self._request(
            "DELETE",
            "/v1/assets/{asset_id}",
            path_params={"asset_id": asset_id},
            params={"confirm": confirm},
        )
        return self._model(AssetDeleteResponse, response)

    async def bulk_delete(
        self,
        asset_ids: Sequence[UUID | str],
        *,
        confirm: bool = False,
    ) -> BulkAssetDeleteResponse:
        response = await self._request(
            "DELETE",
            "/v1/assets",
            json=_serialize_bulk_asset_delete(asset_ids, confirm=confirm),
        )
        return self._model(BulkAssetDeleteResponse, response)
