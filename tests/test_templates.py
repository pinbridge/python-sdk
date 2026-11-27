"""Pin templates (DEV-719): list and get templates, publish or schedule a pin drawn from
one, and the typed errors drawing can raise."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

import httpx
import pytest
from _payloads import (
    UUID1,
    UUID3,
    UUID4,
    api_error_body,
    pin_response,
    pin_validation_response,
    schedule_response,
    template_detail_response,
    template_response,
)
from pydantic import ValidationError as PydanticValidationError

from pinbridge_sdk import (
    APIError,
    AsyncPinbridgeClient,
    AuthenticationError,
    NotFoundError,
    PinbridgeClient,
    RenderBusyError,
    RenderUnavailableError,
    TemplateInputsInvalidError,
    TemplatesNotAvailableError,
    ValidationError,
)
from pinbridge_sdk.errors import map_api_error
from pinbridge_sdk.models import (
    Page,
    PinCreate,
    PinImportCreate,
    PinResponse,
    ScheduleCreate,
    ScheduleResponse,
    TemplateDetailResponse,
    TemplateInput,
    TemplateInputProblem,
    TemplateResponse,
)

BASE_URL = "https://api.pinbridge.test"
INPUTS = {"title": "Lemon pasta", "photo": {"src": "https://example.com/pasta.jpg", "zoom": 1.2}}
RUN_AT = datetime(2030, 1, 1, 10, 0, tzinfo=timezone.utc)


def _drawn_pin() -> dict:
    return {**pin_response(), "asset_id": UUID3, "template_id": UUID1, "template_version": 3}


def _drawn_schedule() -> dict:
    return {**schedule_response(), "template_id": UUID1, "template_version": 3}


def _pin(**overrides: object) -> PinCreate:
    fields: dict = {
        "account_id": UUID4,
        "board_id": "123-board",
        "title": "Lemon pasta",
        "idempotency_key": "lemon-pasta-1",
        "template_id": UUID1,
        "template_inputs": INPUTS,
    }
    fields.update(overrides)
    return PinCreate(**fields)


def _schedule(**overrides: object) -> ScheduleCreate:
    fields: dict = {
        "account_id": UUID4,
        "run_at": RUN_AT,
        "board_id": "123-board",
        "title": "Lemon pasta",
        "template_id": UUID1,
        "template_inputs": INPUTS,
    }
    fields.update(overrides)
    return ScheduleCreate(**fields)


# --- templates.list / list_page / get ------------------------------------------------


def _templates_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if (request.method, path) == ("GET", "/v1/templates"):
        params = request.url.params
        if params.get("q") == "default":
            assert dict(params) == {"limit": "50", "offset": "0", "q": "default"}
            return httpx.Response(200, json=[template_response()])
        assert params.get_list("niche") == ["food", "diy"]
        assert {key: params[key] for key in ("limit", "offset", "source", "q", "sort")} == {
            "limit": "10",
            "offset": "20",
            "source": "gallery",
            "q": "pasta",
            "sort": "pins",
        }
        return httpx.Response(
            200, json=[template_response(source="gallery")], headers={"X-Total-Count": "31"}
        )
    if (request.method, path) == ("GET", f"/v1/templates/{UUID1}"):
        if request.url.params.get("gallery") == "true":
            return httpx.Response(200, json={**template_detail_response(), "source": "gallery"})
        assert "gallery" not in request.url.params
        return httpx.Response(200, json=template_detail_response())
    raise AssertionError(f"Unexpected request: {request.method} {request.url}")


def _client(handler) -> PinbridgeClient:  # type: ignore[no-untyped-def]
    return PinbridgeClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))


def test_list_sends_the_filters_and_reads_the_templates() -> None:
    with _client(_templates_handler) as client:
        templates = client.templates.list(
            limit=10, offset=20, source="gallery", niche=["food", "diy"], q="pasta", sort="pins"
        )
        plain = client.templates.list(q="default")

    assert len(templates) == 1
    template = templates[0]
    assert isinstance(template, TemplateResponse)
    assert (template.source, template.version, template.pins_count) == ("gallery", 3, 12)
    assert template.niches == ["food", "diy"]
    assert template.review is None
    assert plain[0].review is not None and plain[0].review.gallery_version == 2
    assert plain[0].maker.name == "Outfit Notes"


def test_list_page_reads_the_total() -> None:
    with _client(_templates_handler) as client:
        page = client.templates.list_page(
            limit=10,
            offset=20,
            source="gallery",
            niche=["food", " ", "diy"],
            q="pasta",
            sort="pins",
        )

    assert isinstance(page, Page)
    assert (page.total, page.limit, page.offset, len(page.items)) == (31, 10, 20, 1)
    assert page.has_more


def test_get_reads_the_inputs_and_the_size() -> None:
    with _client(_templates_handler) as client:
        template = client.templates.get(UUID1)
        listed = client.templates.get(UUID1, gallery=True)

    assert isinstance(template, TemplateDetailResponse)
    assert template.size == (1000, 1500)
    assert template.copied_from is not None and template.copied_from.version == 1
    inputs = template.inputs
    assert list(inputs) == ["title", "photo", "accent", "servings"]
    assert all(isinstance(spec, TemplateInput) for spec in inputs.values())
    assert (inputs["title"].type, inputs["title"].required, inputs["title"].max_length) == (
        "text",
        True,
        60,
    )
    assert inputs["accent"].default == "#D81E2F" and not inputs["accent"].required
    assert (inputs["servings"].min, inputs["servings"].max) == (1, 12)
    assert template.sample_inputs["title"] == "Lemon pasta"
    assert listed.source == "gallery"
    # inputs and size are read from the definition; a dump keeps the API's shape.
    assert "inputs" not in template.model_dump()


def test_a_definition_without_inputs_or_canvas() -> None:
    template = TemplateDetailResponse.model_validate(
        {**template_detail_response(), "definition": {}}
    )

    assert template.inputs == {}
    assert template.size is None


def test_async_list_and_get() -> None:
    async def run() -> (
        tuple[list[TemplateResponse], Page[TemplateResponse], TemplateDetailResponse]
    ):
        async with AsyncPinbridgeClient(
            base_url=BASE_URL, transport=httpx.MockTransport(_templates_handler)
        ) as client:
            listed = await client.templates.list(
                limit=10, offset=20, source="gallery", niche=["food", "diy"], q="pasta", sort="pins"
            )
            page = await client.templates.list_page(
                limit=10, offset=20, source="gallery", niche=("food", "diy"), q="pasta", sort="pins"
            )
            return listed, page, await client.templates.get(UUID1)

    listed, page, template = asyncio.run(run())

    assert listed[0].source == "gallery"
    assert page.total == 31
    assert template.inputs["photo"].type == "image"


def test_a_single_niche_is_sent_once() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get_list("niche") == ["food"]
        return httpx.Response(200, json=[])

    with _client(handler) as client:
        assert client.templates.list(niche="food") == []


# --- templates not turned on for the workspace ----------------------------------------


def _gated(request: httpx.Request) -> httpx.Response:
    # The API's feature gate: a bare FastAPI 404.
    return httpx.Response(404, json={"detail": "Not Found"})


def test_feature_gate_raises_templates_not_available() -> None:
    with _client(_gated) as client:
        with pytest.raises(TemplatesNotAvailableError) as listed:
            client.templates.list()
        with pytest.raises(TemplatesNotAvailableError) as fetched:
            client.templates.get(UUID1)

    for exc in (listed.value, fetched.value):
        assert exc.code == "templates_not_available"
        assert exc.status_code == 404
        assert isinstance(exc.__cause__, NotFoundError)


def test_async_feature_gate_raises_templates_not_available() -> None:
    async def run() -> None:
        async with AsyncPinbridgeClient(
            base_url=BASE_URL, transport=httpx.MockTransport(_gated)
        ) as client:
            await client.templates.get(UUID1)

    with pytest.raises(TemplatesNotAvailableError):
        asyncio.run(run())


def test_an_unknown_template_stays_not_found() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Template not found"})

    with _client(handler) as client:
        with pytest.raises(NotFoundError) as caught:
            client.templates.get(UUID1)

    assert not isinstance(caught.value, TemplatesNotAvailableError)
    assert caught.value.message == "Template not found"


# --- pins and schedules drawn from a template -----------------------------------------


def _draw_handler(seen: list[httpx.Request]):  # type: ignore[no-untyped-def]
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path.endswith("/validate"):
            return httpx.Response(200, json=pin_validation_response())
        if request.url.path.startswith("/v1/schedules"):
            return httpx.Response(201, json=_drawn_schedule())
        return httpx.Response(201, json=_drawn_pin())

    return handler


def _body(request: httpx.Request) -> dict:
    return json.loads(request.content)


def _read_timeout(request: httpx.Request) -> float | None:
    return request.extensions["timeout"]["read"]


def test_create_a_pin_from_a_template() -> None:
    seen: list[httpx.Request] = []
    with _client(_draw_handler(seen)) as client:
        pin = client.pins.create(_pin(template_version=2))

    body = _body(seen[0])
    assert body["template_id"] == UUID1
    assert body["template_version"] == 2
    assert body["template_inputs"] == INPUTS
    assert "image_url" not in body and "asset_id" not in body
    assert isinstance(pin, PinResponse)
    assert (str(pin.template_id), pin.template_version) == (UUID1, 3)


def test_schedule_a_pin_from_a_template() -> None:
    seen: list[httpx.Request] = []
    with _client(_draw_handler(seen)) as client:
        schedule = client.schedules.create(_schedule())

    body = _body(seen[0])
    assert body["template_inputs"] == INPUTS
    assert body["run_at"] == "2030-01-01T10:00:00Z"
    assert "image_url" not in body
    assert isinstance(schedule, ScheduleResponse)
    assert (str(schedule.template_id), schedule.template_version) == (UUID1, 3)


def test_a_plain_dict_payload_works_too() -> None:
    seen: list[httpx.Request] = []
    payload = {
        "account_id": UUID4,
        "board_id": "123-board",
        "title": "Lemon pasta",
        "idempotency_key": "lemon-pasta-2",
        "template_id": UUID1,
        "template_inputs": INPUTS,
    }
    with _client(_draw_handler(seen)) as client:
        client.pins.create(payload)

    assert _body(seen[0]) == payload
    assert _read_timeout(seen[0]) == 90.0


def test_drawing_requests_get_a_longer_read_timeout() -> None:
    seen: list[httpx.Request] = []
    plain = PinCreate(
        account_id=UUID4,
        board_id="123-board",
        title="Photo pin",
        image_url="https://example.com/pin.jpg",
        idempotency_key="photo-1",
    )
    with _client(_draw_handler(seen)) as client:
        client.pins.create(_pin())
        client.pins.validate(_pin())
        client.schedules.create(_schedule())
        client.schedules.validate(_schedule())
        client.pins.create(plain)

    assert [_read_timeout(request) for request in seen] == [90.0, 90.0, 90.0, 90.0, 30.0]
    # Only the read timeout grows.
    assert seen[0].extensions["timeout"]["connect"] == 30.0


def test_a_longer_or_disabled_client_timeout_is_kept() -> None:
    seen: list[httpx.Request] = []
    transport = httpx.MockTransport(_draw_handler(seen))
    with PinbridgeClient(base_url=BASE_URL, transport=transport, timeout=120.0) as client:
        client.pins.create(_pin())
    with PinbridgeClient(base_url=BASE_URL, transport=transport, timeout=None) as client:
        client.pins.create(_pin())

    assert [_read_timeout(request) for request in seen] == [120.0, None]


def test_async_drawing_requests_get_a_longer_read_timeout() -> None:
    seen: list[httpx.Request] = []

    async def run() -> None:
        async with AsyncPinbridgeClient(
            base_url=BASE_URL, transport=httpx.MockTransport(_draw_handler(seen))
        ) as client:
            await client.pins.create(_pin())
            await client.pins.validate(_pin())
            await client.schedules.create(_schedule())
            await client.schedules.validate(_schedule())

    asyncio.run(run())

    assert [_read_timeout(request) for request in seen] == [90.0, 90.0, 90.0, 90.0]


# --- model checks, the same as the API's ----------------------------------------------


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"template_id": None}, "template_inputs needs template_id"),
        ({"image_url": "https://example.com/pin.jpg"}, "not both: with template_inputs"),
        ({"asset_id": UUID3}, "Provide template_inputs or an image"),
        ({"template_inputs": None}, "Either image_url, asset_id or template_inputs"),
        (
            {"template_id": None, "template_inputs": None, "image_url": "https://e.com/a.jpg"},
            None,
        ),
        (
            {
                "template_id": None,
                "template_inputs": None,
                "template_version": 2,
                "image_url": "https://e.com/a.jpg",
            },
            "template_version needs template_id",
        ),
        ({"template_version": 0}, "greater than or equal to 1"),
    ],
)
def test_pin_and_schedule_template_checks(overrides: dict, message: str | None) -> None:
    for build in (_pin, _schedule):
        if message is None:
            build(**overrides)
            continue
        with pytest.raises(PydanticValidationError, match=message):
            build(**overrides)


def test_template_id_next_to_an_image_only_records_it() -> None:
    pin = _pin(template_inputs=None, asset_id=UUID3, template_version=3)

    dumped = pin.model_dump(mode="json", exclude_none=True)
    assert (dumped["template_id"], dumped["template_version"], dumped["asset_id"]) == (
        UUID1,
        3,
        UUID3,
    )
    assert "template_inputs" not in dumped


def test_import_rows_refuse_template_inputs() -> None:
    with pytest.raises(PydanticValidationError, match="template_inputs can't be imported yet"):
        PinImportCreate(
            account_id=UUID4,
            board_id="123-board",
            title="Imported",
            idempotency_key="import-1",
            template_id=UUID1,
            template_inputs=INPUTS,
        )


def test_older_responses_without_template_fields() -> None:
    assert PinResponse.model_validate(pin_response()).template_id is None
    assert ScheduleResponse.model_validate(schedule_response()).template_version is None


# --- typed errors ---------------------------------------------------------------------


def _error(status: int, body: dict, headers: dict | None = None) -> APIError:
    request = httpx.Request("POST", f"{BASE_URL}/v1/pins")
    return map_api_error(httpx.Response(status, json=body, headers=headers, request=request))


def test_template_inputs_invalid_lists_every_problem() -> None:
    err = _error(
        422,
        api_error_body(
            "template_inputs_invalid",
            "Some template_inputs can't be used with this template.",
            remediation="Fix each entry of problems.",
            problems=[
                {
                    "input": "title",
                    "code": "too_long",
                    "message": '"title" has 72 characters, the maximum is 60',
                    "length": 72,
                    "max_length": 60,
                },
                {"input": "photo", "code": "required", "message": '"photo" is required'},
                {
                    "input": "servings",
                    "code": "out_of_range",
                    "message": '"servings" is 20, it must be from 1 to 12',
                    "value": 20,
                    "min": 1,
                    "max": 12,
                },
            ],
        ),
    )

    assert isinstance(err, TemplateInputsInvalidError)
    # Code that caught ValidationError for any 422 still catches it.
    assert isinstance(err, ValidationError)
    assert err.code == "template_inputs_invalid"
    problems = err.problems
    assert all(isinstance(problem, TemplateInputProblem) for problem in problems)
    assert [(p.input, p.code) for p in problems] == [
        ("title", "too_long"),
        ("photo", "required"),
        ("servings", "out_of_range"),
    ]
    assert (problems[0].length, problems[0].max_length) == (72, 60)
    assert (problems[2].value, problems[2].min, problems[2].max) == (20, 1, 12)


def test_problems_also_read_from_detail_only() -> None:
    body = api_error_body("template_inputs_invalid", "Bad inputs.", problems=[])
    body["detail"]["error"]["problems"] = [{"input": "x", "code": "unknown_input", "message": "?"}]
    del body["error"]

    err = _error(422, body)

    assert isinstance(err, TemplateInputsInvalidError)
    assert [p.code for p in err.problems] == ["unknown_input"]


def test_templates_not_available_is_not_an_authentication_error() -> None:
    err = _error(
        403,
        api_error_body(
            "templates_not_available",
            "Drawing pins from templates is not available for this workspace yet.",
            remediation="Send the image as image_url or asset_id.",
        ),
    )

    assert isinstance(err, TemplatesNotAvailableError)
    assert not isinstance(err, AuthenticationError)
    assert err.status_code == 403


def test_render_unavailable_carries_retry_after_and_reason() -> None:
    err = _error(
        503,
        api_error_body(
            "render_unavailable", "Pins can't be drawn from templates right now.", reason="timeout"
        ),
        headers={"Retry-After": "5"},
    )

    assert type(err) is RenderUnavailableError
    assert (err.retry_after, err.reason) == (5, "timeout")


def test_render_busy_is_a_render_unavailable_error() -> None:
    err = _error(
        503,
        api_error_body(
            "render_busy", "Every renderer is busy, so the pin wasn't drawn.", reason="queue_full"
        ),
        headers={"Retry-After": "12"},
    )

    assert isinstance(err, RenderBusyError)
    assert isinstance(err, RenderUnavailableError)
    assert (err.retry_after, err.reason, err.status_code) == (12, "queue_full", 503)


def test_render_errors_without_retry_after() -> None:
    err = _error(503, api_error_body("render_busy", "Busy."))

    assert isinstance(err, RenderBusyError)
    assert err.retry_after is None
    assert err.reason is None


def test_create_raises_the_typed_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503, json=api_error_body("render_busy", "Busy."), headers={"Retry-After": "3"}
        )

    with _client(handler) as client:
        with pytest.raises(RenderBusyError) as caught:
            client.schedules.create(_schedule())

    assert caught.value.retry_after == 3


def test_other_template_codes_keep_their_status_class() -> None:
    err = _error(
        422,
        api_error_body(
            "template_version_not_found", "The template has no version 9.", current_version=3
        ),
    )

    assert type(err) is ValidationError
    assert err.code == "template_version_not_found"
