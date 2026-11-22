from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import Field, field_validator
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
    isDemoRecord: bool = False
    provenance: str = "live_search"
    deliveryError: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("recipientEmail")
    @classmethod
    def validate_recipient_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not clean or "@" not in clean or "." not in clean.split("@")[-1]:
            raise ValueError(f"Invalid recipient email format: '{v}'")
        return clean

class EmailDraftUpdate(BaseDBModel):
    subject: Optional[str] = None
    body: Optional[str] = None
