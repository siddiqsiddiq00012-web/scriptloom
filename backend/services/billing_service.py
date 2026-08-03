from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.billing import UsageRecord, UserSubscription

PLAN_LIMITS = {
    "starter": {
        "max_hours": 5.0,
        "max_packs": 10,
        "max_voice_dna": 1,
        "name": "Starter Plan",
    },
    "founder_pro": {
        "max_hours": 50.0,
        "max_packs": 500,
        "max_voice_dna": 3,
        "name": "Founder Pro Plan ($49/mo)",
    },
    "enterprise": {
        "max_hours": 9999.0,
        "max_packs": 99999,
        "max_voice_dna": 10,
        "name": "Enterprise Plan",
    },
}


class BillingService:
    def __init__(self, db: Session):
        self.db = db

    def _get_current_period_month(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def get_or_create_subscription(self, user_id: int) -> UserSubscription:
        sub = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.user_id == user_id)
            .first()
        )
        if not sub:
            sub = UserSubscription(user_id=user_id, plan_name="starter", status="active")
            self.db.add(sub)
            self.db.commit()
            self.db.refresh(sub)
        return sub

    def get_or_create_usage(self, user_id: int) -> UsageRecord:
        period = self._get_current_period_month()
        usage = (
            self.db.query(UsageRecord)
            .filter(
                UsageRecord.user_id == user_id,
                UsageRecord.period_month == period,
            )
            .first()
        )
        if not usage:
            usage = UsageRecord(
                user_id=user_id,
                hours_processed=0.0,
                campaign_packs_generated=0,
                period_month=period,
            )
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
        return usage

    def get_user_billing_summary(self, user_id: int) -> dict:
        sub = self.get_or_create_subscription(user_id)
        usage = self.get_or_create_usage(user_id)

        plan = PLAN_LIMITS.get(sub.plan_name, PLAN_LIMITS["starter"])
        hours_remaining = max(0.0, plan["max_hours"] - usage.hours_processed)

        return {
            "user_id": user_id,
            "plan_name": sub.plan_name,
            "plan_display_name": plan["name"],
            "status": sub.status,
            "hours_processed": round(usage.hours_processed, 2),
            "hours_limit": plan["max_hours"],
            "hours_remaining": round(hours_remaining, 2),
            "campaign_packs_generated": usage.campaign_packs_generated,
            "campaign_packs_limit": plan["max_packs"],
            "period_month": usage.period_month,
        }

    def check_quota(self, user_id: int, duration_seconds: float = 0.0):
        summary = self.get_user_billing_summary(user_id)
        additional_hours = duration_seconds / 3600.0

        if summary["hours_processed"] + additional_hours > summary["hours_limit"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Monthly audio processing quota exceeded. Used {summary['hours_processed']}h of {summary['hours_limit']}h. Please upgrade to Founder Pro.",
            )

    def record_usage(self, user_id: int, duration_seconds: float = 0.0, packs_count: int = 0):
        usage = self.get_or_create_usage(user_id)
        hours_added = duration_seconds / 3600.0
        usage.hours_processed += hours_added
        usage.campaign_packs_generated += packs_count
        self.db.commit()
        self.db.refresh(usage)
        return usage

    def upgrade_subscription(self, user_id: int, new_plan: str) -> UserSubscription:
        if new_plan not in PLAN_LIMITS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan '{new_plan}'. Supported: {', '.join(PLAN_LIMITS.keys())}",
            )

        sub = self.get_or_create_subscription(user_id)
        sub.plan_name = new_plan
        sub.status = "active"
        self.db.commit()
        self.db.refresh(sub)
        return sub
