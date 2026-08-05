import uuid
import time
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from backend.db.dependencies import get_db
from backend.core.dependencies import get_current_user, verify_webhook_endpoint_ownership
from backend.models.user import User
from backend.models.webhook import WebhookEndpoint, WebhookDeliveryLog
from backend.schemas.webhook import (
    WebhookEndpointCreate,
    WebhookEndpointUpdate,
    WebhookEndpointResponse,
    WebhookDeliveryLogResponse,
)
from backend.events.event_bus import EventSchema

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post(
    "/endpoints",
    response_model=WebhookEndpointResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_webhook_endpoint(
    data: WebhookEndpointCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    endpoint = WebhookEndpoint(
        user_id=current_user.id,
        url=str(data.url),
        secret=data.secret,
        subscribed_events=data.subscribed_events,
        is_active=True,
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint


@router.get(
    "/endpoints",
    response_model=List[WebhookEndpointResponse],
)
def list_webhook_endpoints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(WebhookEndpoint)
        .filter(WebhookEndpoint.user_id == current_user.id)
        .all()
    )


@router.get(
    "/endpoints/{endpoint_id}",
    response_model=WebhookEndpointResponse,
)
def get_webhook_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return verify_webhook_endpoint_ownership(endpoint_id, current_user, db)


@router.put(
    "/endpoints/{endpoint_id}",
    response_model=WebhookEndpointResponse,
)
def update_webhook_endpoint(
    endpoint_id: int,
    data: WebhookEndpointUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    endpoint = verify_webhook_endpoint_ownership(endpoint_id, current_user, db)
    
    if data.url is not None:
        endpoint.url = str(data.url)
    if data.secret is not None:
        endpoint.secret = data.secret
    if data.subscribed_events is not None:
        endpoint.subscribed_events = data.subscribed_events
    if data.is_active is not None:
        endpoint.is_active = data.is_active

    db.commit()
    db.refresh(endpoint)
    return endpoint


@router.delete(
    "/endpoints/{endpoint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_webhook_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    endpoint = verify_webhook_endpoint_ownership(endpoint_id, current_user, db)
    db.delete(endpoint)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/endpoints/{endpoint_id}/deliveries",
    response_model=List[WebhookDeliveryLogResponse],
)
def list_webhook_deliveries(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_webhook_endpoint_ownership(endpoint_id, current_user, db)
    return (
        db.query(WebhookDeliveryLog)
        .filter(WebhookDeliveryLog.webhook_id == endpoint_id)
        .order_by(WebhookDeliveryLog.created_at.desc())
        .all()
    )


@router.post(
    "/endpoints/{endpoint_id}/test",
    status_code=status.HTTP_202_ACCEPTED,
)
def test_webhook_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    endpoint = verify_webhook_endpoint_ownership(endpoint_id, current_user, db)
    
    # Construct a real event payload to trigger the dispatcher
    test_event = EventSchema(
        event_type="test.ping",
        user_id=current_user.id,
        payload={
            "message": "This is a test event from Scriptloom webhooks management system.",
            "triggered_at": time.time(),
        },
    )
    
    # Import dispatcher locally to trigger event
    from backend.services.webhook_service import WebhookDispatcher
    dispatched = WebhookDispatcher.dispatch_event(db, test_event)
    
    if not dispatched:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Test event dispatch failed to queue.",
        )
        
    return {
        "message": "Test event queued successfully.",
        "delivery_id": dispatched[0],
        "event_id": test_event.event_id,
    }
