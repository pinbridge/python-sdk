"""Asset resources."""

from __future__ import annotations

from mimetypes import guess_type
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from ..models.assets import AssetResponse
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
            content_type
            or guess_type(resolved_filename)[0]
            or "application/octet-stream"
        )
        return resolved_filename, bytes(file), resolved_content_type

    if isinstance(file, (str, Path)):
        path = Path(file)
        resolved_filename = filename or path.name
        resolved_content_type = (
            content_type
            or guess_type(resolved_filename)[0]
            or "application/octet-stream"
        )
        return resolved_filename, path.read_bytes(), resolved_content_type

    resolved_filename = filename or Path(getattr(file, "name", "upload.bin")).name
    resolved_content_type = (
        content_type
        or guess_type(resolved_filename)[0]
        or "application/octet-stream"
    )
    return resolved_filename, file.read(), resolved_content_type


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
