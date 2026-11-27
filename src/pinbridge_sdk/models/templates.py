"""Pin template models (API 1.70.0+)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from .base import PinbridgeModel

# Where ``GET /v1/templates`` looks: the gallery (approved templates of every workspace,
# as approved) or the workspace's own. Both when left out.
TemplateSource = Literal["gallery", "workspace"]
# pins or copies: most used first; name: A to Z; updated: newest first (the default).
TemplateSort = Literal["pins", "copies", "name", "updated"]


class TemplateMaker(PinbridgeModel):
    """Who made a template: the company name of its workspace, when one is set."""

    name: str | None = None


class TemplateReview(PinbridgeModel):
    """Where one of the workspace's own templates stands with the gallery.

    ``status`` is ``draft``, ``pending``, ``approved``, ``denied`` or ``taken_down``;
    ``note`` gives PinBridge's reason for a denial or take-down.
    """

    status: str
    note: str | None = None
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    # The approved version the gallery shows; None when not listed.
    gallery_version: int | None = None


class TemplateCopiedFrom(PinbridgeModel):
    """The template a workspace template was copied from, and the version copied."""

    id: UUID
    name: str
    version: int


class TemplateInput(PinbridgeModel):
    """One input of a template: a value a pin drawn from it can set.

    ``type`` is ``text``, ``image``, ``color`` or ``number``. Text inputs may set
    ``min_length`` / ``max_length`` (characters), number inputs ``min`` / ``max``.
    An input that is not ``required`` falls back to ``default`` or to what the
    template shows.
    """

    type: str
    label: str | None = None
    required: bool = False
    min_length: int | None = None
    max_length: int | None = None
    min: float | None = None
    max: float | None = None
    default: Any = None


class TemplateResponse(PinbridgeModel):
    """A pin template in a list (``GET /v1/templates``).

    ``source`` is ``workspace`` for the workspace's own template, as it is now, and
    ``gallery`` for an approved gallery template, as it was approved. ``version`` is
    the current version, or the approved one for the gallery.
    """

    id: UUID
    # The template's own id from its definition.
    key: str
    name: str
    description: str | None = None
    niches: list[str] = Field(default_factory=list)
    # Deprecated by the API in favour of niches: the first of them.
    niche: str | None = None
    tags: list[str] = Field(default_factory=list)
    source: str
    version: int
    # public: offered to the gallery after review; private: this workspace only.
    visibility: str
    maker: TemplateMaker = Field(default_factory=TemplateMaker)
    # Gallery review of the workspace's own template; None for others.
    review: TemplateReview | None = None
    copied_from: TemplateCopiedFrom | None = None
    copies_count: int = 0
    pins_count: int = 0
    uses_custom_fonts: bool = False
    # Uses fonts or images the workspace uploaded; such a template can only be private.
    uses_uploads: bool = False
    created_at: datetime
    updated_at: datetime


class TemplateDetailResponse(TemplateResponse):
    """A pin template with its definition and preview values (``GET /v1/templates/{id}``).

    :attr:`inputs` reads the inputs a pin can set from the definition, and
    :attr:`size` the size the template draws pins at.
    """

    # The template document (pin-template format).
    definition: dict[str, Any] = Field(default_factory=dict)
    # Values for previews. Image inputs hold sample photo file names, or objects with src
    # and focus.
    sample_inputs: dict[str, Any] = Field(default_factory=dict)

    @property
    def inputs(self) -> dict[str, TemplateInput]:
        """The template's inputs by name, as ``template_inputs`` takes them."""
        raw = self.definition.get("inputs")
        if not isinstance(raw, dict):
            return {}
        return {
            name: TemplateInput.model_validate(spec)
            for name, spec in raw.items()
            if isinstance(spec, dict)
        }

    @property
    def size(self) -> tuple[int, int] | None:
        """``(width, height)`` in pixels of the pins this template draws, when known."""
        canvas = self.definition.get("canvas")
        if not isinstance(canvas, dict):
            return None
        width, height = canvas.get("width"), canvas.get("height")
        if isinstance(width, int) and isinstance(height, int):
            return width, height
        return None


class TemplateInputProblem(PinbridgeModel):
    """One problem of a ``template_inputs_invalid`` error.

    ``code`` is for example ``required``, ``unknown_input``, ``wrong_type``,
    ``too_short``, ``too_long``, ``out_of_range``, ``photo_unreachable`` or
    ``asset_not_found``; new codes may appear. The limits are set for the codes
    they explain.
    """

    # The input's name.
    input: str | None = None
    code: str
    message: str
    # too_short / too_long: the text's length and the input's limits.
    length: int | None = None
    min_length: int | None = None
    max_length: int | None = None
    # out_of_range: the number sent and the input's limits.
    value: float | None = None
    min: float | None = None
    max: float | None = None
