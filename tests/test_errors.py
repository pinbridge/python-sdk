from __future__ import annotations

import httpx
import pytest

from pinbridge_sdk.errors import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    _extract_error_payload,
    map_api_error,
)


def _response(status: int, payload: object) -> httpx.Response:
    request = httpx.Request("GET", "https://api.pinbridge.test/test")
    if isinstance(payload, str):
        return httpx.Response(status, text=payload, request=request)
    return httpx.Response(status, json=payload, request=request)


@pytest.mark.parametrize(
    ("payload", "expected_message", "expected_code"),
    [
        ({"detail": "Invalid token"}, "Invalid token", None),
        ({"detail": {"message": "Nested", "code": "nested_code"}}, "Nested", "nested_code"),
        ({"message": "Top", "code": "top_code"}, "Top", "top_code"),
        ({"unexpected": True}, "Request failed", None),
        ("plain text body", "plain text body", None),
    ],
)
def test_extract_error_payload(
    payload: object, expected_message: str, expected_code: str | None
) -> None:
    message, code, details = _extract_error_payload(_response(400, payload))
    assert message == expected_message
    assert code == expected_code
    assert details is not None


@pytest.mark.parametrize(
    ("status", "error_type"),
    [
        (401, AuthenticationError),
        (403, AuthenticationError),
        (404, NotFoundError),
        (422, ValidationError),
        (429, RateLimitError),
        (500, APIError),
    ],
)
def test_map_api_error_types(status: int, error_type: type[APIError]) -> None:
    err = map_api_error(_response(status, {"detail": "boom"}))
    assert isinstance(err, error_type)
    assert err.status_code == status
