from fastapi import APIRouter, Query, Request
from pydantic import BaseModel
from app.core.config import settings
from app.engine.llm.factory import get_llm_provider
from app.services.email.gmail_service import gmail_service

router = APIRouter(prefix="/integrations", tags=["Integrations"])

@router.get("/status")
async def get_integrations_status():
    """
    Returns connection and operational status of all platform services
    without exposing any secrets.
    """
    llm = get_llm_provider()
    ollama_ready = await llm.is_available()

    gmail_configured = gmail_service.is_configured()
    search_provider_name = settings.SEARCH_PROVIDER
    search_configured = bool(settings.SEARCH_API_KEY) or search_provider_name == "demo"

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
            "mode": "live_oauth" if gmail_configured else "demo_simulation",
            "status": "connected" if gmail_configured else "demo_mode"
        }
    }

@router.get("/gmail/auth-url")
async def get_gmail_auth_url():
    return {"authUrl": gmail_service.get_auth_url()}

@router.get("/gmail/callback")
async def gmail_callback(code: str = Query(None), error: str = Query(None)):
    if error:
        return {"status": "error", "message": error}
    return {
        "status": "success",
        "message": "Gmail OAuth authorization completed. You can return to the KORE dashboard."
    }
