from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
import ipaddress
from urllib.parse import urlparse
import socket


def _validate_webhook_url(url: str) -> str:
    """Validate webhook URL: must be http/https, no private/loopback IPs."""
    parsed = urlparse(url)

    # Scheme check
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"URL scheme must be http or https, got '{parsed.scheme}'")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must have a valid hostname")

    # Resolve hostname to IP and check for private/loopback/link-local
    try:
        resolved = socket.getaddrinfo(hostname, None)
        if resolved:
            ip_str = resolved[0][4][0]
            ip = ipaddress.ip_address(ip_str)
            if ip.is_loopback:
                raise ValueError(f"URL hostname '{hostname}' resolves to a loopback address ({ip})")
            if ip.is_private:
                raise ValueError(f"URL hostname '{hostname}' resolves to a private address ({ip})")
            if ip.is_link_local:
                raise ValueError(f"URL hostname '{hostname}' resolves to a link-local address ({ip})")
    except (socket.gaierror, IndexError):
        # DNS resolution failed — reject (can't verify safety)
        raise ValueError(f"Cannot resolve hostname '{hostname}'")
    except ValueError:
        raise  # re-raise our own ValidationErrors

    return url


class WebhookEndpointCreate(BaseModel):
    url: str = Field(..., max_length=500, description="Target URL of the webhook")
    secret: str = Field(..., min_length=16, max_length=255, description="Secret token used for HMAC signing")
    subscribed_events: List[str] = Field(default=["*"], description="List of event names this webhook subscribes to")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return _validate_webhook_url(v)

class WebhookEndpointUpdate(BaseModel):
    url: Optional[str] = Field(None, max_length=500)
    secret: Optional[str] = Field(None, max_length=255)
    subscribed_events: Optional[List[str]] = None
    is_active: Optional[bool] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return _validate_webhook_url(v)
        return v

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
