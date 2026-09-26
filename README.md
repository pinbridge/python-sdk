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

- `create(APIKeyCreate | dict)` — optional `scopes` (`read` / `write` / `destructive`) and `pinterest_account_ids` allow-list
- `list()` — responses carry `scopes`, `pinterest_account_ids`, `source` (`manual` / `oauth`), `last_used_at`
- `update(key_id, APIKeyUpdate | dict)` — partial: `name`, `scopes`, `pinterest_account_ids`
- `revoke(key_id)`

### Pinterest (`client.pinterest`)

- `start_oauth()`
- `oauth_callback(code=..., state=..., follow_redirects=False)`
- `list_accounts()`
- `revoke_account(account_id)`
- `list_boards(account_id)`
- `check_board_access(board_id, account_id=..., fresh=False)` — can this account publish to this board, and why not
- `account_analytics(account_id, start_date=None, end_date=None, metrics=None)` — impressions, saves, clicks per day (max 90 days)
- `list_related_terms(account_id, terms, exact_match=False)`
- `create_board(BoardCreateRequest | dict)` — `SECRET` needs `boards:write_secret` (accounts connected before API 1.37 must reconnect)
- `update_board(board_id, BoardUpdateRequest | dict)`
- `delete_board(board_id, account_id=...)` — deletes the board on Pinterest with every pin on it (irreversible)

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
- `client.assets.list(workspace_id=None, sort="created_at_desc", limit=50, offset=0, q=None, asset_type=None, in_use=None, since=None, until=None)` — `total` counts every match; `q` searches file names, `in_use` keeps assets referenced (or not) by a pin
- `client.assets.get(asset_id)`
- `client.assets.get_content(asset_id)`
- `client.assets.delete(asset_id, confirm=False)`
- `client.assets.bulk_delete([asset_id, ...], confirm=False)`
- `client.pins.create(PinCreate | dict)`
- `client.pins.validate(PinCreate | dict)` — dry run: every check the API runs, nothing published
- `client.pins.create_batch([PinCreate | dict, ...])` — up to 100 pins, per-item outcome
- `client.pins.update(pin_id, PinUpdate | dict)` — edit title / description / link / alt text / board of a pin that has not published; a published pin raises `APIError` with `code == "pin_already_published"`
- `client.pins.analytics(pin_id, start_date=None, end_date=None, metrics=None)`
- `client.pins.import_json(list[PinImportCreate | PinCreate | dict])`
- `client.pins.import_csv(file, filename=..., content_type=...)`
- `client.pins.get_import(job_id)`
- `client.pins.list_imports(limit=50, offset=0, status=None, source_type=None)`
- `client.pins.get(pin_id)`
- `client.pins.list(limit=50, offset=0, account_id=None, board_id=None, status=None, error_code=None, since=None, until=None, q=None, sort=None)` — `q` searches title, description and link; `sort` is one of `PinSort` (`created_at_desc` by default, `published_at_*`, `title_*`, `status_*`)
- `client.pins.list_page(...)` — same filters, returns a `Page` with `items`, `total` (from `X-Total-Count`) and `has_more`
- `client.pins.delete(pin_id, delete_from_pinterest=False)` — returns `None`, or a `PinDeleteResponse` when the Pinterest-side delete was requested
- `client.pins.retry(pin_id, PinRetryRequest | dict | None)`
- `client.pins.bulk_delete([pin_id, ...])`
- `client.pins.bulk_retry([pin_id, ...])`
- `client.jobs.get(job_id)`

```python
from pinbridge_sdk.models import PinCreate, PinUpdate

draft = PinCreate(account_id=account.id, board_id=board.id, title="Autumn recipes",
                  image_url="https://example.com/soup.jpg", idempotency_key="soup-2026-09")
check = client.pins.validate(draft)            # nothing published
if check.valid:
    pin = client.pins.create(draft)
    client.pins.update(pin.id, PinUpdate(title="Autumn soup recipes"))
    stats = client.pins.analytics(pin.id, metrics=["IMPRESSION", "SAVE"])
else:
    print([(c.name, c.code, c.remediation) for c in check.checks if c.status.value == "failed"])
```

Deletes on an asset referenced by pins return `requires_confirmation=True`; pass `confirm=True`
to force the deletion. Bulk actions (`bulk_delete`, `bulk_retry`) return a `BulkOperationResponse`
with per-item `results` (`succeeded` / `skipped` / `failed`).

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
- `validate(ScheduleCreate | dict)` — dry run, including `run_at`
- `get(schedule_id)`
- `list(limit=50, offset=0, account_id=None, board_id=None, status=None, since=None, until=None, q=None, sort=None)` — `sort` is one of `ScheduleSort`; `run_at_asc` lists the next run first
- `list_page(...)` — same filters, returns a `Page` with `items`, `total` and `has_more`
- `update(schedule_id, ScheduleUpdate | dict)` — edit a pending schedule in place (time, board, text, media)
- `cancel(schedule_id)`
- `retry(schedule_id)`
- `delete(schedule_id)`
- `bulk_cancel([schedule_id, ...])`
- `bulk_retry([schedule_id, ...])`
- `bulk_delete([schedule_id, ...])`

Pins and schedules accept either a public `image_url` or an uploaded `asset_id`. Video publishes and schedules should use uploaded assets.
Pinterest-compatible limits are enforced in SDK models: `title <= 100`, `description <= 800`,
`alt_text <= 500`, and URLs (`link_url`, `cover_image_url`) `<= 2048`.

### Dashboard (`client.dashboard`)

- `summary(start=None, end=None, tz=None, account_id=None)` — publishing activity for `[start, end)`:
  pin counts by status and success rate, the same figures for the previous period of equal
  length, an hourly (ranges up to 48 hours) or daily series bucketed in `tz`, published pins per
  account, the current queue, schedules and import jobs. Defaults to the last 30 days; up to 366
  days. A naive `start`/`end` is read as wall-clock time in `tz`.

```python
from datetime import datetime

week = client.dashboard.summary(start=datetime(2026, 9, 1), end=datetime(2026, 9, 8), tz="Europe/Paris")
print(week.pins.total, week.pins.success_rate, week.previous_pins.total)
for point in week.series:
    print(point.start.date(), point.created, point.published, point.failed)

page = client.pins.list_page(account_id=account.id, q="soup", sort="created_at_desc", limit=25)
print(f"{len(page.items)} of {page.total}", "more" if page.has_more else "done")
```

Search, sort, `list_page` totals, the asset filters and the dashboard need API 1.34.0 or later.

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

### Team (`client.team`)

- `preview_invitation(token)`
- `list_members()`
- `list_invitations()`
- `create_invitation(TeamInvitationCreateRequest | dict)`
- `resend_invitation(invitation_id)`
- `revoke_invitation(invitation_id)`
- `update_member(member_id, TeamMemberUpdateRequest | dict)`
- `remove_member(member_id)`
- `accept_invitation(TeamInvitationAcceptRequest | dict)`

```python
from pinbridge_sdk.models import TeamInvitationCreateRequest

invitation = client.team.create_invitation(
    TeamInvitationCreateRequest(email="teammate@example.com", role="editor")
)
members = client.team.list_members()
```

### MCP Usage (`client.mcp`)

- `quota()` — current-week MCP request usage and quota for the workspace
- `track()` — increment the counter after a tool call, returning the updated usage

### Email Preferences (`client.email`)

- `get_preferences()`
- `update_preferences(EmailPreferencesUpdateRequest | dict)`
- `unsubscribe(workspace_id=..., token=..., user_id=...)` — public token-based unsubscribe

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
