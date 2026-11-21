import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.draft import ApprovalStatus

@pytest.mark.asyncio
async def test_full_user_journey_end_to_end():
    """
    Validates the complete 15-step user journey described in Section 2 and Section 16 (Definition of Done):
    1. Student checks/creates career profile.
    2. Student creates outreach campaign with natural-language objective.
    3. Campaign agent executes discovery, website research, contact sourcing, relevance scoring, and draft generation.
    4. Prospects (companies, contacts, research) are inspected.
    5. Drafts are retrieved.
    6. Tampering/unapproved sending is rejected by the Approval Gate.
    7. Draft is edited and saved (approval reset).
    8. Student explicitly approves draft (cryptographic SHA-256 hash generated).
    9. Gmail delivery sends approved draft and logs delivery with provider message ID.
    10. Duplicate send protection prevents re-sending.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Profile
        prof_res = await client.get("/api/profiles/me")
        assert prof_res.status_code == 200
        profile = prof_res.json()
        assert profile["fullName"] is not None

        # Step 2: Campaign Creation
        camp_payload = {
            "name": "India AI Startups - Summer 2025 Internship",
            "objective": "Find 2 early-stage AI startups in India for a computer science student interested in AI engineering and full-stack development.",
            "targetIndustry": "AI Startups",
            "targetLocation": "India",
            "targetRoles": ["Founders", "Engineering Managers"],
            "targetProspectCount": 2,
            "preferredTechnologies": ["Python", "FastAPI", "React", "LLMs"]
        }
        camp_res = await client.post("/api/campaigns", json=camp_payload)
        assert camp_res.status_code == 200
        campaign = camp_res.json()
        campaign_id = campaign["_id"]
        assert campaign_id is not None

        # Step 3: Directly run agent workflow for this campaign
        from app.engine.agent import kore_agent_service
        agent_result = await kore_agent_service.run_campaign_agent(
            campaign_id=campaign_id,
            user_id="665000000000000000000001"
        )
        assert agent_result["status"] == "completed"
        assert agent_result["companiesCount"] > 0
        assert agent_result["contactsCount"] > 0
        assert agent_result["draftsCount"] > 0

        # Step 4: Verify prospects endpoint
        prospects_res = await client.get(f"/api/campaigns/{campaign_id}/prospects")
        assert prospects_res.status_code == 200
        prospects_data = prospects_res.json()
        assert len(prospects_data["companies"]) > 0
        assert len(prospects_data["contacts"]) > 0
        assert len(prospects_data["research"]) > 0

        first_company = prospects_data["companies"][0]
        assert "name" in first_company
        assert "website" in first_company

        first_contact = prospects_data["contacts"][0]
        assert "name" in first_contact
        assert "sourceUrl" in first_contact
        assert first_contact["confidence"] > 0.5

        # Step 5: Verify Drafts generated in approval queue
        drafts_res = await client.get(f"/api/drafts?campaignId={campaign_id}")
        assert drafts_res.status_code == 200
        drafts = drafts_res.json()
        assert len(drafts) > 0
        draft = drafts[0]
        draft_id = draft["_id"]
        assert draft["approvalStatus"] == ApprovalStatus.GENERATED.value

        # Step 6: Security Gate Check - Attempting to send unapproved draft MUST FAIL (HTTP 403)
        send_unapproved = await client.post(f"/api/drafts/{draft_id}/send")
        assert send_unapproved.status_code == 403
        assert "Approval Gate" in send_unapproved.json()["detail"]

        # Step 7: Edit draft
        edit_res = await client.put(f"/api/drafts/{draft_id}", json={
            "subject": "Tailored Inquiry: AI Engineering Internship at " + draft["companyName"],
            "body": "Dear " + draft["recipientName"] + ",\n\nI would love to contribute to your engineering team as an intern."
        })
        assert edit_res.status_code == 200
        edited_draft = edit_res.json()
        assert edited_draft["approvalStatus"] == ApprovalStatus.PENDING_REVIEW.value
        assert edited_draft["approvedContentHash"] is None

        # Step 8: Explicit Human Approval
        approve_res = await client.post(f"/api/drafts/{draft_id}/approve")
        assert approve_res.status_code == 200
        approve_data = approve_res.json()
        assert approve_data["status"] == "approved"
        assert approve_data["approvedContentHash"] is not None

        # Step 9: Secure Dispatch through Gmail Service
        send_res = await client.post(f"/api/drafts/{draft_id}/send")
        assert send_res.status_code == 200
        send_data = send_res.json()
        assert send_data["status"] == "sent"
        assert send_data["deliveryResult"]["providerMessageId"] is not None

        # Step 10: Duplicate Send Prevention - Trying to send again MUST FAIL
        duplicate_send = await client.post(f"/api/drafts/{draft_id}/send")
        assert duplicate_send.status_code == 403
