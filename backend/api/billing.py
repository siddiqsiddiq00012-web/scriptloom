import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional

from backend.core.dependencies import get_current_user
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.schemas.billing import (
    SubscriptionResponse,
    UsageResponse,
    CheckoutRequest,
    CheckoutResponse,
    PlanResponse,
    PaymentProviderStatus,
    InvoiceResponse,
    CancelSubscriptionRequest,
)
from backend.services.billing_service import BillingService
from backend.services.payment import get_payment_provider

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/billing",
    tags=["Billing & Usage"],
)


@router.get("/plans", response_model=list[PlanResponse])
def list_plans(
    db: Session = Depends(get_db),
):
    service = BillingService(db)
    return service.get_all_plans()


@router.get("/provider-status", response_model=PaymentProviderStatus)
def get_provider_status():
    provider = get_payment_provider()
    return {
        "provider": provider.name,
        "is_configured": provider.is_configured,
        "publishable_key": provider.publishable_key,
    }


@router.get("/subscription", response_model=SubscriptionResponse)
def get_user_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BillingService(db)
    summary = service.get_user_billing_summary(current_user)
    return SubscriptionResponse(
        user_id=summary["user_id"],
        plan_key=summary["plan_key"],
        plan_name=summary["plan_name"],
        plan_display_name=summary["plan_display_name"],
        status=summary["status"],
        billing_cycle=summary["billing_cycle"],
    )


@router.get("/usage", response_model=UsageResponse)
def get_user_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BillingService(db)
    summary = service.get_user_billing_summary(current_user)
    return UsageResponse(
        user_id=summary["user_id"],
        plan_key=summary["plan_key"],
        plan_name=summary["plan_name"],
        plan_display_name=summary["plan_display_name"],
        status=summary["status"],
        billing_cycle=summary["billing_cycle"],
        media_uploads=summary["media_uploads"],
        processing_minutes=summary["processing_minutes"],
        ai_generations=summary["ai_generations"],
        storage=summary["storage"],
        features=summary["features"],
        period_month=summary["period_month"],
    )


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout_session(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from backend.core.config import settings
    
    service = BillingService(db)
    
    success_url = request.success_url or f"{settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else 'http://localhost:5173'}/billing/success"
    cancel_url = request.cancel_url or f"{settings.ALLOWED_ORIGINS[0] if settings.ALLOWED_ORIGINS else 'http://localhost:5173'}/billing/cancel"
    
    result = service.create_checkout_session(
        user=current_user,
        plan_key=request.plan_key,
        billing_cycle=request.billing_cycle,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    
    return CheckoutResponse(**result)


@router.post("/cancel-subscription")
def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BillingService(db)
    subscription = service.cancel_subscription(current_user, immediately=request.immediately)
    
    return {
        "success": True,
        "status": subscription.status,
        "cancel_at_period_end": subscription.cancel_at_period_end,
    }


@router.get("/invoices", response_model=list[InvoiceResponse])
def list_invoices(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BillingService(db)
    return service.list_invoices(current_user, limit=limit)


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
):
    provider = get_payment_provider()
    
    if not provider.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhooks not configured",
        )
    
    payload = await request.body()
    
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header",
        )
    
    try:
        event = provider.verify_webhook_signature(payload, stripe_signature)
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )
    
    service = BillingService(db)
    service.handle_webhook_event(event)
    
    return {"received": True}


@router.post("/upgrade", response_model=SubscriptionResponse, deprecated=True)
def upgrade_user_plan(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="This endpoint is deprecated. Use POST /billing/checkout instead.",
    )
