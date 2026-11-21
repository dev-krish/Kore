from typing import List, Optional
from app.engine.tools.base import BaseTool, ToolResult
from app.services.discovery.search_provider import search_provider

class DiscoverContactsTool(BaseTool):
    name = "discover_contacts"
    description = "Discovers publicly listed professional contacts (Founders, CTOs, Engineering Managers, HR/Recruiters) for a target company."

    async def execute(
        self,
        company_name: str,
        company_website: str,
        target_roles: Optional[List[str]] = None,
        **kwargs
    ) -> ToolResult:
        try:
            roles = target_roles or ["Founder", "Co-Founder", "CTO", "Head of Engineering", "Engineering Manager"]
            contacts = await search_provider.search_company_contacts(
                company_name=company_name,
                company_website=company_website,
                target_roles=roles
            )
            return ToolResult(
                success=True,
                data=[c.model_dump() for c in contacts],
                source_attribution=f"Public domain leadership disclosures and official company channels for {company_name}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Contact discovery failed: {str(e)}"
            )
