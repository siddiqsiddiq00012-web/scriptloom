import logging
from datetime import datetime, timezone
from typing import Any, Optional

from backend.services.payment.base import (
    BillingCycle,
    CheckoutSessionResult,
    CustomerResult,
    InvoiceResult,
    PaymentMethodResult,
    PaymentProvider,
    PaymentStatus,
    SubscriptionResult,
    SubscriptionStatus,
    WebhookEvent,
)

logger = logging.getLogger(__name__)


class StripeProvider(PaymentProvider):
    def __init__(self):
        import stripe
        from backend.core.config import settings
        
        self._stripe = stripe
        self._stripe.api_key = settings.STRIPE_SECRET_KEY
        self._webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self._publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        
        self._price_mapping = {
            ("pro", BillingCycle.MONTHLY): settings.STRIPE_PRICE_PRO_MONTHLY,
            ("pro", BillingCycle.ANNUAL): settings.STRIPE_PRICE_PRO_ANNUAL,
        }

    @property
    def name(self) -> str:
        return "stripe"

    @property
    def is_configured(self) -> bool:
        return bool(self._stripe.api_key)

    @property
    def publishable_key(self) -> Optional[str]:
        return self._publishable_key

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> CustomerResult:
        try:
            customer = self._stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            return CustomerResult(
                provider_customer_id=customer.id,
                email=customer.email,
                name=customer.name,
            )
        except self._stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {e}")
            raise RuntimeError(f"Failed to create customer: {e}")

    def create_checkout_session(
        self,
        customer_id: str,
        plan_key: str,
        billing_cycle: BillingCycle,
        success_url: str,
        cancel_url: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> CheckoutSessionResult:
        price_id = self.construct_plan_price_id(plan_key, billing_cycle)
        if not price_id:
            raise ValueError(f"No Stripe price configured for plan '{plan_key}' with {billing_cycle} billing")
        
        try:
            session = self._stripe.checkout.Session.create(
                customer=customer_id,
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
                subscription_data={
                    "metadata": metadata or {},
                },
            )
            return CheckoutSessionResult(
                session_id=session.id,
                url=session.url,
                provider=self.name,
            )
        except self._stripe.error.StripeError as e:
            logger.error(f"Stripe checkout session creation failed: {e}")
            raise RuntimeError(f"Failed to create checkout session: {e}")

    def get_subscription(self, subscription_id: str) -> SubscriptionResult:
        try:
            sub = self._stripe.Subscription.retrieve(subscription_id)
            return SubscriptionResult(
                provider_subscription_id=sub.id,
                status=SubscriptionStatus(sub.status),
                current_period_start=datetime.fromtimestamp(sub.current_period_start, tz=timezone.utc),
                current_period_end=datetime.fromtimestamp(sub.current_period_end, tz=timezone.utc),
                cancel_at_period_end=sub.cancel_at_period_end,
            )
        except self._stripe.error.StripeError as e:
            logger.error(f"Stripe subscription retrieval failed: {e}")
            raise RuntimeError(f"Failed to get subscription: {e}")

    def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False,
    ) -> SubscriptionResult:
        try:
            if immediately:
                sub = self._stripe.Subscription.delete(subscription_id)
            else:
                sub = self._stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )
            return SubscriptionResult(
                provider_subscription_id=sub.id,
                status=SubscriptionStatus(sub.status),
                current_period_start=datetime.fromtimestamp(sub.current_period_start, tz=timezone.utc) if sub.current_period_start else None,
                current_period_end=datetime.fromtimestamp(sub.current_period_end, tz=timezone.utc) if sub.current_period_end else None,
                cancel_at_period_end=sub.cancel_at_period_end,
            )
        except self._stripe.error.StripeError as e:
            logger.error(f"Stripe subscription cancellation failed: {e}")
            raise RuntimeError(f"Failed to cancel subscription: {e}")

    def list_invoices(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[InvoiceResult]:
        try:
            invoices = self._stripe.Invoice.list(
                customer=customer_id,
                limit=limit,
            )
            results = []
            for inv in invoices.data:
                status_map = {
                    "paid": PaymentStatus.SUCCEEDED,
                    "open": PaymentStatus.PENDING,
                    "void": PaymentStatus.FAILED,
                    "refunded": PaymentStatus.REFUNDED,
                }
                results.append(InvoiceResult(
                    provider_invoice_id=inv.id,
                    amount_cents=inv.amount_paid,
                    currency=inv.currency.upper(),
                    status=status_map.get(inv.status, PaymentStatus.PENDING),
                    created_at=datetime.fromtimestamp(inv.created, tz=timezone.utc),
                    invoice_url=inv.hosted_invoice_url,
                    invoice_pdf=inv.invoice_pdf,
                ))
            return results
        except self._stripe.error.StripeError as e:
            logger.error(f"Stripe invoice listing failed: {e}")
            return []

    def get_payment_methods(self, customer_id: str) -> list[PaymentMethodResult]:
        try:
            methods = self._stripe.PaymentMethod.list(
                customer=customer_id,
                type="card",
            )
            results = []
            for pm in methods.data:
                card = pm.card or {}
                results.append(PaymentMethodResult(
                    provider_payment_method_id=pm.id,
                    brand=card.get("brand"),
                    last4=card.get("last4"),
                    exp_month=card.get("exp_month"),
                    exp_year=card.get("exp_year"),
                ))
            return results
        except self._stripe.error.StripeError as e:
            logger.error(f"Stripe payment method listing failed: {e}")
            return []

    def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> PaymentMethodResult:
        try:
            pm = self._stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )
            card = pm.card or {}
            return PaymentMethodResult(
                provider_payment_method_id=pm.id,
                brand=card.get("brand"),
                last4=card.get("last4"),
                exp_month=card.get("exp_month"),
                exp_year=card.get("exp_year"),
            )
        except self._stripe.error.StripeError as e:
            logger.error(f"Stripe payment method attachment failed: {e}")
            raise RuntimeError(f"Failed to attach payment method: {e}")

    def detach_payment_method(self, payment_method_id: str) -> bool:
        try:
            self._stripe.PaymentMethod.detach(payment_method_id)
            return True
        except self._stripe.error.StripeError as e:
            logger.error(f"Stripe payment method detachment failed: {e}")
            return False

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> WebhookEvent:
        if not self._webhook_secret:
            raise RuntimeError("Stripe webhook secret not configured")
        
        try:
            event = self._stripe.Webhook.construct_event(
                payload,
                signature,
                self._webhook_secret,
            )
            return WebhookEvent(
                event_id=event.id,
                event_type=event.type,
                provider=self.name,
                data=event.data.object,
                created_at=datetime.fromtimestamp(event.created, tz=timezone.utc),
            )
        except self._stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe webhook signature verification failed: {e}")
            raise RuntimeError(f"Invalid webhook signature: {e}")

    def construct_plan_price_id(self, plan_key: str, billing_cycle: BillingCycle) -> Optional[str]:
        return self._price_mapping.get((plan_key, billing_cycle))
