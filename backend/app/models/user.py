from datetime import datetime, timezone
from typing import Optional
from pydantic import EmailStr, Field
from app.models.common import BaseDBModel

class UserCreate(BaseDBModel):
    email: EmailStr
    name: str
    password: Optional[str] = "password123"

class UserResponse(BaseDBModel):
    id: str = Field(alias="_id")
    email: EmailStr
    name: str
    createdAt: datetime

class UserInDB(BaseDBModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    name: str
    hashed_password: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
