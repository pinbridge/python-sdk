# PinBridge Python SDK

Official Python SDK for the PinBridge API.

## Installation

```bash
pip install pinbridge-sdk
```

For local development from this monorepo:

```bash
pip install -e .[dev]
```

## Requirements

- Python `>=3.10`
- PinBridge API URL (default: `https://api.pinbridge.io`)
- Authentication via API key and/or bearer token

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

Use as a context manager to close internal HTTP resources automatically:

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
- `stripe_webhook(body, stripe_signature=...)`

```python
health = client.system.health()
print(health.status, health.database)
```

### Auth (`client.auth`)

- `register(RegisterRequest | dict)`
- `login(LoginRequest | dict)`
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
- `create_board(BoardCreateRequest | dict)`
- `delete_board(board_id, account_id=...)`

```python
from pinbridge_sdk.models import BoardCreateRequest

accounts = client.pinterest.list_accounts()
boards = client.pinterest.list_boards(accounts[0].id)
created = client.pinterest.create_board(
    BoardCreateRequest(account_id=accounts[0].id, name="SDK Board")
)
```

### Projects (`client.projects`)

- `list()`
- `create_sandbox(CreateSandboxProjectRequest | dict | None = None)`
- `switch(SwitchProjectRequest | dict)`

```python
projects = client.projects.list()
sandbox = next((p for p in projects.projects if p.environment.value == "sandbox"), None)
if sandbox is None:
    sandbox = next(
        p for p in client.projects.create_sandbox().projects if p.environment.value == "sandbox"
    )
switched = client.projects.switch({"project_id": str(sandbox.id)})
client.set_bearer_token(switched.access_token)
```

### Pins and Jobs (`client.pins`, `client.jobs`)

- `client.pins.create(PinCreate | dict)`
- `client.pins.get(pin_id)`
- `client.pins.list(limit=50, offset=0)`
- `client.pins.delete(pin_id)`
- `client.jobs.get(job_id)`

```python
from pinbridge_sdk.models import PinCreate

pin = client.pins.create(
    PinCreate(
        account_id="...",
        board_id="...",
        title="Hello",
        description="From SDK",
        image_url="https://example.com/image.jpg",
        idempotency_key="my-idempotency-key",
    )
)
status = client.jobs.get(pin.id)
print(status.status)
```

### Schedules (`client.schedules`)

- `create(ScheduleCreate | dict)`
- `get(schedule_id)`
- `list(limit=50, offset=0)`
- `cancel(schedule_id)`

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
