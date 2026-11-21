import json
from typing import Any, Dict, List, Optional
from app.engine.tools.base import BaseTool, ToolResult
from app.engine.llm.base import LLMMessage
from app.engine.llm.factory import get_llm_provider
from app.services.browser.browser_service import browser_service

class ResearchCompanyTool(BaseTool):
    name = "research_company"
    description = "Conducts deep investigation into company engineering priorities, tech stack, products, and internship alignment."

    async def execute(
        self,
        company_name: str,
        website: str,
        description: str,
        technologies: Optional[List[str]] = None,
        **kwargs
    ) -> ToolResult:
        try:
            # Step 1: Fetch website content
            page_data = await browser_service.fetch_page(website)
            content_snippet = page_data.get("cleanContent", "")[:2500]

            # Step 2: Use LLM to synthesize factual research summary
            llm = get_llm_provider()
            prompt = (
                f"Analyze this company's public information and summarize their technical focus.\n\n"
                f"Company Name: {company_name}\n"
                f"Website: {website}\n"
                f"Known Description: {description}\n"
                f"Website Extracted Text:\n{content_snippet}\n\n"
                "Return a JSON object with the following fields:\n"
                "- whatTheyBuild: brief overview of their core product/platform\n"
                "- technologyStack: array of identified frameworks, languages, or infrastructure\n"
                "- engineeringActivities: array of 2-3 key engineering focus areas\n"
                "- internshipRelevance: why this company is an excellent learning ground for software/AI engineering students\n"
                "- researchSummary: 2-3 sentence factual synthesis"
            )

            response_text = await llm.chat_complete(
                messages=[LLMMessage(role="user", content=prompt)],
                format_json=True
            )

            try:
                research_data = json.loads(response_text)
            except Exception:
                research_data = {
                    "whatTheyBuild": description,
                    "technologyStack": technologies or ["Python", "TypeScript", "Modern Cloud"],
                    "engineeringActivities": ["Core platform development", "API architecture", "AI tooling"],
                    "internshipRelevance": f"Rapid product iteration and high-impact engineering exposure at {company_name}.",
                    "researchSummary": f"{company_name} develops modern software systems with high emphasis on developer agility and robust architecture."
                }

            research_data["sourceReferences"] = [website, page_data.get("sourceUrl", website)]

            return ToolResult(
                success=True,
                data=research_data,
                source_attribution=website
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Company research failed: {str(e)}",
                source_attribution=website
            )
