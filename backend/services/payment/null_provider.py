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


class NullProvider(PaymentProvider):
    def __init__(self):
        logger.info("PaymentProvider: Using NullProvider - payments are disabled")

    @property
    def name(self) -> str:
        return "null"

    @property
    def is_configured(self) -> bool:
        return False

    @property
    def publishable_key(self) -> Optional[str]:
        return None

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> CustomerResult:
        raise RuntimeError("Payments are not configured. Please add Stripe credentials to enable payments.")

    def create_checkout_session(
        self,
        customer_id: str,
        plan_key: str,
        billing_cycle: BillingCycle,
        success_url: str,
        cancel_url: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> CheckoutSessionResult:
        raise RuntimeError("Payments are not configured. Please add Stripe credentials to enable payments.")

    def get_subscription(self, subscription_id: str) -> SubscriptionResult:
        raise RuntimeError("Payments are not configured. Please add Stripe credentials to enable payments.")

    def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False,
    ) -> SubscriptionResult:
        raise RuntimeError("Payments are not configured. Please add Stripe credentials to enable payments.")

    def list_invoices(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[InvoiceResult]:
        return []

    def get_payment_methods(self, customer_id: str) -> list[PaymentMethodResult]:
        return []

    def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> PaymentMethodResult:
        raise RuntimeError("Payments are not configured. Please add Stripe credentials to enable payments.")

    def detach_payment_method(self, payment_method_id: str) -> bool:
        return False

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> WebhookEvent:
        raise RuntimeError("Payments are not configured. Please add Stripe credentials to enable payments.")

    def construct_plan_price_id(self, plan_key: str, billing_cycle: BillingCycle) -> Optional[str]:
        return None
