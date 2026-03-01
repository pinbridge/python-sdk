# Webhooks

The webhooks resource manages outbound webhook endpoints for workspace events.

## Create A Webhook

```python
from pinbridge_sdk.models import WebhookCreate

created = client.webhooks.create(
    WebhookCreate(
        url="https://example.com/hook",
        secret="0123456789012345",
        events=["pin.published", "pin.failed"],
    )
)
print(created.id)
```

## Update Or Disable A Webhook

```python
updated = client.webhooks.update(created.id, {"is_enabled": False})
print(updated.is_enabled)
```

## List And Delete

```python
for webhook in client.webhooks.list():
    print(webhook.url, webhook.is_enabled)

client.webhooks.delete(created.id)
```

## Secret Handling

- Treat webhook secrets as credentials
- Rotate them through `update()` instead of creating ad hoc secondary endpoints
- Keep a minimum length of 16 characters to match API validation
