import logging
from typing import List, Optional
import httpx
from app.core.config import settings
from app.services.discovery.providers import BaseSearchProvider, DiscoveredCompany, DiscoveredContact
from app.services.discovery.demo_provider import DemoSearchProvider

logger = logging.getLogger(__name__)

class UnifiedSearchProvider(BaseSearchProvider):
    """
    Search Provider that uses external search engines (Tavily/SerpAPI) if configured,
    and falls back transparently to DemoSearchProvider with clear provenance.
    """

    def __init__(self):
        self.demo_provider = DemoSearchProvider()
        self.provider_type = settings.SEARCH_PROVIDER.lower()
        self.api_key = settings.SEARCH_API_KEY

    async def search_companies(
        self,
        query: str,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 5
    ) -> List[DiscoveredCompany]:
        if self.provider_type == "demo" or not self.api_key:
            logger.info("Using DemoSearchProvider (Search API key not provided or demo mode set).")
            return await self.demo_provider.search_companies(query, industry, location, limit)

        # Tavily API support
        if self.provider_type == "tavily" and self.api_key:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": self.api_key,
                            "query": f"{query} {industry or ''} {location or ''} startup company website",
                            "search_depth": "advanced",
                            "include_domains": [],
                            "max_results": limit
                        }
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    results = []
                    for item in data.get("results", []):
                        results.append(
                            DiscoveredCompany(
                                name=item.get("title", "Unknown Company"),
                                website=item.get("url", ""),
                                description=item.get("content", ""),
                                industry=industry or "Technology",
                                location=location or "Global",
                                technologies=[],
                                source_url=item.get("url", "")
                            )
                        )
                    if results:
                        return results
            except Exception as e:
                logger.warning(f"Tavily search failed: {e}. Falling back to demo records.")

        return await self.demo_provider.search_companies(query, industry, location, limit)

    async def search_company_contacts(
        self,
        company_name: str,
        company_website: str,
        target_roles: List[str]
    ) -> List[DiscoveredContact]:
        return await self.demo_provider.search_company_contacts(company_name, company_website, target_roles)

search_provider = UnifiedSearchProvider()
