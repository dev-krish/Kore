import logging
from typing import Dict, List, Optional
from app.engine.tools.base import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]

tool_registry = ToolRegistry()

def init_default_tools():
    from app.engine.tools.company_search import CompanySearchTool
    from app.engine.tools.fetch_website import FetchWebsiteTool
    from app.engine.tools.discover_contacts import DiscoverContactsTool
    from app.engine.tools.research_company import ResearchCompanyTool
    from app.engine.tools.evaluate_relevance import EvaluateRelevanceTool
    from app.engine.tools.generate_email import GenerateEmailTool
    from app.engine.tools.send_email import SendEmailTool

    tool_registry.register(CompanySearchTool())
    tool_registry.register(FetchWebsiteTool())
    tool_registry.register(DiscoverContactsTool())
    tool_registry.register(ResearchCompanyTool())
    tool_registry.register(EvaluateRelevanceTool())
    tool_registry.register(GenerateEmailTool())
    tool_registry.register(SendEmailTool())
