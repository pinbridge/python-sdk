"""Pin template resources (API 1.70.0+)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

import httpx

from ..errors import NotFoundError, TemplatesNotAvailableError
from ..models.pagination import Page
from ..models.templates import (
    TemplateDetailResponse,
    TemplateResponse,
    TemplateSort,
    TemplateSource,
)
from .base import AsyncAPIResource, SyncAPIResource


def _serialize_template_filters(
    *,
    limit: int,
    offset: int,
    source: TemplateSource | str | None,
    niche: Sequence[str] | str | None,
    q: str | None,
    sort: TemplateSort | str | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if source is not None:
        params["source"] = source
    if niche is not None:
        slugs = [niche] if isinstance(niche, str) else list(niche)
        slugs = [slug for slug in slugs if slug.strip()]
        if slugs:
            # Repeated as niche=food&niche=diy.
            params["niche"] = slugs
    if q is not None:
        params["q"] = q
    if sort is not None:
        params["sort"] = sort
    return params


def _feature_gate(exc: NotFoundError) -> bool:
    """A bare 404 "Not Found" on a template route: the workspace has no pin templates.

    The API's feature gate answers it; a template the workspace can't see is
    "Template not found" instead.
    """
    return exc.code is None and exc.message.strip().lower() == "not found"


def _templates_not_available(exc: NotFoundError) -> TemplatesNotAvailableError:
    return TemplatesNotAvailableError(
        status_code=exc.status_code,
        message="Pin templates are not turned on for this workspace yet.",
        code="templates_not_available",
        details=exc.details,
        response=exc.response,
    )


class TemplatesResource(SyncAPIResource):
    def _get(self, path: str, **kwargs: Any) -> httpx.Response:
        try:
            return self._request("GET", path, **kwargs)
        except NotFoundError as exc:
            if _feature_gate(exc):
                raise _templates_not_available(exc) from exc
            raise

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        source: TemplateSource | str | None = None,
        niche: Sequence[str] | str | None = None,
        q: str | None = None,
        sort: TemplateSort | str | None = None,
    ) -> list[TemplateResponse]:
        """List the workspace's own templates and the gallery, without archived ones.

        ``source="workspace"`` keeps the workspace's own, ``"gallery"`` the approved
        templates of every workspace; both when left out. ``niche`` takes one or more
        niche slugs such as ``food``. ``q`` searches name, description and tags.
        ``sort`` is ``updated`` (the default), ``pins``, ``copies`` or ``name``. Use
        :meth:`list_page` to also get the total.

        Raises :class:`~pinbridge_sdk.errors.TemplatesNotAvailableError` when the
        workspace does not have pin templates.
        """
        params = _serialize_template_filters(
            limit=limit, offset=offset, source=source, niche=niche, q=q, sort=sort
        )
        response = self._get("/v1/templates", params=params)
        return self._list(TemplateResponse, response)

    def list_page(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        source: TemplateSource | str | None = None,
        niche: Sequence[str] | str | None = None,
        q: str | None = None,
        sort: TemplateSort | str | None = None,
    ) -> Page[TemplateResponse]:
        """Same filters as :meth:`list`, plus the total matching templates."""
        params = _serialize_template_filters(
            limit=limit, offset=offset, source=source, niche=niche, q=q, sort=sort
        )
        response = self._get("/v1/templates", params=params)
        return self._page(TemplateResponse, response, limit=limit, offset=offset)

    def get(self, template_id: UUID | str, *, gallery: bool = False) -> TemplateDetailResponse:
        """Get a workspace or gallery template with its definition.

        ``inputs`` on the result lists what ``template_inputs`` takes. ``gallery=True``
        returns the gallery listing, as approved, even for the workspace's own
        template. An unknown id raises :class:`~pinbridge_sdk.errors.NotFoundError`.
        """
        params: Mapping[str, Any] | None = {"gallery": "true"} if gallery else None
        response = self._get(
            "/v1/templates/{template_id}",
            path_params={"template_id": template_id},
            params=params,
        )
        return self._model(TemplateDetailResponse, response)


class AsyncTemplatesResource(AsyncAPIResource):
    async def _get(self, path: str, **kwargs: Any) -> httpx.Response:
        try:
            return await self._request("GET", path, **kwargs)
        except NotFoundError as exc:
            if _feature_gate(exc):
                raise _templates_not_available(exc) from exc
            raise

    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        source: TemplateSource | str | None = None,
        niche: Sequence[str] | str | None = None,
        q: str | None = None,
        sort: TemplateSort | str | None = None,
    ) -> list[TemplateResponse]:
        """List the workspace's own templates and the gallery (see ``TemplatesResource.list``)."""
        params = _serialize_template_filters(
            limit=limit, offset=offset, source=source, niche=niche, q=q, sort=sort
        )
        response = await self._get("/v1/templates", params=params)
        return self._list(TemplateResponse, response)

    async def list_page(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        source: TemplateSource | str | None = None,
        niche: Sequence[str] | str | None = None,
        q: str | None = None,
        sort: TemplateSort | str | None = None,
    ) -> Page[TemplateResponse]:
        """Same filters as :meth:`list`, plus the total matching templates."""
        params = _serialize_template_filters(
            limit=limit, offset=offset, source=source, niche=niche, q=q, sort=sort
        )
        response = await self._get("/v1/templates", params=params)
        return self._page(TemplateResponse, response, limit=limit, offset=offset)

    async def get(
        self, template_id: UUID | str, *, gallery: bool = False
    ) -> TemplateDetailResponse:
        """Get a workspace or gallery template with its definition."""
        params: Mapping[str, Any] | None = {"gallery": "true"} if gallery else None
        response = await self._get(
            "/v1/templates/{template_id}",
            path_params={"template_id": template_id},
            params=params,
        )
        return self._model(TemplateDetailResponse, response)
