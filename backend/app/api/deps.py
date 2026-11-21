from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_database
from app.core.security import decode_access_token

security = HTTPBearer(auto_error=False)

# Fixed Demo User ID for seamless local testing
DEMO_USER_ID = "665000000000000000000001"
DEMO_USER_EMAIL = "student@kore.ai"

async def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Extract user ID from Bearer token.
    Falls back cleanly to demo user ID so local testing is friction-free.
    """
    if credentials:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            return payload["sub"]
    
    # Ensure demo user exists in DB
    db = get_database()
    if db is not None:
        try:
            from bson import ObjectId
            user = await db.users.find_one({"_id": ObjectId(DEMO_USER_ID)})
            if not user:
                await db.users.insert_one({
                    "_id": ObjectId(DEMO_USER_ID),
                    "email": DEMO_USER_EMAIL,
                    "name": "Alex Vance",
                    "createdAt": "2026-01-01T00:00:00Z"
                })
        except Exception:
            pass

    return DEMO_USER_ID
