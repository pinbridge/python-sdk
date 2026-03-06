# PinBridge Python SDK

The PinBridge Python SDK wraps the PinBridge API with typed request and response models,
synchronous and asynchronous clients, and resource groups that mirror the API surface.

## Install

```bash
pip install pinbridge-sdk
```

For local development from source:

```bash
pip install -e .[dev]
```

For documentation work:

```bash
pip install -e .[docs]
python scripts/generate_reference.py
mkdocs serve
```

## What The SDK Gives You

- `PinbridgeClient` and `AsyncPinbridgeClient` for sync and async use cases
- Typed models under `pinbridge_sdk.models`
- Resource groups for assets, auth, projects, Pinterest, pins, schedules, webhooks, billing, and more
- Local image and video uploads through the assets resource before pin publishing
- Consistent error mapping through `pinbridge_sdk.errors`

## Start Here

```python
from pinbridge_sdk import PinbridgeClient
from pinbridge_sdk.models import LoginRequest

with PinbridgeClient(base_url="https://api.pinbridge.io") as client:
    auth = client.auth.login(
        LoginRequest(email="you@example.com", password="super-secret")
    )
    client.set_bearer_token(auth.access_token)
    profile = client.auth.me()
    print(profile.active_project.name)
```

## Documentation Layout

- Guides: task-oriented walkthroughs for common workflows
- Reference: generated API reference for clients, resources, models, and errors
- Development: how to regenerate and validate the docs
