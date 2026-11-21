from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import Field
from app.models.common import BaseDBModel

class CompanySource(BaseDBModel):
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    discoveredAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CompanyModel(BaseDBModel):
    id: Optional[str] = Field(default=None, alias="_id")
    campaignId: str
    name: str
    website: str
    description: str
    industry: str
    location: str
    technologies: List[str] = []
    sources: List[CompanySource] = []
    discoveryMetadata: Dict[str, Any] = {}
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
