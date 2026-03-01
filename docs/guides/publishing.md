# Publishing

Pin publishing in the SDK is split between immediate publishing with `pins` and deferred
publishing with `schedules`.

## Publish A Pin Immediately

```python
from pinbridge_sdk.models import PinCreate

pin = client.pins.create(
    PinCreate(
        account_id="44444444-4444-4444-4444-444444444444",
        board_id="123-board",
        title="Hello from PinBridge",
        description="Published through the Python SDK",
        link_url="https://example.com",
        image_url="https://example.com/image.jpg",
        idempotency_key="pinbridge-demo-001",
    )
)
print(pin.status.value)
```

## Track Job Status

The jobs resource exposes queue status for published pins.

```python
job = client.jobs.get(pin.id)
print(job.status.value)
```

## Schedule A Pin

```python
from datetime import datetime, timezone
from pinbridge_sdk.models import ScheduleCreate

schedule = client.schedules.create(
    ScheduleCreate(
        account_id="44444444-4444-4444-4444-444444444444",
        run_at=datetime(2026, 3, 2, 18, 0, tzinfo=timezone.utc),
        board_id="123-board",
        title="Scheduled pin",
        description="Created from docs",
        link_url="https://example.com",
        image_url="https://example.com/image.jpg",
    )
)
print(schedule.id)
```

## Cancel A Schedule

```python
client.schedules.cancel(schedule.id)
```

## Operational Notes

- Always provide a stable `idempotency_key` for immediate publishing
- Use timezone-aware datetimes for `run_at`
- Poll `jobs.get()` or fetch the saved pin/schedule record instead of assuming success immediately
