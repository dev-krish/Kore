from typing import Optional
from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_database
from app.core.security import decode_access_token
from app.core.config import settings

# HTTPBearer with auto_error=False so we can provide clean, standard 401 messages
security = HTTPBearer(auto_error=False)

DEMO_USER_ID = "665000000000000000000001"
DEMO_USER_EMAIL = "student@kore.ai"

async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Validates the Bearer token and returns the authenticated user ID.
    Rejects any unauthenticated or invalid request with HTTP 401.
    Does NOT silently fall back to demo user identity.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload["sub"]

    # Verify user exists in database
    db = get_database()
    if db is not None:
        try:
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account associated with this token no longer exists.",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            # Handle invalid ObjectId format
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token format.",
                headers={"WWW-Authenticate": "Bearer"}
            )

    return user_id
