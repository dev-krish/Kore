import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.core.database import get_database
from app.api.deps import get_current_user_id
from app.models.campaign import CampaignCreate, CampaignModel, CampaignStatus
from app.engine.agent import kore_agent_service

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.post("")
async def create_campaign(campaign_in: CampaignCreate, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    camp_doc = {
        "userId": user_id,
        "name": campaign_in.name,
        "objective": campaign_in.objective,
        "targetIndustry": campaign_in.targetIndustry or "AI & Software Startups",
        "targetLocation": campaign_in.targetLocation or "India & Global Remote",
        "targetRoles": campaign_in.targetRoles,
        "targetProspectCount": campaign_in.targetProspectCount,
        "preferredTechnologies": campaign_in.preferredTechnologies,
        "status": CampaignStatus.DRAFT.value,
        "companiesCount": 0,
        "contactsCount": 0,
        "draftsCount": 0,
        "emailsSentCount": 0,
        "lastExecutionId": None,
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc)
    }
    res = await db.campaigns.insert_one(camp_doc)
    camp_doc["_id"] = str(res.inserted_id)
    return camp_doc

@router.get("")
async def list_campaigns(user_id: str = Depends(get_current_user_id)):
    db = get_database()
    cursor = db.campaigns.find({"userId": user_id}).sort("createdAt", -1)
    campaigns = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        campaigns.append(doc)
    return campaigns

@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    doc = await db.campaigns.find_one({"_id": ObjectId(campaign_id), "userId": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Campaign not found")
    doc["_id"] = str(doc["_id"])
    return doc

@router.post("/{campaign_id}/execute")
async def execute_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id)
):
    db = get_database()
    doc = await db.campaigns.find_one({"_id": ObjectId(campaign_id), "userId": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Launch agent workflow in background task so UI gets instant acknowledgment
    background_tasks.add_task(kore_agent_service.run_campaign_agent, campaign_id, user_id)

    return {
        "status": "executing",
        "campaignId": campaign_id,
        "message": "Autonomous agent execution initiated. Stream live events via /api/executions/{campaign_id}/events"
    }

@router.get("/{campaign_id}/prospects")
async def get_campaign_prospects(campaign_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    # Verify ownership
    camp = await db.campaigns.find_one({"_id": ObjectId(campaign_id), "userId": user_id})
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")

    companies_cursor = db.companies.find({"campaignId": campaign_id})
    companies = []
    async for c in companies_cursor:
        c["_id"] = str(c["_id"])
        companies.append(c)

    contacts_cursor = db.contacts.find({"campaignId": campaign_id})
    contacts = []
    async for ct in contacts_cursor:
        ct["_id"] = str(ct["_id"])
        contacts.append(ct)

    research_cursor = db.research.find({"campaignId": campaign_id})
    research = []
    async for r in research_cursor:
        r["_id"] = str(r["_id"])
        research.append(r)

    return {
        "campaignId": campaign_id,
        "companies": companies,
        "contacts": contacts,
        "research": research
    }
