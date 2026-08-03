from pydantic import BaseModel, ConfigDict


class SubscriptionResponse(BaseModel):
    user_id: int
    plan_name: str
    plan_display_name: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class UsageResponse(BaseModel):
    user_id: int
    plan_name: str
    plan_display_name: str
    status: str
    hours_processed: float
    hours_limit: float
    hours_remaining: float
    campaign_packs_generated: int
    campaign_packs_limit: int
    period_month: str

    model_config = ConfigDict(from_attributes=True)


class UpgradeRequest(BaseModel):
    plan_name: str
