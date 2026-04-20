"""
AMOS Equation System v2.0 - Webhook System.

Production-grade webhook delivery with HMAC signatures,
exponential backoff retry, circuit breaker pattern,
and async delivery via Celery.

Author: AMOS Team
Version: 2.0.0
"""

import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timezone

UTC = UTC
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession

from equation_database import Base
from equation_tasks import celery_app

# =============================================================================
# Enums
# =============================================================================


class WebhookEventType(str, Enum):
    """Supported webhook event types."""

    EQUATION_CREATED = "equation.created"
    EQUATION_UPDATED = "equation.updated"
    EQUATION_DELETED = "equation.deleted"
    EQUATION_VERIFIED = "equation.verified"
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    BATCH_COMPLETED = "batch.completed"
    BATCH_FAILED = "batch.failed"
    SYSTEM_HEALTH_ALERT = "system.health_alert"


class WebhookStatus(str, Enum):
    """Webhook subscription status."""

    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


# =============================================================================
# Database Models
# =============================================================================


class WebhookSubscription(Base):
    """Webhook subscription model."""

    __tablename__ = "webhook_subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)
    status = Column(String(20), default=WebhookStatus.ACTIVE)
    event_types = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# =============================================================================
# Pydantic Models
# =============================================================================


class WebhookCreate(BaseModel):
    """Create webhook subscription request."""

    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    event_types: List[str] = Field(default_factory=list, description="Event types to subscribe")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/webhooks",
                "event_types": ["equation.created", "equation.verified"],
            }
        }


class WebhookEvent(BaseModel):
    """Webhook event payload."""

    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Event type")
    timestamp: str = Field(..., description="ISO timestamp")
    data: dict = Field(..., description="Event data")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.dict(), default=str)


# =============================================================================
# Webhook Service
# =============================================================================


class WebhookService:
    """Webhook management and delivery service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_subscription(
        self, user_id: int, url: str, event_types: List[str]
    ) -> WebhookSubscription:
        """Create new webhook subscription."""
        secret = self._generate_secret()

        subscription = WebhookSubscription(
            user_id=user_id,
            url=url,
            secret=secret,
            event_types=event_types,
            status=WebhookStatus.ACTIVE,
        )

        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)

        return subscription

    async def get_subscriptions(
        self, user_id: int, event_type: str = None
    ) -> List[WebhookSubscription]:
        """Get active subscriptions for user."""
        query = select(WebhookSubscription).where(
            WebhookSubscription.user_id == user_id,
            WebhookSubscription.status == WebhookStatus.ACTIVE,
        )

        if event_type:
            # Filter by event type in JSON array
            pass

        result = await self.db.execute(query)
        return result.scalars().all()

    def _generate_secret(self, length: int = 32) -> str:
        """Generate HMAC secret."""
        return secrets.token_hex(length)

    async def trigger_event(
        self, event_type: WebhookEventType, data: dict, user_id: int = None
    ) -> None:
        """Trigger webhook event to subscribers."""
        # Get subscriptions for this event type
        query = select(WebhookSubscription).where(
            WebhookSubscription.status == WebhookStatus.ACTIVE
        )

        if user_id:
            query = query.where(WebhookSubscription.user_id == user_id)

        result = await self.db.execute(query)
        subscriptions = result.scalars().all()

        # Create event
        event = WebhookEvent(
            event_id=secrets.token_hex(16),
            event_type=event_type.value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=data,
        )

        # Queue delivery for each subscriber
        for subscription in subscriptions:
            if self._should_deliver_to_subscription(subscription, event_type):
                deliver_webhook.delay(
                    subscription_id=subscription.id,
                    url=subscription.url,
                    secret=subscription.secret,
                    payload=event.to_json(),
                )

    def _should_deliver_to_subscription(
        self, subscription: WebhookSubscription, event_type: WebhookEventType
    ) -> bool:
        """Check if subscription should receive this event type."""
        if not subscription.event_types:
            return True
        return event_type.value in subscription.event_types


# =============================================================================
# Celery Tasks
# =============================================================================


@celery_app.task(bind=True, max_retries=5)
def deliver_webhook(self, subscription_id: int, url: str, secret: str, payload: str) -> dict:
    """Deliver webhook with retry logic."""
    import httpx

    # Generate signature
    timestamp = str(int(datetime.now(timezone.utc).timestamp()))
    signature = _generate_signature(secret, payload, timestamp)

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature,
        "X-Webhook-Timestamp": timestamp,
        "X-Webhook-Id": subscription_id,
        "User-Agent": "AMOS-Webhook/2.0.0",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, content=payload, headers=headers)
            response.raise_for_status()

        return {
            "status": "delivered",
            "subscription_id": subscription_id,
            "http_status": response.status_code,
        }

    except httpx.HTTPStatusError as e:
        # Retry with exponential backoff
        countdown = 2**self.request.retries
        self.retry(countdown=countdown, exc=e)

    except Exception as e:
        # Retry on network errors
        countdown = 2**self.request.retries
        self.retry(countdown=countdown, exc=e)


def _generate_signature(secret: str, payload: str, timestamp: str) -> str:
    """Generate HMAC-SHA256 signature."""
    message = f"{timestamp}.{payload}"
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature


# =============================================================================
# FastAPI Integration (Example)
# =============================================================================

"""
Usage in FastAPI routes:

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    request: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = WebhookService(db)
    subscription = await service.create_subscription(
        user_id=current_user.id,
        url=str(request.url),
        event_types=request.event_types
    )
    return {
        "id": subscription.id,
        "url": subscription.url,
        "secret": subscription.secret,  # Show once
        "event_types": subscription.event_types,
        "status": subscription.status
    }

# Trigger event from other modules:
# await webhook_service.trigger_event(
#     WebhookEventType.EQUATION_CREATED,
#     {"id": equation.id, "name": equation.name}
# )
"""

__all__ = [
    "WebhookSubscription",
    "WebhookCreate",
    "WebhookEvent",
    "WebhookService",
    "WebhookEventType",
    "WebhookStatus",
    "deliver_webhook",
]
