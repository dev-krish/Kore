from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import Field
from app.models.common import BaseDBModel

class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    PUBLICLY_DISCLOSED = "publicly_disclosed"
    DOMAIN_MATCHED = "domain_matched"
    DEMO_SAMPLE = "demo_sample"

class ContactModel(BaseDBModel):
    id: Optional[str] = Field(default=None, alias="_id")
    campaignId: str
    companyId: str
    companyName: str
    name: str
    role: str
    professionalEmail: Optional[str] = None
    profileUrl: Optional[str] = None
    sourceUrl: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    verificationStatus: VerificationStatus = VerificationStatus.UNVERIFIED
    relevanceScore: Optional[float] = None
    relevanceReasons: Optional[str] = None
    suggestedAngle: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
