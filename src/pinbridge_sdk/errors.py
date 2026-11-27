"""SDK exception hierarchy."""

from __future__ import annotations

from typing import Any

import httpx

from .models.templates import TemplateInputProblem


class PinbridgeError(Exception):
    """Base SDK error."""


class APIError(PinbridgeError):
    """Represents a non-2xx API response."""

    def __init__(
        self,
        *,
        status_code: int,
        message: str,
        code: str | None = None,
        details: Any = None,
        response: httpx.Response | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.code = code
        self.details = details
        self.response = response
        super().__init__(f"[{status_code}] {message}")


class AuthenticationError(APIError):
    """Authentication or authorization failure."""


class NotFoundError(APIError):
    """Resource was not found."""


class RateLimitError(APIError):
    """API rate limit exceeded."""


class ValidationError(APIError):
    """Input payload was invalid."""


def _envelope(details: Any) -> dict[str, Any]:
    """The ``error`` envelope of an API error body, or an empty dict."""
    if not isinstance(details, dict):
        return {}
    error = details.get("error")
    if isinstance(error, dict):
        return error
    detail = details.get("detail")
    if isinstance(detail, dict) and isinstance(detail.get("error"), dict):
        return detail["error"]
    return {}


class TemplateInputsInvalidError(ValidationError):
    """422 ``template_inputs_invalid``: some ``template_inputs`` can't be used.

    :attr:`problems` lists every problem at once, one entry per input.
    ``client.templates.get(template_id).inputs`` shows what each input takes.
    """

    @property
    def problems(self) -> list[TemplateInputProblem]:
        raw = _envelope(self.details).get("problems")
        if not isinstance(raw, list):
            return []
        return [TemplateInputProblem.model_validate(item) for item in raw if isinstance(item, dict)]


class TemplatesNotAvailableError(APIError):
    """Pin templates are not turned on for this workspace yet.

    The API answers ``403 templates_not_available`` to a pin or schedule sent with
    ``template_inputs``. Its template routes answer a bare ``404 Not Found`` instead,
    which ``client.templates`` raises as this error (``code`` is set to
    ``templates_not_available`` and ``status_code`` stays 404). Send the image as
    ``image_url`` or ``asset_id``.
    """


class RenderUnavailableError(APIError):
    """503 ``render_unavailable``: pins can't be drawn from templates right now.

    Nothing was created. Try again after :attr:`retry_after` seconds, or send the
    image as ``image_url`` or ``asset_id``. :attr:`reason` says what went wrong
    (for example ``timeout`` or ``unreachable``) when the API tells.
    """

    @property
    def retry_after(self) -> int | None:
        """Seconds from the ``Retry-After`` header, when the API sent one."""
        if self.response is None:
            return None
        try:
            return int(self.response.headers.get("retry-after", ""))
        except ValueError:
            return None

    @property
    def reason(self) -> str | None:
        reason = _envelope(self.details).get("reason")
        return reason if isinstance(reason, str) else None


class RenderBusyError(RenderUnavailableError):
    """503 ``render_busy``: every renderer is busy, so the pin wasn't drawn.

    Nothing was created. Send the same request again after :attr:`retry_after`
    seconds (1 to 60). Catching :class:`RenderUnavailableError` also catches this.
    """


# Typed errors chosen by the API's stable ``code`` before the status code decides.
_ERRORS_BY_CODE: dict[str, type[APIError]] = {
    "template_inputs_invalid": TemplateInputsInvalidError,
    "templates_not_available": TemplatesNotAvailableError,
    "render_unavailable": RenderUnavailableError,
    "render_busy": RenderBusyError,
}


def _extract_error_payload(response: httpx.Response) -> tuple[str, str | None, Any]:
    """Parse message/code from common API error payloads."""
    details: Any
    try:
        details = response.json()
    except ValueError:
        text = response.text.strip()
        return text or "Request failed", None, text or None

    if isinstance(details, dict):
        detail = details.get("detail")
        if isinstance(detail, str):
            return detail, None, details
        if isinstance(detail, dict):
            if isinstance(detail.get("message"), str):
                code = detail.get("code")
                return detail["message"], code if isinstance(code, str) else None, details

        if isinstance(details.get("message"), str):
            code = details.get("code")
            return details["message"], code if isinstance(code, str) else None, details

    return "Request failed", None, details


def map_api_error(response: httpx.Response) -> APIError:
    """Convert a response into a typed APIError."""
    message, code, details = _extract_error_payload(response)
    kwargs = {
        "status_code": response.status_code,
        "message": message,
        "code": code,
        "details": details,
        "response": response,
    }

    if code in _ERRORS_BY_CODE:
        return _ERRORS_BY_CODE[code](**kwargs)
    if response.status_code in {401, 403}:
        return AuthenticationError(**kwargs)
    if response.status_code == 404:
        return NotFoundError(**kwargs)
    if response.status_code == 422:
        return ValidationError(**kwargs)
    if response.status_code == 429:
        return RateLimitError(**kwargs)
    return APIError(**kwargs)
