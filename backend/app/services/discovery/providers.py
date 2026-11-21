from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class DiscoveredCompany(BaseModel):
    name: str
    website: str
    description: str
    industry: str
    location: str
    technologies: List[str] = []
    source_url: str
    is_demo_record: bool = False
    provenance: str = "live_search"

class DiscoveredContact(BaseModel):
    name: str
    role: str
    company_name: str
    professional_email: Optional[str] = None
    profile_url: Optional[str] = None
    source_url: str
    confidence: float = 0.8
    verification_status: str = "unverified"
    is_demo_record: bool = False
    provenance: str = "live_search"

class BaseSearchProvider(ABC):
    @abstractmethod
    async def search_companies(
        self,
        query: str,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 5
    ) -> List[DiscoveredCompany]:
        pass

    @abstractmethod
    async def search_company_contacts(
        self,
        company_name: str,
        company_website: str,
        target_roles: List[str]
    ) -> List[DiscoveredContact]:
        pass
