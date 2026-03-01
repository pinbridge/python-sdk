# Authentication

The SDK supports API key authentication, bearer-token authentication, or both at once.

## API Key Flow

Use API keys for server-to-server requests against workspace-scoped endpoints.

```python
from pinbridge_sdk import PinbridgeClient

with PinbridgeClient(api_key="pb_live_...") as client:
    keys = client.api_keys.list()
    print(len(keys))
```

## Bearer Token Flow

Use the auth resource to log in, then set the bearer token on the client.

```python
from pinbridge_sdk import PinbridgeClient
from pinbridge_sdk.models import LoginRequest

with PinbridgeClient() as client:
    auth = client.auth.login(
        LoginRequest(email="you@example.com", password="super-secret")
    )
    client.set_bearer_token(auth.access_token)
    print(client.auth.me().active_project.name)
```

## Switching Credentials

You can update auth on the same client instance:

```python
client.set_api_key("pb_live_new")
client.set_bearer_token("new-jwt")
client.clear_auth()
```

## Choosing Which Auth To Use

- Use API keys for backend integrations that only need workspace-level operations
- Use bearer tokens for login, profile, and project-switching flows
- Use both when a session starts with user auth and later performs API-key-compatible actions
