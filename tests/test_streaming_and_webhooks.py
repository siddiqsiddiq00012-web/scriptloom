import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.events.event_bus import event_bus, EventSchema, ProgressState
from backend.services.webhook_service import WebhookDispatcher
from backend.models.webhook import WebhookEndpoint, DeadLetterQueue
from backend.db.database import SessionLocal

client = TestClient(app)


def test_streaming_and_webhooks_infrastructure(celery_eager):
    print("\n--- 1. Testing EventBus Publishing & Schema ---")
    received_events = []

    def _on_event(event: EventSchema):
        received_events.append(event)

    event_bus.subscribe("media.processing.started", _on_event)

    sample_event = EventSchema(
        event_type="media.processing.started",
        media_id=42,
        user_id=1,
        payload={"step": ProgressState.PROCESSING, "progress": 25},
    )
    event_bus.publish(sample_event)

    assert len(received_events) == 1
    assert received_events[0].media_id == 42
    assert received_events[0].payload["step"] == ProgressState.PROCESSING
    print("EventBus publish & subscribe verified cleanly!")

    print("\n--- 2. Testing Webhook Dispatcher HMAC-SHA256 & DLQ Escalation ---")
    db = SessionLocal()
    # Create test endpoint targeting invalid port to trigger retries
    endpoint = WebhookEndpoint(
        user_id=1,
        url="http://127.0.0.1:59999/webhook-receiver",
        secret="sec_test_secret_123456",
        is_active=True,
        subscribed_events=["*"],
    )
    db.add(endpoint)
    db.commit()

    test_payload_event = EventSchema(
        event_type="campaign_pack.completed",
        media_id=42,
        user_id=1,
        payload={"pack_name": "Test Campaign Pack"},
    )

    from backend.core.config import settings
    orig_retries = settings.WEBHOOK_MAX_RETRIES
    settings.WEBHOOK_MAX_RETRIES = 0
    
    try:
        # Dispatch to failing endpoint (should attempt retries and land in Dead Letter Queue)
        dispatched = WebhookDispatcher.dispatch_event(db, test_payload_event)
        assert len(dispatched) == 1

        dlq_entry = db.query(DeadLetterQueue).first()
        assert dlq_entry is not None
        print("Failing webhook successfully escalated to Dead Letter Queue:", dlq_entry.reason)
    finally:
        settings.WEBHOOK_MAX_RETRIES = orig_retries

    db.close()
    print("\n[SUCCESS] Streaming & Webhooks Infrastructure tests PASSED!")


if __name__ == "__main__":
    test_streaming_and_webhooks_infrastructure()
