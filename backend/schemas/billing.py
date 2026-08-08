from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class SubscriptionResponse(BaseModel):
    user_id: int
    plan_key: str
    plan_name: str
    plan_display_name: str
    status: str
    billing_cycle: str

    model_config = ConfigDict(from_attributes=True)


class UsageDetail(BaseModel):
    used: int
    limit: int
    remaining: int


class StorageDetail(BaseModel):
    used_bytes: int
    limit_bytes: int
    used_gb: float
    limit_gb: float


class MediaUploadsUsage(BaseModel):
    used: int
    limit: int
    remaining: int


class ProcessingMinutesUsage(BaseModel):
    used: int
    limit: int
    remaining: int


class AIGenerationsUsage(BaseModel):
    used: int
    limit: int
    remaining: int


class StorageUsage(BaseModel):
    used_bytes: int
    limit_bytes: int
    used_gb: float
    limit_gb: float


class FeaturesStatus(BaseModel):
    priority_processing: bool
    creator_intelligence_advanced: bool
    api_access: bool
    team_workspaces: bool


class UsageResponse(BaseModel):
    user_id: int
    plan_key: str
    plan_name: str
    plan_display_name: str
    status: str
    billing_cycle: str
    media_uploads: MediaUploadsUsage
    processing_minutes: ProcessingMinutesUsage
    ai_generations: AIGenerationsUsage
    storage: StorageUsage
    features: FeaturesStatus
    period_month: str

    model_config = ConfigDict(from_attributes=True)


class CheckoutRequest(BaseModel):
    plan_key: str
    billing_cycle: str = "monthly"
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    session_id: str
    url: str
    provider: str


class PlanLimits(BaseModel):
    max_projects: int
    max_media_uploads: int
    max_processing_minutes: int
    max_ai_generations: int
    max_storage_gb: float


class TierFeatures(BaseModel):
    priority_processing: bool
    creator_intelligence_advanced: bool
    api_access: bool
    team_workspaces: bool
    enterprise_support: bool


class PlanResponse(BaseModel):
    key: str
    name: str
    description: Optional[str]
    price_monthly_cents: int
    price_annual_cents: int
    currency: str
    limits: PlanLimits
    features: dict
    tier_features: TierFeatures

    model_config = ConfigDict(from_attributes=True)


class PaymentProviderStatus(BaseModel):
    provider: str
    is_configured: bool
    publishable_key: Optional[str]


class InvoiceResponse(BaseModel):
    id: int
    provider_invoice_id: str
    amount_cents: int
    currency: str
    status: str
    invoice_url: Optional[str]
    invoice_pdf: Optional[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class CancelSubscriptionRequest(BaseModel):
    immediately: bool = False


class UpgradeRequest(BaseModel):
    plan_name: str
