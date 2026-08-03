import hmac
import hashlib
import json
import random
import time
import uuid
import requests
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models.webhook import WebhookEndpoint, WebhookDeliveryLog, DeadLetterQueue
from backend.events.event_bus import event_bus, EventSchema


class WebhookDispatcher:
    @staticmethod
    def generate_signature(payload_bytes: bytes, secret: str) -> str:
        return hmac.new(
            secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def dispatch_event(
        db: Session,
        endpoint: WebhookEndpoint,
        event: EventSchema,
    ) -> bool:
        delivery_id = f"del_{uuid.uuid4().hex[:12]}"
        timestamp_str = str(int(time.time()))
        payload_bytes = json.dumps(event.model_dump()).encode("utf-8")
        signature = WebhookDispatcher.generate_signature(payload_bytes, endpoint.secret)

        headers = {
            "Content-Type": "application/json",
            "X-Scriptloom-Signature": signature,
            "X-Scriptloom-Event": event.event_type,
            "X-Scriptloom-Timestamp": timestamp_str,
            "X-Scriptloom-Delivery-ID": delivery_id,
            "X-Scriptloom-Version": "1.0",
        }

        # Record initial delivery log
        log_entry = WebhookDeliveryLog(
            webhook_id=endpoint.id,
            delivery_id=delivery_id,
            event_type=event.event_type,
            status_code=0,
            attempts=1,
            status="PENDING",
            payload_json=event.model_dump(),
        )
        db.add(log_entry)
        db.commit()

        # Retry Schedule Delays (with jitter)
        delays = [0, 30, 120, 600]
        success = False
        last_status_code = 0

        for attempt_idx, delay in enumerate(delays, start=1):
            if delay > 0:
                jitter = random.uniform(0.5, 2.0)
                time.sleep(delay * 0.05 + jitter)  # Compressed delay for responsive processing

            try:
                resp = requests.post(
                    endpoint.url,
                    data=payload_bytes,
                    headers=headers,
                    timeout=5.0,
                )
                last_status_code = resp.status_code
                log_entry.status_code = last_status_code
                log_entry.attempts = attempt_idx

                if 200 <= resp.status_code < 300:
                    log_entry.status = "DELIVERED"
                    db.commit()
                    success = True
                    break
                else:
                    log_entry.status = "FAILED"
                    db.commit()
            except Exception as exc:
                log_entry.attempts = attempt_idx
                log_entry.status = "FAILED"
                db.commit()

        # If permanently failed after max retries, send to Dead Letter Queue
        if not success:
            log_entry.status = "DEAD_LETTER"
            dlq_entry = DeadLetterQueue(
                delivery_id=delivery_id,
                reason=f"Exhausted retries. Last status code: {last_status_code}",
            )
            db.add(dlq_entry)
            db.commit()

        return success
