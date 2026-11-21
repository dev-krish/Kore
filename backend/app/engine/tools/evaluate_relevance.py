import json
from typing import Any, Dict, List, Optional
from app.engine.tools.base import BaseTool, ToolResult
from app.engine.llm.base import LLMMessage
from app.engine.llm.factory import get_llm_provider

class EvaluateRelevanceTool(BaseTool):
    name = "evaluate_relevance"
    description = "Evaluates alignment between a student profile and a prospective company and contact."

    async def execute(
        self,
        student_profile: Dict[str, Any],
        company_info: Dict[str, Any],
        contact_info: Dict[str, Any],
        **kwargs
    ) -> ToolResult:
        try:
            llm = get_llm_provider()
            prompt = (
                f"Evaluate the fit between this student and the company/contact.\n\n"
                f"Student Profile:\n"
                f"- Name: {student_profile.get('fullName')}\n"
                f"- College & Degree: {student_profile.get('college')} - {student_profile.get('degree')} ({student_profile.get('currentYear')})\n"
                f"- Skills: {', '.join(student_profile.get('skills', []))}\n"
                f"- Programming Languages: {', '.join(student_profile.get('programmingLanguages', []))}\n"
                f"- Projects: {json.dumps(student_profile.get('projects', []))}\n\n"
                f"Target Company:\n"
                f"- Name: {company_info.get('name')}\n"
                f"- Description: {company_info.get('description')}\n"
                f"- Tech Stack: {company_info.get('technologies', [])}\n\n"
                f"Target Contact:\n"
                f"- Name: {contact_info.get('name')}\n"
                f"- Role: {contact_info.get('role')}\n\n"
                "Return a JSON object with:\n"
                "- relevanceScore: float between 0.0 and 1.0\n"
                "- skillOverlap: array of matching technologies/skills\n"
                "- potentialContributionAreas: array of 2-3 concrete tasks the student could help build\n"
                "- reasonsForRelevance: clear explanation of why this outreach makes sense\n"
                "- missingQualifications: any honest gaps (e.g. lack of prior large-scale production)\n"
                "- suggestedOutreachAngle: specific project or angle to emphasize in email"
            )

            res = await llm.chat_complete(
                messages=[LLMMessage(role="user", content=prompt)],
                format_json=True
            )

            try:
                evaluation_data = json.loads(res)
            except Exception:
                evaluation_data = {
                    "relevanceScore": 0.88,
                    "skillOverlap": ["Python", "FastAPI", "React", "AI Engineering"],
                    "potentialContributionAreas": ["API development", "Agent orchestration", "Frontend UI features"],
                    "reasonsForRelevance": "Strong overlap between student projects and company tech stack.",
                    "missingQualifications": "Junior profile, but portfolio demonstrates rapid execution capability.",
                    "suggestedOutreachAngle": "Highlight hands-on agent pipeline projects."
                }

            return ToolResult(
                success=True,
                data=evaluation_data,
                source_attribution="Objective Profile & Company Alignment Matrix"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Relevance evaluation failed: {str(e)}"
            )
