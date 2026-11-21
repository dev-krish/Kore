from app.engine.tools.base import BaseTool, ToolResult
from app.services.browser.browser_service import browser_service

class FetchWebsiteTool(BaseTool):
    name = "fetch_website"
    description = "Fetches and extracts structured textual content, relevant links, and meta information from a company website URL."

    async def execute(self, website_url: str, **kwargs) -> ToolResult:
        try:
            if not website_url:
                return ToolResult(success=False, error="website_url is required")
            
            result = await browser_service.fetch_page(website_url)
            return ToolResult(
                success=True,
                data=result,
                source_attribution=website_url
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Website extraction failed: {str(e)}",
                source_attribution=website_url
            )
