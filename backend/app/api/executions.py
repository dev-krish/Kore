import asyncio
import json
import logging
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.core.database import get_database
from app.api.deps import get_current_user_id
from app.services.events import event_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Agent Executions"])

@router.get("/{execution_id}")
async def get_execution(execution_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    doc = await db.agentExecutions.find_one({"_id": ObjectId(execution_id), "userId": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Execution record not found")
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("/campaign/{campaign_id}")
async def get_campaign_latest_execution(campaign_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    doc = await db.agentExecutions.find_one(
        {"campaignId": campaign_id, "userId": user_id},
        sort=[("startedAt", -1)]
    )
    if not doc:
        return {"status": "none", "steps": [], "toolCalls": []}
    doc["_id"] = str(doc["_id"])
    return doc

@router.get("/{campaign_id}/events")
async def stream_execution_events(campaign_id: str, request: Request):
    """
    Server-Sent Events (SSE) endpoint for live agent step streaming,
    tool call observations, and progress updates.
    """
    queue = event_manager.subscribe(campaign_id)

    async def event_generator():
        try:
            # Yield initial connection confirmation
            yield f"data: {json.dumps({'type': 'connected', 'campaignId': campaign_id})}\n\n"
            while True:
                # Disconnect check
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat
                    yield f": heartbeat\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            event_manager.unsubscribe(campaign_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
