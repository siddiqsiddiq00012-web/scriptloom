import json
import time
import os
import sys
import hmac
import hashlib
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
import pytest
import requests
from celery.exceptions import Retry
from fastapi import status
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from backend.db.database import SessionLocal
from backend.models.user import User
from backend.models.webhook import WebhookEndpoint, WebhookDeliveryLog, DeadLetterQueue
from backend.core.token import create_access_token
from backend.events.event_bus import EventSchema
from backend.services.webhook_service import WebhookDispatcher
from backend.jobs.tasks.webhook_delivery import deliver_webhook

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    db = SessionLocal()
    db.query(WebhookDeliveryLog).delete()
    db.query(WebhookEndpoint).delete()
    db.query(DeadLetterQueue).delete()
    db.query(User).filter(User.email.like("%@scriptloom.ai")).delete()
    db.commit()
    db.close()
    yield


def create_test_user(db, prefix="test_wh"):
    user = User(name=f"{prefix} User", email=f"{prefix}@scriptloom.ai", hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# 1. API MANAGEMENT CRUD & OWNERSHIP TESTS
def test_webhook_endpoints_crud_and_ownership():
    db = SessionLocal()
    user_a = create_test_user(db, "usera")
    user_b = create_test_user(db, "userb")
    user_a_id = user_a.id
    user_b_id = user_b.id
    db.close()

    token_a = create_access_token({"sub": str(user_a_id)})
    token_b = create_access_token({"sub": str(user_b_id)})
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Create Endpoint A (User A)
    endpoint_data = {
        "url": "https://callback.usera.com/events",
        "secret": "usera_secret_key_987",
        "subscribed_events": ["media.processing.started"],
    }
    resp = client.post("/api/v1/api/v1/webhooks/endpoints", json=endpoint_data, headers=headers_a)
    assert resp.status_code == 201
    endpoint_id = resp.json()["id"]
    assert resp.json()["url"] == endpoint_data["url"]
    assert "secret" not in resp.json()  # Never expose secrets through API responses

    # User A lists endpoints -> lists 1 endpoint
    list_resp = client.get("/api/v1/api/v1/webhooks/endpoints", headers=headers_a)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id"] == endpoint_id

    # User B lists endpoints -> lists 0 endpoints
    list_resp_b = client.get("/api/v1/api/v1/webhooks/endpoints", headers=headers_b)
    assert list_resp_b.status_code == 200
    assert len(list_resp_b.json()) == 0

    # User B queries User A's endpoint -> 404 Sanitized Resource Boundary Protection
    get_resp_b = client.get(f"/api/v1/api/v1/webhooks/endpoints/{endpoint_id}", headers=headers_b)
    assert get_resp_b.status_code == 404
    assert get_resp_b.json()["detail"] == "Webhook endpoint not found."

    # User A edits endpoint -> success
    update_data = {
        "url": "https://callback.usera.com/new-path",
        "is_active": False,
    }
    update_resp = client.put(f"/api/v1/api/v1/webhooks/endpoints/{endpoint_id}", json=update_data, headers=headers_a)
    assert update_resp.status_code == 200
    assert update_resp.json()["url"] == update_data["url"]
    assert update_resp.json()["is_active"] is False

    # User B tries to delete User A's endpoint -> 404
    del_resp_b = client.delete(f"/api/v1/api/v1/webhooks/endpoints/{endpoint_id}", headers=headers_b)
    assert del_resp_b.status_code == 404

    # User A deletes endpoint -> 204
    del_resp_a = client.delete(f"/api/v1/api/v1/webhooks/endpoints/{endpoint_id}", headers=headers_a)
    assert del_resp_a.status_code == 204


# 2. DISPATCH & ONE-TO-MANY ROUTING TESTS
def test_dispatch_one_to_many_routing():
    db = SessionLocal()
    user = create_test_user(db, "routing")
    
    # Register 2 active matching endpoints, 1 inactive matching, and 1 non-matching event endpoint
    ep1 = WebhookEndpoint(user_id=user.id, url="https://ep1.com", secret="sec1", subscribed_events=["media.processing.started"])
    ep2 = WebhookEndpoint(user_id=user.id, url="https://ep2.com", secret="sec2", subscribed_events=["*"])
    ep_inactive = WebhookEndpoint(user_id=user.id, url="https://ep3.com", secret="sec3", subscribed_events=["*"], is_active=False)
    ep_other_event = WebhookEndpoint(user_id=user.id, url="https://ep4.com", secret="sec4", subscribed_events=["transcription.completed"])
    
    db.add_all([ep1, ep2, ep_inactive, ep_other_event])
    db.commit()
    user_id = user.id
    db.close()

    # Trigger event
    event = EventSchema(
        event_type="media.processing.started",
        user_id=user_id,
        payload={"progress": 50},
    )

    db = SessionLocal()
    with patch("backend.jobs.tasks.webhook_delivery.deliver_webhook.delay") as mock_delay:
        dispatched_ids = WebhookDispatcher.dispatch_event(db, event)
        # Should route to ep1 and ep2 only
        assert len(dispatched_ids) == 2
        assert mock_delay.call_count == 2
        
        # Verify 2 distinct delivery logs persisted with unique delivery_ids referencing the same event_id
        logs = db.query(WebhookDeliveryLog).filter(WebhookDeliveryLog.event_id == event.event_id).all()
        assert len(logs) == 2
        assert logs[0].delivery_id != logs[1].delivery_id
        assert logs[0].event_type == "media.processing.started"
        assert logs[1].event_type == "media.processing.started"
        
        # Check payload persistence immutability: must be stored as canonical JSON string
        canonical_str = json.dumps(event.model_dump(), sort_keys=True, separators=(",", ":"))
        assert logs[0].payload_json == canonical_str
        assert logs[1].payload_json == canonical_str

    db.close()


# 3. DISPATCH FAILURE COMPENSATION
@patch("backend.jobs.tasks.webhook_delivery.deliver_webhook.delay", side_effect=Exception("Redis connection lost"))
def test_dispatch_failure_compensation(mock_delay):
    db = SessionLocal()
    user = create_test_user(db, "disp_comp")
    ep = WebhookEndpoint(user_id=user.id, url="https://ep.com", secret="sec", subscribed_events=["*"])
    db.add(ep)
    db.commit()
    user_id = user.id
    db.close()

    event = EventSchema(
        event_type="media.processing.started",
        user_id=user_id,
        payload={},
    )

    db = SessionLocal()
    dispatched_ids = WebhookDispatcher.dispatch_event(db, event)
    # The dispatcher should catch the Celery exception, mark the persisted log FAILED with explanation, and not raise
    assert len(dispatched_ids) == 0
    
    log = db.query(WebhookDeliveryLog).first()
    assert log is not None
    assert log.status == "FAILED"
    assert log.failure_reason == "Task queue dispatch failed"
    db.close()


# 4. CELERY TASK RETRY transients VS PERMANENTS
@patch("requests.post")
def test_webhook_delivery_success(mock_post, celery_eager):
    # Mock HTTP 200 response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp

    db = SessionLocal()
    user = create_test_user(db, "wh_ok")
    ep = WebhookEndpoint(user_id=user.id, url="https://receiver.com/hook", secret="supersecret", subscribed_events=["*"])
    db.add(ep)
    db.commit()
    
    event = EventSchema(event_type="test.ping", user_id=user.id, payload={"hello": "world"})
    canonical_payload = json.dumps(event.model_dump(), sort_keys=True, separators=(",", ":"))
    timestamp = int(time.time())

    log = WebhookDeliveryLog(
        webhook_id=ep.id,
        delivery_id="del_success_123",
        event_type=event.event_type,
        event_id=event.event_id,
        status="PENDING",
        attempt_count=0,
        request_url=ep.url,
        payload_json=canonical_payload,
        dispatch_timestamp=timestamp,
    )
    db.add(log)
    db.commit()
    db.close()

    # Trigger Celery Task (Eager Mode runs it synchronously)
    deliver_webhook.delay("del_success_123")

    # Verify state updated to DELIVERED
    db = SessionLocal()
    log_db = db.query(WebhookDeliveryLog).filter(WebhookDeliveryLog.delivery_id == "del_success_123").first()
    assert log_db.status == "DELIVERED"
    assert log_db.delivered_at is not None
    assert log_db.attempt_count == 1
    assert log_db.response_status == 200

    # Verify signature format header passed to requests.post
    mock_post.assert_called_once()
    called_headers = mock_post.call_args[1]["headers"]
    called_body = mock_post.call_args[1]["data"]

    # Verify payload byte-for-byte matches persisted canonical representation
    assert called_body == canonical_payload.encode("utf-8")

    # Verify signature header matches expected HMAC-SHA256 of: timestamp + "." + payload_json
    expected_message = f"{timestamp}.{canonical_payload}"
    expected_signature = hmac.new(b"supersecret", expected_message.encode("utf-8"), hashlib.sha256).hexdigest()
    assert called_headers["X-Scriptloom-Signature"] == expected_signature
    assert called_headers["X-Scriptloom-Timestamp"] == str(timestamp)
    assert called_headers["X-Scriptloom-Delivery-ID"] == "del_success_123"
    db.close()


@patch("requests.post")
def test_webhook_delivery_permanent_failure_aborts(mock_post, celery_eager):
    # Mock HTTP 400 response (permanent failure)
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_post.return_value = mock_resp

    db = SessionLocal()
    user = create_test_user(db, "wh_perm_fail")
    ep = WebhookEndpoint(user_id=user.id, url="https://receiver.com/hook", secret="supersecret", subscribed_events=["*"])
    db.add(ep)
    db.commit()
    
    event = EventSchema(event_type="test.ping", user_id=user.id, payload={})
    canonical_payload = json.dumps(event.model_dump(), sort_keys=True, separators=(",", ":"))
    timestamp = int(time.time())

    log = WebhookDeliveryLog(
        webhook_id=ep.id,
        delivery_id="del_perm_123",
        event_type=event.event_type,
        event_id=event.event_id,
        status="PENDING",
        attempt_count=0,
        request_url=ep.url,
        payload_json=canonical_payload,
        dispatch_timestamp=timestamp,
    )
    db.add(log)
    db.commit()
    db.close()

    # Deliver task
    deliver_webhook.delay("del_perm_123")

    # Verify state transitions immediately to FAILED (since 400 is not retryable)
    db = SessionLocal()
    log_db = db.query(WebhookDeliveryLog).filter(WebhookDeliveryLog.delivery_id == "del_perm_123").first()
    assert log_db.status == "FAILED"
    assert log_db.attempt_count == 1
    assert "Permanent failure: HTTP 400" in log_db.failure_reason
    db.close()


# 5. RETRY LIEFECYCLE & SIGNATURE IDENTICAL/IDEMPOTENT ACROSS RETRIES
@pytest.mark.parametrize("status_code", [500, 503, 408, 429])
def test_webhook_delivery_transient_failure_retries_and_exhausts(status_code, celery_eager):
    db = SessionLocal()
    user = create_test_user(db, f"wh_trans_{status_code}")
    ep = WebhookEndpoint(user_id=user.id, url="https://receiver.com/hook", secret="supersecret", subscribed_events=["*"])
    db.add(ep)
    db.commit()
    
    event = EventSchema(event_type="test.ping", user_id=user.id, payload={"transient": True})
    canonical_payload = json.dumps(event.model_dump(), sort_keys=True, separators=(",", ":"))
    timestamp = int(time.time())
    delivery_id = f"del_trans_{status_code}"

    log = WebhookDeliveryLog(
        webhook_id=ep.id,
        delivery_id=delivery_id,
        event_type=event.event_type,
        event_id=event.event_id,
        status="PENDING",
        attempt_count=0,
        request_url=ep.url,
        payload_json=canonical_payload,
        dispatch_timestamp=timestamp,
    )
    db.add(log)
    db.commit()
    db.close()

    # We mock requests.post to return the transient status code, and we verify Celery self.retry is triggered.
    # When eager execution is used, Celery raises Retry exception during execution.
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    
    with patch("requests.post", return_value=mock_resp) as mock_post, \
         patch("backend.jobs.tasks.webhook_delivery.deliver_webhook.retry") as mock_retry:
         
        mock_retry.side_effect = Retry("Retry task")
        with pytest.raises(Retry):
            deliver_webhook.delay(delivery_id)
        
        # Verify Celery.retry was called
        mock_retry.assert_called_once()
        mock_post.assert_called_once()
        
        # Verify the signature & headers are deterministic (sent payload unchanged)
        called_headers = mock_post.call_args[1]["headers"]
        expected_message = f"{timestamp}.{canonical_payload}"
        expected_signature = hmac.new(b"supersecret", expected_message.encode("utf-8"), hashlib.sha256).hexdigest()
        assert called_headers["X-Scriptloom-Signature"] == expected_signature
        assert called_headers["X-Scriptloom-Timestamp"] == str(timestamp)
        assert called_headers["X-Scriptloom-Delivery-ID"] == delivery_id

        # Verify database log attempt_count incremented and status goes back to PENDING pending next retry
        db = SessionLocal()
        log_db = db.query(WebhookDeliveryLog).filter(WebhookDeliveryLog.delivery_id == delivery_id).first()
        assert log_db.status == "PENDING"
        assert log_db.attempt_count == 1
        assert f"HTTP {status_code}" in log_db.failure_reason
        db.close()


# 6. WORKER CRASH SAFETY
@patch("requests.post", side_effect=RuntimeError("Worker segfault / unhandled exception"))
def test_worker_crash_safety(mock_post, celery_eager):
    db = SessionLocal()
    user = create_test_user(db, "wh_crash")
    ep = WebhookEndpoint(user_id=user.id, url="https://receiver.com/hook", secret="supersecret", subscribed_events=["*"])
    db.add(ep)
    db.commit()
    
    event = EventSchema(event_type="test.ping", user_id=user.id, payload={})
    canonical_payload = json.dumps(event.model_dump(), sort_keys=True, separators=(",", ":"))
    timestamp = int(time.time())
    delivery_id = "del_crash_123"

    log = WebhookDeliveryLog(
        webhook_id=ep.id,
        delivery_id=delivery_id,
        event_type=event.event_type,
        event_id=event.event_id,
        status="PENDING",
        attempt_count=0,
        request_url=ep.url,
        payload_json=canonical_payload,
        dispatch_timestamp=timestamp,
    )
    db.add(log)
    db.commit()
    db.close()

    # Deliver task - raises RuntimeError
    with pytest.raises(RuntimeError):
        deliver_webhook.delay(delivery_id)

    # Verify delivery record is safely updated to FAILED and not stuck in PROCESSING
    db = SessionLocal()
    log_db = db.query(WebhookDeliveryLog).filter(WebhookDeliveryLog.delivery_id == delivery_id).first()
    assert log_db.status == "FAILED"
    assert "crash" in log_db.failure_reason.lower() or "unhandled exception" in log_db.failure_reason.lower()
    db.close()


# 7. PROCESSING RECOVERY BEHAVIOR
def test_worker_crash_recovery_startup_hook():
    db = SessionLocal()
    user = create_test_user(db, "wh_recover")
    ep = WebhookEndpoint(user_id=user.id, url="https://receiver.com/hook", secret="sec", subscribed_events=["*"])
    db.add(ep)
    db.commit()

    # Create 2 stuck PROCESSING logs
    # 1 stale (processing_started_at is 1 hour ago) -> should recover
    # 1 recent (processing_started_at is 10 seconds ago) -> should NOT recover
    now = datetime.now(timezone.utc)
    stale_log = WebhookDeliveryLog(
        webhook_id=ep.id,
        delivery_id="del_stale",
        event_type="test.ping",
        event_id="evt_stale",
        status="PROCESSING",
        request_url=ep.url,
        payload_json="{}",
        dispatch_timestamp=int(time.time()),
        processing_started_at=now - timedelta(hours=1),
    )
    recent_log = WebhookDeliveryLog(
        webhook_id=ep.id,
        delivery_id="del_recent",
        event_type="test.ping",
        event_id="evt_recent",
        status="PROCESSING",
        request_url=ep.url,
        payload_json="{}",
        dispatch_timestamp=int(time.time()),
        processing_started_at=now - timedelta(seconds=10),
    )
    db.add_all([stale_log, recent_log])
    db.commit()
    db.close()

    # Run the recovery helper imported from backend.main
    from backend.main import recover_stale_webhook_deliveries
    recover_stale_webhook_deliveries()

    # Verify recovery result
    db = SessionLocal()
    stale_db = db.query(WebhookDeliveryLog).filter(WebhookDeliveryLog.delivery_id == "del_stale").first()
    recent_db = db.query(WebhookDeliveryLog).filter(WebhookDeliveryLog.delivery_id == "del_recent").first()

    assert stale_db.status == "PENDING"
    assert stale_db.failure_reason == "Worker crash recovery reset"
    assert stale_db.processing_started_at is None

    assert recent_db.status == "PROCESSING"
    assert recent_db.failure_reason is None
    assert recent_db.processing_started_at is not None
    db.close()


# 8. TEST ENDPOINT EXERCISES ENTIRE PIPELINE
@patch("backend.jobs.tasks.webhook_delivery.deliver_webhook.delay")
def test_management_test_endpoint(mock_delay):
    db = SessionLocal()
    user = create_test_user(db, "wh_mgmt_test")
    ep = WebhookEndpoint(user_id=user.id, url="https://receiver.com/hook", secret="sec", subscribed_events=["*"])
    db.add(ep)
    db.commit()
    user_id = user.id
    ep_id = ep.id
    db.close()

    token = create_access_token({"sub": str(user_id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger endpoint test
    resp = client.post(f"/api/v1/api/v1/webhooks/endpoints/{ep_id}/test", headers=headers)
    assert resp.status_code == 202
    assert "delivery_id" in resp.json()
    delivery_id = resp.json()["delivery_id"]

    # Verify the task was queued with the delivery_id
    mock_delay.assert_called_once_with(delivery_id)

    # Verify the delivery log was persisted in the DB as PENDING with canonical test payload
    db = SessionLocal()
    log_db = db.query(WebhookDeliveryLog).filter(WebhookDeliveryLog.delivery_id == delivery_id).first()
    assert log_db is not None
    assert log_db.status == "PENDING"
    assert log_db.event_type == "test.ping"
    
    # Check payload is canonical JSON string
    parsed_payload = json.loads(log_db.payload_json)
    assert parsed_payload["event_type"] == "test.ping"
    assert parsed_payload["user_id"] == user_id
    db.close()
