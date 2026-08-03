from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.schemas.billing import (
    SubscriptionResponse,
    UpgradeRequest,
    UsageResponse,
)
from backend.services.billing_service import BillingService

router = APIRouter(
    prefix="/billing",
    tags=["Billing & Usage"],
)


@router.get(
    "/subscription",
    response_model=SubscriptionResponse,
)
def get_user_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BillingService(db)
    summary = service.get_user_billing_summary(current_user.id)
    return SubscriptionResponse(
        user_id=summary["user_id"],
        plan_name=summary["plan_name"],
        plan_display_name=summary["plan_display_name"],
        status=summary["status"],
    )


@router.get(
    "/usage",
    response_model=UsageResponse,
)
def get_user_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BillingService(db)
    summary = service.get_user_billing_summary(current_user.id)
    return UsageResponse(**summary)


@router.post(
    "/upgrade",
    response_model=SubscriptionResponse,
)
def upgrade_user_plan(
    request: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BillingService(db)
    upgraded_sub = service.upgrade_subscription(
        user_id=current_user.id,
        new_plan=request.plan_name,
    )
    summary = service.get_user_billing_summary(current_user.id)
    return SubscriptionResponse(
        user_id=summary["user_id"],
        plan_name=summary["plan_name"],
        plan_display_name=summary["plan_display_name"],
        status=summary["status"],
    )
