from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import Field
from app.models.common import BaseDBModel, PyObjectId

class DeliveryStatus(str, Enum):
    SUCCESS = "success"                  # Verified Live Gmail API delivery
    DEMO_DELIVERED = "demo_delivered"    # Simulated demo delivery (OAuth unconfigured)
    FAILED = "failed"                    # Delivery failed or error returned
    UNCERTAIN = "uncertain"              # Network timeout / unconfirmed delivery

class EmailDeliveryModel(BaseDBModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    draftId: str
    campaignId: str
    userId: str
    recipient: str
    subject: str
    contentHash: str
    providerMessageId: Optional[str] = None
    status: DeliveryStatus
    mode: str = "live_gmail"             # "live_gmail" | "demo_delivery"
    error: Optional[str] = None
    sentAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
