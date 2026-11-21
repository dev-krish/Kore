import json
import logging
from typing import Any, Dict, List
from pydantic import BaseModel
from app.engine.llm.base import LLMMessage
from app.engine.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

class PlanOutput(BaseModel):
    tasks: List[str]
    targetIndustry: str
    targetRoles: List[str]
    reasoning: str

class AgentPlanner:
    """
    Parses a student's natural-language campaign objective and profile
    into a structured, multi-step execution plan.
    """

    async def create_plan(self, objective: str, profile: Dict[str, Any], preferences: Dict[str, Any]) -> PlanOutput:
        logger.info(f"Creating execution plan for objective: {objective}")
        llm = get_llm_provider()

        prompt = (
            f"You are the Lead Planning Agent for KORE, an autonomous professional outreach platform for university students.\n"
            f"Convert the user's objective and profile into a concise, ordered list of execution tasks.\n\n"
            f"User Objective:\n{objective}\n\n"
            f"User Profile Summary:\n"
            f"- Name: {profile.get('fullName')}\n"
            f"- College: {profile.get('college')}\n"
            f"- Degree: {profile.get('degree')} ({profile.get('currentYear')})\n"
            f"- Skills: {', '.join(profile.get('skills', []))}\n\n"
            f"Preferences:\n{json.dumps(preferences)}\n\n"
            "Return a JSON object conforming to:\n"
            "{\n"
            '  "tasks": ["Task 1", "Task 2", ...],\n'
            '  "targetIndustry": "string",\n'
            '  "targetRoles": ["role1", "role2"],\n'
            '  "reasoning": "brief explanation"\n'
            "}"
        )

        try:
            response = await llm.chat_complete(
                messages=[LLMMessage(role="user", content=prompt)],
                format_json=True
            )
            data = json.loads(response)
            return PlanOutput(**data)
        except Exception as e:
            logger.warning(f"LLM planning failed or returned invalid JSON ({e}). Falling back to robust default plan.")
            return PlanOutput(
                tasks=[
                    "Analyze objective and filter company candidates in target industry",
                    "Conduct automated website and tech-stack research",
                    "Discover verified technical leadership and recruitment contacts",
                    "Evaluate profile fit and calculate relevance scores",
                    "Synthesize research into personalized, human-reviewed email drafts"
                ],
                targetIndustry=preferences.get("targetIndustry", "AI & Software Startups"),
                targetRoles=preferences.get("targetRoles", ["Founders", "Engineering Managers"]),
                reasoning="Default high-precision execution plan covering discovery, research, and personalization."
            )

agent_planner = AgentPlanner()
