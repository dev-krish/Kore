from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import Field
from app.models.common import BaseDBModel

class DeliveryStatus(str, Enum):
    SUCCESS = "success"
    DEMO_DELIVERED = "demo_delivered"
    FAILED = "failed"

class EmailDeliveryModel(BaseDBModel):
    id: Optional[str] = Field(default=None, alias="_id")
    draftId: str
    campaignId: str
    userId: str
    recipient: str
    subject: str
    contentHash: str
    providerMessageId: Optional[str] = None
    status: DeliveryStatus
    error: Optional[str] = None
    sentAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
