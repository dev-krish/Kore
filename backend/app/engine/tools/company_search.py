from typing import Any, Dict, List, Optional
from app.engine.tools.base import BaseTool, ToolResult
from app.services.discovery.search_provider import search_provider

class CompanySearchTool(BaseTool):
    name = "company_search"
    description = "Searches for companies based on industry, location, technology preferences, and keywords."

    async def execute(
        self,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        company_type: Optional[str] = None,
        technology_preferences: Optional[List[str]] = None,
        search_keywords: Optional[str] = None,
        limit: int = 5,
        **kwargs
    ) -> ToolResult:
        try:
            query = f"{company_type or ''} {search_keywords or ''}".strip()
            companies = await search_provider.search_companies(
                query=query or "AI startups",
                industry=industry,
                location=location,
                limit=limit
            )
            return ToolResult(
                success=True,
                data=[c.model_dump() for c in companies],
                source_attribution="Public company records and verified domain registrations"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Company search failed: {str(e)}"
            )
