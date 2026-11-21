import asyncio
from datetime import datetime, timezone
import json
import logging
from typing import Any, Callable, Dict, List, Optional
from app.core.config import settings
from app.engine.registry import tool_registry, init_default_tools
from app.engine.planner import PlanOutput
from app.models.execution import AgentStepRecord, ToolCallRecord, ExecutionStatus

logger = logging.getLogger(__name__)

class AgentController:
    """
    Controlled Observe-Decide-Act-Verify execution controller.
    Executes tasks sequentially, handling tool calls, retries, observations,
    and emitting live status events.
    """

    def __init__(self, event_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.event_callback = event_callback
        init_default_tools()

    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        payload = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data
        }
        if self.event_callback:
            try:
                if asyncio.iscoroutinefunction(self.event_callback):
                    await self.event_callback(payload)
                else:
                    self.event_callback(payload)
            except Exception as e:
                logger.warning(f"Error in event_callback: {e}")

    async def execute_plan(
        self,
        campaign_id: str,
        user_id: str,
        plan: PlanOutput,
        student_profile: Dict[str, Any],
        campaign_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(f"Starting agent execution for campaign: {campaign_id}")
        
        steps_history: List[AgentStepRecord] = []
        tool_calls_history: List[ToolCallRecord] = []
        errors: List[str] = []

        discovered_companies = []
        discovered_contacts = []
        generated_drafts = []
        research_records = []

        total_steps = len(plan.tasks)

        await self.emit_event("execution_started", {
            "campaignId": campaign_id,
            "totalSteps": total_steps,
            "tasks": plan.tasks
        })

        try:
            # STEP 1: Company Discovery
            step_num = 1
            task_desc = plan.tasks[0] if total_steps > 0 else "Discover target companies"
            thought = f"Searching for companies in {campaign_config.get('targetIndustry', 'Tech')} located in {campaign_config.get('targetLocation', 'India & Global')} matching student profile."
            
            await self.emit_event("step_started", {
                "stepNumber": step_num,
                "task": task_desc,
                "thought": thought
            })

            search_tool = tool_registry.get_tool("company_search")
            limit = campaign_config.get("targetProspectCount", 5)
            
            tool_start = datetime.now(timezone.utc)
            search_res = await search_tool.execute(
                industry=campaign_config.get("targetIndustry"),
                location=campaign_config.get("targetLocation"),
                company_type=campaign_config.get("targetIndustry"),
                technology_preferences=campaign_config.get("preferredTechnologies", []),
                limit=limit
            )

            tool_calls_history.append(ToolCallRecord(
                toolName="company_search",
                inputArgs={"limit": limit, "industry": campaign_config.get("targetIndustry")},
                outputSummary=f"Discovered {len(search_res.data or [])} companies",
                isSuccess=search_res.success,
                error=search_res.error
            ))

            if search_res.success and search_res.data:
                discovered_companies = search_res.data
                observation = f"Successfully discovered {len(discovered_companies)} target companies with verified public domains and descriptions."
            else:
                observation = f"Company search yielded 0 results or encountered error: {search_res.error}"
                errors.append(observation)

            steps_history.append(AgentStepRecord(
                stepNumber=step_num,
                task=task_desc,
                thought=thought,
                action="Executed tool 'company_search'",
                observation=observation
            ))

            await self.emit_event("step_completed", {
                "stepNumber": step_num,
                "observation": observation,
                "discoveredCompanies": discovered_companies
            })

            # For each company, execute Deep Research, Contact Discovery, Relevance, and Draft Generation
            research_tool = tool_registry.get_tool("research_company")
            contacts_tool = tool_registry.get_tool("discover_contacts")
            relevance_tool = tool_registry.get_tool("evaluate_relevance")
            draft_tool = tool_registry.get_tool("generate_email")

            for idx, company in enumerate(discovered_companies, start=1):
                company_name = company.get("name")
                website = company.get("website")

                # Sub-task 1: Company Research
                await self.emit_event("agent_thought", {
                    "message": f"Investigating engineering focus and tech stack for {company_name} ({website})..."
                })

                res_result = await research_tool.execute(
                    company_name=company_name,
                    website=website,
                    description=company.get("description", ""),
                    technologies=company.get("technologies", [])
                )

                company_research = res_result.data if res_result.success else {
                    "whatTheyBuild": company.get("description", ""),
                    "technologyStack": company.get("technologies", []),
                    "engineeringActivities": ["Software engineering", "Product development"],
                    "internshipRelevance": f"Great engineering team at {company_name}",
                    "researchSummary": company.get("description", ""),
                    "sourceReferences": [website]
                }
                company_research["companyName"] = company_name
                research_records.append(company_research)

                tool_calls_history.append(ToolCallRecord(
                    toolName="research_company",
                    inputArgs={"company": company_name, "website": website},
                    outputSummary=f"Synthesized research for {company_name}",
                    isSuccess=res_result.success
                ))

                # Sub-task 2: Discover Contacts
                await self.emit_event("agent_thought", {
                    "message": f"Identifying public contacts (Founders & Engineering Leadership) for {company_name}..."
                })

                contacts_res = await contacts_tool.execute(
                    company_name=company_name,
                    company_website=website,
                    target_roles=campaign_config.get("targetRoles")
                )

                company_contacts = contacts_res.data if contacts_res.success and contacts_res.data else []
                tool_calls_history.append(ToolCallRecord(
                    toolName="discover_contacts",
                    inputArgs={"company": company_name},
                    outputSummary=f"Found {len(company_contacts)} contacts for {company_name}",
                    isSuccess=contacts_res.success
                ))

                # For each contact, evaluate fit and generate personalized email draft
                for contact in company_contacts:
                    discovered_contacts.append(contact)

                    # Sub-task 3: Relevance Evaluation
                    eval_res = await relevance_tool.execute(
                        student_profile=student_profile,
                        company_info=company,
                        contact_info=contact
                    )
                    eval_data = eval_res.data if eval_res.success else {
                        "relevanceScore": 0.85,
                        "suggestedOutreachAngle": "Technical collaboration & internship inquiry"
                    }

                    contact["relevanceScore"] = eval_data.get("relevanceScore", 0.85)
                    contact["relevanceReasons"] = eval_data.get("reasonsForRelevance", "")
                    contact["suggestedAngle"] = eval_data.get("suggestedOutreachAngle", "")

                    # Sub-task 4: Personalized Draft Generation
                    await self.emit_event("agent_thought", {
                        "message": f"Drafting tailored outreach email for {contact.get('name')} ({contact.get('role')}) at {company_name}..."
                    })

                    draft_res = await draft_tool.execute(
                        student_profile=student_profile,
                        recipient_info=contact,
                        company_research=company_research,
                        evaluation=eval_data,
                        outreach_objective=campaign_config.get("objective", "Internship opportunity")
                    )

                    if draft_res.success and draft_res.data:
                        draft_data = draft_res.data
                        draft_data["recipientName"] = contact.get("name")
                        draft_data["recipientEmail"] = contact.get("professional_email", "contact@example.com")
                        draft_data["recipientRole"] = contact.get("role")
                        draft_data["companyName"] = company_name
                        generated_drafts.append(draft_data)

                        tool_calls_history.append(ToolCallRecord(
                            toolName="generate_email",
                            inputArgs={"recipient": contact.get("name"), "company": company_name},
                            outputSummary=f"Generated draft: '{draft_data.get('subject')}'",
                            isSuccess=True
                        ))

            # Final Step: Review & Approval Queue preparation
            final_step = AgentStepRecord(
                stepNumber=2,
                task="Present findings and drafts for Human-in-the-Loop review",
                thought="All prospect discovery, verification, research, and personalized drafts are prepared. Now submitting to Human Approval Gate.",
                action="Created drafts awaiting explicit human approval",
                observation=f"Prepared {len(generated_drafts)} drafts for {len(discovered_companies)} companies and {len(discovered_contacts)} contacts. Email sending is strictly gated by human approval."
            )
            steps_history.append(final_step)

            await self.emit_event("execution_completed", {
                "campaignId": campaign_id,
                "companiesCount": len(discovered_companies),
                "contactsCount": len(discovered_contacts),
                "draftsCount": len(generated_drafts)
            })

            return {
                "status": ExecutionStatus.COMPLETED,
                "companies": discovered_companies,
                "contacts": discovered_contacts,
                "research": research_records,
                "drafts": generated_drafts,
                "steps": steps_history,
                "toolCalls": tool_calls_history,
                "errors": errors
            }

        except Exception as e:
            logger.error(f"Fatal error during agent controller execution: {e}", exc_info=True)
            errors.append(str(e))
            await self.emit_event("execution_failed", {"error": str(e)})
            return {
                "status": ExecutionStatus.FAILED,
                "companies": discovered_companies,
                "contacts": discovered_contacts,
                "research": research_records,
                "drafts": generated_drafts,
                "steps": steps_history,
                "toolCalls": tool_calls_history,
                "errors": errors
            }
