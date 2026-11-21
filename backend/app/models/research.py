from datetime import datetime, timezone
from typing import List, Optional
from pydantic import Field
from app.models.common import BaseDBModel

class ResearchModel(BaseDBModel):
    id: Optional[str] = Field(default=None, alias="_id")
    campaignId: str
    companyId: str
    companyName: str
    researchSummary: str
    whatTheyBuild: str
    technologyStack: List[str] = []
    engineeringActivities: List[str] = []
    internshipRelevance: str
    sourceReferences: List[str] = []
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
