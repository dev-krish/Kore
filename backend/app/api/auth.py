from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.core.database import get_database
from app.core.security import create_access_token, verify_password, get_password_hash
from app.api.deps import DEMO_USER_ID, DEMO_USER_EMAIL

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: dict

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    db = get_database()
    user = await db.users.find_one({"email": req.email})
    if not user:
        # Create user on the fly for ease of use in MVP
        from bson import ObjectId
        new_user = {
            "email": req.email,
            "name": req.email.split("@")[0].capitalize(),
            "hashed_password": get_password_hash(req.password),
            "createdAt": datetime.now(timezone.utc)
        }
        res = await db.users.insert_one(new_user)
        user_id = str(res.inserted_id)
        user_name = new_user["name"]
    else:
        user_id = str(user["_id"])
        user_name = user.get("name", "User")

    token = create_access_token(subject=user_id)
    return AuthResponse(
        accessToken=token,
        user={"id": user_id, "email": req.email, "name": user_name}
    )

@router.get("/demo-session", response_model=AuthResponse)
async def demo_session():
    token = create_access_token(subject=DEMO_USER_ID)
    return AuthResponse(
        accessToken=token,
        user={"id": DEMO_USER_ID, "email": DEMO_USER_EMAIL, "name": "Alex Vance (Student)"}
    )
