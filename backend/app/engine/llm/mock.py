import json
import logging
from typing import Any, Dict, List, Optional
from app.engine.llm.base import BaseLLMProvider, LLMMessage

logger = logging.getLogger(__name__)

class MockLLMProvider(BaseLLMProvider):
    """Deterministic, high-quality fallback LLM provider for zero-failure local testing."""

    async def is_available(self) -> bool:
        return True

    async def chat_complete(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.2,
        format_json: bool = False,
        system_prompt: Optional[str] = None
    ) -> str:
        last_message = messages[-1].content.lower() if messages else ""

        # 1. Email / Draft generation request
        if "generate an individualized" in last_message or "subject line" in last_message or "email body" in last_message:
            if format_json:
                return json.dumps({
                    "subject": "Inquiring about Engineering / AI Internship Opportunities at Sarvam AI",
                    "body": (
                        "Dear Pratyush,\n\n"
                        "I have been closely following Sarvam AI's work in foundational AI models and language infrastructure tailored for enterprise workflows. "
                        "As a computer science student with hands-on experience developing agent orchestration pipelines and full-stack systems, "
                        "I was particularly impressed by your engineering focus on real-world tooling.\n\n"
                        "Recently, I built multi-agent applications using Python, FastAPI, and Next.js that execute automated tool workflows. "
                        "I would love the opportunity to contribute to your engineering team as an intern for Summer 2025/2026.\n\n"
                        "Could we schedule a brief 10-minute conversation next week to discuss if my background aligns with any upcoming needs on your team?\n\n"
                        "Best regards,\nAlex Vance"
                    ),
                    "personalizationEvidence": [
                        "Referenced recipient's specific role and company domain",
                        "Aligned student's agent systems experience with company tech stack",
                        "Maintained concise, respectful, non-presumptive tone"
                    ],
                    "researchReferences": ["Company public engineering blog and mission overview"],
                    "warnings": []
                })

        # 2. Relevance evaluation request
        if "relevance" in last_message or "fit between this student" in last_message:
            if format_json:
                return json.dumps({
                    "relevanceScore": 0.92,
                    "skillOverlap": ["Python", "FastAPI", "Full-Stack Development", "LLMs"],
                    "potentialContributionAreas": ["API development", "Model orchestration workflows", "Agent pipeline optimization"],
                    "reasonsForRelevance": "The student has strong foundational software skills and hands-on project experience with agent architectures matching the company's stack.",
                    "missingQualifications": "Prior production experience at scale is limited, but strong project portfolio compensates.",
                    "suggestedOutreachAngle": "Highlight projects demonstrating autonomous agent systems and full-stack API capabilities."
                })

        # 3. Company research request
        if "whattheybuild" in last_message or "engineeringactivities" in last_message or "technical focus" in last_message:
            if format_json:
                return json.dumps({
                    "whatTheyBuild": "Foundational AI models, voice-first LLMs, and language infrastructure tailored for Indian languages.",
                    "technologyStack": ["PyTorch", "Transformers", "CUDA", "FastAPI", "Python", "Kubernetes"],
                    "engineeringActivities": ["Core platform development", "Large-scale distributed training", "API latency optimization"],
                    "internshipRelevance": "High exposure to foundational model engineering and enterprise AI systems at scale.",
                    "researchSummary": "Sarvam AI is developing sovereign AI foundation models and high-throughput enterprise APIs in Bengaluru."
                })

        # 4. Plan generation request
        if "lead planning agent" in last_message or "plan" in last_message:
            if format_json:
                return json.dumps({
                    "tasks": [
                        "Parse outreach objective and target preferences",
                        "Discover candidate companies matching criteria in target region",
                        "Extract and research company technical domain and engineering activities",
                        "Identify verified founders and technical leadership contacts",
                        "Evaluate student profile relevance against company engineering priorities",
                        "Generate highly personalized, human-approved internship outreach drafts"
                    ],
                    "targetIndustry": "AI & Software Startups",
                    "targetRoles": ["Founders", "Engineering Managers"],
                    "reasoning": "A structured step-by-step strategy ensures high-precision contact matching and personalized drafting."
                })

        if format_json:
            return json.dumps({"status": "success", "message": "Standard agent evaluation complete."})
        return "Standard agent reasoning completed successfully."
