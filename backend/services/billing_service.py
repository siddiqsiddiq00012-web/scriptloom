import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.billing import Plan, UserSubscription, UsageRecord, Invoice, PaymentMethod
from backend.models.user import User
from backend.services.plan_config import get_plan_config, PlanConfig, PLAN_CONFIGS
from backend.services.feature_gate import FeatureGate, Feature
from backend.services.payment import get_payment_provider

logger = logging.getLogger(__name__)


class BillingService:
    def __init__(self, db: Session):
        self.db = db
        self.feature_gate = FeatureGate(db)

    def initialize_plans(self) -> None:
        for plan_config in PLAN_CONFIGS.values():
            existing = self.db.query(Plan).filter(Plan.key == plan_config.key).first()
            if not existing:
                plan = Plan(
                    key=plan_config.key,
                    name=plan_config.name,
                    description=plan_config.description,
                    price_monthly_cents=plan_config.price_monthly_cents,
                    price_annual_cents=plan_config.price_annual_cents,
                    max_projects=plan_config.max_projects,
                    max_media_uploads=plan_config.max_media_uploads,
                    max_processing_minutes=plan_config.max_processing_minutes,
                    max_ai_generations=plan_config.max_ai_generations,
                    max_storage_bytes=plan_config.max_storage_bytes,
                    priority_processing=plan_config.priority_processing,
                    creator_intelligence_advanced=plan_config.creator_intelligence_advanced,
                    api_access=plan_config.api_access,
                    team_workspaces=plan_config.team_workspaces,
                    enterprise_support=plan_config.enterprise_support,
                    features=plan_config.features,
                    is_active=plan_config.is_active,
                    display_order=plan_config.display_order,
                )
                self.db.add(plan)
        
        self.db.commit()

    def get_or_create_subscription(self, user: User) -> UserSubscription:
        subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.user_id == user.id)
            .first()
        )
        
        if not subscription:
            free_plan = self.db.query(Plan).filter(Plan.key == "free").first()
            if not free_plan:
                self.initialize_plans()
                free_plan = self.db.query(Plan).filter(Plan.key == "free").first()
            
            subscription = UserSubscription(
                user_id=user.id,
                plan_id=free_plan.id if free_plan else None,
                status="active",
                billing_cycle="monthly",
            )
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
        
        return subscription

    def get_or_create_usage(self, user: User) -> UsageRecord:
        return self.feature_gate.get_usage(user)

    def get_user_billing_summary(self, user: User) -> dict:
        subscription = self.get_or_create_subscription(user)
        usage = self.get_or_create_usage(user)
        
        plan_config = self.feature_gate.get_user_plan(user)
        
        return {
            "user_id": user.id,
            "plan_key": plan_config.key,
            "plan_name": plan_config.name,
            "plan_display_name": plan_config.name,
            "status": subscription.status,
            "billing_cycle": subscription.billing_cycle,
            "media_uploads": {
                "used": usage.media_uploads,
                "limit": plan_config.max_media_uploads,
                "remaining": self._calculate_remaining(usage.media_uploads, plan_config.max_media_uploads),
            },
            "processing_minutes": {
                "used": usage.processing_seconds // 60,
                "limit": plan_config.max_processing_minutes,
                "remaining": self._calculate_remaining(usage.processing_seconds // 60, plan_config.max_processing_minutes),
            },
            "ai_generations": {
                "used": usage.ai_generations,
                "limit": plan_config.max_ai_generations,
                "remaining": self._calculate_remaining(usage.ai_generations, plan_config.max_ai_generations),
            },
            "storage": {
                "used_bytes": usage.storage_bytes,
                "limit_bytes": plan_config.max_storage_bytes,
                "used_gb": round(usage.storage_bytes / (1024 ** 3), 2),
                "limit_gb": round(plan_config.max_storage_bytes / (1024 ** 3), 2) if plan_config.max_storage_bytes > 0 else -1,
            },
            "features": {
                "priority_processing": plan_config.priority_processing,
                "creator_intelligence_advanced": plan_config.creator_intelligence_advanced,
                "api_access": plan_config.api_access,
                "team_workspaces": plan_config.team_workspaces,
            },
            "period_month": usage.period_month,
        }

    def _calculate_remaining(self, used: int, limit: int) -> int:
        if limit == -1:
            return -1
        return max(0, limit - used)

    def check_quota(self, user: User, feature: Feature, additional: int = 1) -> None:
        self.feature_gate.require_usage_limit(user, feature, additional)

    def record_usage(
        self,
        user: User,
        media_uploads: int = 0,
        processing_seconds: int = 0,
        ai_generations: int = 0,
        storage_bytes: int = 0,
    ) -> UsageRecord:
        return self.feature_gate.record_usage(
            user,
            media_uploads=media_uploads,
            processing_seconds=processing_seconds,
            ai_generations=ai_generations,
            storage_bytes=storage_bytes,
        )

    def create_checkout_session(
        self,
        user: User,
        plan_key: str,
        billing_cycle: str,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        provider = get_payment_provider()
        
        if not provider.is_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payments are not configured. Please contact support.",
            )
        
        plan_config = get_plan_config(plan_key)
        if not plan_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan: {plan_key}",
            )
        
        if plan_key == "enterprise":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enterprise plan requires contacting sales. Please email support@scriptloom.com",
            )
        
        subscription = self.get_or_create_subscription(user)
        
        if not subscription.provider_customer_id:
            try:
                customer = provider.create_customer(
                    email=user.email,
                    name=user.name,
                    metadata={"user_id": str(user.id)},
                )
                subscription.provider_customer_id = customer.provider_customer_id
                self.db.commit()
            except Exception as e:
                logger.error(f"Failed to create payment customer: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to initialize payment customer",
                )
        
        from backend.services.payment.base import BillingCycle
        cycle = BillingCycle(billing_cycle)
        
        try:
            session = provider.create_checkout_session(
                customer_id=subscription.provider_customer_id,
                plan_key=plan_key,
                billing_cycle=cycle,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user.id),
                    "plan_key": plan_key,
                    "billing_cycle": billing_cycle,
                },
            )
            
            return {
                "session_id": session.session_id,
                "url": session.url,
                "provider": session.provider,
            }
        except Exception as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    def handle_webhook_event(self, event) -> None:
        from backend.services.payment.base import WebhookEvent
        
        event_type = event.event_type
        data = event.data
        
        if event_type == "checkout.session.completed":
            self._handle_checkout_completed(data)
        elif event_type == "customer.subscription.updated":
            self._handle_subscription_updated(data)
        elif event_type == "customer.subscription.deleted":
            self._handle_subscription_deleted(data)
        elif event_type == "invoice.paid":
            self._handle_invoice_paid(data)
        elif event_type == "invoice.payment_failed":
            self._handle_payment_failed(data)

    def _handle_checkout_completed(self, data: dict) -> None:
        metadata = data.get("metadata", {})
        user_id = metadata.get("user_id")
        plan_key = metadata.get("plan_key")
        billing_cycle = metadata.get("billing_cycle", "monthly")
        
        if not user_id or not plan_key:
            logger.error(f"Checkout completed without user_id or plan_key: {data}")
            return
        
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            logger.error(f"User not found for checkout: {user_id}")
            return
        
        plan = self.db.query(Plan).filter(Plan.key == plan_key).first()
        if not plan:
            logger.error(f"Plan not found for checkout: {plan_key}")
            return
        
        subscription = self.get_or_create_subscription(user)
        subscription.plan_id = plan.id
        subscription.billing_cycle = billing_cycle
        subscription.status = "active"
        subscription.provider_subscription_id = data.get("subscription")
        
        self.db.commit()
        logger.info(f"Upgraded user {user_id} to {plan_key}")

    def _handle_subscription_updated(self, data: dict) -> None:
        subscription_id = data.get("id")
        status_val = data.get("status")
        
        subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.provider_subscription_id == subscription_id)
            .first()
        )
        
        if subscription:
            subscription.status = status_val
            self.db.commit()
            logger.info(f"Updated subscription {subscription_id} to {status_val}")

    def _handle_subscription_deleted(self, data: dict) -> None:
        subscription_id = data.get("id")
        
        subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.provider_subscription_id == subscription_id)
            .first()
        )
        
        if subscription:
            free_plan = self.db.query(Plan).filter(Plan.key == "free").first()
            if free_plan:
                subscription.plan_id = free_plan.id
            subscription.status = "cancelled"
            subscription.provider_subscription_id = None
            self.db.commit()
            logger.info(f"Downgraded subscription {subscription_id} to free")

    def _handle_invoice_paid(self, data: dict) -> None:
        customer_id = data.get("customer")
        invoice_id = data.get("id")
        
        subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.provider_customer_id == customer_id)
            .first()
        )
        
        if subscription:
            invoice = Invoice(
                user_id=subscription.user_id,
                provider_invoice_id=invoice_id,
                amount_cents=data.get("amount_paid", 0),
                currency=data.get("currency", "USD").upper(),
                status="paid",
                invoice_url=data.get("hosted_invoice_url"),
                invoice_pdf=data.get("invoice_pdf"),
            )
            self.db.add(invoice)
            self.db.commit()
            logger.info(f"Recorded invoice {invoice_id} for user {subscription.user_id}")

    def _handle_payment_failed(self, data: dict) -> None:
        customer_id = data.get("customer")
        
        subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.provider_customer_id == customer_id)
            .first()
        )
        
        if subscription:
            subscription.status = "past_due"
            self.db.commit()
            logger.warning(f"Payment failed for user {subscription.user_id}")

    def cancel_subscription(self, user: User, immediately: bool = False) -> UserSubscription:
        subscription = self.get_or_create_subscription(user)
        
        if not subscription.provider_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active paid subscription to cancel",
            )
        
        provider = get_payment_provider()
        
        if provider.is_configured:
            try:
                result = provider.cancel_subscription(
                    subscription.provider_subscription_id,
                    immediately=immediately,
                )
                
                if immediately:
                    free_plan = self.db.query(Plan).filter(Plan.key == "free").first()
                    if free_plan:
                        subscription.plan_id = free_plan.id
                    subscription.status = "cancelled"
                    subscription.provider_subscription_id = None
                    subscription.cancelled_at = datetime.now(timezone.utc)
                else:
                    subscription.cancel_at_period_end = True
                
                self.db.commit()
            except Exception as e:
                logger.error(f"Failed to cancel subscription: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        
        return subscription

    def list_invoices(self, user: User, limit: int = 10) -> list[dict]:
        invoices = (
            self.db.query(Invoice)
            .filter(Invoice.user_id == user.id)
            .order_by(Invoice.created_at.desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "id": inv.id,
                "provider_invoice_id": inv.provider_invoice_id,
                "amount_cents": inv.amount_cents,
                "currency": inv.currency,
                "status": inv.status,
                "invoice_url": inv.invoice_url,
                "invoice_pdf": inv.invoice_pdf,
                "created_at": inv.created_at.isoformat(),
            }
            for inv in invoices
        ]

    def get_payment_provider_status(self) -> dict:
        provider = get_payment_provider()
        
        return {
            "provider": provider.name,
            "is_configured": provider.is_configured,
            "publishable_key": provider.publishable_key,
        }

    def get_all_plans(self) -> list[dict]:
        plans = (
            self.db.query(Plan)
            .filter(Plan.is_active == True)
            .order_by(Plan.display_order)
            .all()
        )
        
        if not plans:
            self.initialize_plans()
            plans = (
                self.db.query(Plan)
                .filter(Plan.is_active == True)
                .order_by(Plan.display_order)
                .all()
            )
        
        return [
            {
                "key": plan.key,
                "name": plan.name,
                "description": plan.description,
                "price_monthly_cents": plan.price_monthly_cents,
                "price_annual_cents": plan.price_annual_cents,
                "currency": plan.currency,
                "limits": {
                    "max_projects": plan.max_projects,
                    "max_media_uploads": plan.max_media_uploads,
                    "max_processing_minutes": plan.max_processing_minutes,
                    "max_ai_generations": plan.max_ai_generations,
                    "max_storage_gb": round(plan.max_storage_bytes / (1024 ** 3), 2) if plan.max_storage_bytes > 0 else -1,
                },
                "features": plan.features or {},
                "tier_features": {
                    "priority_processing": plan.priority_processing,
                    "creator_intelligence_advanced": plan.creator_intelligence_advanced,
                    "api_access": plan.api_access,
                    "team_workspaces": plan.team_workspaces,
                    "enterprise_support": plan.enterprise_support,
                },
            }
            for plan in plans
        ]
