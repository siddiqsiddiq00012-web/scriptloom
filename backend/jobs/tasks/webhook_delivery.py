import hmac
import hashlib
import json
import logging
import requests
from datetime import datetime, timezone
from celery.exceptions import MaxRetriesExceededError, Retry

from backend.db.database import SessionLocal
from backend.jobs.celery_app import celery_app
from backend.models.webhook import WebhookEndpoint, WebhookDeliveryLog, DeadLetterQueue
from backend.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="backend.jobs.tasks.webhook_delivery.deliver_webhook",
    max_retries=None,  # We manage max retries manually based on settings
)
def deliver_webhook(self, delivery_id: str):
    db = SessionLocal()
    try:
        # 1. Retrieve the delivery log record
        log_entry = (
            db.query(WebhookDeliveryLog)
            .filter(WebhookDeliveryLog.delivery_id == delivery_id)
            .first()
        )
        if not log_entry:
            logger.error(f"Webhook delivery log {delivery_id} not found.")
            return

        # Check for idempotency: if already completed/failed, abort processing
        if log_entry.status in ("DELIVERED", "FAILED"):
            logger.warning(
                f"Webhook delivery {delivery_id} already has final state {log_entry.status}. Aborting."
            )
            return

        # 2. Retrieve endpoint config
        endpoint = (
            db.query(WebhookEndpoint)
            .filter(WebhookEndpoint.id == log_entry.webhook_id)
            .first()
        )
        if not endpoint:
            log_entry.status = "FAILED"
            log_entry.failure_reason = "Webhook endpoint not found"
            log_entry.updated_at = datetime.now(timezone.utc)
            db.commit()
            return

        if not endpoint.is_active:
            log_entry.status = "FAILED"
            log_entry.failure_reason = "Webhook endpoint is inactive"
            log_entry.updated_at = datetime.now(timezone.utc)
            db.commit()
            return

        # Update attempt count and state to PROCESSING
        log_entry.attempt_count += 1
        log_entry.attempts = log_entry.attempt_count  # Sync attempts for backward compatibility
        log_entry.status = "PROCESSING"
        log_entry.processing_started_at = datetime.now(timezone.utc)
        log_entry.updated_at = datetime.now(timezone.utc)
        db.commit()

        # 3. Deterministic HMAC signing & payload serialization
        # The payload_json in the database is already stored in canonical string format.
        # We also reuse the dispatch_timestamp persisted inside the delivery record.
        message = f"{log_entry.dispatch_timestamp}.{log_entry.payload_json}"
        signature = hmac.new(
            endpoint.secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Idempotency and signature headers
        headers = {
            "Content-Type": "application/json",
            "X-Scriptloom-Signature": signature,
            "X-Scriptloom-Event": log_entry.event_type,
            "X-Scriptloom-Timestamp": str(log_entry.dispatch_timestamp),
            "X-Scriptloom-Delivery-ID": log_entry.delivery_id,
            "X-Scriptloom-Version": "1.0",
        }

        # 4. Perform HTTP delivery with connect/read timeout
        timeout = getattr(settings, "WEBHOOK_TIMEOUT", 5.0)
        is_transient = False
        error_msg = ""

        try:
            resp = requests.post(
                log_entry.request_url,
                data=log_entry.payload_json.encode("utf-8"),
                headers=headers,
                timeout=timeout,
            )
            log_entry.response_status = resp.status_code
            log_entry.status_code = resp.status_code  # Sync status_code for backward compatibility
            
            if 200 <= resp.status_code < 300:
                log_entry.status = "DELIVERED"
                log_entry.delivered_at = datetime.now(timezone.utc)
                log_entry.failure_reason = None
                log_entry.updated_at = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"Webhook delivery {delivery_id} succeeded with HTTP {resp.status_code}.")
                return
            
            # Non-2xx response transient vs permanent checks
            is_transient = resp.status_code in (408, 429) or (resp.status_code >= 500)
            error_msg = f"HTTP {resp.status_code}"
            
        except requests.exceptions.Timeout as t_err:
            is_transient = True
            log_entry.response_status = None
            log_entry.status_code = 0
            error_msg = "connection timeout"
        except requests.exceptions.RequestException as req_err:
            is_transient = True
            log_entry.response_status = None
            log_entry.status_code = 0
            # Clean up/sanitize network exception messages to keep failure_reason clean
            if "Max retries exceeded" in str(req_err) or "Failed to establish a new connection" in str(req_err):
                error_msg = "receiver unavailable"
            elif "Name or service not known" in str(req_err) or "DNS resolution" in str(req_err):
                error_msg = "DNS resolution failed"
            else:
                error_msg = "receiver unavailable"

        # 5. Retry timing & schedule management
        max_retries = getattr(settings, "WEBHOOK_MAX_RETRIES", 3)
        retry_delay = getattr(settings, "WEBHOOK_RETRY_DELAY", 60)

        # Retry logic if failure is transient and within limit
        if is_transient and (log_entry.attempt_count - 1) < max_retries:
            # Backoff delay: WEBHOOK_RETRY_DELAY * 2 ** (attempt - 1)
            backoff_multiplier = 2 ** (log_entry.attempt_count - 1)
            next_delay = retry_delay * backoff_multiplier
            next_delay = min(next_delay, 3600)  # cap at 1 hour

            # Transition back to PENDING while waiting for retry task
            log_entry.status = "PENDING"
            log_entry.failure_reason = error_msg
            log_entry.updated_at = datetime.now(timezone.utc)
            db.commit()

            logger.info(
                f"Webhook delivery {delivery_id} failed transiently ({error_msg}). "
                f"Retrying in {next_delay} seconds (attempt {log_entry.attempt_count}/{max_retries + 1})."
            )
            
            # Trigger Celery retry scheduling
            self.retry(exc=Exception(error_msg), countdown=next_delay)
        else:
            # Permanent failure or retries exhausted
            log_entry.status = "FAILED"
            if log_entry.attempt_count > max_retries:
                log_entry.failure_reason = f"Exhausted retries. Last error: {error_msg}"
            else:
                log_entry.failure_reason = f"Permanent failure: {error_msg}"
            log_entry.updated_at = datetime.now(timezone.utc)
            
            # Escalate to DLQ
            dlq_entry = DeadLetterQueue(
                delivery_id=log_entry.delivery_id,
                reason=log_entry.failure_reason,
                failed_at=datetime.now(timezone.utc),
            )
            db.add(dlq_entry)
            db.commit()
            logger.error(f"Webhook delivery {delivery_id} permanently failed: {log_entry.failure_reason}")

    except Exception as exc:
        db.rollback()
        # If not a Celery retry control exception, handle unhandled worker crash recovery updates
        if not isinstance(exc, Retry):
            logger.error(f"Crash during webhook delivery {delivery_id}: {exc}", exc_info=True)
            err_db = SessionLocal()
            try:
                err_entry = (
                    err_db.query(WebhookDeliveryLog)
                    .filter(WebhookDeliveryLog.delivery_id == delivery_id)
                    .first()
                )
                if err_entry and err_entry.status not in ("DELIVERED", "FAILED"):
                    err_entry.status = "FAILED"
                    err_entry.failure_reason = "Worker crash/unhandled exception"
                    err_entry.updated_at = datetime.now(timezone.utc)
                    err_db.commit()
            except Exception as crash_exc:
                logger.error(f"Failed to record crash state for delivery {delivery_id}: {crash_exc}")
            finally:
                err_db.close()
        raise exc
    finally:
        db.close()
