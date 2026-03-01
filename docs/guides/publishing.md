# Publishing

Pin publishing in the SDK is split between immediate publishing with `pins` and deferred
publishing with `schedules`. When your source media is local, upload it first and then
reference the returned `asset_id`.

## Publish A Pin Immediately

```python
from pinbridge_sdk.models import PinCreate

asset = client.assets.upload_image(
    "./pin-image.png",
    content_type="image/png",
)

pin = client.pins.create(
    PinCreate(
        account_id="44444444-4444-4444-4444-444444444444",
        board_id="123-board",
        title="Hello from PinBridge",
        description="Published through the Python SDK",
        link_url="https://example.com",
        asset_id=asset.id,
        idempotency_key="pinbridge-demo-001",
    )
)
print(pin.status.value)
```

## Publish A Video Pin

```python
video_asset = client.assets.upload_video(
    "./pin-video.mp4",
    content_type="video/mp4",
)

video_pin = client.pins.create(
    PinCreate(
        account_id="44444444-4444-4444-4444-444444444444",
        board_id="123-board",
        title="Video launch",
        description="Published through the Python SDK",
        asset_id=video_asset.id,
        idempotency_key="pinbridge-video-001",
    )
)
print(video_pin.media_type.value)
```

## Track Job Status

The jobs resource exposes queue status for published pins.

```python
job = client.jobs.get(pin.id)
print(job.status.value)
```

## Bulk Import Pins

Use `pins.import_json()` when you already have a list of pin payloads and `pins.import_csv()`
when your workflow starts from a CSV file. Both methods return an import job that can be polled.

```python
from pinbridge_sdk.models import PinCreate

import_job = client.pins.import_json(
    [
        PinCreate(
            account_id="44444444-4444-4444-4444-444444444444",
            board_id="123-board",
            title="Bulk pin one",
            image_url="https://example.com/bulk-1.jpg",
            idempotency_key="bulk-demo-001",
        ),
        {
            "account_id": "44444444-4444-4444-4444-444444444444",
            "board_id": "123-board",
            "title": "Bulk pin two",
            "image_url": "https://example.com/bulk-2.jpg",
            "idempotency_key": "bulk-demo-002",
        },
    ]
)

csv_job = client.pins.import_csv("./pins.csv")

latest = client.pins.get_import(import_job.id)
for row in latest.results:
    print(row.row_number, row.status, row.error_message)
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
        asset_id=asset.id,
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
- Use `assets.upload_image()` or `assets.upload_video()` for local files
- Keep `image_url` for already hosted images
- Use uploaded `asset_id` values for video publishes and schedules
- Poll `jobs.get()` or fetch the saved pin/schedule record instead of assuming success immediately
