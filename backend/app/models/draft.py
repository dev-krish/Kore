from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import Field
from app.models.common import BaseDBModel, PyObjectId

class ApprovalStatus(str, Enum):
    GENERATED = "generated"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"

class EmailDraftModel(BaseDBModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    userId: str
    campaignId: str
    contactId: str
    companyId: str
    recipientName: str
    recipientEmail: str
    recipientRole: str
    companyName: str
    subject: str
    body: str
    personalizationEvidence: List[str] = []
    researchReferences: List[str] = []
    warnings: List[str] = []
    approvalStatus: ApprovalStatus = ApprovalStatus.GENERATED
    approvedContentHash: Optional[str] = None  # SHA-256 of recipient + subject + body when approved
    approvedAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EmailDraftUpdate(BaseDBModel):
    subject: Optional[str] = None
    body: Optional[str] = None
