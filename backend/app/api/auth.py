from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from app.core.config import settings
from app.core.database import get_database
from app.core.security import create_access_token, verify_password, get_password_hash
from app.api.deps import DEMO_USER_ID, DEMO_USER_EMAIL

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters.")
    name: str = Field(min_length=1, description="Full name is required.")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: dict

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest):
    """
    Registers a new student user account with a securely hashed password.
    Rejects duplicate email addresses with HTTP 409 Conflict.
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")

    existing_user = await db.users.find_one({"email": req.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists. Please log in."
        )

    new_user = {
        "email": req.email.lower(),
        "name": req.name.strip(),
        "hashed_password": get_password_hash(req.password),
        "createdAt": datetime.now(timezone.utc)
    }
    res = await db.users.insert_one(new_user)
    user_id = str(res.inserted_id)

    token = create_access_token(subject=user_id)
    return AuthResponse(
        accessToken=token,
        user={"id": user_id, "email": req.email.lower(), "name": req.name.strip()}
    )

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """
    Authenticates an existing user via password verification.
    Rejects nonexistent users and incorrect passwords with HTTP 401 Unauthorized.
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")

    user = await db.users.find_one({"email": req.email.lower()})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Strictly verify hashed password
    stored_hash = user.get("hashed_password")
    if not stored_hash or not verify_password(req.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = str(user["_id"])
    token = create_access_token(subject=user_id)
    return AuthResponse(
        accessToken=token,
        user={"id": user_id, "email": user["email"], "name": user.get("name", "User")}
    )

@router.get("/demo-session", response_model=AuthResponse)
async def demo_session():
    """
    Explicit development-only demo session endpoint.
    Strictly disabled and rejected in production environments.
    """
    if not settings.ALLOW_DEMO_AUTH or settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo authentication is strictly disabled in production environments."
        )

    db = get_database()
    if db is not None:
        # Ensure demo user exists in database with a valid ObjectId
        demo_user = await db.users.find_one({"_id": ObjectId(DEMO_USER_ID)})
        if not demo_user:
            await db.users.insert_one({
                "_id": ObjectId(DEMO_USER_ID),
                "email": DEMO_USER_EMAIL,
                "name": "Alex Vance (Demo Student)",
                "hashed_password": get_password_hash("demopassword123"),
                "createdAt": datetime.now(timezone.utc)
            })

    token = create_access_token(subject=DEMO_USER_ID)
    return AuthResponse(
        accessToken=token,
        user={"id": DEMO_USER_ID, "email": DEMO_USER_EMAIL, "name": "Alex Vance (Demo Student)"}
    )
