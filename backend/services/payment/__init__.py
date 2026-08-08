from backend.services.payment.base import PaymentProvider
from backend.services.payment.stripe_provider import StripeProvider
from backend.services.payment.null_provider import NullProvider

__all__ = ["PaymentProvider", "StripeProvider", "NullProvider", "get_payment_provider"]

def get_payment_provider() -> PaymentProvider:
    from backend.core.config import settings
    
    if settings.STRIPE_SECRET_KEY:
        return StripeProvider()
    else:
        return NullProvider()
