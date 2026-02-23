"""SDK exception hierarchy."""

from __future__ import annotations

from typing import Any

import httpx


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

    if response.status_code in {401, 403}:
        return AuthenticationError(**kwargs)
    if response.status_code == 404:
        return NotFoundError(**kwargs)
    if response.status_code == 422:
        return ValidationError(**kwargs)
    if response.status_code == 429:
        return RateLimitError(**kwargs)
    return APIError(**kwargs)
