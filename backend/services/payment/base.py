from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from enum import Enum


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    INCOMPLETE = "incomplete"
    TRIALING = "trialing"


class PaymentStatus(str, Enum):
    SUCCEEDED = "succeeded"
    PENDING = "pending"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class CheckoutSessionResult:
    session_id: str
    url: str
    provider: str


@dataclass
class SubscriptionResult:
    provider_subscription_id: str
    status: SubscriptionStatus
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False


@dataclass
class CustomerResult:
    provider_customer_id: str
    email: str
    name: Optional[str] = None


@dataclass
class InvoiceResult:
    provider_invoice_id: str
    amount_cents: int
    currency: str
    status: PaymentStatus
    created_at: datetime
    invoice_url: Optional[str] = None
    invoice_pdf: Optional[str] = None


@dataclass
class PaymentMethodResult:
    provider_payment_method_id: str
    brand: Optional[str] = None
    last4: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None


@dataclass
class WebhookEvent:
    event_id: str
    event_type: str
    provider: str
    data: dict[str, Any]
    created_at: datetime


class PaymentProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def is_configured(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def publishable_key(self) -> Optional[str]:
        pass

    @abstractmethod
    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> CustomerResult:
        pass

    @abstractmethod
    def create_checkout_session(
        self,
        customer_id: str,
        plan_key: str,
        billing_cycle: BillingCycle,
        success_url: str,
        cancel_url: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> CheckoutSessionResult:
        pass

    @abstractmethod
    def get_subscription(self, subscription_id: str) -> SubscriptionResult:
        pass

    @abstractmethod
    def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False,
    ) -> SubscriptionResult:
        pass

    @abstractmethod
    def list_invoices(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[InvoiceResult]:
        pass

    @abstractmethod
    def get_payment_methods(self, customer_id: str) -> list[PaymentMethodResult]:
        pass

    @abstractmethod
    def attach_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
    ) -> PaymentMethodResult:
        pass

    @abstractmethod
    def detach_payment_method(self, payment_method_id: str) -> bool:
        pass

    @abstractmethod
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> WebhookEvent:
        pass

    @abstractmethod
    def construct_plan_price_id(self, plan_key: str, billing_cycle: BillingCycle) -> Optional[str]:
        pass
