from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class WebhookEndpointCreate(BaseModel):
    url: str = Field(..., max_length=500, description="Target URL of the webhook")
    secret: str = Field(..., max_length=255, description="Secret token used for HMAC signing")
    subscribed_events: List[str] = Field(default=["*"], description="List of event names this webhook subscribes to")

class WebhookEndpointUpdate(BaseModel):
    url: Optional[str] = Field(None, max_length=500)
    secret: Optional[str] = Field(None, max_length=255)
    subscribed_events: Optional[List[str]] = None
    is_active: Optional[bool] = None

class WebhookEndpointResponse(BaseModel):
    id: int
    user_id: int
    url: str
    is_active: bool
    subscribed_events: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class WebhookDeliveryLogResponse(BaseModel):
    delivery_id: str
    webhook_id: int
    event_type: str
    event_id: str
    status: str
    attempt_count: int
    request_url: str
    response_status: Optional[int] = None
    failure_reason: Optional[str] = None
    payload_json: str
    dispatch_timestamp: int
    created_at: datetime
    updated_at: datetime
    processing_started_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True
