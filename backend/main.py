from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router
from backend.core.config import settings
from backend.db.database import engine
from backend.models import Base  # Imports all models via __init__.py


from backend.middleware.request_id import RequestIDMiddleware
from backend.core.security_headers import SecurityHeadersMiddleware
from backend.middleware.rate_limiter import RateLimiterMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# Add Middleware Stack
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def recover_stale_webhook_deliveries():
    from backend.db.database import SessionLocal
    from backend.models.webhook import WebhookDeliveryLog
    from datetime import datetime, timezone
    
    db = SessionLocal()
    try:
        timeout = getattr(settings, "WEBHOOK_RECOVERY_TIMEOUT", 300)
        current_time = datetime.now(timezone.utc)
        
        # Select processing logs
        processing_deliveries = (
            db.query(WebhookDeliveryLog)
            .filter(WebhookDeliveryLog.status == "PROCESSING")
            .all()
        )
        
        recovered_count = 0
        for delivery in processing_deliveries:
            if delivery.processing_started_at:
                started_at = delivery.processing_started_at
                if started_at.tzinfo is None:
                    started_at = started_at.replace(tzinfo=timezone.utc)
                elapsed = (current_time - started_at).total_seconds()
                if elapsed > timeout:
                    delivery.status = "PENDING"
                    delivery.failure_reason = "Worker crash recovery reset"
                    delivery.processing_started_at = None
                    recovered_count += 1
                    
        if recovered_count > 0:
            db.commit()
            print(f"[RECOVERY] Successfully recovered {recovered_count} stuck webhook deliveries.")
    except Exception as err:
        db.rollback()
        print(f"[RECOVERY ERROR] Failed to run webhook crash recovery on startup: {err}")
    finally:
        db.close()


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    recover_stale_webhook_deliveries()


app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} is running."
    }