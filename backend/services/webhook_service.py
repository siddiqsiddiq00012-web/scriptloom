import hmac
import hashlib
import json
import logging
import uuid
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.db.database import SessionLocal
from backend.models.webhook import WebhookEndpoint, WebhookDeliveryLog
from backend.events.event_bus import event_bus, EventSchema

logger = logging.getLogger(__name__)


class WebhookDispatcher:
    @staticmethod
    def generate_signature(dispatch_timestamp: int, payload_json: str, secret: str) -> str:
        message = f"{dispatch_timestamp}.{payload_json}"
        return hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def dispatch_event(
        db: Session,
        event: EventSchema,
    ) -> list[str]:
        # 1. Fetch active webhook endpoints matching the event user context
        if not event.user_id:
            logger.warning(f"Event {event.event_id} ({event.event_type}) has no user_id. Aborting webhook dispatch.")
            return []

        endpoints = (
            db.query(WebhookEndpoint)
            .filter(
                WebhookEndpoint.user_id == event.user_id,
                WebhookEndpoint.is_active == True,
            )
            .all()
        )

        dispatched_ids = []

        # 2. Iterate and match subscription rules
        for endpoint in endpoints:
            subscribed = endpoint.subscribed_events
            is_matched = False
            if isinstance(subscribed, list):
                is_matched = "*" in subscribed or event.event_type in subscribed

            if not is_matched:
                continue

            # 3. Serialize payload exactly once to canonical format
            canonical_payload = json.dumps(
                event.model_dump(),
                sort_keys=True,
                separators=(",", ":"),
            )

            delivery_id = f"del_{uuid.uuid4()}"
            dispatch_timestamp = int(time.time())

            # Create PENDING delivery log record
            log_entry = WebhookDeliveryLog(
                webhook_id=endpoint.id,
                delivery_id=delivery_id,
                event_type=event.event_type,
                event_id=event.event_id,
                status="PENDING",
                attempt_count=0,
                attempts=0,  # Sync attempts column for backward compatibility
                request_url=endpoint.url,
                response_status=None,
                status_code=0,  # Sync status_code column for backward compatibility
                failure_reason=None,
                payload_json=canonical_payload,
                dispatch_timestamp=dispatch_timestamp,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)

            # 4. Asynchronously queue standard Celery task
            from backend.jobs.tasks.webhook_delivery import deliver_webhook
            from celery.exceptions import Retry
            try:
                deliver_webhook.delay(delivery_id)
                dispatched_ids.append(delivery_id)
                logger.info(
                    f"Successfully queued webhook task {delivery_id} for url {endpoint.url}."
                )
            except Retry:
                # Eager mode Celery retry trigger is treated as a successful queueing
                dispatched_ids.append(delivery_id)
            except Exception as cel_err:
                # Dispatch failure compensation strategy:
                # Mark delivery FAILED immediately inside DB if queue publication fails
                log_entry.status = "FAILED"
                log_entry.failure_reason = "Task queue dispatch failed"
                log_entry.updated_at = datetime.now(timezone.utc)
                db.commit()
                logger.error(
                    f"Celery dispatch failed for webhook delivery {delivery_id}: {cel_err}",
                    exc_info=True,
                )

        return dispatched_ids


def webhook_event_bus_subscriber(event: EventSchema):
    """
    Subscribes to all event_bus publications, resolving database context 
    and routing matching event deliveries asynchronously.
    """
    db = SessionLocal()
    try:
        WebhookDispatcher.dispatch_event(db, event)
    except Exception as err:
        logger.error(
            f"Error during event bus webhook dispatch for event {event.event_id}: {err}",
            exc_info=True,
        )
    finally:
        db.close()


# Connect global event bus to webhooks delivery dispatcher
event_bus.subscribe("*", webhook_event_bus_subscriber)
