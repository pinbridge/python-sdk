# PinBridge Python SDK

Official Python SDK for the PinBridge API, including multipart image and video asset upload support for local publishing workflows.

Documentation in this repository is built with MkDocs. After installing docs dependencies,
run `python scripts/generate_reference.py` and `mkdocs serve` from the `python-sdk/`
directory for a local docs site.

## Installation

```bash
pip install pinbridge-sdk
```

For local development from source:

```bash
pip install -e .[dev]
```

## Requirements

- Python `>=3.10`
- PinBridge API URL (default: `https://api.pinbridge.io`)
- Authentication via API key and/or bearer token

## Publish to PyPI

After updating and committing the target SDK version:

3. Create and push a matching version tag:

```bash
git tag v1.1.0
git push origin main
git push origin v1.0.2
```

4. Wait for the GitHub Actions `Publish` workflow to finish and verify the package on PyPI.

## Client Initialization

```python
from pinbridge_sdk import PinbridgeClient

client = PinbridgeClient(
    base_url="https://api.pinbridge.io",  # optional
    api_key="pb_live_...",                # optional
    bearer_token=None,                     # optional
    timeout=30.0,                          # optional
    headers={"x-request-source": "my-app"},
)
```

Use as a context manager to close HTTP resources automatically:

```python
with PinbridgeClient(api_key="pb_live_...") as client:
    print(client.system.health().status)
```

## Authentication Patterns

### 1. API key auth

```python
from pinbridge_sdk import PinbridgeClient

with PinbridgeClient(api_key="pb_live_...") as client:
    keys = client.api_keys.list()
```

### 2. Login to bearer token

```python
from pinbridge_sdk import PinbridgeClient
from pinbridge_sdk.models import LoginRequest

with PinbridgeClient() as client:
    auth = client.auth.login(LoginRequest(email="you@example.com", password="super-secret"))
    client.set_bearer_token(auth.access_token)
    print(client.auth.me().workspace.name)
```

### 3. Switching auth at runtime

```python
client.set_api_key("pb_live_new")
client.set_bearer_token("new-jwt")
client.clear_auth()  # removes both
```

## Async Client

```python
from pinbridge_sdk import AsyncPinbridgeClient

async def run() -> None:
    async with AsyncPinbridgeClient(api_key="pb_live_...") as client:
        pricing = await client.billing.pricing()
        print(pricing.source)
```

## Resource Guide

All sync resources are available on `PinbridgeClient`; async equivalents have identical names on `AsyncPinbridgeClient`.

### System (`client.system`)

- `root()`
- `health()`
- `readiness()`
- `stripe_webhook(body, stripe_signature=...)`

```python
health = client.system.health()
print(health.status, health.checks)

ready = client.system.readiness()
print(ready.status, ready.database)
```

### Auth (`client.auth`)

- `register(RegisterRequest | dict)`
- `login(LoginRequest | dict)`
- `forgot_password(ForgotPasswordRequest | dict)`
- `reset_password(ResetPasswordRequest | dict)`
- `change_password(ChangePasswordRequest | dict)`
- `request_email_verification()`
- `verify_email(token=...)`
- `me()`
- `get_profile()`
- `update_profile(ProfileUpdateRequest | dict)`

### API Keys (`client.api_keys`)

- `create(APIKeyCreate | dict)`
- `list()`
- `update(key_id, APIKeyUpdate | dict)`
- `revoke(key_id)`

### Pinterest (`client.pinterest`)

- `start_oauth()`
- `oauth_callback(code=..., state=..., follow_redirects=False)`
- `list_accounts()`
- `revoke_account(account_id)`
- `list_boards(account_id)`
- `list_related_terms(account_id, terms, exact_match=False)`
- `create_board(BoardCreateRequest | dict)`
- `delete_board(board_id, account_id=...)`

```python
from pinbridge_sdk.models import BoardCreateRequest

accounts = client.pinterest.list_accounts()
boards = client.pinterest.list_boards(accounts[0].id)
related = client.pinterest.list_related_terms(
    accounts[0].id,
    ["workout", "yoga"],
    exact_match=True,
)
created = client.pinterest.create_board(
    BoardCreateRequest(account_id=accounts[0].id, name="SDK Board")
)
print(related.related_terms_list[0].related_terms)
```

### Projects (`client.projects`)

- `list()`
- `create_sandbox(CreateSandboxProjectRequest | dict | None = None)`
- `reset_sandbox()`
- `switch(SwitchProjectRequest | dict)`

```python
projects = client.projects.list()
sandbox = next((p for p in projects.projects if p.environment.value == "sandbox"), None)
if sandbox is None:
    sandbox = next(
        p for p in client.projects.create_sandbox().projects if p.environment.value == "sandbox"
    )
client.projects.reset_sandbox()
switched = client.projects.switch({"project_id": str(sandbox.id)})
client.set_bearer_token(switched.access_token)
```

### Pins and Jobs (`client.pins`, `client.jobs`)

- `client.assets.upload_image(file, filename=..., content_type=...)`
- `client.assets.upload_video(file, filename=..., content_type=...)`
- `client.assets.get(asset_id)`
- `client.assets.get_content(asset_id)`
- `client.pins.create(PinCreate | dict)`
- `client.pins.import_json(list[PinImportCreate | PinCreate | dict])`
- `client.pins.import_csv(file, filename=..., content_type=...)`
- `client.pins.get_import(job_id)`
- `client.pins.list_imports(limit=50, offset=0, status=None, source_type=None)`
- `client.pins.get(pin_id)`
- `client.pins.list(limit=50, offset=0)`
- `client.pins.delete(pin_id)`
- `client.jobs.get(job_id)`

```python
from pinbridge_sdk.models import PinCreate, PinImportCreate

asset = client.assets.upload_image(
    "./pin-image.png",
    content_type="image/png",
)

pin = client.pins.create(
    PinCreate(
        account_id="...",
        board_id="...",
        title="Hello",
        description="From SDK",
        alt_text="Descriptive alt text for accessibility",
        related_terms=["meal prep", "vegetables"],
        dominant_color="#E88A2D",
        asset_id=asset.id,
        idempotency_key="my-idempotency-key",
    )
)
status = client.jobs.get(pin.id)
print(status.status)
```

```python
video_asset = client.assets.upload_video(
    "./pin-video.mp4",
    content_type="video/mp4",
)

video_pin = client.pins.create(
    PinCreate(
        account_id="...",
        board_id="...",
        title="Video launch",
        asset_id=video_asset.id,
        cover_image_url="https://cdn.example.com/video-cover.jpg",
        idempotency_key="video-idempotency-key",
    )
)
print(video_pin.media_type.value, video_pin.media_url)
```

```python
import_job = client.pins.import_json(
    [
        PinImportCreate(
            account_id="...",
            board_id="...",
            title="Bulk one",
            image_url="https://example.com/bulk-1.jpg",
            idempotency_key="bulk-json-1",
            run_at="2026-03-06T10:00:00Z",  # optional: omit for immediate queueing
        ),
        {
            "account_id": "...",
            "board_id": "...",
            "title": "Bulk two",
            "image_url": "https://example.com/bulk-2.jpg",
            "idempotency_key": "bulk-json-2",
        },
    ]
)
print(import_job.status.value)
print(client.pins.get_import(import_job.id).processed_rows)
```

For scheduled publishing fields (`run_at` on schedules/import rows), send absolute ISO 8601
timestamps with an explicit timezone offset (for example `2026-03-06T10:00:00Z`).

### Schedules (`client.schedules`)

- `create(ScheduleCreate | dict)`
- `get(schedule_id)`
- `list(limit=50, offset=0)`
- `cancel(schedule_id)`

Pins and schedules accept either a public `image_url` or an uploaded `asset_id`. Video publishes and schedules should use uploaded assets.
Pinterest-compatible limits are enforced in SDK models: `title <= 100`, `description <= 800`,
`alt_text <= 500`, and URLs (`link_url`, `cover_image_url`) `<= 2048`.

### Webhooks (`client.webhooks`)

- `create(WebhookCreate | dict)`
- `list()`
- `get(webhook_id)`
- `update(webhook_id, WebhookUpdate | dict)`
- `delete(webhook_id)`

### Billing and Rate Meter (`client.billing`, `client.rate_meter`)

- `client.billing.pricing()`
- `client.billing.checkout(CheckoutRequest | dict)`
- `client.billing.portal()`
- `client.billing.status()`
- `client.rate_meter.get(account_id)`

## Typed Models

All methods return typed Pydantic models from `pinbridge_sdk.models`.

Use either model instances or plain dictionaries as method input.

```python
from pinbridge_sdk.models import WebhookCreate

created = client.webhooks.create(
    WebhookCreate(
        url="https://example.com/hook",
        secret="0123456789012345",
        events=["pin.published", "pin.failed"],
    )
)
```

## Error Handling

Raised exceptions:

- `pinbridge_sdk.AuthenticationError`
- `pinbridge_sdk.NotFoundError`
- `pinbridge_sdk.ValidationError`
- `pinbridge_sdk.RateLimitError`
- `pinbridge_sdk.APIError`

```python
from pinbridge_sdk import APIError, PinbridgeClient

try:
    with PinbridgeClient(api_key="bad") as client:
        client.auth.me()
except APIError as exc:
    print(exc.status_code, exc.message, exc.code)
```

## Extending the SDK

You can register custom resources without changing core classes.

```python
from pinbridge_sdk import PinbridgeClient
from pinbridge_sdk.resources.base import SyncAPIResource

class DiagnosticsResource(SyncAPIResource):
    def ping(self):
        return self._request("GET", "/healthz").json()

with PinbridgeClient(api_key="pb_live_...") as client:
    client.register_resource("diagnostics", DiagnosticsResource)
    print(client.diagnostics.ping())
```

This keeps new API groups low-risk: add models + resource class and register/bind it.

## Testing, Formatting, Coverage

```bash
black .
ruff check .
pytest --cov=pinbridge_sdk --cov-config=.coveragerc --cov-report=term-missing --cov-report=xml
```

Coverage config file: `.coveragerc`

Detailed release runbook: `RELEASING.md`
