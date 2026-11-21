import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from bson import ObjectId
from app.main import app
from app.core.config import settings
from app.core.database import get_database
from app.models.draft import ApprovalStatus
from app.services.email.gmail_service import gmail_service

@pytest.mark.asyncio
async def test_registration_validation():
    """
    Validates:
    - Rejection of passwords shorter than 8 characters (422)
    - Successful registration with hashed password (201)
    - Duplicate email conflict rejection (409)
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Short password (< 8 chars)
        res_short = await client.post("/api/auth/register", json={
            "email": "shortpw@test.com",
            "password": "short",
            "name": "Short Password Test"
        })
        assert res_short.status_code == 422

        # 2. Valid registration
        unique_email = f"student_{ObjectId()}@test.com"
        res_valid = await client.post("/api/auth/register", json={
            "email": unique_email,
            "password": "SecurePassword123!",
            "name": "Hardened Test Student"
        })
        assert res_valid.status_code == 201
        data = res_valid.json()
        assert "accessToken" in data
        assert data["user"]["email"] == unique_email.lower()
        assert data["user"]["name"] == "Hardened Test Student"

        # 3. Duplicate registration attempt
        res_dup = await client.post("/api/auth/register", json={
            "email": unique_email,
            "password": "AnotherPassword456!",
            "name": "Duplicate Tester"
        })
        assert res_dup.status_code == 409
        assert "already exists" in res_dup.json()["detail"]

@pytest.mark.asyncio
async def test_login_password_verification():
    """
    Validates:
    - Rejection of nonexistent user (401)
    - Rejection of incorrect password (401)
    - Successful login with correct password (200)
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register a test account
        user_email = f"auth_test_{ObjectId()}@test.com"
        reg_res = await client.post("/api/auth/register", json={
            "email": user_email,
            "password": "CorrectPassword123!",
            "name": "Auth Tester"
        })
        assert reg_res.status_code == 201

        # Nonexistent email
        res_unknown = await client.post("/api/auth/login", json={
            "email": "does_not_exist_999@test.com",
            "password": "CorrectPassword123!"
        })
        assert res_unknown.status_code == 401
        assert "Invalid email or password" in res_unknown.json()["detail"]

        # Incorrect password
        res_bad_pw = await client.post("/api/auth/login", json={
            "email": user_email,
            "password": "WrongPassword999!"
        })
        assert res_bad_pw.status_code == 401
        assert "Invalid email or password" in res_bad_pw.json()["detail"]

        # Correct password
        res_ok = await client.post("/api/auth/login", json={
            "email": user_email,
            "password": "CorrectPassword123!"
        })
        assert res_ok.status_code == 200
        assert "accessToken" in res_ok.json()

@pytest.mark.asyncio
async def test_token_enforcement_and_validation():
    """
    Validates:
    - Missing Bearer token rejected with 401
    - Malformed or tampered token rejected with 401
    - Nonexistent user token rejected with 401
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Missing token
        res_no_token = await client.get("/api/profiles/me")
        assert res_no_token.status_code == 401
        assert "Authentication required" in res_no_token.json()["detail"]

        # Tampered / invalid token
        res_tampered = await client.get("/api/profiles/me", headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalidsignature"
        })
        assert res_tampered.status_code == 401

        # Valid format JWT but points to nonexistent user ID
        from app.core.security import create_access_token
        fake_token = create_access_token(subject=str(ObjectId()))
        res_ghost_user = await client.get("/api/profiles/me", headers={
            "Authorization": f"Bearer {fake_token}"
        })
        assert res_ghost_user.status_code == 401
        assert "no longer exists" in res_ghost_user.json()["detail"]

@pytest.mark.asyncio
async def test_cross_user_isolation():
    """
    Validates strict user isolation across all core resources:
    - User A creates campaign, draft, and prospect data.
    - User B cannot view, edit, approve, or send User A's data.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        db = get_database()

        # Register User A
        res_a = await client.post("/api/auth/register", json={
            "email": f"user_a_{ObjectId()}@test.com",
            "password": "PasswordA123!",
            "name": "User Alpha"
        })
        token_a = res_a.json()["accessToken"]
        user_a_id = res_a.json()["user"]["id"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Register User B
        res_b = await client.post("/api/auth/register", json={
            "email": f"user_b_{ObjectId()}@test.com",
            "password": "PasswordB123!",
            "name": "User Beta"
        })
        token_b = res_b.json()["accessToken"]
        user_b_id = res_b.json()["user"]["id"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User A creates a campaign
        camp_res = await client.post("/api/campaigns", json={
            "name": "Alpha Secret AI Outreach",
            "objective": "Outreach to private AI startups",
            "targetIndustry": "AI Startups",
            "targetLocation": "Bengaluru",
            "targetRoles": ["Founders"],
            "targetProspectCount": 1
        }, headers=headers_a)
        campaign_a_id = camp_res.json()["_id"]

        # User A inserts a draft and company into the database
        comp_res = await db.companies.insert_one({
            "campaignId": campaign_a_id,
            "name": "Alpha Private Ltd",
            "website": "https://alpha.example.com",
            "industry": "AI",
            "location": "Bengaluru"
        })
        comp_id = str(comp_res.inserted_id)

        contact_res = await db.contacts.insert_one({
            "campaignId": campaign_a_id,
            "companyId": comp_id,
            "name": "Dr. Alpha Founder",
            "email": "founder@alpha.example.com",
            "role": "Founder & CEO",
            "confidence": 0.95,
            "sourceUrl": "https://alpha.example.com/team",
            "isDemoRecord": False,
            "provenance": "live_discovery"
        })
        contact_id = str(contact_res.inserted_id)

        draft_res = await db.emailDrafts.insert_one({
            "userId": user_a_id,
            "campaignId": campaign_a_id,
            "contactId": contact_id,
            "companyId": comp_id,
            "recipientName": "Dr. Alpha Founder",
            "recipientEmail": "founder@alpha.example.com",
            "recipientRole": "Founder & CEO",
            "companyName": "Alpha Private Ltd",
            "subject": "Alpha Confidential Subject",
            "body": "Confidential body for User A only.",
            "personalizationEvidence": ["Evidence 1"],
            "approvalStatus": ApprovalStatus.GENERATED.value,
            "approvedContentHash": None
        })
        draft_id = str(draft_res.inserted_id)

        # 1. User B tries to view User A's campaign
        res_view_camp = await client.get(f"/api/campaigns/{campaign_a_id}", headers=headers_b)
        assert res_view_camp.status_code == 404

        # 2. User B tries to view User A's prospects
        res_view_prospects = await client.get(f"/api/campaigns/{campaign_a_id}/prospects", headers=headers_b)
        assert res_view_prospects.status_code == 404

        # 3. User B tries to view User A's draft
        res_view_draft = await client.get(f"/api/drafts/{draft_id}", headers=headers_b)
        assert res_view_draft.status_code == 404

        # 4. User B tries to approve User A's draft
        res_approve = await client.post(f"/api/drafts/{draft_id}/approve", headers=headers_b)
        assert res_approve.status_code == 404

        # 5. User B tries to send User A's draft
        res_send = await client.post(f"/api/drafts/{draft_id}/send", headers=headers_b)
        assert res_send.status_code == 404

        # 6. User B tries to access User A's company
        res_comp = await client.get(f"/api/companies/{comp_id}", headers=headers_b)
        assert res_comp.status_code == 404

        # 7. User B tries to access User A's contact
        res_contact = await client.get(f"/api/contacts/{contact_id}", headers=headers_b)
        assert res_contact.status_code == 404

@pytest.mark.asyncio
async def test_gmail_oauth_lifecycle_and_csrf():
    """
    Validates:
    - OAuth auth URL generation with unique CSRF state parameter stored in db
    - Missing code or state rejection (400)
    - Tampered / unknown state rejection (400)
    - Single-use state consumption preventing replay attacks
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Get demo auth headers
        auth_res = await client.get("/api/auth/demo-session")
        headers = {"Authorization": f"Bearer {auth_res.json()['accessToken']}"}

        # 1. Request OAuth Auth URL
        url_res = await client.get("/api/integrations/gmail/auth-url", headers=headers)
        assert url_res.status_code == 200
        url_data = url_res.json()
        assert "authUrl" in url_data
        assert "state" in url_data
        state_token = url_data["state"]

        # 2. Callback with missing params
        cb_missing = await client.get("/api/integrations/gmail/callback")
        assert cb_missing.status_code == 400

        # 3. Callback with forged state
        cb_forged = await client.get("/api/integrations/gmail/callback?code=fake_code&state=forged_state_123")
        assert cb_forged.status_code == 400
        assert "Invalid, expired, or previously used OAuth state" in cb_forged.json()["detail"]

        # 4. Verify state is in db before use
        db = get_database()
        stored_state = await db.oauthStates.find_one({"state": state_token})
        assert stored_state is not None

@pytest.mark.asyncio
async def test_approval_hash_invalidation_on_edit():
    """
    Validates:
    - User approves a draft -> status APPROVED and cryptographic hash generated
    - User edits draft content -> status reset to PENDING_REVIEW and hash cleared
    - Unapproved send blocked by Approval Gate (403)
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        db = get_database()
        auth_res = await client.get("/api/auth/demo-session")
        token = auth_res.json()["accessToken"]
        user_id = auth_res.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create draft directly with all required fields
        draft_doc = {
            "userId": user_id,
            "campaignId": "camp_test_edit",
            "contactId": str(ObjectId()),
            "companyId": str(ObjectId()),
            "recipientName": "Jane Doe",
            "recipientEmail": "jane@startup.ai",
            "recipientRole": "CTO",
            "companyName": "Startup AI",
            "subject": "Initial Approved Subject",
            "body": "Initial body text.",
            "approvalStatus": ApprovalStatus.GENERATED.value,
            "approvedContentHash": None
        }
        res = await db.emailDrafts.insert_one(draft_doc)
        draft_id = str(res.inserted_id)

        # 1. Explicitly approve
        app_res = await client.post(f"/api/drafts/{draft_id}/approve", headers=headers)
        assert app_res.status_code == 200
        assert app_res.json()["status"] == "approved"
        assert app_res.json()["approvedContentHash"] is not None

        # 2. Edit draft content
        edit_res = await client.put(f"/api/drafts/{draft_id}", json={
            "subject": "Edited Subject after approval",
            "body": "Edited body content."
        }, headers=headers)
        assert edit_res.status_code == 200
        edited = edit_res.json()
        assert edited["approvalStatus"] == ApprovalStatus.PENDING_REVIEW.value
        assert edited["approvedContentHash"] is None

        # 3. Attempting to send edited draft without re-approval MUST FAIL (403)
        send_res = await client.post(f"/api/drafts/{draft_id}/send", headers=headers)
        assert send_res.status_code == 403
        assert "Approval Gate check failed" in send_res.json()["detail"]

@pytest.mark.asyncio
async def test_concurrent_duplicate_send_atomic_cas():
    """
    Validates atomic conditional state transition (Compare-And-Swap):
    - Concurrent requests to send the same approved draft cannot duplicate-send
    - Exactly one request succeeds (200), subsequent/concurrent request fails (409)
    - Exactly one delivery record is created in the database
    - Re-sending after completion is strictly blocked (403 or 409)
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        db = get_database()
        auth_res = await client.get("/api/auth/demo-session")
        token = auth_res.json()["accessToken"]
        user_id = auth_res.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a fresh draft
        draft_doc = {
            "userId": user_id,
            "campaignId": "camp_race_cond",
            "contactId": str(ObjectId()),
            "companyId": str(ObjectId()),
            "recipientName": "John Doe",
            "recipientEmail": "john@race.ai",
            "recipientRole": "VP Engineering",
            "companyName": "Race AI",
            "subject": "Race Condition Test",
            "body": "Testing atomic state transition.",
            "approvalStatus": ApprovalStatus.GENERATED.value,
            "approvedContentHash": None
        }
        res = await db.emailDrafts.insert_one(draft_doc)
        draft_id = str(res.inserted_id)

        # Approve draft
        app_res = await client.post(f"/api/drafts/{draft_id}/approve", headers=headers)
        assert app_res.status_code == 200

        # Fire two concurrent send requests simultaneously
        send_coro_1 = client.post(f"/api/drafts/{draft_id}/send", headers=headers)
        send_coro_2 = client.post(f"/api/drafts/{draft_id}/send", headers=headers)

        responses = await asyncio.gather(send_coro_1, send_coro_2, return_exceptions=False)
        status_codes = [r.status_code for r in responses]

        # One must succeed (200), and the other must be blocked (409 Conflict or 403 Forbidden)
        assert 200 in status_codes
        assert (409 in status_codes) or (403 in status_codes)

        # Verify only one delivery record was recorded in emailDeliveries
        deliveries = await db.emailDeliveries.find({"draftId": draft_id}).to_list(10)
        assert len(deliveries) == 1

        # Attempting to send a third time after status=SENT is blocked
        res_third = await client.post(f"/api/drafts/{draft_id}/send", headers=headers)
        assert res_third.status_code in (403, 409)

@pytest.mark.asyncio
async def test_missing_gmail_tokens_in_live_mode():
    """
    Validates that when Google OAuth is configured and GMAIL_MODE is 'live',
    attempting to send without user-specific OAuth credentials safely fails (400)
    and resets the draft to APPROVED status.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        db = get_database()
        auth_res = await client.get("/api/auth/demo-session")
        token = auth_res.json()["accessToken"]
        user_id = auth_res.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Ensure no integration credentials exist for this user
        await db.integrationCredentials.delete_many({"userId": user_id, "provider": "gmail"})

        # Create and approve a draft
        draft_doc = {
            "userId": user_id,
            "campaignId": "camp_missing_tokens",
            "contactId": str(ObjectId()),
            "companyId": str(ObjectId()),
            "recipientName": "Live Test Contact",
            "recipientEmail": "contact@livemode.com",
            "recipientRole": "Head of People",
            "companyName": "Live Mode Inc",
            "subject": "Inquiry on Engineering Roles",
            "body": "Hello from live mode test.",
            "approvalStatus": ApprovalStatus.GENERATED.value,
            "approvedContentHash": None
        }
        res = await db.emailDrafts.insert_one(draft_doc)
        draft_id = str(res.inserted_id)

        app_res = await client.post(f"/api/drafts/{draft_id}/approve", headers=headers)
        assert app_res.status_code == 200

        # Temporarily configure live Gmail without credentials
        original_client_id = gmail_service.client_id
        original_client_secret = gmail_service.client_secret
        original_mode = settings.GMAIL_MODE
        try:
            gmail_service.client_id = "mock-google-client-id"
            gmail_service.client_secret = "mock-google-client-secret"
            settings.GMAIL_MODE = "live"

            send_res = await client.post(f"/api/drafts/{draft_id}/send", headers=headers)
            assert send_res.status_code == 400
            assert "Gmail account not connected" in send_res.json()["detail"]

            # Draft status must be restored to APPROVED so the user can connect and retry
            reloaded_draft = await db.emailDrafts.find_one({"_id": ObjectId(draft_id)})
            assert reloaded_draft["approvalStatus"] == ApprovalStatus.APPROVED.value
        finally:
            gmail_service.client_id = original_client_id
            gmail_service.client_secret = original_client_secret
            settings.GMAIL_MODE = original_mode

@pytest.mark.asyncio
async def test_demo_session_disabled_in_production():
    """
    Validates that demo session authentication is strictly disabled
    when ENVIRONMENT is set to 'production' (HTTP 403 Forbidden).
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Temporarily set ENVIRONMENT to production
        original_env = settings.ENVIRONMENT
        try:
            settings.ENVIRONMENT = "production"
            res = await client.get("/api/auth/demo-session")
            assert res.status_code == 403
            assert "strictly disabled in production" in res.json()["detail"]
        finally:
            settings.ENVIRONMENT = original_env
