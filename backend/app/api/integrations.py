import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import get_database
from app.api.deps import get_current_user_id
from app.engine.llm.factory import get_llm_provider
from app.services.email.gmail_service import gmail_service

router = APIRouter(prefix="/integrations", tags=["Integrations"])

@router.get("/status")
async def get_integrations_status(user_id: str = Depends(get_current_user_id)):
    """
    Returns connection and operational status of all platform services
    scoped to the authenticated user, without exposing any secrets or tokens.
    """
    db = get_database()
    llm = get_llm_provider()
    ollama_ready = await llm.is_available()

    gmail_configured = gmail_service.is_configured()
    search_provider_name = settings.SEARCH_PROVIDER
    search_configured = bool(settings.SEARCH_API_KEY) or search_provider_name == "demo"

    # Check if this specific user has connected Gmail
    user_gmail_connected = False
    if db is not None:
        user_cred = await db.integrationCredentials.find_one({"userId": user_id, "provider": "gmail"})
        user_gmail_connected = user_cred is not None

    return {
        "ollama": {
            "name": "Ollama Local Inference",
            "model": settings.OLLAMA_MODEL,
            "connected": ollama_ready,
            "baseUrl": settings.OLLAMA_BASE_URL,
            "status": "ready" if ollama_ready else "unreachable"
        },
        "search": {
            "name": f"Search Provider ({search_provider_name.capitalize()})",
            "provider": search_provider_name,
            "isDemoMode": not bool(settings.SEARCH_API_KEY),
            "connected": search_configured,
            "status": "active"
        },
        "gmail": {
            "name": "Gmail API (OAuth 2.0)",
            "configured": gmail_configured,
            "userConnected": user_gmail_connected,
            "mode": "live_oauth" if (gmail_configured and settings.GMAIL_MODE != "demo") else "demo_simulation",
            "status": "connected" if user_gmail_connected else ("ready_to_connect" if gmail_configured else "demo_mode")
        }
    }

@router.get("/gmail/auth-url")
async def get_gmail_auth_url(user_id: str = Depends(get_current_user_id)):
    """
    Generates a secure OAuth authorization URL bound to a cryptographic CSRF state token.
    """
    db = get_database()
    state = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    
    if db is not None:
        await db.oauthStates.insert_one({
            "state": state,
            "userId": user_id,
            "createdAt": now,
            "expiresAt": now + timedelta(minutes=15)
        })

    return {"authUrl": gmail_service.get_auth_url(state=state), "state": state}

@router.get("/gmail/callback")
async def gmail_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """
    OAuth 2.0 callback endpoint.
    Strictly verifies the state parameter against database records to prevent CSRF,
    exchanges the authorization code for credentials, and stores them scoped to the user.
    """
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth authorization denied: {error}")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing required 'code' or 'state' parameter.")

    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")

    # 1. Look up and atomically consume the state token
    oauth_record = await db.oauthStates.find_one_and_delete({"state": state})
    if not oauth_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or previously used OAuth state parameter. Please retry from Integrations."
        )

    # Verify expiration (15 minutes)
    created_at = oauth_record.get("createdAt")
    if created_at and datetime.now(timezone.utc) - created_at.replace(tzinfo=timezone.utc) > timedelta(minutes=15):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state parameter has expired. Please retry."
        )

    user_id = oauth_record["userId"]

    # 2. Exchange authorization code for user credentials
    try:
        token_data = gmail_service.exchange_code(code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to exchange OAuth code for tokens: {str(e)}")

    # 3. Store credentials securely scoped to the user ID
    now = datetime.now(timezone.utc)
    await db.integrationCredentials.update_one(
        {"userId": user_id, "provider": "gmail"},
        {
            "$set": {
                "userId": user_id,
                "provider": "gmail",
                "tokens": token_data,
                "updatedAt": now
            }
        },
        upsert=True
    )

    return {
        "status": "success",
        "message": "Gmail account successfully connected. You can now send approved outreach emails.",
        "connectedAt": now.isoformat()
    }

@router.post("/gmail/disconnect")
async def disconnect_gmail(user_id: str = Depends(get_current_user_id)):
    """Disconnects the authenticated user's Gmail OAuth tokens."""
    db = get_database()
    if db is not None:
        await db.integrationCredentials.delete_one({"userId": user_id, "provider": "gmail"})
    return {"status": "success", "message": "Gmail account disconnected successfully."}
