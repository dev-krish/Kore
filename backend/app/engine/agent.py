from datetime import datetime, timezone
import logging
from typing import Any, Dict, Optional
from bson import ObjectId
from app.core.database import get_database
from app.engine.planner import agent_planner
from app.engine.controller import AgentController
from app.models.campaign import CampaignStatus
from app.models.draft import ApprovalStatus
from app.models.execution import ExecutionStatus
from app.services.events import event_manager

logger = logging.getLogger(__name__)

class KoreAgentService:
    """
    Main orchestration service coordinating planning, execution, persistence,
    and live real-time event streaming.
    """

    async def run_campaign_agent(self, campaign_id: str, user_id: str) -> Dict[str, Any]:
        db = get_database()
        if db is None:
            raise RuntimeError("Database connection unavailable.")

        # 1. Fetch Campaign
        campaign = await db.campaigns.find_one({"_id": ObjectId(campaign_id), "userId": user_id})
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found.")

        # 2. Fetch User Profile
        profile = await db.profiles.find_one({"userId": user_id})
        if not profile:
            # Create a default student profile if not exists yet
            profile = {
                "userId": user_id,
                "fullName": "Student Candidate",
                "email": "candidate@example.com",
                "college": "University Institute of Technology",
                "degree": "B.Tech in Computer Science",
                "branch": "Computer Science & Engineering",
                "currentYear": "3rd Year",
                "skills": ["Python", "TypeScript", "FastAPI", "React", "Docker", "Machine Learning"],
                "programmingLanguages": ["Python", "TypeScript", "SQL"],
                "frameworks": ["FastAPI", "Next.js", "PyTorch"],
                "projects": [
                    {
                        "title": "Autonomous Agent Tool Orchestration Engine",
                        "description": "Multi-agent system with web scraping, LLM reasoning, and human approval verification.",
                        "technologies": ["Python", "FastAPI", "Playwright", "LLMs"]
                    }
                ],
                "preferences": {
                    "targetRoles": ["Software Engineering Intern", "AI/ML Intern"]
                }
            }
            await db.profiles.insert_one(profile)

        # 3. Create Execution Record
        execution_doc = {
            "campaignId": campaign_id,
            "userId": user_id,
            "currentStep": 0,
            "totalSteps": 5,
            "executionStatus": ExecutionStatus.RUNNING.value,
            "planTasks": [],
            "toolCalls": [],
            "steps": [],
            "errors": [],
            "startedAt": datetime.now(timezone.utc)
        }
        res_exec = await db.agentExecutions.insert_one(execution_doc)
        execution_id = str(res_exec.inserted_id)

        # Update Campaign status to RUNNING
        await db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$set": {"status": CampaignStatus.RUNNING.value, "lastExecutionId": execution_id, "updatedAt": datetime.now(timezone.utc)}}
        )

        # Callback to broadcast events to active SSE listeners & DB
        async def event_callback(event: Dict[str, Any]):
            await event_manager.broadcast(campaign_id, event)

        controller = AgentController(event_callback=event_callback)

        try:
            # 4. Generate Structured Plan
            plan = await agent_planner.create_plan(
                objective=campaign.get("objective", ""),
                profile=profile,
                preferences={
                    "targetIndustry": campaign.get("targetIndustry"),
                    "targetLocation": campaign.get("targetLocation"),
                    "targetRoles": campaign.get("targetRoles", []),
                    "targetProspectCount": campaign.get("targetProspectCount", 5)
                }
            )

            await db.agentExecutions.update_one(
                {"_id": ObjectId(execution_id)},
                {"$set": {"planTasks": plan.tasks, "currentStep": 1}}
            )

            # 5. Execute Plan via Controller
            result = await controller.execute_plan(
                campaign_id=campaign_id,
                user_id=user_id,
                plan=plan,
                student_profile=profile,
                campaign_config=campaign
            )

            # 6. Persist Discovered Companies
            saved_company_map = {}
            for comp in result.get("companies", []):
                comp_doc = {
                    "campaignId": campaign_id,
                    "name": comp.get("name"),
                    "website": comp.get("website"),
                    "description": comp.get("description"),
                    "industry": comp.get("industry"),
                    "location": comp.get("location"),
                    "technologies": comp.get("technologies", []),
                    "sources": [{"url": comp.get("source_url", comp.get("website")), "discoveredAt": datetime.now(timezone.utc)}],
                    "createdAt": datetime.now(timezone.utc)
                }
                c_res = await db.companies.insert_one(comp_doc)
                saved_company_map[comp.get("name")] = str(c_res.inserted_id)

            # 7. Persist Contacts
            saved_contact_map = {}
            for contact in result.get("contacts", []):
                comp_name = contact.get("company_name")
                comp_id = saved_company_map.get(comp_name, "")
                contact_doc = {
                    "campaignId": campaign_id,
                    "companyId": comp_id,
                    "companyName": comp_name,
                    "name": contact.get("name"),
                    "role": contact.get("role"),
                    "professionalEmail": contact.get("professional_email"),
                    "profileUrl": contact.get("profile_url"),
                    "sourceUrl": contact.get("source_url"),
                    "confidence": contact.get("confidence", 0.8),
                    "verificationStatus": contact.get("verification_status", "publicly_disclosed"),
                    "relevanceScore": contact.get("relevanceScore", 0.85),
                    "relevanceReasons": contact.get("relevanceReasons", ""),
                    "suggestedAngle": contact.get("suggestedAngle", ""),
                    "createdAt": datetime.now(timezone.utc)
                }
                ct_res = await db.contacts.insert_one(contact_doc)
                saved_contact_map[contact.get("name")] = str(ct_res.inserted_id)

            # 8. Persist Research Records
            for r_rec in result.get("research", []):
                comp_name = r_rec.get("companyName")
                comp_id = saved_company_map.get(comp_name, "")
                r_doc = {
                    "campaignId": campaign_id,
                    "companyId": comp_id,
                    "companyName": comp_name,
                    "researchSummary": r_rec.get("researchSummary", ""),
                    "whatTheyBuild": r_rec.get("whatTheyBuild", ""),
                    "technologyStack": r_rec.get("technologyStack", []),
                    "engineeringActivities": r_rec.get("engineeringActivities", []),
                    "internshipRelevance": r_rec.get("internshipRelevance", ""),
                    "sourceReferences": r_rec.get("sourceReferences", []),
                    "createdAt": datetime.now(timezone.utc)
                }
                await db.research.insert_one(r_doc)

            # 9. Persist Email Drafts (Status: GENERATED, Awaiting explicit Human Approval)
            draft_ids = []
            for d in result.get("drafts", []):
                comp_name = d.get("companyName")
                recip_name = d.get("recipientName")
                comp_id = saved_company_map.get(comp_name, "")
                ct_id = saved_contact_map.get(recip_name, "")

                draft_doc = {
                    "userId": user_id,
                    "campaignId": campaign_id,
                    "contactId": ct_id,
                    "companyId": comp_id,
                    "recipientName": recip_name,
                    "recipientEmail": d.get("recipientEmail", "contact@example.com"),
                    "recipientRole": d.get("recipientRole", ""),
                    "companyName": comp_name,
                    "subject": d.get("subject", ""),
                    "body": d.get("body", ""),
                    "personalizationEvidence": d.get("personalizationEvidence", []),
                    "researchReferences": d.get("researchReferences", []),
                    "warnings": d.get("warnings", []),
                    "approvalStatus": ApprovalStatus.GENERATED.value,
                    "approvedContentHash": None,
                    "createdAt": datetime.now(timezone.utc),
                    "updatedAt": datetime.now(timezone.utc)
                }
                dr_res = await db.emailDrafts.insert_one(draft_doc)
                draft_ids.append(str(dr_res.inserted_id))

            # 10. Update Agent Execution Document
            completed_status = ExecutionStatus.COMPLETED.value if result.get("status") == ExecutionStatus.COMPLETED else ExecutionStatus.FAILED.value
            await db.agentExecutions.update_one(
                {"_id": ObjectId(execution_id)},
                {
                    "$set": {
                        "executionStatus": completed_status,
                        "currentStep": len(result.get("steps", [])),
                        "totalSteps": len(result.get("steps", [])),
                        "steps": [s.model_dump() for s in result.get("steps", [])],
                        "toolCalls": [t.model_dump() for t in result.get("toolCalls", [])],
                        "errors": result.get("errors", []),
                        "completedAt": datetime.now(timezone.utc)
                    }
                }
            )

            # 11. Update Campaign Summary Counts
            await db.campaigns.update_one(
                {"_id": ObjectId(campaign_id)},
                {
                    "$set": {
                        "status": CampaignStatus.COMPLETED.value,
                        "companiesCount": len(result.get("companies", [])),
                        "contactsCount": len(result.get("contacts", [])),
                        "draftsCount": len(result.get("drafts", [])),
                        "updatedAt": datetime.now(timezone.utc)
                    }
                }
            )

            logger.info(f"Campaign {campaign_id} agent execution successfully finished.")
            return {
                "executionId": execution_id,
                "status": completed_status,
                "companiesCount": len(result.get("companies", [])),
                "contactsCount": len(result.get("contacts", [])),
                "draftsCount": len(result.get("drafts", []))
            }

        except Exception as e:
            logger.error(f"Error executing agent workflow for campaign {campaign_id}: {e}", exc_info=True)
            await db.campaigns.update_one(
                {"_id": ObjectId(campaign_id)},
                {"$set": {"status": CampaignStatus.FAILED.value, "updatedAt": datetime.now(timezone.utc)}}
            )
            await db.agentExecutions.update_one(
                {"_id": ObjectId(execution_id)},
                {
                    "$set": {
                        "executionStatus": ExecutionStatus.FAILED.value,
                        "errors": [str(e)],
                        "completedAt": datetime.now(timezone.utc)
                    }
                }
            )
            raise e

kore_agent_service = KoreAgentService()
