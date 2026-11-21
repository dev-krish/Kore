from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import Field
from app.models.common import BaseDBModel

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    PLANNING = "planning"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"

class CampaignCreate(BaseDBModel):
    name: str
    objective: str
    targetIndustry: Optional[str] = "AI & Software Startups"
    targetLocation: Optional[str] = "India & Global Remote"
    targetRoles: List[str] = ["Founder", "Co-Founder", "CTO", "Head of Engineering", "Engineering Manager"]
    targetProspectCount: int = 5
    preferredTechnologies: List[str] = ["Python", "TypeScript", "React", "PyTorch", "LLMs"]

class CampaignModel(BaseDBModel):
    id: Optional[str] = Field(default=None, alias="_id")
    userId: str
    name: str
    objective: str
    targetIndustry: str
    targetLocation: str
    targetRoles: List[str] = []
    targetProspectCount: int = 5
    preferredTechnologies: List[str] = []
    status: CampaignStatus = CampaignStatus.DRAFT
    companiesCount: int = 0
    contactsCount: int = 0
    draftsCount: int = 0
    emailsSentCount: int = 0
    lastExecutionId: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
